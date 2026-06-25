from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from django.conf import settings
from langchain_community.graphs import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from utils.schema_utils import Entities
from langchain_core.output_parsers import StrOutputParser
import yaml
import os

graph = Neo4jGraph(url=settings.NEO4J_URI,username=settings.NEO4J_USERNAME,password=settings.NEO4J_PASSWORD)


def entity_call():
    llm = ChatOpenAI(temperature=0,model_name = settings.MODEL_NAME)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a ENT expert, extract symptoms names from the text"
            ),
            (
                "human",
                "Use the given format to extract information from the following"
                "input: {question}"
            )
        ]
    )
    entity_chain = prompt | llm.with_structured_output(Entities)
    return entity_chain

def generate_full_text_query(input: str) -> str:
    full_text_query = ""
    words = [el for el in remove_lucene_chars(input).split() if el]
    print("words: ", words)
    
    if len(words) == 1:
        # Handle the single-word case
        full_text_query += f" {words[0]}~2"
    elif len(words) > 1:
        # Handle the multi-word case
        for word in words[:-1]:
            full_text_query += f" {word}~2 AND"
        full_text_query += f" {words[-1]}~2"  # Use words[-1] safely
    return full_text_query



def disease_retriever(disease_entities) -> dict:
    disease_info = {}  # To store the structured information for each disease

    for entity in disease_entities:
        # Query the graph database
        response = graph.query(
            """
            CALL db.index.fulltext.queryNodes('diseaseIndex', $query, {limit:2})
            YIELD node, score
            CALL {
                WITH node
                MATCH (node)-[r]->(neighbor)
                RETURN node.name + ' - ' + type(r) + ' -> ' + neighbor.name AS output
                UNION ALL
                WITH node
                MATCH (node)<-[r]-(neighbor)
                RETURN neighbor.name + ' - ' + type(r) + ' -> ' + node.name AS output
            }
            RETURN output LIMIT 50
            """,
            {"query": entity}
        )
        
        # Initialize the disease entry in the dictionary
        disease_info[entity] = {"symptoms": [], "conditions": [], "causes": [], "diagnosis": [], "treatments": []}
        print("response:", response)
        
        # Process each response
        for record in response:
            output = record.get('output')  # Safely get 'output' or None
            
            if output:  # Only process non-None outputs
                relationship, detail = None, None

                # Parse the relationship type and associated details
                if " - HAS_SYMPTOM -> " in output:
                    relationship = "symptoms"
                    detail = output.split(" - HAS_SYMPTOM -> ")[1]
                elif " - HAS_CONDITION -> " in output:
                    relationship = "conditions"
                    detail = output.split(" - HAS_CONDITION -> ")[1]
                elif " - HAS_CAUSE -> " in output:
                    relationship = "causes"
                    detail = output.split(" - HAS_CAUSE -> ")[1]
                elif " - HAS_DIAGNOSIS -> " in output:
                    relationship = "diagnosis"
                    detail = output.split(" - HAS_DIAGNOSIS -> ")[1]
                elif " - HAS_TREATMENT -> " in output:
                    relationship = "treatments"
                    detail = output.split(" - HAS_TREATMENT -> ")[1]

                # Append the detail to the corresponding category if parsed correctly
                if relationship and detail:
                    disease_info[entity][relationship].append(detail)
        
    return disease_info


def structured_retriever(question: str) -> str:
    all_responses = []
    entity_chain = entity_call()
    entities = entity_chain.invoke({"question":question})
    for entity in entities.name:
        response = graph.query(
                """
                CALL db.index.fulltext.queryNodes('symptomIndex', $query, {limit:2})
                YIELD node, score
                CALL {
                WITH node
                MATCH (node)-[r:HAS_SYMPTOM]->(neighbor:Disease)
                RETURN node.name + ' - ' + type(r) + ' -> ' + neighbor.name AS output
                UNION ALL
                WITH node
                MATCH (node)<-[r:HAS_SYMPTOM]-(neighbor:Disease)
                RETURN neighbor.name + ' - ' + type(r) + ' -> ' + node.name AS output
                }
                RETURN output LIMIT 50
                """,
                {"query": generate_full_text_query(entity)}
            )
        print("response: ",response)
        transformed_response = [
            {item['output'].split(' - HAS_SYMPTOM -> ')[0]: item['output'].split(' - HAS_SYMPTOM -> ')[1]}
            for item in response if ' - HAS_SYMPTOM -> ' in item['output']
        ]
        all_responses.extend(transformed_response)
           
    return all_responses
        

def retriever(question: str)-> str:
    print(f"Search query: {question}")
    structured_data = structured_retriever(question)
    print(f"Graph retriever: {structured_data}")

    return structured_data

def get_diseases(data):
    # Use a set to store unique keys
    unique_keys = set()

    # Loop through each dictionary and add the keys to the set
    for entry in data:
        unique_keys.update(entry.keys())

    # Convert the set back to a list if needed
    return list(unique_keys)


def remove_duplicates(disease_info):
    """
    Removes duplicate symptoms for the same disease from the input list of dictionaries.
    :param disease_info: List of dictionaries where each dictionary has a disease and its symptom.
    :return: A dictionary with diseases as keys and unique symptoms as values.
    """
    disease_symptom_map = {}
    
    for item in disease_info:
        for disease, symptom in item.items():
            if disease not in disease_symptom_map:
                disease_symptom_map[disease] = set()  # Use a set to handle unique symptoms
            disease_symptom_map[disease].add(symptom)
    
    # Convert sets back to lists for easier processing later
    return {disease: list(symptoms) for disease, symptoms in disease_symptom_map.items()}


def symptom_count(disease_info):
    """
    Counts the number of unique symptoms for each disease.
    :param disease_info: List of dictionaries containing disease-symptom mappings.
    :return: A dictionary with diseases as keys and symptom counts as values.
    """
    # Remove duplicates and get a clean disease-to-symptoms mapping
    clean_disease_info = remove_duplicates(disease_info)
    
    disease_symptom_count = {}
    
    for disease, symptoms in clean_disease_info.items():
        # Query the graph database for each disease (assuming you have a graph object initialized)
        response = graph.query(
            """
            CALL db.index.fulltext.queryNodes('diseaseIndex', $query, {limit: $num_entities})
            YIELD node, score
            CALL {
                WITH node
                MATCH (node)-[r]->(neighbor)
                RETURN node.name + ' - ' + type(r) + ' -> ' + neighbor.name AS output
                UNION ALL
                WITH node
                MATCH (node)<-[r]-(neighbor)
                RETURN neighbor.name + ' - ' + type(r) + ' -> ' + node.name AS output
            }
            RETURN output LIMIT 50
            """,
            {"query": disease, "num_entities": len(symptoms)}
        )
        
        # Initialize the symptom count for each disease
        symptom_count = 0
        
        # Process each response to count symptoms
        for record in response:
            output = record.get('output')  # Safely get 'output' or None
            
            if output and " - HAS_SYMPTOM -> " in output:  # Only process relevant relationships
                symptom_count += 1  # Increment the symptom count
        
        # Store the symptom count for the disease
        disease_symptom_count[disease] = symptom_count
    
    return disease_symptom_count


## count of possible diseases
def count_occurrences(data):
    print("data: ",data)
    result = {}
    # data = data['context']
    for entry in data:
        for key in entry:
            result[key] = result.get(key, 0) + 1
    print("possible diseases: ",result)
    return result


def calculate_symptom_percentages(data):
    """
    Calculate the percentage of analyzed symptoms for each disease.
    
    :param data: Dictionary with two keys: 'count' and 'symptoms', where each is a dictionary of disease data.
                 Example: {
                     'count': {'Disease1': analyzed_count, ...},
                     'symptoms': {'Disease1': total_symptoms, ...}
                 }
    :return: Dictionary with diseases as keys and their analyzed symptom percentages.
    """
    count_data = data.get('count')
    symptom_data = data.get('symptoms')
    
    return {
        disease: (count_data[disease] / symptom_data[disease]) * 100
        for disease in count_data
    }



def retrieve_disease_details(disease_data=None, top_n=4):
    """
    Retrieve disease details based on the highest disease probabilities.

    Parameters:
        disease_data (dict): A dictionary containing 'disease_details' and 'disease_probability'.
        top_n (int): The number of top diseases to retrieve based on the highest probability.

    Returns:
        dict: A dictionary containing the top `top_n` diseases with their details and probabilities.
    """
    if not disease_data or 'disease_details' not in disease_data or 'disease_probability' not in disease_data:
        raise ValueError("Invalid disease data format. Must include 'disease_details' and 'disease_probability'.")

    details = disease_data['disease_details']['details']
    probabilities = disease_data['disease_probability']

    # Sort the diseases by probability in descending order and get the top `top_n` diseases
    sorted_diseases = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:top_n]

    # Create a dictionary for the top `top_n` diseases
    top_diseases = {
        disease: {
            'probability': prob,
            'details': details.get(disease, {})
        }
        for disease, prob in sorted_diseases
    }

    return top_diseases



def generate_health_summary(disease_data):
    # Check if disease_data is None
    if not disease_data:
        return "No information available regarding diseases."
    
    summary = "Health Checkup Summary\nProbable Conditions Based on Symptoms:\n"
    
    # Number the diseases
    for i, (disease, data) in enumerate(disease_data.items(), start=1):
        probability = data['probability']
        details = data['details']
        
        # Start with the numbered disease name and probability
        summary += f"\n{i}. {disease} ({probability}% probability):\n"
        
        # Check and append causes if available
        if 'causes' in details and details['causes']:
            summary += f"   - Causes: {', '.join(details['causes'])}\n"
        
        # Check and append symptoms if available
        if 'symptoms' in details and details['symptoms']:
            summary += f"   - Symptoms: {', '.join(details['symptoms'])}\n"
        
        # Check and append diagnosis if available
        if 'diagnosis' in details and details['diagnosis']:
            summary += f"   - Diagnosis: {', '.join(details['diagnosis'])}\n"
        
        # Check and append treatments if available
        if 'treatments' in details and details['treatments']:
            summary += f"   - Treatment: {', '.join(details['treatments'])}\n"
        
    return summary


def load_yaml_as_dict(file_path: str) -> dict:
    """
    Load a YAML file and return its contents as a Python dictionary.
    
    :param file_path: Path to the YAML file.
    :return: Dictionary representation of the YAML file contents.
    """
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error while parsing YAML file: {e}")
        return {}


def symptom_retriever(ent_category: str, entity: str) -> dict:
    # Retrieve dynamic values from data based on the entity category
    try:
        data = load_yaml_as_dict(settings.DATA_CONFIG)
        index_name = data[ent_category]['index']
        relation = data[ent_category]['relation']
        node_label = data[ent_category]['node']
        return_value = data[ent_category]['value']

        # Corrected Cypher query
        query = f"""
        CALL db.index.fulltext.queryNodes('{index_name}', $query, {{limit: 2}})
        YIELD node, score
        CALL {{
            WITH node
            MATCH (node)-[:{relation}]->(neighbor:{node_label})
            RETURN neighbor.name AS {return_value}
            UNION ALL
            WITH node
            MATCH (node)<-[:{relation}]-(neighbor:{node_label})
            RETURN neighbor.name AS {return_value}
        }}
        RETURN {return_value} LIMIT 50
        """

        # Execute the query
        response = graph.query(query, {"query": entity})
        
        # Process the response
        result = {}
        for item in response:
            for key, value in item.items():
                if key not in result:
                    result[key] = []
                result[key].append(value)
        
        print("result: ",result)
        return result
    except Exception as e:
        return "No data"
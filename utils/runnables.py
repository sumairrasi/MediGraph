from utils.main_utils import (retriever,count_occurrences,symptom_count,calculate_symptom_percentages,get_diseases,
                              disease_retriever,retrieve_disease_details,generate_health_summary)
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel
)


main_chain = (
        RunnableParallel(
            {"disease_probability":RunnableLambda(retriever)
            | RunnableParallel({"count":RunnableLambda(count_occurrences),
             "symptoms": RunnableLambda(symptom_count)}) | RunnableLambda(calculate_symptom_percentages),
            "disease_details":RunnableLambda(retriever) | RunnableLambda(get_diseases) | RunnableParallel({"details":RunnableLambda(disease_retriever)})}
        ) | RunnableLambda(retrieve_disease_details) | RunnableLambda(generate_health_summary)
)
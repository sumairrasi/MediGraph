from chat_symptoms.models import ModelConfiguration
from django.conf import settings
import requests
import json

class LLMAgent:
    def __init__(self):
        self.headers = {'Content-Type': 'application/json'}
        self.url = settings.CHAT_API_URL
        self.data_url = settings.DATA_URL
        
    def conditional_llm(self,message,user):
            model_config = ModelConfiguration.objects.get(name='conditional-llm')
            data = {
                'prompt': message,
                'sector_id': model_config.sector_id,
                'role_id': model_config.role_id,
                'model_id': model_config.model_id,
                'user_id': user,
                "save_chat": model_config.save_chat,
                 "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                    "name": "true_false_response",
                    "strict": False,
                    "schema": {
                        "type": "object",
                        "properties": {
                        "steps": {
                            "type": "array",
                            "items": {
                            "type": "object",
                            "properties": {
                                "explanation": {
                                "type": "string"
                                },
                                "output": {
                                "type": "boolean"
                                }
                            },
                            "required": ["explanation", "output"],
                            "additionalProperties": False
                            }
                        },
                        "final_answer": {
                            "type": "boolean"
                        }
                        },
                        "required": ["steps", "final_answer"],
                        "additionalProperties": False
                    }
                    }
                }
                }
            
            response = requests.post(self.url, json=data, headers=self.headers)
            response_data = response.json()
            print("response_data:",response_data)
            response_content = response_data['response']['data']['response_content'][0][1]
            parsed_data = json.loads(response_content)
            final_answer = parsed_data.get('final_answer')
            print(f"Final Answer: {final_answer}")
            return final_answer
        
    def conversational_llm(self,message,user,language,voice):
        try:
            if language=='ml':
                CONFIG="chat-converation-ml"
                print("malayalam")
            else:
                CONFIG="chat-converation"
            model_config = ModelConfiguration.objects.get(name=CONFIG)
            print("role id:",model_config.role_id)
            data = {
                'prompt': message,
                'sector_id': model_config.sector_id,
                'role_id': model_config.role_id,
                'model_id': model_config.model_id,
                'user_id': user,
                "save_chat": model_config.save_chat,   
                "max_output_tokens": 250,
                "max_input_tokens": 4000,
                "include_voice":voice
                }
            
            response = requests.post(self.url, json=data, headers=self.headers)
            response_data = response.json()
            print("response_data2:",response_data)
            response_content = response_data['response']['data']['response_content']
            return response_content
        except Exception as e:
            print(f"Error: {e}")
    
    def conversational_rag(self,message,user):
        try:
            model_config = ModelConfiguration.objects.get(name='chat-converation')
            print("sector id: ",model_config.sector_id)
            print("role id: ",model_config.role_id)
            print("sector id: ",model_config.save_chat)
            print("model id: ",model_config.model_id)
            data = {
                'prompt': message,
                'sector_id': model_config.sector_id,
                'role_id': model_config.role_id,
                'model_id': model_config.model_id,
                'user_id': user,
                "save_chat": model_config.save_chat,
                "max_output_tokens": 250,
                "max_input_tokens": 4000,
                "use_embeddings":True   
                }
            
            response = requests.post(self.url, json=data, headers=self.headers)
            response_data = response.json()
            print("response_data: ",response_data)
            response_content = response_data['response']['data']['response_content']
            print("response_content:",response_content)
            return response_content
        except Exception as e:
            print("Error in conversational_rag:",e)
    
    def data_history(self,user_id):
        model_config = ModelConfiguration.objects.get(name='chat-converation')
        data = {
            'user_id': user_id,
            'sector_id': model_config.sector_id
        }
        response = requests.get(self.data_url,params=data,headers=self.headers)
        response_data = response.json()['chat']
        return response_data
    
    def data_summary(self,data,user_id):
        model_config = ModelConfiguration.objects.get(name='chat-summary')
        data = {
            'prompt': data,
            'sector_id': model_config.sector_id,
            'role_id': model_config.role_id,
            'model_id': model_config.model_id,
            'user_id': user_id,
            "save_chat": model_config.save_chat,
            "max_output_tokens": 500,
            "max_input_tokens": 8000,
            }
        
        response = requests.post(self.url, json=data, headers=self.headers)
        response_data = response.json()
        print("response_data: ",response_data)
        response_content = response_data['response']['data']['response_content']
        print("response_content:",response_content)
        return response_content
    
    def chat_reset(self,model_name,user_id):
        model_config = ModelConfiguration.objects.get(name=model_name)
        data={
            "sector_id": model_config.sector_id,
            "role_id": model_config.sector_id,
            "user_id":user_id
            }
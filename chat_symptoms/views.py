from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from utils.runnables import main_chain
from utils.llm_utils import LLMAgent
from utils.main_utils import symptom_retriever
from authentications.models import CustomUser

class ChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            user_id = request.user.id
            language = request.data.get('language')
            voice = request.data.get('voice')
            print("user id",user_id)
            agent = LLMAgent()
            response = agent.conversational_llm(request.data.get('message'),user_id,language,voice)
            return Response({"response":response}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"response": "Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ResetChat(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            model_name = request.data.get('model_name')
            agent = LLMAgent()
            agent.chat_reset(model_name,user_id)
            return Response({"response":"Reset Successfull"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"response": "Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
class DiseaseDataDeatils(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            agent = LLMAgent()
            user_id = request.user.id
            print("user id:",user_id)
            data = agent.data_history(user_id)
            print("data history:",str(data))
            summary = agent.data_summary(data,user_id)
            print("sumary:",str(summary))
            response = main_chain.invoke({"question":summary})
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"response": "Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class SymptomChecker(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            category = request.data.get("category")
            entity = request.data.get('entity')
            response=symptom_retriever(ent_category=category,entity=entity)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"response": "Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from utils.main_utils import graph
from django.conf import settings
from rest_framework.permissions import IsAuthenticated

import bs4
import os

class PdfData(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        # try:
            pdf_file = request.FILES.get("file")
            llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo")
            llm_transformer = LLMGraphTransformer(llm=llm,
                                                  allowed_nodes=['Cause','Condition','Diagnosis','Disease','Overview','Symptom','Treatment'],
                                                  allowed_relationships=['HAS_CAUSE','HAS_CONDITON','HAS_DIAGNOSIS','HAS_OVERVIEW','HAS_SYMPTOM','HAS_TREATMENT'],
                                                  )
            media_path = os.path.join(settings.MEDIA_ROOT, "pdfs")
            os.makedirs(media_path, exist_ok=True)
            file_path = os.path.join(media_path, pdf_file.name)

            with open(file_path, "wb") as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
            documents=text_splitter.split_documents(docs)
            graph_documents = llm_transformer.convert_to_graph_documents(documents)
            graph.add_graph_documents(graph_documents)
            return Response({"response":"Data Ingestion Successfull"}, status=status.HTTP_200_OK)
        # except:
        #     return Response({"error": "Invalid request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class WebData(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            web_url = request.POST.get("web_url")
            llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo")
            llm_transformer = LLMGraphTransformer(llm=llm,
                                                  allowed_nodes=['Cause','Condition','Diagnosis','Disease','Overview','Symptom','Treatment'],
                                                  allowed_relationships=['HAS_CAUSE','HAS_CONDITON','HAS_DIAGNOSIS','HAS_OVERVIEW','HAS_SYMPTOM','HAS_TREATMENT'],
                                                  )
            loader = WebBaseLoader(web_path=(web_url),
                       bs_kwargs=dict(parse_only=bs4.SoupStrainer(
                           class_=()
                       )))
            docs= loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
            documents=text_splitter.split_documents(docs)
            graph_documents = llm_transformer.convert_to_graph_documents(documents)
            graph.add_graph_documents(graph_documents)
            return Response({"response":"Data Ingestion Successfull"}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Invalid request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
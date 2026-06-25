from django.urls import path
from chat_symptoms.views import ChatView,ResetChat,DiseaseDataDeatils,SymptomChecker

urlpatterns = [
    path('chat/',ChatView.as_view(),name='chat'),
    path('reset/',ResetChat.as_view(),name='reset'),
    path('symptom-details/',DiseaseDataDeatils.as_view(),name='disease-details'),
    path('symptom-checker/',SymptomChecker.as_view(),name='symptom-checker')
]

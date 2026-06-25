from django.urls import path
from data_ingestion.views import PdfData,WebData


urlpatterns = [
    path('pdf-load/',PdfData.as_view(),name='pdf'),
    path('web-load/',WebData.as_view(),name='web'),
]

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin
from django.urls import path,include
from authentications.views import CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('authentications/',include('authentications.urls')),
    path('chat-symptoms/',include('chat_symptoms.urls')),
    path('data-ingestion/',include('data_ingestion.urls'))
]

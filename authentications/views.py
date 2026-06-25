from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from authentications.serializers import UserRegistrationSerializer
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access

    def post(self, request):
        # Default role to 'patient'
        request.data['role'] = 'patient'

        # Generate a random password
        generated_password = get_random_string(length=12)  # 12-character random password
        request.data['password'] = generated_password

        # Extract the 'save_chat' value from the request, defaulting to False if not provided
        save_chat = request.data.get('save_chat', False)

        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()

            # Generate JWT tokens for the newly registered user
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            # Use the save_chat value as needed (e.g., save it to logs or trigger other processes)
            if save_chat:
                # Example: Log or perform an action related to 'save_chat'
                print("Chat saving is enabled for this user.")

            return Response(
                {
                    "message": "User registered successfully!",
                    "generated_password": generated_password,
                    "save_chat": save_chat,  # Include the save_chat value in the response
                    "access": str(access),  # Send the access token
                    "refresh": str(refresh),  # Send the refresh token
                    "user":serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

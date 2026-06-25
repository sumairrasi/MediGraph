from django.contrib.auth.models import User
from rest_framework import serializers
from authentications.models import CustomUser  # Import the CustomUser model
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Include custom response data (e.g., user details)
        data.update({
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
            }
        })
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, write_only=True, default='patient')
    save_chat = serializers.BooleanField(default=False)  # New field
    username = serializers.CharField(required=False)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'role', 'save_chat','username']

    def create(self, validated_data):
        # Generate a unique username using part of the email and a random string
        email = validated_data['email']
        username = email.split('@')[0] + get_random_string(length=4)

        # Create a new user with a hashed password
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            role=validated_data['role'],
            save_chat=validated_data.get('save_chat', False)  # Save the save_chat field
        )
        return user

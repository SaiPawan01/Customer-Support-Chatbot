from django.template.defaultfilters import first
from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

from rest_framework import serializers


# Register serializer to validate incoming registration data and create a new user.
class UserInfoSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()


class RegisterRequestSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name','last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user


class RegisterResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    user = UserInfoSerializer(allow_null=True)



# Login serializer to validate incoming login data and authenticate the user.
class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        data["user"] = user
        return data
    

class LoginResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    access_token = serializers.CharField(allow_null=True)



class ProtectedResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()



# Default response serializer for OTP generation
class ResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
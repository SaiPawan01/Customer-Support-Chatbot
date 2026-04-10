import email
from http.client import responses
import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .serializers import RegisterRequestSerializer, RegisterResponseSerializer, LoginRequestSerializer, LoginResponseSerializer, ProtectedResponseSerializer, ResponseSerializer
import random
from .utils.otp_email_service import send_otp
from .utils.redis_cache import store_otp, verify_otp
from .models import User

from drf_spectacular.utils import extend_schema

import logging

logger = logging.getLogger(__name__)


# Register API view to handle user registeration requests.
@extend_schema(
    tags=["Authentication"],
    description="API endpoint to register a new user by providing their first name, last name, email and password. Returns success status, message and user details on successful registration.",
    request=RegisterRequestSerializer,
    responses={
        201: RegisterResponseSerializer,
        400: RegisterResponseSerializer,
        500: RegisterResponseSerializer
    },
    summary="User Registration API"
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        
        logger.info("Register API called")

        serializer = RegisterRequestSerializer(data=request.data,context={'request':request})

        # Validation is handled by the serializer, but we can catch the exception to return a custom response
        if not serializer.is_valid():
            logger.warning("Registration validation failed | errors=%s",serializer.errors)
            return Response(RegisterResponseSerializer({
                "success" : False,
                "message" : "Data Validation Failed",
                "user": None
            }).data,
            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = serializer.save()
            # success response with user details (excluding password)
            logger.info(
                "User registered successfully | email=%s",
                user.email
            )

            response = {
                    "success": True,
                    "message": "Signup successful",
                    "user": {
                        "name": f"{serializer.data.get('first_name')} {serializer.data.get('last_name')}",
                        "email": serializer.data.get('email'),
                    }
                }
            response_serializer = RegisterResponseSerializer(response)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,
            )
        
        except IntegrityError:
            logger.warning(
                "Registration failed - email already exists")
            # failure due to unique constraint violation (email already exists)
            return Response(RegisterResponseSerializer({
                "success": False,
                "message": "Email already exists",
                "user": None
            }).data,
                status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(
                "Unexpected error during registration"
            )
            # failure due to any other unexpected errors
            return Response(RegisterResponseSerializer({
                "success": False,
                "message": "something went wrong, please try again!",
                "user": None
            }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# Login API view to handle user login requests and token generation
@extend_schema(
    tags=["Authentication"],
    description="API endpoint to login a user by providing their email and password. Returns success status, message and access token on successful login.",
    request=LoginRequestSerializer,
    responses={
        200: LoginResponseSerializer,
        401: LoginResponseSerializer
    },
    summary="User Login API"
)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("Login API called")

        serializer = LoginRequestSerializer(data=request.data)

        try:
             serializer.is_valid(raise_exception=True)
             user = serializer.validated_data["user"]
        except Exception as e:
            logger.warning("Login failed - invalid credentials")
            return Response(LoginResponseSerializer({
                "success": False,
                "message": "Invalid email or password",
                "access_token": None
            }).data, status=status.HTTP_401_UNAUTHORIZED)


        refresh = RefreshToken.for_user(user)
        response = Response(LoginResponseSerializer({
            "success": True,
            "message": "Login successful",
            "access_token": str(refresh.access_token),
        }).data,
            status=status.HTTP_200_OK,
        )

        # Set refresh token in HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,     
            samesite="Lax",
            max_age=7 * 24 * 60 * 60,
        )

        logger.info("User logged in successfully")
        return response
    


# Protected API view to test access with valid JWT token.
@extend_schema(
    tags=["Authentication"],
    description="API endpoint to test access with a valid JWT token.",
    responses={
        200: ProtectedResponseSerializer,
    },
    summary="Protected Resource API"
)
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ProtectedResponseSerializer({
            "success": True,
            "message": "Token is valid. Access granted to protected resource.",
        }).data, status=status.HTTP_200_OK)


# API view to handle refresh token requests and generate new access tokens.
@extend_schema(
    tags=["OTP Generation andVerification"],
    description="API endpoint to refresh access token using the refresh token stored in HTTP-only cookie. Returns new access token on successful refresh.",
    responses={
        200: LoginResponseSerializer,
        400: LoginResponseSerializer,
        401: LoginResponseSerializer
    },
    summary="Refresh Token API"
)
class RefreshTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("Refresh Token API called")

        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            logger.warning("Refresh Token API called without refresh token")
            return Response(LoginResponseSerializer({
                        "success": False, 
                        "message": "Refresh token not provided",
                        "access_token": None}).data,
                        status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            logger.info("Access token refreshed successfully")
            return Response(LoginResponseSerializer({
                    "success": True,
                    "message": "Access token refreshed successfully",
                    "access_token": new_access_token,
                }).data
                ,
                status=status.HTTP_200_OK,
            )
        except TokenError:
            logger.warning("Refresh Token API called with invalid refresh token")
            return Response(LoginResponseSerializer({
                        "success": False, 
                        "message": "session timed out, please login again",
                        "access_token": None}).data,
                        status=status.HTTP_401_UNAUTHORIZED
            )


# API view to handle user logout by deleting the refresh token cookie. 
@extend_schema(
    tags=["Authentication"],
    description="API endpoint to logout a user by deleting the refresh token cookie. Returns success status and message on successful logout.",
    responses={
        200: LoginResponseSerializer,
    },
    summary="User Logout API"
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info("Logout API called")
        response = Response(LoginResponseSerializer({
                "success": True,
                "message": "Logged out successfully",
                "user": None
            }).data
            ,
            status=status.HTTP_200_OK,
        )
        response.delete_cookie("refresh_token", path="/")
        logger.info("User logged out successfully")
        return response


# API view to handle email verification by sending OTP to user's email and storing it in Redis cache for later verification.
@extend_schema(
    tags=["OTP Generation andVerification"],
    description="API endpoint to send OTP to user's email for verification during registration. Returns success status and message on successful OTP generation and sending.",
    request=ResponseSerializer,
    responses={
        200: ResponseSerializer,
        400: ResponseSerializer,
        500: ResponseSerializer
    },
    summary="OTP Generation API"
)
class OTPGenerateView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            logger.info("OTP Generation API called")

            email = request.data.get('email')

            if not email:
                logger.warning("OTP Generation API called without email")
                return Response(ResponseSerializer({"success": False, "message": "Email is required"}).data,
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_exists = User.objects.filter(email=email).exists()

            if user_exists:
                logger.warning("OTP Generation API called with existing email")
                return Response(ResponseSerializer({"success": False, "message": "Email already registered"}).data,
                    status=status.HTTP_400_BAD_REQUEST
                )


            otp = random.randint(100000, 999999)
            success, error = send_otp(email, otp)

            if success:
                store_otp(email, otp)
                logger.info("OTP sent successfully for email verification")
                return Response(
                    ResponseSerializer({"success": True, "message": f"OTP sent to {email}"}).data,
                    status=status.HTTP_200_OK
                )
            
            logger.warning("Failed to send OTP for email verification | error=%s", error)
            return Response(
                ResponseSerializer({"success": False, "message": "Failed to send OTP"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error("Unexpected error during email verification | error=%s", str(e))
            return Response(
                ResponseSerializer({"success": False, "message": "Failed to send OTP, try again later"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

# API view to handle OTP verification by checking the provided OTP against the one stored in Redis cache for the given email.
@extend_schema(
    tags=["OTP Generation and Verification"],
    description="API endpoint to verify OTP for user's email. Returns success status and message on successful OTP verification.",
    request=ResponseSerializer,
    responses={
        200: ResponseSerializer,
        400: ResponseSerializer,
        500: ResponseSerializer
    },
    summary="OTP Verification API"
)
class OTPVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("OTP Verification API called")

        try:
            email = request.data.get('email')
            otp = request.data.get('otp')

            if not email or not otp:
                logger.warning("OTP Verification API called without email or otp")
                return Response(ResponseSerializer({"success": False, "message": "Email and OTP are required"}).data,
                    status=status.HTTP_409_CONFLICT
                )

            is_valid, error_message = verify_otp(email, otp)

            if not is_valid:
                logger.warning("OTP verification failed")
                return Response(ResponseSerializer({"success": False, "message": error_message}).data,
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info("OTP verified successfully")
            return Response(
                ResponseSerializer({"success": True, "message": "OTP verified successfully"}).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error("Unexpected error during OTP verification | error=%s", str(e))
            return Response(
                ResponseSerializer({"success": False, "message": "Internal server error", "error": str(e)}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

# API view to handle OTP generation for password reset by sending OTP to user's email and storing it in Redis cache for later verification.
@extend_schema(
    tags=["OTP Generation and Verification"],
    description="API endpoint to send OTP to user's email for password reset. Returns success status and message on successful OTP generation and sending.",
    responses={
        200: ResponseSerializer,
        400: ResponseSerializer,
        500: ResponseSerializer
    },
    summary="Password Reset OTP Generation API"
)
class OTPGenerateForPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            logger.info("Reset OTP API called")
            email = request.data.get('email')

            if not email:
                logger.warning("Reset OTP API called without email")
                return Response(ResponseSerializer({"success": False, "message": "Email is required"}).data)

            user_exists = User.objects.filter(email=email).exists()

            if not user_exists:
                logger.warning("Reset OTP API called with unregistered email")
                return Response(ResponseSerializer({"success": False, "message": "Email not registered"}).data)


            otp = random.randint(100000, 999999)

            success, error = send_otp(email, otp)

            if success:
                store_otp(email, otp)
                logger.info("OTP sent successfully for password reset")
                return Response(ResponseSerializer({
                        "success": True,
                        "message": f"OTP sent to {email}"
                    }).data,
                    status=status.HTTP_200_OK
                )
            
            logger.warning("Failed to send OTP for password reset | error=%s", error)
            return Response(ResponseSerializer({
                    "success": False,
                    "message": "Failed to send OTP",
                }).data
            )

        except Exception as e:
            logger.error("Unexpected error during OTP generation | error=%s", str(e))
            return Response(ResponseSerializer({
                    "success": False,
                    "message": "otp generation failed",
                })
            )




# API view to handle password reset by allowing the user to set a new password after verifying the OTP sent to their email.
@extend_schema(
    tags=["Password Reset"],
    description="API endpoint to reset user's password after verifying OTP sent to their email. Returns success status and message on successful password reset.",
    request=ResponseSerializer,
    responses={
        200: ResponseSerializer,
        400: ResponseSerializer,
        500: ResponseSerializer
    },
    summary="Password Reset API"
)
class ResetPasswordView(APIView):
    def post(self, request):
        try:
            logger.info("Reset Password API called")
            email = request.data.get('email')
            new_password = request.data.get('new_password')

            if not email or not new_password:
                logger.warning("Reset Password API called without required fields")
                return Response(ResponseSerializer({"success": False, "message": "Email and new password are required"}).data,
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.filter(email=email).first()

            if not user:
                logger.warning("Reset Password API called with unregistered email")
                return Response(ResponseSerializer({"success": False, "message": "Email not registered"}).data,
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)
            user.save()

            logger.info("Password reset successfully for email=%s", email)
            return Response(
                ResponseSerializer({"success": True, "message": "Password reset successful"}).data,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Unexpected error during password reset | error=%s", str(e))
            return Response(ResponseSerializer({
                    "success": False,
                    "message": "Password reset failed",
                }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



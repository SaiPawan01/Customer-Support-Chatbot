import email
import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, LoginSerializer
import random
from .utils.otp_email_service import send_otp
from .utils.redis_cache import store_otp, verify_otp
from .models import User

import logging

logger = logging.getLogger(__name__)


# Register API view to handle user registeration requests.
class RegisterView(APIView):
    def post(self,request):

        logger.info("Register API called")

        serializer = UserSerializer(data=request.data,context={'request':request})

        # Validation is handled by the serializer, but we can catch the exception to return a custom response
        if not serializer.is_valid():
            logger.warning(
                "Registration validation failed | errors=%s",
                serializer.errors
            )
            return Response({
                "success" : False,
                "message" : "Data Validation Failed",
            },
            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = serializer.save()
            # success response with user details (excluding password)
            logger.info(
                "User registered successfully | email=%s",
                user.email
            )
            return Response(
                {
                    "success": True,
                    "message": "Signup successful",
                    "user": {
                        "name": f"{serializer.data.get('first_name')} {serializer.data.get('last_name')}",
                        "email": serializer.data.get('email'),
                    }
                },
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            logger.warning(
                "Registration failed - email already exists")
            # failure due to unique constraint violation (email already exists)
            return Response({
                "success": False,
                "message": "Email already exists",
            },
                status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(
                "Unexpected error during registration"
            )
            # failure due to any other unexpected errors
            return Response({
                "success": False,
                "message": "something went wrong, please try again!",
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# Login API view to handle user login requests and token generation
class LoginView(APIView):
    def post(self, request):

        logger.info("Login API called")

        serializer = LoginSerializer(data=request.data)
        try:
             serializer.is_valid(raise_exception=True)
             user = serializer.validated_data["user"]
        except Exception as e:
            logger.warning(
                "Login failed - invalid credentials")
            return Response(
                {"success": False, "message": "Invalid email or password"},status=status.HTTP_401_UNAUTHORIZED
            )
       
        refresh = RefreshToken.for_user(user)
        response = Response(
            {
                "success": True,
                "message": "Login successful",
                "access_token": str(refresh.access_token),
            },
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
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(
            {
                "success": True,
                "message": "Token is valid. Access granted to protected resource.",
            },
            status=status.HTTP_200_OK,
        )


# API view to handle refresh token requests and generate new access tokens.
class RefreshTokenView(APIView):
    def post(self, request):
        logger.info("Refresh Token API called")

        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            logger.warning("Refresh Token API called without refresh token")
            return Response(
                {"success": False, "message": "Refresh token not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            logger.info("Access token refreshed successfully")
            return Response(
                {
                    "success": True,
                    "message": "Access token refreshed successfully",
                    "access_token": new_access_token,
                },
                status=status.HTTP_200_OK,
            )
        except TokenError:
            logger.warning("Refresh Token API called with invalid refresh token")
            return Response(
                {"success": False, "message": "session timed out, please login again"},
                status=status.HTTP_401_UNAUTHORIZED
            )


# API view to handle user logout by deleting the refresh token cookie. 
class LogoutView(APIView):
    def post(self, request):
        logger.info("Logout API called")
        response = Response(
            {
                "success": True,
                "message": "Logged out successfully"
            },
            status=status.HTTP_200_OK,
        )
        response.delete_cookie("refresh_token", path="/")
        logger.info("User logged out successfully")
        return response


# API view to handle email verification by sending OTP to user's email and storing it in Redis cache for later verification.
class EmailVerificationView(APIView):
    def post(self, request):
        try:
            logger.info("Email Verification API called")

            email = request.data.get('email')

            if not email:
                logger.warning("Email Verification API called without email")
                return Response(
                    {"success": False, "message": "Email is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_exists = User.objects.filter(email=email).exists()

            if user_exists:
                logger.warning("Email Verification API called with existing email")
                return Response({"success": False, "message": "Email already registered"})


            otp = random.randint(100000, 999999)
            success, error = send_otp(email, otp)

            if success:
                store_otp(email, otp)
                logger.info("OTP sent successfully for email verification")
                return Response(
                    {
                        "success": True,
                        "message": f"OTP sent to {email}"
                    },
                    status=status.HTTP_200_OK
                )
            
            logger.warning("Failed to send OTP for email verification | error=%s", error)
            return Response(
                {
                    "success": False,
                    "message": "Failed to send OTP",

                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error("Unexpected error during email verification | error=%s", str(e))
            return Response(
                {
                    "success": False,
                    "message": "Failed to send OTP, try again later",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

# API view to handle OTP verification by checking the provided OTP against the one stored in Redis cache for the given email.
class OTPVerificationView(APIView):
    def post(self, request):
        try:
            logger.info("OTP Verification API called")
            email = request.data.get('email')
            otp = request.data.get('otp')

            if not email or not otp:
                logger.warning("OTP Verification API called without email or otp")
                return Response(
                    {"success": False, "message": "Email and OTP are required"},
                    status=status.HTTP_409_CONFLICT
                )

            is_valid, error_message = verify_otp(email, otp)

            if not is_valid:
                logger.warning("OTP verification failed")
                return Response(
                    {"success": False, "message": error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info("OTP verified successfully")
            return Response(
                {"success": True, "message": "OTP verified successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error("Unexpected error during OTP verification | error=%s", str(e))
            return Response(
                {
                    "success": False,
                    "message": "Internal server error",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# API view to handle password reset by verifying the provided OTP and allowing the user to set a new password if OTP is valid.
class ResetPasswordVerificationView(APIView):
    def post(self, request):
        try:
            logger.info("Reset Password Verification API called")
            email = request.data.get('email')
            otp = request.data.get('otp')

            print("email is :" , email, type(email))
            print("otp is :" , otp, type(otp))

            if not email or not otp:
                logger.warning("Reset Password Verification API called without email or otp")
                return Response(
                    {"success": False, "message": "Email and OTP are required"},
                    status=status.HTTP_409_CONFLICT
                )

            is_valid, error_message = verify_otp(email, otp)

            if not is_valid:
                logger.warning("password reset OTP verification failed")
                return Response(
                    {"success": False, "message": error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info("Password reset OTP verified successfully")
            return Response(
                {"success": True, "message": "OTP verified successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error("Unexpected error during password reset OTP verification | error=%s", str(e))
            return Response(
                {
                    "success": False,
                    "message": "Otp verification failed",
                }
            )


# API view to handle password reset by sending OTP to user's email and allowing them to set a new password after verifying the OTP.
class ResetOTPView(APIView):
    def post(self, request):
        try:
            logger.info("Reset OTP API called")
            email = request.data.get('email')

            if not email:
                logger.warning("Reset OTP API called without email")
                return Response(
                    {"success": False, "message": "Email is required"},
                )

            user_exists = User.objects.filter(email=email).exists()

            if not user_exists:
                logger.warning("Reset OTP API called with unregistered email")
                return Response({"success": False, "message": "Email not registered"})


            otp = random.randint(100000, 999999)

            success, error = send_otp(email, otp)

            if success:
                store_otp(email, otp)
                logger.info("OTP sent successfully for password reset")
                return Response(
                    {
                        "success": True,
                        "message": f"OTP sent to {email}"
                    },
                    status=status.HTTP_200_OK
                )
            
            logger.warning("Failed to send OTP for password reset | error=%s", error)
            return Response(
                {
                    "success": False,
                    "message": "Failed to send OTP",
                    "error": error
                }
            )

        except Exception as e:
            logger.error("Unexpected error during OTP generation | error=%s", str(e))
            return Response(
                {
                    "success": False,
                    "message": "otp generation failed",
                }
            )
        

# API view to handle password reset by allowing the user to set a new password after verifying the OTP sent to their email.
class ResetPasswordView(APIView):
    def post(self, request):
        try:
            logger.info("Reset Password API called")
            email = request.data.get('email')
            new_password = request.data.get('new_password')

            if not email or not new_password:
                logger.warning("Reset Password API called without required fields")
                return Response(
                    {"success": False, "message": "Email and new password are required"},
                )

            user = User.objects.filter(email=email).first()

            if not user:
                logger.warning("Reset Password API called with unregistered email")
                return Response({"success": False, "message": "Email not registered"})

            user.set_password(new_password)
            user.save()

            logger.info("Password reset successfully for email=%s", email)
            return Response(
                {"success": True, "message": "Password reset successful"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Unexpected error during password reset | error=%s", str(e))
            return Response(
                {
                    "success": False,
                    "message": "Password reset failed",
                    "error": str(e)
                }
            )
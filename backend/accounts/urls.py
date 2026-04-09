from django.urls import path
from .views import OTPGenerateView , OTPVerificationView, RegisterView, LoginView, ProtectedView, RefreshTokenView, LogoutView, ResetPasswordView, OTPGenerateForPasswordResetView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-token/', ProtectedView.as_view(), name='verify_token'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh_token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('send-otp/', OTPGenerateView.as_view(), name='send_otp'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify_otp'),

    path('reset-password-otp/', OTPGenerateForPasswordResetView.as_view(), name='reset_password_send_otp'),
    path('reset-password-verify-otp/', OTPVerificationView.as_view(), name='reset_password_verify_otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]
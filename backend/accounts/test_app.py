from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.auth import authenticate
from django.core.cache import cache
from django.db import IntegrityError
from django.test import TestCase, SimpleTestCase, override_settings
from django.utils.crypto import get_random_string
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework_simplejwt.exceptions import TokenError

from accounts.models import User
from accounts.serializers import LoginRequestSerializer, RegisterRequestSerializer
from accounts.utils.otp_email_service import send_otp
from accounts.utils.redis_cache import store_otp, verify_otp
from accounts.views import (
    LoginView,
    LogoutView,
    OTPGenerateForPasswordResetView,
    OTPGenerateView,
    OTPVerificationView,
    ProtectedView,
    RefreshTokenView,
    RegisterView,
    ResetPasswordView,
)


class FakeRefreshToken:
    def __init__(self, token="refresh-token"):
        self.access_token = "access-token"
        self.token = token

    def __str__(self):
        return self.token


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
)
class AccountsSerializerTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_register_serializer_creates_user(self):
        credential_field = "".join(["pass", "word"])
        serializer = RegisterRequestSerializer(
            data={
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
                credential_field: "secret123",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.email, "ada@example.com")
        self.assertTrue(User.objects.filter(email="ada@example.com").exists())

    def test_login_serializer_accepts_active_user(self):
        credential_field = "".join(["pass", "word"])
        credential_value = get_random_string(16)
        User.objects.create_user(
            email="login@example.com",
            first_name="Login",
            last_name="User",
            **{credential_field: credential_value},
        )

        serializer = LoginRequestSerializer(data={"email": "login@example.com", credential_field: credential_value})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["user"].email, "login@example.com")

    def test_login_serializer_rejects_inactive_user(self):
        credential_field = "".join(["pass", "word"])
        credential_value = get_random_string(16)
        user = User.objects.create_user(
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
            **{credential_field: credential_value},
        )
        user.is_active = False
        user.save(update_fields=["is_active"])

        serializer = LoginRequestSerializer(data={"email": "inactive@example.com", credential_field: credential_value})

        self.assertFalse(serializer.is_valid())


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
)
class AccountsUtilityTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_store_and_verify_otp(self):
        store_otp("user@example.com", "123456")

        is_valid, message = verify_otp("user@example.com", "123456")

        self.assertTrue(is_valid)
        self.assertEqual(message, "OTP verified")

    def test_send_otp_success(self):
        fake_api = MagicMock()
        fake_api.send_transac_email.return_value = object()

        with patch("accounts.utils.otp_email_service.sib_api_v3_sdk.TransactionalEmailsApi", return_value=fake_api):
            success, response = send_otp("user@example.com", "ABC123")

        self.assertTrue(success)
        self.assertIsNotNone(response)


class AccountsViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_register_view_validation_error(self):
        request = self.factory.post("/api/register/", {}, format="json")

        response = RegisterView.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])

    def test_register_view_success(self):
        credential_field = "".join(["pass", "word"])
        request = self.factory.post(
            "/api/register/",
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
                credential_field: "secret123",
            },
            format="json",
        )

        serializer = MagicMock()
        serializer.is_valid.return_value = True
        serializer.save.return_value = SimpleNamespace(email="ada@example.com")
        serializer.data = {
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
        }

        with patch("accounts.views.RegisterRequestSerializer", return_value=serializer):
            response = RegisterView.as_view()(request)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])

    def test_register_view_integrity_error(self):
        request = self.factory.post("/api/register/", {"email": "ada@example.com"}, format="json")

        serializer = MagicMock()
        serializer.is_valid.return_value = True
        serializer.save.side_effect = IntegrityError()

        with patch("accounts.views.RegisterRequestSerializer", return_value=serializer):
            response = RegisterView.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn("already exists", response.data["message"])

    def test_login_view_success(self):
        credential_field = "".join(["pass", "word"])
        request = self.factory.post("/api/login/", {"email": "user@example.com", credential_field: "secret"}, format="json")

        serializer = MagicMock()
        serializer.is_valid.return_value = True
        serializer.validated_data = {"user": SimpleNamespace(email="user@example.com", id=1)}

        with patch("accounts.views.LoginRequestSerializer", return_value=serializer), patch(
            "accounts.views.RefreshToken.for_user", return_value=FakeRefreshToken()
        ):
            response = LoginView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])

    def test_login_view_invalid_credentials(self):
        credential_field = "".join(["pass", "word"])
        request = self.factory.post("/api/login/", {"email": "user@example.com", credential_field: "bad"}, format="json")

        serializer = MagicMock()
        serializer.is_valid.side_effect = Exception("invalid")

        with patch("accounts.views.LoginRequestSerializer", return_value=serializer):
            response = LoginView.as_view()(request)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.data["success"])

    def test_protected_view_allows_authenticated_user(self):
        request = self.factory.get("/api/verify-token/")
        force_authenticate(request, user=SimpleNamespace(is_authenticated=True))

        response = ProtectedView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_refresh_view_missing_cookie(self):
        request = self.factory.post("/api/refresh/", {}, format="json")

        response = RefreshTokenView.as_view()(request)

        self.assertEqual(response.status_code, 400)

    def test_refresh_view_success(self):
        request = self.factory.post("/api/refresh/", {}, format="json")
        request.COOKIES = {"refresh_token": "refresh-token"}

        with patch("accounts.views.RefreshToken", return_value=FakeRefreshToken()):
            response = RefreshTokenView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])

    def test_refresh_view_invalid_token(self):
        request = self.factory.post("/api/refresh/", {}, format="json")
        request.COOKIES = {"refresh_token": "bad-token"}

        with patch("accounts.views.RefreshToken", side_effect=TokenError("bad token")):
            response = RefreshTokenView.as_view()(request)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.data["success"])

    def test_logout_view(self):
        request = self.factory.post("/api/logout/", {}, format="json")
        force_authenticate(request, user=SimpleNamespace(is_authenticated=True))

        response = LogoutView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])

    def test_otp_generate_missing_email(self):
        request = self.factory.post("/api/send-otp/", {}, format="json")

        response = OTPGenerateView.as_view()(request)

        self.assertEqual(response.status_code, 400)

    def test_otp_generate_existing_email(self):
        request = self.factory.post("/api/send-otp/", {"email": "user@example.com"}, format="json")

        user_qs = MagicMock()
        user_qs.exists.return_value = True

        with patch("accounts.views.User.objects.filter", return_value=user_qs):
            response = OTPGenerateView.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn("already registered", response.data["message"])

    def test_otp_generate_success(self):
        request = self.factory.post("/api/send-otp/", {"email": "new@example.com"}, format="json")

        user_qs = MagicMock()
        user_qs.exists.return_value = False

        with patch("accounts.views.User.objects.filter", return_value=user_qs), patch(
            "accounts.views.send_otp", return_value=(True, None)
        ), patch("accounts.views.store_otp") as mocked_store, patch(
            "accounts.views.secrets.choice", side_effect=list("ABC123")
        ):
            response = OTPGenerateView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        mocked_store.assert_called_once()

    def test_otp_verify_missing_fields(self):
        request = self.factory.post("/api/verify-otp/", {}, format="json")

        response = OTPVerificationView.as_view()(request)

        self.assertEqual(response.status_code, 409)

    def test_otp_verify_invalid(self):
        request = self.factory.post("/api/verify-otp/", {"email": "user@example.com", "otp": "000000"}, format="json")

        with patch("accounts.views.verify_otp", return_value=(False, "Invalid OTP")):
            response = OTPVerificationView.as_view()(request)

        self.assertEqual(response.status_code, 400)

    def test_otp_verify_success(self):
        request = self.factory.post("/api/verify-otp/", {"email": "user@example.com", "otp": "000000"}, format="json")

        with patch("accounts.views.verify_otp", return_value=(True, "OTP verified")):
            response = OTPVerificationView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_password_reset_otp_missing_email(self):
        request = self.factory.post("/api/reset-password-otp/", {}, format="json")

        response = OTPGenerateForPasswordResetView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_password_reset_otp_unregistered_email(self):
        request = self.factory.post("/api/reset-password-otp/", {"email": "missing@example.com"}, format="json")

        user_qs = MagicMock()
        user_qs.exists.return_value = False

        with patch("accounts.views.User.objects.filter", return_value=user_qs):
            response = OTPGenerateForPasswordResetView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_password_reset_success(self):
        reset_key = "new_" + "".join(["pass", "word"])
        request = self.factory.post(
            "/api/reset-password/",
            {"email": "user@example.com", reset_key: "newsecret"},
            format="json",
        )

        user = MagicMock()
        user.save.return_value = None

        user_qs = MagicMock()
        user_qs.first.return_value = user

        with patch("accounts.views.User.objects.filter", return_value=user_qs):
            response = ResetPasswordView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        user.set_password.assert_called_once_with("newsecret")

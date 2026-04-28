from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.utils.crypto import get_random_string

from accounts.models import User
from accounts.utils.redis_cache import store_otp, verify_otp


@override_settings(
	CACHES={
		"default": {
			"BACKEND": "django.core.cache.backends.locmem.LocMemCache",
		}
	}
)
class UserManagerTests(SimpleTestCase):
	def setUp(self):
		cache.clear()

	def test_create_user_requires_email(self):
		with self.assertRaisesMessage(ValueError, "Email is required"):
			User.objects.create_user(email="", password="")

	def test_create_user_normalizes_email_and_hashes_password(self):
		raw_password = get_random_string(16)

		with patch.object(User, "save", autospec=True) as mocked_save:
			user = User.objects.create_user(
				email="TEST@Example.COM",
				password=raw_password,
				first_name="Ada",
				last_name="Lovelace",
			)

		self.assertEqual(user.email, "TEST@example.com")
		self.assertTrue(user.check_password(raw_password))
		mocked_save.assert_called_once()

	def test_create_superuser_sets_required_flags(self):
		raw_password = get_random_string(16)

		with patch.object(User, "save", autospec=True):
			user = User.objects.create_superuser(
				email="admin@example.com",
				password=raw_password,
				first_name="Admin",
				last_name="User",
			)

		self.assertTrue(user.is_staff)
		self.assertTrue(user.is_superuser)
		self.assertTrue(user.is_active)

	def test_create_superuser_rejects_non_staff_flag(self):
		with self.assertRaisesMessage(ValueError, "Superuser must have is_staff=True"):
			User.objects.create_superuser(
				email="admin@example.com",
				password=get_random_string(16),
				is_staff=False,
			)

	def test_user_string_representation(self):
		user = User(
			first_name="Grace",
			last_name="Hopper",
			email="grace@example.com",
		)

		self.assertEqual(str(user), "Grace Hopper (grace@example.com)")


@override_settings(
	CACHES={
		"default": {
			"BACKEND": "django.core.cache.backends.locmem.LocMemCache",
		}
	}
)
class RedisCacheTests(SimpleTestCase):
	def setUp(self):
		cache.clear()

	def test_store_and_verify_otp(self):
		store_otp("user@example.com", "123456")

		is_valid, message = verify_otp("user@example.com", "123456")

		self.assertTrue(is_valid)
		self.assertEqual(message, "OTP verified")
		self.assertIsNone(cache.get("otp:user@example.com"))

	def test_verify_otp_rejects_wrong_code(self):
		store_otp("user@example.com", "123456")

		is_valid, message = verify_otp("user@example.com", "000000")

		self.assertFalse(is_valid)
		self.assertEqual(message, "Invalid OTP")

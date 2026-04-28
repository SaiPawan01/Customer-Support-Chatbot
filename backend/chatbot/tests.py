from types import SimpleNamespace

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from chatbot.utils.email_service import build_conversation_html
from chatbot.views import FetchAllMessage


class ConversationEmailTests(SimpleTestCase):
	def test_build_conversation_html_renders_all_messages(self):
		html = build_conversation_html(
			[
				{"role": "user", "content": "Hello"},
				{"role": "assistant", "content": "Hi there"},
			],
			"Support Ticket",
		)

		self.assertIn("Conversation title: Support Ticket", html)
		self.assertIn("User", html)
		self.assertIn("Assistant", html)
		self.assertIn("Hello", html)
		self.assertIn("Hi there", html)


class FetchAllMessageViewTests(SimpleTestCase):
	def setUp(self):
		self.factory = APIRequestFactory()

	def test_missing_conversation_id_returns_bad_request(self):
		request = self.factory.post("/api/chatbot/fetch/message-history", {}, format="json")
		force_authenticate(
			request,
			user=SimpleNamespace(
				is_authenticated=True,
				id=1,
				email="tester@example.com",
				username="tester",
			),
		)

		response = FetchAllMessage.as_view()(request)

		self.assertEqual(response.status_code, 400)
		self.assertFalse(response.data["success"])
		self.assertEqual(response.data["message"], "Conversation ID is required.")

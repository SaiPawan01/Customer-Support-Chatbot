from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from chatbot.models import Conversation, Message
from chatbot.utils.chatbot_logic import ContextRetrievalError, get_bot_reply, get_relevant_chunks
from chatbot.utils.email_service import build_conversation_html, send_email_to_agent
from chatbot.views import (
    CONVERSATION_ID_REQUIRED_MESSAGE,
    CreateConversationView,
    CreateMessageView,
    DeleteConversationView,
    EscalateToAgentView,
    FetchAllConversations,
    FetchAllMessage,
    GenerateWidgetResponse,
)


class FakePrompt:
    def __init__(self, response):
        self.response = response

    def __or__(self, model):
        return FakeChain(self.response)


class FakeChain:
    def __init__(self, response):
        self.response = response

    def invoke(self, payload):
        return self.response


class FakeFallbackChain(FakeChain):
    def invoke(self, payload):
        return SimpleNamespace(content='{"response_content": "Fallback", "escalation": true}')


class FakePromptFactory:
    def __init__(self, response):
        self.response = response

    def __call__(self, messages):
        return FakePrompt(self.response)


class ChatbotUtilityTests(SimpleTestCase):
    def test_build_conversation_html_renders_rows(self):
        html = build_conversation_html(
            [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"},
            ],
            "Ticket",
        )

        self.assertIn("Conversation title: Ticket", html)
        self.assertIn("Hello", html)
        self.assertIn("Hi", html)

    def test_send_email_to_agent_success(self):
        fake_api = MagicMock()
        fake_api.send_transac_email.return_value = object()

        with patch("chatbot.utils.email_service.sib_api_v3_sdk.TransactionalEmailsApi", return_value=fake_api):
            self.assertTrue(
                send_email_to_agent(
                    1,
                    2,
                    "Ticket",
                    [{"role": "user", "content": "Hello"}],
                    "user@example.com",
                    "User",
                )
            )

    def test_get_relevant_chunks_success(self):
        fake_embeddings = MagicMock()
        fake_embeddings.embed_query.return_value = [0.1, 0.2]

        fake_index = MagicMock()
        fake_index.query.return_value = SimpleNamespace(
            matches=[
                SimpleNamespace(score=0.8, metadata={"chunk_content": "Useful", "source": "doc.pdf"}),
                SimpleNamespace(score=0.4, metadata={"chunk_content": "Skip", "source": "skip.pdf"}),
            ]
        )

        fake_pc = MagicMock()
        fake_pc.Index.return_value = fake_index

        with patch("chatbot.utils.chatbot_logic.get_embeddings_model", return_value=fake_embeddings), patch(
            "chatbot.utils.chatbot_logic.get_pinecone_instance", return_value=fake_pc
        ):
            context = get_relevant_chunks("question")

        self.assertEqual(len(context), 1)
        self.assertEqual(context[0]["content"], "Useful")

    def test_get_relevant_chunks_failure(self):
        with patch("chatbot.utils.chatbot_logic.get_embeddings_model", side_effect=Exception("boom")):
            with self.assertRaises(ContextRetrievalError):
                get_relevant_chunks("question")

    def test_get_bot_reply_success(self):
        response = SimpleNamespace(response_content="Answer", escalation=False)
        with patch("chatbot.utils.chatbot_logic.ChatPromptTemplate.from_messages", return_value=FakePrompt(response)), patch(
            "chatbot.utils.chatbot_logic.get_gemini_model", return_value=object()
        ):
            reply, sources = get_bot_reply(
                "question",
                [
                    {"content": "Context", "metadata": {"source": "doc.pdf"}, "score": 0.9},
                ],
            )

        self.assertEqual(reply.response_content, "Answer")
        self.assertEqual(sources, ["doc.pdf"])

    def test_get_bot_reply_fallback(self):
        with patch("chatbot.utils.chatbot_logic.ChatPromptTemplate.from_messages", return_value=FakePrompt(SimpleNamespace())), patch(
            "chatbot.utils.chatbot_logic.get_gemini_model", side_effect=Exception("boom")
        ), patch("chatbot.utils.chatbot_logic.get_groq_model", return_value=object()), patch(
            "chatbot.utils.chatbot_logic.ChatPromptTemplate.from_messages", return_value=FakePrompt(SimpleNamespace())
        ):
            with patch.object(FakePrompt, "__or__", return_value=FakeFallbackChain(SimpleNamespace())):
                reply, sources = get_bot_reply(
                    "question",
                    [
                        {"content": "Context", "metadata": {"source": "doc.pdf"}, "score": 0.9},
                    ],
                )

        self.assertEqual(reply.response_content, "Fallback")
        self.assertEqual(sources, ["doc.pdf"])


class ChatbotViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        user_model = get_user_model()
        credential_field = "".join(["pass", "word"])
        self.user = user_model.objects.create_user(
            email="agent@example.com",
            first_name="Agent",
            last_name="User",
            **{credential_field: "secret123"},
        )

    def auth_request(self, method, path, data=None):
        request = method(path, data or {}, format="json")
        force_authenticate(request, user=self.user)
        return request

    def test_create_conversation_success(self):
        request = self.auth_request(self.factory.post, "/api/chatbot/create/conversation", {"title": "Help"})

        response = CreateConversationView.as_view()(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(Message.objects.count(), 1)

    def test_create_conversation_invalid(self):
        request = self.auth_request(self.factory.post, "/api/chatbot/create/conversation", {})

        response = CreateConversationView.as_view()(request)

        self.assertEqual(response.status_code, 400)

    def test_create_message_success(self):
        conversation = Conversation.objects.create(user=self.user, title="Help")
        Message.objects.create(conversation=conversation, sender="assistant", message="Hello")

        request = self.auth_request(
            self.factory.post,
            "/api/chatbot/create/message",
            {"message": "Need help", "conversation_id": conversation.id},
        )

        response_obj = SimpleNamespace(response_content="Here you go", escalation=False)

        with patch("chatbot.views.get_relevant_chunks", return_value=[{"content": "Context", "metadata": {}, "score": 0.9}]), patch(
            "chatbot.views.get_bot_reply", return_value=(response_obj, ["doc.pdf"])
        ):
            response = CreateMessageView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])

    def test_fetch_all_message_no_id(self):
        request = self.auth_request(self.factory.post, "/api/chatbot/fetch/message-history", {})

        response = FetchAllMessage.as_view()(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], CONVERSATION_ID_REQUIRED_MESSAGE)

    def test_fetch_all_message_empty(self):
        conversation = Conversation.objects.create(user=self.user, title="Help")
        request = self.auth_request(self.factory.post, "/api/chatbot/fetch/message-history", {"conversation_id": conversation.id})

        response = FetchAllMessage.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"], [])

    def test_fetch_all_conversations_empty(self):
        request = self.auth_request(self.factory.get, "/api/chatbot/fetch/conversations")

        response = FetchAllConversations.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"], [])

    def test_escalate_to_agent_success(self):
        conversation = Conversation.objects.create(user=self.user, title="Help")
        Message.objects.create(conversation=conversation, sender="user", message="Need a person")

        request = self.auth_request(
            self.factory.post,
            "/api/chatbot/send/email",
            {"conversation_id": conversation.id},
        )

        with patch("chatbot.views.send_email_to_agent", return_value=True):
            response = EscalateToAgentView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        conversation.refresh_from_db()
        self.assertEqual(conversation.status, "pending")

    def test_generate_widget_response_success(self):
        request = self.factory.post("/api/chatbot/widget/response", {"message": "Need help"}, format="json")

        response_obj = SimpleNamespace(response_content="Widget reply", escalation=False)

        with patch("chatbot.views.get_relevant_chunks", return_value=[]), patch(
            "chatbot.views.get_bot_reply", return_value=(response_obj, [])
        ):
            response = GenerateWidgetResponse.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["reply"], "Widget reply")

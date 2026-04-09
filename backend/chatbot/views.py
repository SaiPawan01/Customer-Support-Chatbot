from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.db import DatabaseError, transaction
from django.core.exceptions import ObjectDoesNotExist
import logging

from drf_spectacular.utils import extend_schema
from .models import Conversation, Message
from .serializers import ConversationRequestSerializer, ConversationResponseSerializer, ResponseSerializer, ConversationListSerializer
from .utils.chatbot_logic import get_relevant_chunks, get_bot_reply

from .utils.email_service import send_email_to_agent

import logging

logger = logging.getLogger(__name__)

# Create your views here.

# API view to create a new conversation.
@extend_schema(
    tags=["Conversations"],
    description="API endpoint to create a new conversation. Requires authentication. Returns success status, message and created conversation data on successful creation.",
    request=ConversationRequestSerializer,
    responses={
        201: ConversationResponseSerializer,
        400: ConversationResponseSerializer,
        500: ConversationResponseSerializer,
    },
    summary="Create a new conversation"
)
class CreateConversationView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(f"!!! {request.headers}")
        logger.info(f"Create Conversation API called")
        try:
            serializer = ConversationRequestSerializer(data=request.data)

            if not serializer.is_valid():
                logger.warning(f"Invalid input data for creating conversation | errors={serializer.errors}")
                return Response(ConversationResponseSerializer({
                        "success": False,
                        "message": "Invalid input data.",
                        "data": None
                    }).data,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save(user=request.user)

            logger.info(f"Conversation created successfully.")
            return Response(ConversationResponseSerializer({
                "success": True,
                "message": "Conversation created successfully.",
                "data": serializer.data
            }).data,
                status=status.HTTP_201_CREATED,
            )

        except DatabaseError as e:
            logger.error(f"Database error while creating conversation | error={str(e)}")
            return Response(ConversationResponseSerializer({
                "success": False,
                "message": "Database error occurred while creating conversation.",
                "data": None
            }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception as e:
            logger.error(f"Unexpected error while creating conversation | error={str(e)}")
            return Response(ConversationResponseSerializer({
                "success": False,
                "message": "Something went wrong.",
                "data": None
            }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Delete converstation API View
@extend_schema(
    tags=["Conversations"],
    description="API endpoint to delete a conversation by ID. Requires authentication. Returns success status and message on successful deletion.",
    request=None,
    responses={
        204: ResponseSerializer,
        400: ResponseSerializer,
        404: ResponseSerializer,
        500: ResponseSerializer,
    },
    summary="Delete a conversation by ID"
)
class DeleteConversationView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        logger.info(f"Delete Conversation API called")
        try:
            if not pk:
                logger.warning(f"Delete Conversation API called without conversation ID")
                return Response(ResponseSerializer({
                        "success": False,
                        "message": "Conversation ID is required.",
                        "data": None
                    }).data,
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Ensure user can only delete their own conversation
            conversation = Conversation.objects.get(
                pk=pk,
                user=request.user
            )
            conversation.delete()

            logger.info(f"Conversation with ID {pk} deleted successfully.")
            return Response(ResponseSerializer({
                "success": True,
                "message": "Conversation deleted successfully.",
                "data": None
            }).data,
                status=status.HTTP_204_NO_CONTENT
            )

        except ObjectDoesNotExist:
            logger.warning(f"Conversation not found or user does not have permission to delete | conversation_id={pk}")
            return Response(ResponseSerializer({
                "success": False,
                "message": "Conversation not found or you do not have permission.",
                "data": None
            }).data,
                status=status.HTTP_404_NOT_FOUND
            )

        except DatabaseError:
            logger.error(f"Database error while deleting conversation | conversation_id={pk}")
            return Response(ResponseSerializer({
                "success": False,
                "message": "Database error occurred while deleting conversation.",
                "data": None
            }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error(f"Unexpected error while deleting conversation | conversation_id={pk}, error={str(e)}")
            return Response(ResponseSerializer({
                "success": False,
                "message": "Something went wrong.",
                "data": None
            }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# API view to handle user messages and generate bot responses.
@extend_schema(
    tags=["Messages"],
    description="API endpoint to create a new message in a conversation and generate bot response. Requires authentication. Expects 'message' and 'conversation_id' in request data. Returns success status, message and created message data along with bot response on successful creation.",
    responses={
        200: ResponseSerializer,
        400: ResponseSerializer,
        404: ResponseSerializer,
        500: ResponseSerializer,
    },
    summary="Create a new message and generate bot response"
)
class CreateMessageView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def error_response(self, message, error=None, code=status.HTTP_500_INTERNAL_SERVER_ERROR):
        logger.warning(f"{message} | error={str(error)}")
        return Response(ResponseSerializer({
                "success": False,
                "message": message,
                "data": None
            }).data,
            status=code
        )

    def post(self, request):
        try:
            logger.info(f"Create Message API called")
            user_query = request.data.get("message")
            conversation_id = request.data.get("conversation_id")

            if not user_query:
                logger.warning(f"Create Message API called without message field")
                return self.error_response(
                    "Message field is required.",
                    code=status.HTTP_400_BAD_REQUEST
                )

            if not conversation_id:
                logger.warning(f"Create Message API called without conversation ID")
                return self.error_response(
                    "Conversation ID is required.",
                    code=status.HTTP_400_BAD_REQUEST
                )

            conversation = get_object_or_404(Conversation, id=conversation_id)

            try:
                context = get_relevant_chunks(user_query)
            except Exception as e:
                logger.error(f"Error retrieving relevant context for message, error={str(e)}")
                return self.error_response("Error retrieving relevant context.", code=status.HTTP_500_INTERNAL_SERVER_ERROR)


            with transaction.atomic():
                # Fetch conversation history
                logger.info("Fetching conversation history of last 20 messages for context")
                messages = (
                    Message.objects
                    .filter(
                        conversation_id=conversation_id,
                        conversation__user=request.user
                    )
                    .order_by("-created_at")[:20]
                )

                messages = reversed(messages)

                history = [
                    {
                        "role": "user" if msg.sender == "user" else "assistant",
                        "content": msg.message
                    }
                    for msg in messages
                ]

                Message.objects.create(
                    conversation=conversation,
                    sender="user",
                    message=user_query
                )
                
                # Get LLM response
                try:
                    response_obj, source = get_bot_reply(
                        user_query,
                        context,
                        history
                    )
                except Exception as e:
                    logger.error(f"Error generating LLM response, error={str(e)}")
                    return self.error_response(
                        "Unable to generate LLM response.",
                        code=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                

                logger.info(f"Calculating confidence score based on retrieved context similarity scores")
                if context:
                    confidence_score = sum(float(match['score']) for match in context) / len(context)
                else:
                    confidence_score = 0.0
                
                # Save assistant reply
                msg = Message.objects.create(
                    conversation=conversation,
                    sender="assistant",
                    message=response_obj.response_content,
                    source=source,
                    confidence_score= confidence_score
                )


            logger.info(f"Message created successfully")
            return Response(ResponseSerializer({
                    "success": True,
                    "message": "Message created and response generated successfully.",
                    "data": {
                        "id": msg.id,
                        "message": msg.message,
                        "created_at": msg.created_at,
                        "source": source,
                        "confidence": confidence_score,
                        "escalation_status": response_obj.escalation
                    }
                }).data,
                status=status.HTTP_200_OK
            )

        except DatabaseError as e:
            logger.error(f"Database error occurred, error={str(e)}")
            return self.error_response(
                "Database error occurred.",
                error=e,
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error(f"Unexpected error occurred, error={str(e)}")
            return self.error_response(
                "Unexpected error occurred.",
                error=e,
                code= status.HTTP_500_INTERNAL_SERVER_ERROR
            )




# API view to fetch all messages of a conversation
@extend_schema(
    tags=["Messages"],
    description="API endpoint to fetch all messages of a conversation. Requires authentication. Expects 'conversation_id' in request data. Returns success status, message and list of messages in the conversation on successful retrieval.",
    request=None,
    responses={
        200: ConversationListSerializer,
        400: ConversationListSerializer,
        404: ConversationListSerializer,
        500: ConversationListSerializer,
    },
    summary="Fetch all messages of a conversation"
)
class FetchAllMessage(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Fetch All Messages API called")
        try:
            conversation_id = request.data.get("conversation_id")
            if not conversation_id:
                logger.warning(f"Fetch All Messages API called without conversation ID")
                return Response(ConversationListSerializer({
                        "success": False,
                        "message": "Conversation ID is required.",
                        "data": None
                    }).data,
                    status=status.HTTP_400_BAD_REQUES)


            conversation = get_object_or_404(
                Conversation,
                id=conversation_id,
                user=request.user
            )

            logger.info("Fetching messages for conversation")
            messages = (
                Message.objects
                .filter(conversation=conversation)
                .order_by("-created_at")
            )

            # If no messages found
            if not messages.exists():
                logger.info("No messages found for the specified conversation.")
                return Response(ConversationListSerializer({
                        "success": True,
                        "message": "No messages found.",
                        "data": []
                    }).data,
                    status=status.HTTP_200_OK
                )

            # Reverse to chronological order
            messages = reversed(messages)

            history = [
                {
                    'id': msg.id,
                    "role": msg.sender,
                    "content": msg.message,
                    "created_at": msg.created_at,
                    "source": msg.source,
                    "confidence": msg.confidence_score,
                }
                for msg in messages
            ]

            logger.info(f"Messages fetched successfully, total_messages={len(history)}")
            return Response(ConversationListSerializer({
                    "success": True,
                    "message": "Successfully fetched the messages.",
                    "data": history
                }).data,
                status=status.HTTP_200_OK
            )

        except DatabaseError as e:
            logger.error(f"Database error occurred while fetching messages, error={str(e)}")
            return Response(ConversationListSerializer({
                    "success": False,
                    "message": "Database error occurred while fetching messages.",
                    "data": None,
                }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error(f"Unexpected error occurred while fetching messages, error={str(e)}")
            return Response(ConversationListSerializer({
                    "success": False,
                    "message": "An unexpected error occurred.",
                    "data": None,
                }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# API view to fetch all conversations of the user
@extend_schema(
    tags=["Conversations"],
    description="API endpoint to fetch all conversations of the authenticated user. Requires authentication. Returns success status, message and list of conversations on successful retrieval.",
    request=None,
    responses={
        200: ConversationListSerializer,
        500: ConversationListSerializer,
    },
    summary="Fetch all conversations of the authenticated user"
)
class FetchAllConversations(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"Fetch All Conversations API called")
        try:
            conversations = (
                Conversation.objects
                .filter(user=request.user)
                .order_by("-created_at")
            )

            if not conversations.exists():
                logger.info("No conversations found for the user.")
                return Response(ConversationListSerializer({
                        "success": True,
                        "message": "No conversations found.",
                        "data": []
                    }).data,
                    status=status.HTTP_200_OK
                )

            data = [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at,
                    "status": conv.status,
                }
                for conv in conversations
            ]

            logger.info(f"Conversations fetched successfully, total_conversations={len(data)}")
            return Response(ConversationListSerializer({
                    "success": True,
                    "message": "Conversations fetched successfully.",
                    "data": data
                }).data,
                status=status.HTTP_200_OK
            )

        except DatabaseError as e:
            logger.error(f"Database error occurred while fetching conversations, error={str(e)}")
            return Response(ConversationListSerializer({
                    "success": False,
                    "message": "Database error occurred while fetching conversations.",
                    "data": None,
                }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error(f"Unexpected error occurred while fetching conversations, error={str(e)}")
            return Response(ConversationListSerializer({
                    "success": False,
                    "message": "An unexpected error occurred.",
                    "data": None
                }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# API view to handle escalation to human agent
@extend_schema(
    tags=["Query Escalation"],
    description="API endpoint to escalate a conversation to a human agent. Requires authentication. Expects 'conversation_id' in request data. Returns success status and message on successful escalation.",
    responses={
        200: ResponseSerializer,
        400: ResponseSerializer,   
        404: ResponseSerializer,
        500: ResponseSerializer,
    }
)
class EscalateToAgentView(APIView):
    authentication_classes= [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Escalate to Agent API called")
        try:
            conversation_id = request.data.get("conversation_id")
            user_id = request.user.id

            if not conversation_id:
                logger.warning(f"Escalate to Agent API called without conversation ID")
                return Response(ResponseSerializer({
                        "success": False,
                        "message": "Conversation ID is required."
                    }).data,
                    status=status.HTTP_400_BAD_REQUEST
                )


            conversation = get_object_or_404(
                Conversation,
                id=conversation_id,
                user=request.user
            )

            logger.info("Fetching conversation history for escalation email")
            messages = (
                Message.objects
                .filter(conversation=conversation)
                .order_by("-created_at")[:20]
            )


            messages = reversed(messages)

            conversation_history = [
                {
                    "role": msg.sender,
                    "content": msg.message,
                    "source": msg.source,
                }
                for msg in messages
            ]

            email_sent = send_email_to_agent(user_id, conversation_id, conversation.title, conversation_history, request.user.email, request.user.username)

            if email_sent:
                conversation.status = "pending"
                conversation.save()

                logger.info(f"Message escalated to agent successfully and conversation status updated to pending.")
                return Response(ResponseSerializer({
                        "success": True,
                        "message": "Message escalated to agent successfully."
                    }).data,
                    status=status.HTTP_200_OK
                )
            else:
                logger.error(f"Failed to send escalation email to agent.")
                return Response(ResponseSerializer({
                        "success": False,
                        "message": "Failed to escalate message to agent."
                    }).data,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except ObjectDoesNotExist:
            logger.warning(f"Conversation not found or user does not have permission to escalate | conversation_id={conversation_id}")
            return Response(ResponseSerializer({
                    "success": False,
                    "message": "Message not found."
                }).data,
                status=status.HTTP_404_NOT_FOUND
            )

        except DatabaseError as e:
            logger.error(f"Database error occurred while escalating message, error={str(e)}")
            return Response(ResponseSerializer( {
                    "success": False,
                    "message": "Database error occurred while escalating message."
                }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error(f"Unexpected error occurred while escalating message, error={str(e)}")
            return Response(ResponseSerializer({
                    "success": False,
                    "message": "An unexpected error occurred.",
                }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# API view to generate bot response for widget (without saving messages or conversation) - can be used by frontend widget to get quick responses without creating conversation first
@extend_schema(
    tags=["Widget"],
    description="API endpoint to generate bot response for widget. Does not save messages or conversation.",
    responses={
        200: ResponseSerializer,
        400: ResponseSerializer,
        500: ResponseSerializer,
    },
    summary="Generate bot response for widget"
)
class GenerateWidgetResponse(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info(f"Generate Widget Response API called")
        message = request.data.get("message")
        # history = request.data.get("history")

        try:
            context = get_relevant_chunks(message)
        except Exception as e:
            logger.error(f"Error retrieving relevant context for widget response, error={str(e)}")
            return Response(ResponseSerializer({
                    "success": False,
                    "message": "Error retrieving relevant context.",
                }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        logger.info(f"Generated relevant context for widget response")
        try:
            response_obj, source = get_bot_reply(
                message,
                context,
            )
        except Exception as e:
            logger.error(f"Error generating bot response for widget, error={str(e)}")
            return Response(ResponseSerializer({
                "success": False,
                "message": "Error generating response.",
            }).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        logger.info(f"Generated bot response for widget successfully")
        return Response(ResponseSerializer({
                "success": True,
                "message": "Bot response generated successfully.",
                "data": {
                    "reply": response_obj.response_content,
                    "escalation": response_obj.escalation
                }
            }).data,
            status=status.HTTP_200_OK
        )



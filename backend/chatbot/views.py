from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import DatabaseError, transaction
from django.core.exceptions import ObjectDoesNotExist
import logging

from .models import Conversation, Message
from .serializers import ConversationSerializer
from .utils.chatbot_logic import get_relevant_chunks, get_bot_reply

from .utils.email_service import send_email_to_agent

import logging

logger = logging.getLogger(__name__)

# Create your views here.

# API view to create a new conversation.
class CreateConversationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logger.info(f"Create Conversation API called")
        try:
            serializer = ConversationSerializer(data=request.data)

            if not serializer.is_valid():
                logger.warning(f"Invalid input data for creating conversation | errors={serializer.errors}")
                return Response(
                    {
                        "success": False,
                        "message": "Invalid input data.",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save(user=request.user)

            logger.info(f"Conversation created successfully.")
            return Response(
                {
                    "success": True,
                    "message": "Conversation created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except DatabaseError as e:
            logger.error(f"Database error while creating conversation | error={str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Database error occurred while creating conversation.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception as e:
            logger.error(f"Unexpected error while creating conversation | error={str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Something went wrong.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Delete converstation API View
class DeleteConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        logger.info(f"Delete Conversation API called")
        try:
            if not pk:
                logger.warning(f"Delete Conversation API called without conversation ID")
                return Response(
                    {
                        "success": False,
                        "message": "Conversation ID is required."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Ensure user can only delete their own conversation
            conversation = Conversation.objects.get(
                pk=pk,
                user=request.user
            )
            conversation.delete()

            logger.info(f"Conversation with deleted successfully.")
            return Response(
                {
                    "success": True,
                    "message": "Conversation deleted successfully."
                },
                status=status.HTTP_204_NO_CONTENT
            )

        except ObjectDoesNotExist:
            logger.warning(f"Conversation not found or user does not have permission to delete | conversation_id={pk}")
            return Response(
                {
                    "success": False,
                    "message": "Conversation not found or you do not have permission."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except DatabaseError:
            logger.error(f"Database error while deleting conversation | conversation_id={pk}")
            return Response(
                {
                    "success": False,
                    "message": "Database error occurred while deleting conversation."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error(f"Unexpected error while deleting conversation | conversation_id={pk}, error={str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Something went wrong.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# API view to handle user messages and generate bot responses.
class CreateMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def error_response(self, message, error=None, code=status.HTTP_500_INTERNAL_SERVER_ERROR):
        logger.warning(f"{message} | error={str(error)}")
        return Response(
            {
                "success": False,
                "message": message,
                "error": str(error) if error else None
            },
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
                return Response({
                    "success": False,
                    "message": "Error retrieving relevant context.",
                })

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
            return Response(
                {
                    "success": True,
                    "data": {
                        "id": msg.id,
                        "message": msg.message,
                        "created_at": msg.created_at,
                        "source": source,
                        "confidence": confidence_score,
                        "escalation_status": response_obj.escalation
                    }
                },
                status=status.HTTP_200_OK
            )

        except DatabaseError as e:
            logger.error(f"Database error occurred, error={str(e)}")
            return self.error_response(
                "Database error occurred.",
                error=e
            )

        except Exception as e:
            logger.error(f"Unexpected error occurred, error={str(e)}")
            return self.error_response(
                "Unexpected error occurred.",
                error=e
            )




# API view to fetch all messages of a conversation
class FetchAllMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Fetch All Messages API called")
        try:
            conversation_id = request.data.get("conversation_id")
            if not conversation_id:
                logger.warning(f"Fetch All Messages API called without conversation ID")
                return Response(
                    {
                        "success": False,
                        "message": "Conversation ID is required."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


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
                return Response(
                    {
                        "success": True,
                        "message": "No messages found.",
                        "data": []
                    },
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
            return Response(
                {
                    "success": True,
                    "message": "Successfully fetched the messages.",
                    "data": history
                },
                status=status.HTTP_200_OK
            )

        except DatabaseError as e:
            logger.error(f"Database error occurred while fetching messages, error={str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Database error occurred while fetching messages."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error(f"Unexpected error occurred while fetching messages, error={str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "An unexpected error occurred.",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# API view to fetch all conversations of the user
class FetchAllConversations(APIView):
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
                return Response(
                    {
                        "success": True,
                        "message": "No conversations found.",
                        "data": []
                    },
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
            return Response(
                {
                    "success": True,
                    "message": "Conversations fetched successfully.",
                    "data": data
                },
                status=status.HTTP_200_OK
            )

        except DatabaseError as e:
            logger.error(f"Database error occurred while fetching conversations, error={str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Database error occurred while fetching conversations."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error(f"Unexpected error occurred while fetching conversations, error={str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "An unexpected error occurred.",
                    "error": str(e)  # remove in production
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# API view to handle escalation to human agent
class EscalateToAgentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Escalate to Agent API called")
        try:
            conversation_id = request.data.get("conversation_id")
            user_id = request.user.id

            if not conversation_id:
                logger.warning(f"Escalate to Agent API called without conversation ID")
                return Response(
                    {
                        "success": False,
                        "message": "Conversation ID is required."
                    },
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
                return Response(
                    {
                        "success": True,
                        "message": "Message escalated to agent successfully."
                    },
                    status=status.HTTP_200_OK
                )
            else:
                logger.error(f"Failed to send escalation email to agent.")
                return Response(
                    {
                        "success": False,
                        "message": "Failed to escalate message to agent."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except ObjectDoesNotExist:
            logger.warning(f"Conversation not found or user does not have permission to escalate | conversation_id={conversation_id}")
            return Response(
                {
                    "success": False,
                    "message": "Message not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except DatabaseError as e:
            logger.error(f"Database error occurred while escalating message, error={str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Database error occurred while escalating message."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error(f"Unexpected error occurred while escalating message, error={str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "An unexpected error occurred.",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# API view to generate bot response for widget (without saving messages or conversation) - can be used by frontend widget to get quick responses without creating conversation first
class GenerateWidgetResponse(APIView):
    # permission_classes = []

    def post(self, request):
        logger.info(f"Generate Widget Response API called")
        message = request.data.get("message")
        # history = request.data.get("history")

        try:
            context = get_relevant_chunks(message)
        except Exception as e:
            logger.error(f"Error retrieving relevant context for widget response, error={str(e)}")
            return Response({
                "success": False,
                "message": "Error retrieving relevant context.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"Generated relevant context for widget response")
        try:
            response_obj, source = get_bot_reply(
                message,
                context,
            )
        except Exception as e:
            logger.error(f"Error generating bot response for widget, error={str(e)}")
            return Response({
                "success": False,
                "message": "Error generating response.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        logger.info(f"Generated bot response for widget successfully")
        return Response(
            {
                "success": True,
                "data": {
                    "reply": response_obj.response_content,
                    "escalation": response_obj.escalation
                }
            },
            status=status.HTTP_200_OK
        )



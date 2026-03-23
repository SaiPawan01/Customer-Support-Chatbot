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

# Create your views here.
class CreateConversationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logger = logging.getLogger(__name__)
        logger.info(f"Creating conversation for user {request.user.username}")
        try:
            serializer = ConversationSerializer(data=request.data)

            if not serializer.is_valid():
                logger.warning(f"Invalid input data for conversation creation by user {request.user.username}: {serializer.errors}")
                return Response(
                    {
                        "success": False,
                        "message": "Invalid input data.",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save(user=request.user)
            logger.info(f"Conversation created successfully for user {request.user.username}")

            return Response(
                {
                    "success": True,
                    "message": "Conversation created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except DatabaseError as e:
            logger.error(f"Database error occurred while creating conversation for user {request.user.username}: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Database error occurred while creating conversation.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Something went wrong.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            if not pk:
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

            return Response(
                {
                    "success": True,
                    "message": "Conversation deleted successfully."
                },
                status=status.HTTP_204_NO_CONTENT
            )

        except ObjectDoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Conversation not found or you do not have permission."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except DatabaseError:
            return Response(
                {
                    "success": False,
                    "message": "Database error occurred while deleting conversation."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Something went wrong.",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class CreateMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def error_response(self, message, error=None, code=status.HTTP_500_INTERNAL_SERVER_ERROR):
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
            user_query = request.data.get("message")
            conversation_id = request.data.get("conversation_id")

            if not user_query:
                return self.error_response(
                    "Message field is required.",
                    code=status.HTTP_400_BAD_REQUEST
                )

            if not conversation_id:
                return self.error_response(
                    "Conversation ID is required.",
                    code=status.HTTP_400_BAD_REQUEST
                )

            conversation = get_object_or_404(Conversation, id=conversation_id)

            with transaction.atomic():
                

                # Retrieve context
                try:
                    context = get_relevant_chunks(user_query)
                except Exception as e:
                    return self.error_response(
                        "Unable to retrieve relevant chunks.",
                        error=e
                    )

                # Fetch conversation history
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
                    return self.error_response(
                        "Unable to generate LLM response.",
                        error=e
                    )
                
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
            return self.error_response(
                "Database error occurred.",
                error=e
            )

        except Exception as e:
            return self.error_response(
                "Unexpected error occurred.",
                error=e
            )





class FetchAllMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            conversation_id = request.data.get("conversation_id")


            if not conversation_id:
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


            messages = (
                Message.objects
                .filter(conversation=conversation)
                .order_by("-created_at")
            )

            # If no messages found
            if not messages.exists():
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

            return Response(
                {
                    "success": True,
                    "message": "Successfully fetched the messages.",
                    "data": history
                },
                status=status.HTTP_200_OK
            )

        except DatabaseError:
            return Response(
                {
                    "success": False,
                    "message": "Database error occurred while fetching messages."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "An unexpected error occurred.",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class FetchAllConversations(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            conversations = (
                Conversation.objects
                .filter(user=request.user)
                .order_by("-created_at")
            )

            if not conversations.exists():
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
                    "id": doc.id,
                    "title": doc.title,
                    "created_at": doc.created_at
                }
                for doc in conversations
            ]

            return Response(
                {
                    "success": True,
                    "message": "Conversations fetched successfully.",
                    "data": data
                },
                status=status.HTTP_200_OK
            )

        except DatabaseError:
            return Response(
                {
                    "success": False,
                    "message": "Database error occurred while fetching conversations."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "An unexpected error occurred.",
                    "error": str(e)  # remove in production
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )









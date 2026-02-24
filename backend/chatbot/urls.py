from django.urls import path
from .views import CreateConversationView, DeleteConversationView, CreateMessageView, FetchAllMessage, FetchAllConversations

urlpatterns = [
    path('create/conversation', CreateConversationView.as_view(), name='create_conversation'),
    path('delete/conversation/<int:pk>', DeleteConversationView.as_view(), name='delete_conversation'),
    path('create/message', CreateMessageView.as_view(), name='create_message'),
    path('fetch/message-history', FetchAllMessage.as_view(),name='fetch_history'),
    path('fetch/conversations', FetchAllConversations.as_view(), name='fetch_conversations')
]
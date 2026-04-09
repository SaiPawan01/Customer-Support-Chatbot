from rest_framework import serializers
from .models import Conversation, Message


class ConversationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["title","id","created_at"]
        read_only_fields = ["id","created_at"]


class ConversationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField(allow_null=True)



class MessageRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['message','sender']


class ResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField(allow_null=True,required=False)


class ConversationListSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.ListField(child=serializers.DictField(), allow_null=True)
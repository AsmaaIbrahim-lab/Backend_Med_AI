# chat/serializers.py

from rest_framework import serializers
from .models import ChatMessage, ChatRoom, ChatRequest

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ' __all__'

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'

class ChatRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRequest
        fields = '__all__'
        read_only_fields = ['patient',]
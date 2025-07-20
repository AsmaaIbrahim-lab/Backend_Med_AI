
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage
from .serializers import ChatMessageSerializer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = data['sender_id']
        room_id = self.room_name

        msg = await self.save_message(room_id, sender_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': ChatMessageSerializer(msg).data
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def save_message(self, room_id, sender_id, message):
        room = ChatRoom.objects.get(id=room_id)
        sender = room.doctor if room.doctor.id == sender_id else room.patient
        return ChatMessage.objects.create(room=room, sender=sender, content=message)
    
    @database_sync_to_async
    def save_message(self, room_id, sender_id, message):
        room = ChatRoom.objects.get(id=room_id)
        sender = room.doctor if room.doctor.id == sender_id else room.patient
        return ChatMessage.objects.create(room=room, sender=sender, content=message, encrypted=True)
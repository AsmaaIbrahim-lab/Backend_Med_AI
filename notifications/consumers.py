# notifications/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification
from .serializers import NotificationSerializer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f'notifications_{self.user.id}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        notification = event['notification']
        await self.send(text_data=json.dumps(notification))

    @database_sync_to_async
    def save_notification(self, sender, receiver, message, notification_type):
        notification = Notification.objects.create(
            sender=sender,
            receiver=receiver,
            message=message,
            type=notification_type
        )
        return NotificationSerializer(notification).data
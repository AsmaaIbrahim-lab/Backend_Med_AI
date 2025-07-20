# notifications/utils.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification
from .serializers import NotificationSerializer
from .firebase import send_push_notification as fcm_send


def send_websocket_notification(user_id, notification):
    channel_layer = get_channel_layer()
    payload = (
        NotificationSerializer(notification).data
        if isinstance(notification, Notification)
        else notification
    )
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user_id}',
        {
            'type': 'send_notification',
            'notification': payload
        }
    )


def send_push_notification(user, message, notif_type, chat_message=None, chat_request=None, health_tip=None, title="New Notification", notification_id=None):
    if not getattr(user, 'fcm_token', None):
        return

    data = {
        "type": notif_type,
        "notification_id": str(notification_id) if notification_id else "",
    }

    if chat_request:
        data["chat_request_id"] = str(chat_request.id)
    if chat_message:
        data["chat_message_id"] = str(chat_message.id)
    if health_tip:
        data["health_tip_id"] = str(health_tip.id)

    fcm_send(
        token=user.fcm_token,
        title=title,
        body=message,
        data=data
    )


def create_notification(sender, receiver, message, notif_type, chat_message=None, chat_request=None, health_tip=None):
    notification = Notification.objects.create(
        sender=sender,
        receiver=receiver,
        message=message,
        type=notif_type,
        chat_message=chat_message,
        chat_request=chat_request,
        health_tip=health_tip
    )

    send_websocket_notification(receiver.id, notification)
    send_push_notification(
        user=receiver,
        message=message,
        notif_type=notif_type,
        chat_message=chat_message,
        chat_request=chat_request,
        health_tip=health_tip,
        notification_id=notification.id
    )
    return notification
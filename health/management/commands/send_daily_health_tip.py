# health/management/commands/send_daily_health_tip.py
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from health.models import HealthTip
from notifications.models import Notification
from notifications.utils import send_push_notification, send_websocket_notification

User = get_user_model()

class Command(BaseCommand):
    help = 'Send a daily random health tip to all users'

    def handle(self, *args, **kwargs):
        tip = random.choice(HealthTip.objects.all())
        users = User.objects.all()

        for user in users:
            notif = Notification.objects.create(
                sender=None,
                receiver=user,
                message=tip.title,
                type='health_tip',
                health_tip=tip
            )

            # WebSocket
            send_websocket_notification(user.id, notif)

            # FCM
            if hasattr(user, 'fcm_token') and user.fcm_token:
                send_push_notification(
                    token=user.fcm_token,
                    title="Daily Health Tip",
                    body=tip.title,
                    data={"type": "health_tip", "tip_id": tip.id}
                )

        self.stdout.write(self.style.SUCCESS('Daily health tip sent'))
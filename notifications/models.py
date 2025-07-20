

# notifications/models.py
from django.db import models
from django.conf import settings

NOTIFICATION_TYPES = (
    ('chat', 'Chat Message'),
    ('request', 'Chat Request'),
    ('health_tip', 'Health Tip'),
)

class Notification(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    chat_message = models.ForeignKey('chat.ChatMessage', null=True, blank=True, on_delete=models.CASCADE)
    chat_request = models.ForeignKey('chat.ChatRequest', null=True, blank=True, on_delete=models.CASCADE)
    health_tip = models.ForeignKey('health.HealthTip', null=True, blank=True, on_delete=models.CASCADE)

    def _str_(self):
        return f"To: {self.receiver} - {self.message}"

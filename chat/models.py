
from django.db import models
from django.conf import settings

class ChatRequest(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_requests')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class ChatRoom(models.Model):
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chat_doctor_rooms', on_delete=models.CASCADE)
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chat_patient_rooms', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    media = models.FileField(upload_to='chat_media/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    encrypted = models.BooleanField(default=True)

class BlockedUser(models.Model):
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='blocked_by', on_delete=models.CASCADE)
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='blocks', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
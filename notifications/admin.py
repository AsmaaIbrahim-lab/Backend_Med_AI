# notifications/admin.py
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'receiver', 'type', 'is_read', 'timestamp']
    readonly_fields = ['timestamp']
    search_fields = ['message', 'sender_username', 'receiver_username']
    list_filter = ['type', 'is_read']
    ordering = ['-timestamp']
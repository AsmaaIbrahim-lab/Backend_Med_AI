from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ChatRoom, ChatRequest, ChatMessage


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'created_at')
    search_fields = ('doctor_username', 'patient_username')
    list_filter = ('created_at',)


@admin.register(ChatRequest)
class ChatRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('doctor_username', 'patient_username')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'sender', 'short_content', 'read', 'timestamp')
    list_filter = ('read', 'timestamp')
    search_fields = ('room_id', 'sender_username', 'content')

    def short_content(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    short_content.short_description = 'Message Preview'
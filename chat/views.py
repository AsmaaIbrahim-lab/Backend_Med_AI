from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ChatRoom, ChatMessage, ChatRequest
from .serializers import ChatRoomSerializer, ChatMessageSerializer, ChatRequestSerializer
from notifications.utils import create_notification


class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(doctor=user) | ChatRoom.objects.filter(patient=user)


class ChatRequestViewSet(viewsets.ModelViewSet):
    queryset = ChatRequest.objects.all()
    serializer_class = ChatRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatRequest.objects.filter(doctor=user) if user.user_type == 'doctor' else ChatRequest.objects.filter(patient=user)

    def perform_create(self, serializer):
        req = serializer.save(patient=self.request.user)
        # Notify doctor with request link
        create_notification(
            sender=req.patient,
            receiver=req.doctor,
            message=f"{req.patient.get_full_name() or req.patient.username} requested to chat with you.",
            type="request",
            chat_request=req
        )

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        req = self.get_object()
        req.status = 'accepted'
        req.save()

        ChatRoom.objects.get_or_create(doctor=req.doctor, patient=req.patient)

        create_notification(
            sender=req.doctor,
            receiver=req.patient,
            message="Your chat request has been approved.",
            type="request",
            chat_request=req
        )
        return Response({'status': 'accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        req = self.get_object()
        req.status = 'rejected'
        req.save()

        create_notification(
            sender=req.doctor,
            receiver=req.patient,
            message="Your chat request was rejected.",
            type="request",
            chat_request=req
        )
        return Response({'status': 'rejected'})


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatMessage.objects.filter(room_doctor=user) | ChatMessage.objects.filter(room_patient=user)

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)
        receiver = message.room.patient if message.sender == message.room.doctor else message.room.doctor

        create_notification(
            sender=message.sender,
            receiver=receiver,
            message=f"New message from {message.sender.get_full_name() or message.sender.username}.",
            type="chat",
            chat_message=message
        )

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        message.read = True
        message.save()
        return Response({'detail': 'Message marked as read.'}, status=status.HTTP_200_OK)
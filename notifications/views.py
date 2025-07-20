from django.shortcuts import render
# notifications/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from chat.models import ChatRoom
from notifications.utils import create_notification

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        return self._mark_as_read(self.get_object())

    @action(detail=True, methods=['post'])
    def approve_request(self, request, pk=None):
        notif = self.get_object()

        if notif.chat_request and notif.receiver == request.user:
            chat_req = notif.chat_request
            if chat_req.status != 'pending':
                return Response({'detail': 'Request is already handled.'}, status=400)

            chat_req.status = 'accepted'
            chat_req.save()

            ChatRoom.objects.get_or_create(
                doctor=chat_req.doctor,
                patient=chat_req.patient
            )

            create_notification(
                sender=chat_req.doctor,
                receiver=chat_req.patient,
                message="Your chat request has been approved.",
                notif_type="request",
                chat_request=chat_req
            )

            return self._mark_as_read(notif)
        return Response({'detail': 'Invalid request or permission denied.'}, status=403)

    @action(detail=True, methods=['post'])
    def reject_request(self, request, pk=None):
        notif = self.get_object()

        if notif.chat_request and notif.receiver == request.user:
            chat_req = notif.chat_request
            if chat_req.status != 'pending':
                return Response({'detail': 'Request is already handled.'}, status=400)

            chat_req.status = 'rejected'
            chat_req.save()

            create_notification(
                sender=chat_req.doctor,
                receiver=chat_req.patient,
                message="Your chat request was rejected.",
                notif_type="request",
                chat_request=chat_req
            )

            return self._mark_as_read(notif)
        return Response({'detail': 'Invalid request or permission denied.'}, status=403)

    def _mark_as_read(self, notification):
        notification.is_read = True
        notification.save()
        return Response({'detail': 'Notification marked as read.'}, status=200)
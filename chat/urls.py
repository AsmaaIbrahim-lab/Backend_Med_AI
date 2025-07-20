# chat/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ChatRoomViewSet, ChatMessageViewSet, ChatRequestViewSet

router = DefaultRouter()
router.register('rooms', ChatRoomViewSet)
router.register('messages', ChatMessageViewSet)
router.register('requests', ChatRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
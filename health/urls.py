# health/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthTipViewSet

router = DefaultRouter()
router.register(r'tips', HealthTipViewSet, basename='healthtip')

urlpatterns = [
    path('', include(router.urls)),
]

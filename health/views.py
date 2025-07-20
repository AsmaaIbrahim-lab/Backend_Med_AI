
# health/views.py

from .serializers import MedicineReminderSerializer,HealthTipSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions
from .models import HealthTip,MedicineReminder

class HealthTipViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing health tips.
    """
    queryset = HealthTip.objects.all().order_by('-created_at')
    serializer_class = HealthTipSerializer
    permission_classes = [permissions.AllowAny]  # You can change to IsAuthenticated if needed



class MedicineReminderViewSet(viewsets.ModelViewSet):
    queryset = MedicineReminder.objects.all()
    serializer_class = MedicineReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

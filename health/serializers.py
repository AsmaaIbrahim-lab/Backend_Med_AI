# health/serializers.py

from rest_framework import serializers
from .models import HealthTip
from .models import MedicineReminder


class HealthTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthTip
        fields = '__all__'


class MedicineReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineReminder
        fields = '__all__'

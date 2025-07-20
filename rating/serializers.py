from rest_framework import serializers
from .models import Review,Users
class ReviewSerializer(serializers.ModelSerializer):
    doctor_email = serializers.EmailField(source='doctor.email', read_only=True)
    patient_email = serializers.EmailField(source='patient.email', read_only=True)
    doctor = serializers.PrimaryKeyRelatedField(queryset=Users.objects.filter(user_type='doctor'))
    
    class Meta:
        model = Review
        fields = [
            'id',
            'doctor',
            'doctor_email',
            'patient_email',
            'rating',
            'comment',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['patient_email', 'created_at', 'updated_at']
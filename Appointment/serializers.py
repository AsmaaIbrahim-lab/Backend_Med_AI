# serializers.py
from rest_framework import serializers
from .models import Availability, Appointment
from user.models import DoctorProfile, Users

class DoctorNameSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorProfile
        fields = ['full_name']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else "Unknown Doctor"
from rest_framework import serializers
from user.models import DoctorProfile

class DoctorFeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ['fees']  

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

class  DoctorProfileSerializer(serializers.ModelSerializer):
    user = UsersSerializer(required=False, write_only=True)
    class Meta:
        model = DoctorProfile
        fields = '__all__'


class AvailabilitySerializer(serializers.ModelSerializer):
    doctor = DoctorNameSerializer(read_only=True)
    
    class Meta:
        model = Availability
        fields = '__all__'
        extra_kwargs = {
            'doctor': {'required': False}
        }
    
def validate(self, data):
    start_time = data.get('start_time', getattr(self.instance, 'start_time', None))
    end_time = data.get('end_time', getattr(self.instance, 'end_time', None))

    if start_time and end_time and start_time >= end_time:
        raise serializers.ValidationError("وقت البداية يجب أن يكون قبل وقت النهاية")
    
    return data

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class CancelAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['cancellation_reason']
from rest_framework import serializers
from .models import DoctorProfile

class DoctorFeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ['fees']


class AppointmenttSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '_all_'
from rest_framework import serializers
from .models import Appointment
class AppointmentSerializer(serializers.ModelSerializer):
    availability = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()  # <-- أضف هذا السطر

    class Meta:
        model = Appointment
        fields = ['id', 'status', 'cancellation_reason', 'availability', 'patient']

    def get_availability(self, obj):
        availability = obj.availability
        doctor = availability.doctor
        return f"{doctor.user.first_name} {doctor.user.last_name} - {doctor.specialty} on {availability.date} from {availability.start_time} to {availability.end_time}"

    def get_patient(self, obj):
        return obj.patient.user.get_full_name()     
from.models import Users ,DoctorProfile
from rest_framework import serializers

class DoctorSummarySerializer(serializers.ModelSerializer):
    specialty = serializers.CharField(source='doctor_profile.specialty')
    id= serializers.IntegerField(source='doctor_profile.id')
    class Meta:
        model = Users
        fields = ['username', 'id','specialty','image']
from rest_framework import serializers
from.models import Users , DoctorProfile
class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model=Users
        fields = '_all_' 
class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model= DoctorProfile
        fields = '_all_' 
class UsernamesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Users
        fields = ['username' ]
class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model=DoctorProfile
        fields = ['specialty' ] 
# serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from .models import (
    Users, 
    DoctorProfile, 
    PatientProfile, 
    CustomOutstandingToken, 
    CustomBlacklistedToken,
     DOCTOR,
     PATIENT
)

from django.contrib.auth import get_user_model 
from .utils import redis_client



# ========== User Serializers ==========

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

class DoctorRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    university = serializers.ChoiceField(choices=DoctorProfile.UNIVERSITIES)
    specialty = serializers.ChoiceField(choices=DoctorProfile.SPECIALTIES)
    license_number = serializers.CharField()
    experience_years = serializers.IntegerField()
    governorate = serializers.PrimaryKeyRelatedField(queryset=DoctorProfile._meta.get_field('governorate').remote_field.model.objects.all(), required=False)
    area = serializers.PrimaryKeyRelatedField(queryset=DoctorProfile._meta.get_field('area').remote_field.model.objects.all(), required=False)
    phone_number = serializers.CharField(max_length=15, required=False)
    class Meta:
        model = get_user_model()
        fields = (
            "first_name", "last_name", "email", "gender", "birth_date",
            "password", "password2", "university", "specialty",
            "license_number", "experience_years", "governorate", "area","phone_number"
        )

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password2")

        university = validated_data.pop("university")
        specialty = validated_data.pop("specialty")
        license_number = validated_data.pop("license_number")
        experience_years = validated_data.pop("experience_years")
        governorate = validated_data.pop("governorate", None)
        area = validated_data.pop("area", None)
        phone_number = validated_data.pop("phone_number", None)

        user = get_user_model().objects.create(
            **validated_data,
           role = DOCTOR
        )
        user.set_password(password)
        user.save()

        DoctorProfile.objects.create(
            user=user,
            university=university,
            specialty=specialty,
            license_number=license_number,
            experience_years=experience_years,
            governorate=governorate,
            area=area,
            phone_number=phone_number

        )

        return user


class PatientRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "first_name", "last_name", "email", "gender", "birth_date"
           ,"medical_history", "password", "password2"
        )


    

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password2")
        user = get_user_model().objects.create(
            **validated_data,
            role=PATIENT
        )
        user.set_password(password)
        user.save()

        PatientProfile.objects.create(user=user)

        return user

# ========== Authentication Serializers ==========



from rest_framework import serializers, status
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from .models import Users  

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = Users.objects.get(email=email)
            if check_password(password, user.password):
                data['user'] = user
                return data
            raise serializers.ValidationError("Invalid credentials")

        except Users.DoesNotExist:
            raise serializers.ValidationError("User not found")

        except Exception as e:
            raise serializers.ValidationError(f"An unexpected error occurred: {str(e)}")



# ========== Token Management Serializers ==========

class CustomOutstandingTokenSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = CustomOutstandingToken
        fields = ['id', 'user', 'jti', 'token', 'created_at', 'expires_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'token': {'write_only': True}
        }

class CustomBlacklistedTokenSerializer(serializers.ModelSerializer):
    token = CustomOutstandingTokenSerializer(read_only=True)
    token_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomOutstandingToken.objects.all(),
        source='token',
        write_only=True
    )

    class Meta:
        model = CustomBlacklistedToken
        fields = ['id', 'token', 'token_id', 'blacklisted_at']
        read_only_fields = ['id', 'blacklisted_at']

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        # Add any custom password validation if needed
        return data

    def save(self):
        email = self.validated_data['email']
        otp = self.validated_data['otp']
        new_password = self.validated_data['new_password']

        # Example OTP check (assumes Redis is used)
        stored_otp = redis_client.get(f"otp:reset:{email}")
        if not stored_otp or stored_otp != otp:
            raise serializers.ValidationError("Invalid or expired OTP.")

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        user.set_password(new_password)
        user.save()
        redis_client.delete(f"otp:reset:{email}")

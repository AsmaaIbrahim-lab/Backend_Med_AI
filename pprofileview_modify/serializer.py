from rest_framework import serializers
from user.models import Users, DoctorProfile, PatientProfile
from django.core.exceptions import ValidationError
from user.utils import generate_username
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'user_type', 'gender', 'age', 'image',
            'birth_date'
        ]
        read_only_fields = ['id', 'email', 'user_type']

    def validate_phone_number(self, value):
        if self.instance and self.instance.phone_number == value:
            return value  # No change — skip uniqueness check
        if Users.objects.filter(phone_number=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("User with this phone number already exists.")
        return value

    def validate(self, data):
        return data


class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False, write_only=True)

    class Meta:
        model = DoctorProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        instance = self.instance
        if instance:
            current_gov = instance.governorate
            current_area = instance.area
            new_gov = data.get('governorate', current_gov)
            new_area = data.get('area', current_area)

            if 'governorate' in data and 'area' not in data:
                if new_gov != current_gov:
                    raise serializers.ValidationError({
                        'area': 'You must specify an area when changing governorate'
                    })

            elif 'area' in data and 'governorate' not in data:
                if new_area != current_area:
                    raise serializers.ValidationError({
                        'governorate': 'You must specify a governorate when changing area'
                    })

            elif 'governorate' in data and 'area' in data:
                if new_area and new_area.governorate != new_gov:
                    raise serializers.ValidationError({
                        'area': 'Selected area does not belong to the specified governorate'
                    })

        return data

    def update(self, instance, validated_data):
     user_data = validated_data.pop('user', {})
     print("Received user data:", user_data)

     for attr, value in validated_data.items():
         print(f"Updating profile field {attr} to {value}")
         setattr(instance, attr, value)
     instance.save()

     user = instance.user
     if user_data:
         print("Updating user fields...")
         first_name = user_data.get('first_name', user.first_name)
         last_name = user_data.get('last_name', user.last_name)
         if 'first_name' in user_data or 'last_name' in user_data:
             user.username = generate_username(first_name, last_name)
         user_serializer = UserSerializer(instance=user, data=user_data, partial=True)
         user_serializer.is_valid(raise_exception=True)
         user_serializer.save()

     return instance


class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False, write_only=True)

    class Meta:
        model = PatientProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        user = instance.user
        if user_data:
            first_name = user_data.get('first_name', user.first_name)
            last_name = user_data.get('last_name', user.last_name)
            if 'first_name' in user_data or 'last_name' in user_data:
                user.username = generate_username(first_name, last_name)
            user_serializer = UserSerializer(instance=user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        return instance

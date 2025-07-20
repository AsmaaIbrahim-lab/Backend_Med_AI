# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from .models import (
    Users,
    DoctorProfile,
    PatientProfile,
    CustomOutstandingToken,
    CustomBlacklistedToken,
)
from .utils import generate_location


# Unregister default Users admin if registered
try:
    admin.site.unregister(Users)
except admin.sites.NotRegistered:
    pass

# Custom User admin
@admin.register(Users)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'password','image','user_type', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter = ('user_type', 'is_active', 'is_staff')
    ordering = ('id',)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Only superusers can delete users

# DoctorProfile admin with model validation
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'specialty', 'license_number', 'university', 'experience_years', 'governorate', 'area','location', 'phone_number','fees')
    def location(self, obj):
        return generate_location(obj.governorate, obj.area)
    location.short_description = 'Location'

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            form.add_error(None,e)

# PatientProfile admin with model validation
@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'medical_history')

    def age(self, obj):
        # Returns the user's age using the related User model
        return obj.user.age if obj.user else None
    age.short_description = 'Age'  

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            form.add_error(None, e)

# Simple token registrations
admin.site.register(CustomOutstandingToken)
admin.site.register(CustomBlacklistedToken)

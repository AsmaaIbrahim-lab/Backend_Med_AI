from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Availability, Appointment

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor','id', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('doctor', 'date', 'is_available')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name')
    ordering = ('-date', 'start_time')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
   list_display = ['id', 'patient','cancellation_reason', 'availability','status']  # شيلتي date و start_time و end_time
   ordering = ['id']  # أو أي حاجة موجودة فعلاً
   list_filter = ['status']

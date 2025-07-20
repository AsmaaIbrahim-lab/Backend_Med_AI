# health/admin.py
from django.contrib import admin
from .models import HealthTip
from .models import MedicineReminder


@admin.register(HealthTip)
class HealthTipAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content', 'category')
    ordering = ('-created_at',)



@admin.register(MedicineReminder)
class MedicineReminderAdmin(admin.ModelAdmin):
    list_display = ('user', 'medicine_name', 'time', 'start_date', 'end_date', 'frequency', 'created_at')
    list_filter = ( 'start_date','end_date', 'frequency')

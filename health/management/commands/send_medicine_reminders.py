# health/management/commands/send_medicine_reminders.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from health.models import MedicineReminder
from notifications.models import Notification
from notifications.utils import send_websocket_notification, send_fcm_notification
import datetime

class Command(BaseCommand):
    help = 'Send scheduled medicine reminders'

    def handle(self, *args, **kwargs):
        now = timezone.localtime()
        current_time = now.time()
        today = now.date()

        reminders = MedicineReminder.objects.filter(
            time__hour=current_time.hour,
            time__minute=current_time.minute,
            start_date__lte=today
        ).exclude(end_date__lt=today)

        for reminder in reminders:
            message = f"Time to take your medicine: {reminder.medicine_name} ({reminder.dosage})"
            notif = Notification.objects.create(
                sender=None,
                receiver=reminder.user,
                message=message,
                type='medicine_reminder'
            )
            send_websocket_notification(reminder.user.id, notif)
            send_fcm_notification(reminder.user.id, message)

        self.stdout.write(self.style.SUCCESS(f"Sent {reminders.count()} medicine reminders"))




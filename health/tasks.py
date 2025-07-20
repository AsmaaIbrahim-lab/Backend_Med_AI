# health/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import date
from .models import MedicineReminder
from notifications.utils import send_websocket_notification, send_push_notification

@shared_task
def send_medicine_reminders():
    now = timezone.localtime()
    today = date.today()

    reminders = MedicineReminder.objects.filter(
        time__hour=now.hour,
        time__minute=now.minute,
        is_active=True,
        start_date__lte=today
    ).exclude(end_date__lt=today)

    for reminder in reminders:
        if reminder.frequency in ['once', 'daily']:
            send_reminder(reminder)

        elif reminder.frequency == 'twice':
            if now.hour in [8, 18]:  # e.g., morning and evening
                send_reminder(reminder)

        elif reminder.frequency == 'three times':
            if now.hour in [8, 13, 19]:  # morning, afternoon, evening
                send_reminder(reminder)


def send_reminder(reminder):
    message = f"Time to take your medicine: {reminder.medicine_name} ({reminder.dosage})"
    
    notification = reminder.user.notifications.create(
        sender=None,
        receiver=reminder.user,
        message=message,
        type='medicine'
    )

    send_websocket_notification(reminder.user.id, notification)

    if reminder.user.fcm_token:
        send_push_notification(
            token=reminder.user.fcm_token,
            title="Medicine Reminder",
            body=message,
            data={"type": "medicine", "reminder_id": reminder.id}
        )

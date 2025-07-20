# project/celery.py
from __future__ import absolute_import
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')  # Replace 'project' with your actual project name

app = Celery('project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-medicine-reminders-every-minute': {
        'task': 'reminders.tasks.send_medicine_reminders',
        'schedule': crontab(minute='*'),  # every minute
    },
}
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send-daily-health-tip': {
        'task': 'health.tasks.send_daily_health_tip_task',
        'schedule': crontab(hour=9, minute=0),  # runs every day at 9 AM
},
}
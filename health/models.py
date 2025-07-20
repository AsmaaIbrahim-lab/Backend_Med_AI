
# models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class HealthTip(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General Health'),
        ('nutrition', 'Nutrition'),
        ('fitness', 'Fitness'),
        ('mental_health', 'Mental Health'),
        ('hygiene', 'Hygiene'),
    ]
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class MedicineReminder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    time = models.TimeField()  # when the medicine should be taken
    frequency = models.CharField(max_length=20, choices=[('once', 'Once'),('twice','Twice'),('three times','Three times'), ('daily', 'Daily')], default='daily')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.medicine_name} at {self.time}"

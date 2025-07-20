from django.db import models
from user.models import Users,DoctorProfile,PatientProfile
class Availability(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.doctor} on {self.date} from {self.start_time} to {self.end_time}"

from .models import Availability

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),  # أضفناها
        ('confirmed', 'confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
         ('missed', 'Missed'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)  # ربط الموعد المتاح
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cancellation_reason = models.TextField(null=True, blank=True)
   
    def __str__(self):
        return f"{self.availability.date}"



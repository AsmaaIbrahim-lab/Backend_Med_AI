from django.db import models
from user.models import Users,DoctorProfile,PatientProfile
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star - Poor'),
        (2, '2 Stars - Fair'),
        (3, '3 Stars - Good'),
        (4, '4 Stars - Very Good'),
        (5, '5 Stars - Excellent'),
    ]

    # العلاقة مع المريض (من خلال المستخدم)
    patient = models.ForeignKey(
       Users,
        on_delete=models.CASCADE,
        related_name='patient_reviews',
        limit_choices_to={'user_type': 'patient'}
    )
    
    # العلاقة مع الطبيب (من خلال المستخدم)
    doctor = models.ForeignKey(
         Users,
        on_delete=models.CASCADE,
        related_name='doctor_reviews',
        limit_choices_to={'user_type': 'doctor'}
    )
    
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    comment = models.TextField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('patient', 'doctor')  # يمنع تقييم نفس الطبيب أكثر من مرة من نفس المريض
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"Review by {self.patient.username} for Dr. {self.doctor.username} - {self.rating} stars"

    def clean(self):
        # التأكد من أن المريض له patient_profile
        if not hasattr(self.patient, 'patient_profile'):
            raise ValidationError("Only patients can submit reviews")
        
        # التأكد من أن الطبيب له doctor_profile
        if not hasattr(self.doctor, 'doctor_profile'):
            raise ValidationError("You can only review doctors")

    def save(self, *args, **kwargs):
        self.full_clean()  # تنفيذ التحقق الموجود في clean()
        super().save(*args, **kwargs)

# Create your models here.

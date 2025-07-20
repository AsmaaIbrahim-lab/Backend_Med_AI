# user/models.py
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.timezone import now
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
from .utils import calculate_age
from django.core.validators import RegexValidator

class Users(AbstractUser):
    USER_TYPE_CHOICES = [
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)      
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True, blank=True)
    user_type = models.CharField(max_length=7, choices=USER_TYPE_CHOICES)
    image = models.ImageField(upload_to='users_images/', null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name="users_custom_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="users_custom_permissions", blank=True)
    bio= models.TextField(null=True, blank=True)
    phone_regex = RegexValidator(
    regex=r'^\d{11,15}$',
    message="Phone number must be between 11 to 15 digits and numeric only.")

    phone_number = models.CharField(
    validators=[phone_regex],
    max_length=15,
    unique=True,
    blank=True,
    null=True
  )
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    

    @property
    def age(self):
        return calculate_age(self.birth_date)

    @property
    def get_gender_display(self):
        return dict(self.GENDER_CHOICES).get(self.gender, 'Unknown')

    @property
    def get_user_type_display(self):
        return dict(self.USER_TYPE_CHOICES).get(self.user_type, 'Unknown')

    def _str_(self):
        return self.username

DOCTOR = 'doctor'
PATIENT ='patient'


class Governorate(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def _str_(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=100)
    governorate = models.ForeignKey(Governorate, related_name='areas', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'governorate')

    def _str_(self):
        return f"{self.name}, {self.governorate.name}"




class DoctorProfile(models.Model):
    UNIVERSITIES = [
        ("Cairo University", "Cairo University"),
        ("Ain Shams University", "Ain Shams University"),
        ("Alexandria University", "Alexandria University"),
        ("Mansoura University", "Mansoura University"),
        ("Zagazig University", "Zagazig University"),
        ("Tanta University", "Tanta University"),
        ("Assiut University", "Assiut University"),
        ("Al-Azhar University", "Al-Azhar University"),
        ("Helwan University", "Helwan University"),
        ("Suez Canal University", "Suez Canal University"),
        ("Menoufia University", "Menoufia University"),
        ("Minia University", "Minia University"),
        ("Beni Suef University", "Beni Suef University"),
        ("Sohag University", "Sohag University"),
        ("South Valley University", "South Valley University"),
        ("Fayoum University", "Fayoum University"),
        ("Kafr El Sheikh University", "Kafr El Sheikh University"),
        ("Damietta University", "Damietta University"),
        ("Benha University", "Benha University"),
    ]

    SPECIALTIES = [
        ("Cardiology", "Cardiology"),
        ("Dermatology", "Dermatology"),
        ("Endocrinology", "Endocrinology"),
        ("Gastroenterology", "Gastroenterology"),
        ("Hematology", "Hematology"),
        ("Infectious Disease", "Infectious Disease"),
        ("Nephrology", "Nephrology"),
        ("Neurology", "Neurology"),
        ("Obstetrics and Gynecology", "Obstetrics and Gynecology"),
        ("Oncology", "Oncology"),
        ("Ophthalmology", "Ophthalmology"),
        ("Orthopedics", "Orthopedics"),
        ("Otolaryngology", "Otolaryngology (ENT)"),
        ("Pediatrics", "Pediatrics"),
        ("Psychiatry", "Psychiatry"),
        ("Pulmonology", "Pulmonology"),
        ("Radiology", "Radiology"),
        ("Rheumatology", "Rheumatology"),
        ("Surgery", "Surgery"),
        ("Urology", "Urology"),
    ]

    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    fees = models.DecimalField(max_digits=8, decimal_places=2,default=150.00)
    governorate = models.ForeignKey(Governorate, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True,null=True)
    user = models.OneToOneField('Users', on_delete=models.CASCADE, related_name='doctor_profile', null=True, blank=True)
    specialty = models.CharField(max_length=255, choices=SPECIALTIES, default='Gastroenterology')
    license_number = models.CharField(max_length=50, unique=True)
    university = models.CharField(max_length=255, choices=UNIVERSITIES, default='Cairo University')
    experience_years = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('license_number'), name='unique_license_number_case_insensitive')
        ]
        default_permissions = ('add', 'change', 'view')
        permissions = [
            ('delete_doctorprofile', 'Can delete doctor profile'),
        ]

    def _str_(self):
        if self.user:
            return f"Dr. {self.user.username} - {self.specialty}"
        return f"DoctorProfile (Unassigned) - {self.specialty}"

    def clean(self):
        if not self.user_id:
            raise ValidationError("Doctor profile must be associated with a user.")
        if self.user.user_type != 'doctor':
            raise ValidationError("Associated user must be of type 'doctor'.")

    def save(self, *args, **kwargs):
        self.clean()
        if self.license_number:
            self.license_number = self.license_number.lower()
        super().save(*args, **kwargs)

    @staticmethod
    def locations():
        governorates_and_areas = {
            "Cairo": ["Nasr City", "Heliopolis", "Maadi", "Shubra", "New Cairo"],
            "Giza": ["Dokki", "Mohandessin", "6th October", "Haram", "Imbaba"],
            "Alexandria": ["Smouha", "Sidi Gaber", "Stanley", "Miami", "Gleem"],
            "Dakahlia": ["Mansoura", "Talkha", "Mit Ghamr", "Dikirnis", "Sherbin"],
            "Red Sea": ["Hurghada", "Safaga", "Quseir", "Marsa Alam"],
            "Beheira": ["Damanhour", "Kafr El Dawwar", "Rashid", "Edku"],
            "Fayoum": ["Fayoum", "Ibshway", "Sinnuris", "Tamiya"],
            "Gharbia": ["Tanta", "Mahalla", "Kafr El-Zayat", "Zifta"],
            "Ismailia": ["Ismailia", "Qantara", "Tell El Kebir"],
            "Monufia": ["Shibin El Kom", "Menouf", "Ashmoun", "Sadat City"],
            "Minya": ["Minya", "Mallawi", "Samalut", "Beni Mazar"],
            "Qaliubiya": ["Banha", "Shubra El Kheima", "Qalyub", "Khosous"],
            "New Valley": ["Kharga", "Dakhla", "Farafra", "Baris"],
            "Suez": ["Suez", "Ain Sokhna", "Ataka"],
            "Aswan": ["Aswan", "Edfu", "Kom Ombo", "Daraw"],
            "Assiut": ["Assiut", "Manfalut", "Abnub", "Dairut"],
            "Beni Suef": ["Beni Suef", "Nasser", "El Wasta", "Beba"],
            "Port Said": ["Port Said", "El Manakh", "El Arab"],
            "Damietta": ["Damietta", "Ras El Bar", "Faraskur", "Kafr Saad"],
            "Sharkia": ["Zagazig", "10th of Ramadan", "Bilbeis", "Fakous"],
            "South Sinai": ["Sharm El Sheikh", "Dahab", "Nuweiba", "El Tor"],
            "Kafr El Sheikh": ["Kafr El Sheikh", "Desouk", "Baltim", "Sidi Salem"],
            "Matrouh": ["Marsa Matrouh", "Siwa", "El Alamein", "Dabaa"],
            "Luxor": ["Luxor", "Esna", "Armant"],
            "Qena": ["Qena", "Nag Hammadi", "Qus"],
            "North Sinai": ["Arish", "Sheikh Zuweid", "Rafah"],
            "Sohag": ["Sohag", "Tahta", "Girga", "Akhmim"]
        }

        for gov_name, area_list in governorates_and_areas.items():
            governorate, _ = Governorate.objects.get_or_create(name=gov_name)
            for area_name in area_list:
                Area.objects.get_or_create(name=area_name, governorate=governorate)



class PatientProfile(models.Model):
    user = models.OneToOneField(
        Users, on_delete=models.CASCADE, related_name='patient_profile', null=True, blank=True
    )

    medical_history = models.TextField(null=True, blank=True)

    class Meta:
        default_permissions = ('add', 'change', 'view')
        permissions = [
            ('delete_patientprofile', 'Can delete patient profile'),
        ]

    def _str_(self):
        if self.user:
            return f"Patient: {self.user.username}"
        return "PatientProfile (Unassigned)"

    def clean(self):
        if not self.user_id:
            raise ValidationError("Patient profile must be associated with a user.")
        if self.user.user_type != 'patient':
            raise ValidationError("Associated user must be of type 'patient'.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)



class CustomOutstandingToken(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='outstanding_tokens')
    jti = models.CharField(max_length=255, unique=True)
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def _str_(self):
        return f"Outstanding Token for User: {self.user.username}"


class CustomBlacklistedToken(models.Model):
    token = models.OneToOneField(CustomOutstandingToken, on_delete=models.CASCADE, related_name='custom_blacklisted_token')
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Blacklisted Token: {self.token.jti}"
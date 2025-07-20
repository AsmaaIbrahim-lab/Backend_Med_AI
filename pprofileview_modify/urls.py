# profileview_modify/urls.py
from django.urls import path
from .views import (
    user_profile_view,
   # DoctorProfileView,
    #PatientProfileView,
)

urlpatterns = [
    # Unified user profile (GET, PUT)
    path('user_profile/', user_profile_view, name='user-profile'),

    # Optional: Specific endpoints (useful for admin or specific frontend logic)
   # path('api/user/me/doctor/', DoctorProfileView.as_view(), name='doctor-profile'),
    #path('api/user/me/patient/', PatientProfileView.as_view(), name='patient-profile'),
]
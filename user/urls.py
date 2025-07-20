# urls.py
from django.urls import path
from . import views 
from .views import (
    start_redirect,
    LoginView,
    LogoutView,
    choose_account_type,
    doctor_registration,
    patient_registration,
    verify_otp_and_create_account,
    request_password_reset_otp,
    reset_password_with_otp,
    delete_account,
    resend_otp,
    CustomTokenRefreshView,

    

)
 
 



urlpatterns = [
    path('', start_redirect, name='home'),
    path('save-data/', views.save_data, name='save_data'),
    path('NewAccessToken/', CustomTokenRefreshView.as_view(), name='login'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('choose-account-type/', choose_account_type, name='choose_account_type'),  # Select doctor or patient
    path('doctor-registration/', doctor_registration, name='doctor_registration'),  # Start doctor registration and send OTP
    path('patient-registration/', patient_registration, name='patient_registration'),  # Start patient registration and send OTP
    path('verify-otp/', verify_otp_and_create_account, name='verify_otp'),  # Verify OTP and complete account creation
    path('request-reset-otp/', request_password_reset_otp, name='request-reset-otp'),  # takes mail and send reset otp
    path('reset-password/', reset_password_with_otp, name='reset-otp'),  # set new password
    path('upload_image/',views.upload_image, name='upload_image'), 
    path('resend_otp/',views.resend_otp, name='resend_otp'),
    path('delete-account/', delete_account, name='delete_account')
]
      


    

     



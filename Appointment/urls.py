from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Availabilityviewset, GetDoctorFeesAPIView  # لاحظ تصحيح الحروف الكبيرة
from .views import AllAvailabilityByDoctorIdAPIView, BookAppointmentAPIView,ConfirmAppointmentAPIView ,CancelAppointmentByPatientAPIView,RejectAppointmentAPIView,MarkAppointmentCompletedAPIView,MarkAppointmentMissedByDoctorAPIView, AddDoctorFeesAPIView
from .views import get_csrf_token
from .views import (AllAvailabilityByDoctorIdAPIView, BookAppointmentAPIView,ConfirmAppointmentAPIView ,CancelAppointmentByPatientAPIView,RejectAppointmentAPIView,MarkAppointmentCompletedAPIView,MarkAppointmentMissedByDoctorAPIView, AddDoctorFeesAPIView,PendingAppointmentsView,ConfirmedAppointmentsView,CompletedAppointmentsView,
                    CancelledAppointmentsView)


router = DefaultRouter()
router.register(r'availability', Availabilityviewset, basename='availability')

urlpatterns = [
    path('', include(router.urls)),
 


    path('api/get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('doctor/<int:doctor_id>/fees/', GetDoctorFeesAPIView.as_view(), name='get-doctor-fees'),
    path('all-availability-by-doctor/<int:doctor_id>/',AllAvailabilityByDoctorIdAPIView.as_view(), name='doctor-by-id'),
    path('book/<int:availability_id>/', BookAppointmentAPIView.as_view(), name='book-appointment'),
    path('appointments/<int:appointment_id>/confirm/', ConfirmAppointmentAPIView.as_view(), name='confirm-appointment'),
    path('appointments/<int:appointment_id>/reject/', RejectAppointmentAPIView.as_view(), name='reject-appointment'),
    path('appointments/<int:appointment_id>/cancel/', CancelAppointmentByPatientAPIView.as_view(), name='cancel-appointment-by-patient'),
    path('appointments/<int:appointment_id>/complete/', MarkAppointmentCompletedAPIView.as_view(), name='complete-appointment-by-patient'),
    path('appointments/<int:appointment_id>/mark-missed/', MarkAppointmentMissedByDoctorAPIView.as_view(), name='mark-appointment-missed'),
    path('doctor/Add-fees/',AddDoctorFeesAPIView.as_view(), name='Add-doctor-fees'),
    path('appointments/pending/', PendingAppointmentsView.as_view(), name='pending-appointments'),
    path('appointments/confirmed/', ConfirmedAppointmentsView.as_view(), name='confirmed-appointments'),
    path('appointments/completed/', CompletedAppointmentsView.as_view(), name='completed-appointments'),
    path('appointments/cancelled/',CancelledAppointmentsView.as_view(), name='cancelled-appointments'),
    

]


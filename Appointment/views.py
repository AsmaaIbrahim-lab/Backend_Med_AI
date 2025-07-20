from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Availability, DoctorProfile
from .serializers import AvailabilitySerializer
from rest_framework import serializers
from django.db.models import Q

class Availabilityviewset(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]
   

    def perform_create(self, serializer):
        try:
            doctor = DoctorProfile.objects.get(user=self.request.user)
        except DoctorProfile.DoesNotExist:
            raise PermissionDenied("المستخدم الحالي ليس طبيبًا")

        # لو many=True هنتعامل مع أكثر من عنصر
        availabilities = serializer.validated_data if isinstance(serializer.validated_data, list) else [serializer.validated_data]

        for availability in availabilities:
            date = availability.get('date')
            start_time = availability.get('start_time')
            end_time = availability.get('end_time')

            # تحقق إذا كان فيه موعد بنفس التوقيت
            exists = Availability.objects.filter(
                doctor=doctor,
                date=date,
                start_time=start_time,
                end_time=end_time
            ).exists()

            if exists:
                raise serializers.ValidationError(
                    f"يوجد بالفعل موعد مسجل لهذا اليوم ({date}) وهذا التوقيت ({start_time} - {end_time})"
                )
            # في Serializer أو APIView
            overlapping = Availability.objects.filter(
              doctor=doctor,
               date=date,
               start_time__lt=end_time,
                end_time__gt=start_time,
                           ).exclude(id=self.instance.id if hasattr(self, 'instance') else None).exists()

            if overlapping:
                    raise serializers.ValidationError(
        "يوجد تداخل زمني مع موعد آخر في نفس اليوم. الرجاء اختيار وقت مختلف."
    )

        serializer.save(doctor=doctor)

    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
# user/views.py
from rest_framework import generics
from .models import Availability
from .serializers import AvailabilitySerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class AllAvailabilityByDoctorIdAPIView(generics.ListAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        return Availability.objects.filter(doctor__id=doctor_id)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Appointment, Availability, PatientProfile
from .serializers import AppointmentSerializer
from rest_framework.permissions import IsAuthenticated

class BookAppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, availability_id):
        availability = get_object_or_404(Availability, id=availability_id)

        try:
            patient = PatientProfile.objects.get(user=request.user)
        except PatientProfile.DoesNotExist:
            return Response({"error": "المستخدم الحالي ليس مريضًا"}, status=status.HTTP_403_FORBIDDEN)

        # ✅ تحقق من عدم وجود حجز نشط على هذا التوقيت
        existing_appointment = Appointment.objects.filter(
            availability=availability,
            status__in=['pending', 'confirmed']
        ).exists()

        if existing_appointment:
            return Response({"error": "هذا الموعد محجوز بالفعل"}, status=status.HTTP_400_BAD_REQUEST)

        # إنشاء الحجز
        appointment = Appointment.objects.create(
            patient=patient,
            availability=availability,
            status='pending',
        )

        # اجعل التوقيت غير متاح
        availability.is_available = False
        availability.save()

        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)


       
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Appointment
from user.models import DoctorProfile
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.utils.timezone import now

class ConfirmAppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # التأكد أن المستخدم الحالي طبيب
        try:
            doctor = DoctorProfile.objects.get(user=request.user)
        except DoctorProfile.DoesNotExist:
            raise PermissionDenied("أنت لست طبيبًا")

        # التأكد أن الموعد يخص الطبيب ده
        if appointment.availability.doctor != doctor:
            raise PermissionDenied("لا يمكنك تأكيد موعد لا يخصك")

        # التأكد أن الموعد فعلاً pending
        if appointment.status != 'pending':
            return Response({"error": "لا يمكن تأكيد هذا الموعد لأنه ليس في حالة pending"}, status=status.HTTP_400_BAD_REQUEST)

        # تحديث الحالة
        appointment.status = 'confirmed'
        appointment.confirmed_at = now()  # لو عايزة تسجلي وقت التأكيد
        appointment.save()

        return Response({"message": "تم تأكيد الموعد بنجاح"}, status=status.HTTP_200_OK)
# views.py
class CancelAppointmentByPatientAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        try:
            patient = PatientProfile.objects.get(user=request.user)
        except PatientProfile.DoesNotExist:
            raise PermissionDenied("أنت لست مريضًا")

        if appointment.patient != patient:
            raise PermissionDenied("لا يمكنك إلغاء موعد لا يخصك")

        if appointment.status not in ['pending', 'confirmed']:
            return Response({"error": "لا يمكن إلغاء هذا الموعد"}, status=status.HTTP_400_BAD_REQUEST)

        # تحديث الحالة
        appointment.status = 'cancelled'
        appointment.cancellation_reason = request.data.get('cancellation_reason', 'تم الإلغاء من قبل المريض')
        appointment.save()

        # جعل الموعد متاحًا مرة أخرى
        appointment.availability.is_available = True
        appointment.availability.save()

        return Response({"message": "تم إلغاء الموعد بنجاح"}, status=status.HTTP_200_OK)
class RejectAppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        try:
            doctor = DoctorProfile.objects.get(user=request.user)
        except DoctorProfile.DoesNotExist:
            raise PermissionDenied("أنت لست طبيبًا")

        if appointment.availability.doctor != doctor:
            raise PermissionDenied("لا يمكنك رفض موعد لا يخصك")

        if appointment.status != 'pending':
            return Response({"error": "لا يمكن رفض هذا الموعد لأنه ليس في حالة pending"}, status=status.HTTP_400_BAD_REQUEST)

        # تحديث الحالة
        appointment.status = 'cancelled'
        appointment.cancellation_reason = request.data.get('cancellation_reason', 'تم الرفض من قبل الطبيب')
        appointment.save()

        # جعل التوقيت متاح مرة أخرى
        availability = appointment.availability
        availability.is_available = True
        availability.save()

        return Response({"message": "تم رفض الموعد بنجاح"}, status=status.HTTP_200_OK)
    
class MarkAppointmentCompletedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if appointment.availability.doctor.user != request.user:
            raise PermissionDenied("هذا الموعد لا يخصك")

        if appointment.status != 'confirmed':
            return Response({"error": "لا يمكن إتمام موعد غير مؤكد"}, status=400)

        appointment.status = 'completed'
        appointment.save()
        return Response({"message": "تم تحويل الموعد إلى completed"}, status=200)
    from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from Appointment.models import Appointment

class MarkAppointmentMissedByDoctorAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # تأكد أن الطبيب هو صاحب الموعد
        if appointment.availability.doctor.user != request.user:
            raise PermissionDenied("هذا الموعد لا يخصك")

        # تأكد أن الحالة حالياً confirmed
        if appointment.status != 'confirmed':
            return Response({"error": "لا يمكن تحويل حالة موعد غير مؤكد إلى missed"}, status=400)

        appointment.status = 'missed'
        appointment.save()
        return Response({"message": "تم تحويل الموعد إلى missed بواسطة الطبيب"}, status=200)
    # views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from user.models import DoctorProfile
from .serializers import DoctorFeesSerializer

class AddDoctorFeesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            doctor = DoctorProfile.objects.get(user=request.user)
        except DoctorProfile.DoesNotExist:
            raise NotFound("لم يتم العثور على دكتور مرتبط بهذا المستخدم.")

        serializer = DoctorFeesSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "تم تحديد سعر الكشف بنجاح", "fees": serializer.data['fees']})
        return Response(serializer.errors, status=400)


class GetDoctorFeesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, doctor_id):
        try:
            doctor = DoctorProfile.objects.get(id=doctor_id)
            return Response({
                'doctor_id': doctor.id,
                'doctor_name': doctor.user.get_full_name(),
                'fees': doctor.fees
            }, status=200)
        except DoctorProfile.DoesNotExist:
            return Response({'error': 'الطبيب غير موجود'}, status=404)

    


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Appointment
from .serializers import AppointmentSerializer
from user.models import DoctorProfile, PatientProfile

class PendingAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # تحقق إذا كان المستخدم طبيب
        try:
            doctor = DoctorProfile.objects.get(user=user)
            pending_appointments = Appointment.objects.filter(
                status='pending',
                availability__doctor=doctor
            )
        except DoctorProfile.DoesNotExist:
            # مش طبيب؟ جرب نشوفه مريض
            try:
                patient = PatientProfile.objects.get(user=user)
                pending_appointments = Appointment.objects.filter(
                    status='pending',
                    patient=patient
                )
            except PatientProfile.DoesNotExist:
                # لا طبيب ولا مريض
                return Response({"detail": "غير مصرح لك بعرض هذه البيانات."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(pending_appointments, many=True)
        return Response(serializer.data)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Appointment
from .serializers import AppointmentSerializer
from user.models import DoctorProfile, PatientProfile

class ConfirmedAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            doctor = DoctorProfile.objects.get(user=user)
            confirmed_appointments = Appointment.objects.filter(
                status='confirmed',
                availability__doctor=doctor
            )
        except DoctorProfile.DoesNotExist:
            try:
                patient = PatientProfile.objects.get(user=user)
                confirmed_appointments = Appointment.objects.filter(
                    status='confirmed',
                    patient=patient
                )
            except PatientProfile.DoesNotExist:
                return Response({"detail": "غير مصرح لك بعرض هذه البيانات."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(confirmed_appointments, many=True)
        return Response(serializer.data)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Appointment
from .serializers import AppointmentSerializer
from user.models import DoctorProfile, PatientProfile

class CompletedAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            doctor = DoctorProfile.objects.get(user=user)
            completed_appointments = Appointment.objects.filter(
                status='completed',
                availability__doctor=doctor
            )
        except DoctorProfile.DoesNotExist:
            try:
                patient = PatientProfile.objects.get(user=user)
                completed_appointments = Appointment.objects.filter(
                    status='completed',
                    patient=patient
                )
            except PatientProfile.DoesNotExist:
                return Response({"detail": "غير مصرح لك بعرض هذه البيانات."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(completed_appointments, many=True)
        return Response(serializer.data)
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Appointment
from .serializers import AppointmentSerializer
from user.models import DoctorProfile, PatientProfile

class CancelledAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            doctor = DoctorProfile.objects.get(user=user)
            cancelled_appointments = Appointment.objects.filter(
                status='cancelled',
                availability__doctor=doctor
            )
        except DoctorProfile.DoesNotExist:
            try:
                patient = PatientProfile.objects.get(user=user)
                cancelled_appointments = Appointment.objects.filter(
                    status='cancelled',
                    patient=patient
                )
            except PatientProfile.DoesNotExist:
                return Response({"detail": "غير مصرح لك بعرض هذه البيانات."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(cancelled_appointments, many=True)
        return Response(serializer.data)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.middleware.csrf import get_token

@api_view(['GET'])
def get_csrf_token(request):
    token = get_token(request)
    return Response({'csrfToken': token})






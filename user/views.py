# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.db import transaction
from django.contrib.auth import get_user_model
import json
import redis
from .models import Users, DoctorProfile, PatientProfile, CustomOutstandingToken, CustomBlacklistedToken
from .utils import is_strong_password, generate_username, send_otp_email, generate_otp, redis_client
from rest_framework.authtoken.models import Token
from django.utils import timezone
from .serializers import LoginSerializer  # Relative import from your app
from rest_framework_simplejwt.exceptions import TokenError
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from .models import Users, DoctorProfile,PatientProfile
from django.core.files import File
import os
from .models import Users, DoctorProfile, PatientProfile, CustomOutstandingToken, CustomBlacklistedToken,Area,Governorate
from user.models import Governorate  
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout






User = get_user_model()


def start_redirect(request):
    # For example, redirecting the user to the home page
    return redirect('home')

@api_view(['POST'])
def save_data(request):
    """
    API for saving user data.
    """
    required_fields = ['username', 'email', 'password', 'user_type', 'age', 'gender']
    data = request.data

    # Validate required fields
    for field in required_fields:
        if field not in data:
            return Response({"msg": f"{field} not found"}, status=status.HTTP_400_BAD_REQUEST)

    if data['user_type'] not in ['doctor', 'patient']:
        return Response({"msg": "Invalid user_type"}, status=status.HTTP_400_BAD_REQUEST)

    password = data['password']
    user = Users(username=data['username'], email=data['email'], age=data['age'], gender=data['gender'], 
                  password=password, user_type=data['user_type'])
    user.save()

    if data['user_type'] == 'doctor':
        doctor_profile = DoctorProfile(users=user, specialty=data.get('specialty', ''), license_number=data.get('license_number', ''))
        doctor_profile.save()
    else:
        patient_profile = PatientProfile(users=user, medical_history=data.get('medical_history', ''))
        patient_profile.save()

    return Response({"status": "success"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']  
        existing_token = CustomOutstandingToken.objects.filter(
            user=user,
            expires_at__gt=timezone.now()
        ).first()

        if existing_token:
            refresh = RefreshToken(existing_token.token)
        else:

         refresh = RefreshToken.for_user(user)
         CustomOutstandingToken.objects.create(
            user=user,
            jti=refresh['jti'],
            token=str(refresh),
            created_at=timezone.now(),
            expires_at=timezone.now() + refresh.lifetime
        )
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_type': user.user_type,
        })
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class CustomTokenRefreshView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')

        if refresh_token is None:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # حاول تحول الـ refresh token لكائن RefreshToken
            token = RefreshToken(refresh_token)
            # اعمل access token جديد
            access_token = str(token.access_token)

            return Response({'access': access_token}, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)



def logout_user(refresh_token):
    try:
        token = RefreshToken(refresh_token)
        outstanding_token = CustomOutstandingToken.objects.get(jti=token['jti'], token=refresh_token)

        if CustomBlacklistedToken.objects.filter(token=outstanding_token).exists():
            return False, "Already logged out"
        
        CustomBlacklistedToken.objects.create(token=outstanding_token, blacklisted_at=timezone.now())
        return True, "Logged out successfully"
    except (CustomOutstandingToken.DoesNotExist, TokenError):
        return False, "Invalid or expired token"
    except Exception as e:
        return False, f"System error: {str(e)}"


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({"status": 0, "message": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        success, message = logout_user(refresh_token)
        return Response({"status": 1 if success else 0, "message": message}, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def choose_account_type(request):
    account_type = request.data.get('account_type', '').strip().lower()
    if account_type not in ['doctor', 'patient']:
        return Response({"error": "Invalid account type. Must be 'doctor' or 'patient'."}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": f"{account_type.capitalize()} account type accepted.", "account_type": account_type}, status=status.HTTP_200_OK)
@api_view(['POST'])
def doctor_registration(request):
    data = request.data
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # Password validation
    if not password or not confirm_password:
        return Response({"error": "Both password and confirm password are required"}, status=status.HTTP_400_BAD_REQUEST)

    if password != confirm_password:
        return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

    required_fields = [
        'first_name', 'last_name', 'email', 'gender', 'birth_date',
        'license_number', 'university', 'specialty', 'experience_years',
        'governorate', 'area', 'phone_number'
    ]
    for field in required_fields:
        if not data.get(field):
            return Response({"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)

    email = data['email'].strip().lower()
    license_number = data['license_number'].strip()

    if Users.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

    if DoctorProfile.objects.filter(license_number__iexact=license_number).exists():
        return Response({"error": "License number already exists"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate governorate and area
    try:
        governorate = Governorate.objects.get(id=data['governorate'])
    except Governorate.DoesNotExist:
        return Response({"error": "Invalid governorate ID"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        area = Area.objects.get(id=data['area'])
    except Area.DoesNotExist:
        return Response({"error": "Invalid area ID"}, status=status.HTTP_400_BAD_REQUEST)

    if area.governorate_id != governorate.id:
        return Response({"error": "Area does not belong to the selected governorate"}, status=status.HTTP_400_BAD_REQUEST)

    data['password'] = data['password']
    data['email'] = email
    data['license_number'] = license_number
    data['user_type'] = 'doctor'

    # Save into Redis for OTP verification later
    otp = generate_otp()
    redis_client.setex(f"otp:{email}", 600, otp)
    redis_client.setex(f"doctor_data:{email}", 600, json.dumps(data))


    success = send_otp_email(email, otp, user_type="Doctor")
    if not success:
        return Response({"error": "Failed to send OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"message": "OTP sent. Please verify."}, status=status.HTTP_200_OK)

    

@api_view(['POST'])
def patient_registration(request):
    data = request.data
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not password or not confirm_password:
        return Response({"error": "Both password and confirm password are required"}, status=status.HTTP_400_BAD_REQUEST)

    if password != confirm_password:
        return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)



    required_fields = ['first_name', 'last_name', 'email','gender','birth_date', ]
    for field in required_fields:
        if not data.get(field):
            return Response({"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)

    email = data['email'].strip()
    if Users.objects.filter(email=email).exists():
        return Response({"error": "Email is already in use"}, status=status.HTTP_400_BAD_REQUEST)

    data['password'] =data['password']

    otp = generate_otp()
    redis_client.setex(f"otp:{email}", 600, otp)
    data['user_type'] = 'patient'  # <- CRITICAL ADDITION
    redis_client.setex(f"patient_data:{email}", 600, json.dumps(data))


    success = send_otp_email(email, otp, user_type="Patient")
    if not success:
        return Response({"error": "Failed to send OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"message": "OTP sent. Please verify."}, status=status.HTTP_200_OK)






@api_view(['POST'])
def verify_otp_and_create_account(request):
    otp = request.data.get('otp')
    if not otp:
        return Response({"error": "OTP is required"}, status=status.HTTP_400_BAD_REQUEST)

    email = None
    role = None
    data = None

    for potential_role in ['doctor', 'patient']:
        data_key = f"{potential_role}_data:*"
        for key in redis_client.scan_iter(data_key):
            current_email = key.split(':')[1]
            stored_otp = redis_client.get(f"otp:{current_email}")
            if stored_otp == otp:
                email = current_email
                role = potential_role
                data = json.loads(redis_client.get(f"{role}_data:{email}"))
                break
        if email:
            break

    if not email:
        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            redis_client.delete(f"otp:{email}")
            redis_client.delete(f"{role}_data:{email}")

            user = User(
                username=generate_username(data['first_name'], data['last_name']),
                email=email,
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                gender=data.get('gender'),
                birth_date=data.get('birth_date'),
                user_type=role  
            )
            user.set_password(data['password'])  # Securely hash the password
            user.save()

            if role == 'doctor':
                governorate_instance = Governorate.objects.get(id=data['governorate']) if data.get('governorate') else None
                area_instance = Area.objects.get(id=data['area']) if data.get('area') else None
                DoctorProfile.objects.create(user=user, license_number=data['license_number'], university=data['university'],
                                             specialty=data['specialty'], experience_years=data['experience_years'],phone_number=data['phone_number'],governorate=governorate_instance, area=area_instance)
            else:
                PatientProfile.objects.create(user=user, medical_history=data['medical_history'])

            transaction.on_commit(lambda: send_mail(
                "Welcome to Slamtak!",
                f"Your account was successfully created.\nUsername: {user.username}",
                "support@slamtak.com",
                [email],
                fail_silently=False
            ))

            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "username": user.username, "user_type": role, "email": user.email},
                            status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def resend_otp(request):
    email = request.data.get("email", "").strip()
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    otp = redis_client.get(f"otp:{email}")
    if not otp:
        return Response({"error": "OTP expired. Please register again."}, status=status.HTTP_400_BAD_REQUEST)

    role = 'doctor' if redis_client.exists(f"doctor_data:{email}") else 'patient'
    success = send_otp_email(email, otp, user_type=role.capitalize())
    if not success:
        return Response({"error": "Failed to resend OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"message": "OTP resent successfully."}, status=status.HTTP_200_OK)

@api_view(['POST'])
def request_password_reset_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required"}, status=400)

    try:
        user = Users.objects.get(email=email)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    otp = generate_otp()  # or generate_numeric_otp()
    redis_client.setex(f"password_reset_otp:{email}", 900, otp)

    send_otp_email(email, otp, user_type="Password Reset")

    return Response({"message": "OTP sent to your email."}, status=200)

@api_view(['POST'])
def reset_password_with_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    if not all([email, otp, new_password, confirm_password]):
        return Response({"error": "All fields are required."}, status=400)

    stored_otp = redis_client.get(f"password_reset_otp:{email}")
    if not stored_otp or stored_otp != otp:
        return Response({"error": "Invalid or expired OTP."}, status=400)

    if new_password != confirm_password:
        return Response({"error": "Passwords do not match."}, status=400)


    try:
        user = Users.objects.get(email=email)
        user.new_password
        user.save()

        redis_client.delete(f"password_reset_otp:{email}")

        send_mail(
            "Your password was changed",
            "Your password has been successfully reset.",
            "support@slamtak.com",
            [email],
            fail_silently=False
        )

        return Response({"message": "Password reset successful."}, status=200)
    except Users.DoesNotExist:
        return Response({"error": "User not found."}, status=404)
from rest_framework.decorators import api_view
from rest_framework.response import Response


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Users, DoctorProfile,PatientProfile
from django.core.files import File
import os

@api_view(['POST'])
def upload_image(request):

    if 'user_email' not in request.data:
        return Response({"error": "يجب تحديد معرف المستخدم"}, status=400)
    
    if 'image' not in request.FILES:  # تغيير من request.data إلى request.FILES
        return Response({"error": "يجب رفع الملف مباشرةً"}, status=400)
    
    try:
        user = Users.objects.get(email=request.data['user_email'])
    except Users.DoesNotExist:
        return Response({"error": "المستخدم غير موجود"}, status=404)
    
    try:
        user.image.save(
            request.FILES['image'].name,
            request.FILES['image']
        )
        return Response({"image_url": user.image.url})
    
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
   

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user

    try:
        # Delete profile if applicable
        if user.user_type == 'doctor':
            user.doctorprofile.delete()
        elif user.user_type == 'patient':
            user.patientprofile.delete()

        # Delete auth token
        Token.objects.filter(user=user).delete()

        # Log the user out
        logout(request)

        # Delete the user
        user.delete()

        return Response({"message": "Account deleted successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"Failed to delete account: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_fcm_token(request):
    token = request.data.get('fcm_token')
    if not token:
        return Response({"error": "FCM token is required"}, status=400)

    user = request.user
    user.fcm_token = token
    user.save()

    return Response({"message": "FCM token updated successfully"})
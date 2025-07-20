from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializer import UserSerializer, DoctorProfileSerializer, PatientProfileSerializer
from user.models import DoctorProfile, PatientProfile
import logging

logger = logging.getLogger(__name__)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    user = request.user
    logger.info(f"Profile view accessed by user: {user.username}")

    # GET request - Return user and profile info
    if request.method == 'GET':
        try:
            user_data = UserSerializer(user).data
            profile_data = {}

            if user.user_type == 'doctor':
                profile = DoctorProfile.objects.filter(user=user).first()
                if profile:
                    profile_data = DoctorProfileSerializer(profile).data

            elif user.user_type == 'patient':
                profile = PatientProfile.objects.filter(user=user).first()
                if profile:
                    profile_data = PatientProfileSerializer(profile).data

            else:
                logger.warning(f"Invalid user type: {user.user_type}")
                return Response(
                    {"error": "Invalid user type."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                "user": user_data,
                "profile": profile_data
            })

        except Exception as e:
            logger.error(f"Error in GET profile: {str(e)}")
            return Response(
                {"error": "An error occurred while fetching profile."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # PUT request - Update user and profile info
    elif request.method == 'PUT':
        try:
            logger.debug(f"Raw request data: {request.data}")

            user_data = request.data.get('user', {})
            user_data.pop('email', None)
            user_data.pop('image', None)
            
            user_data.pop('password', None)
            user_data.pop('user_type', None)

            # Merge request.data with user
            combined_data = dict(request.data)  # all profile fields
            combined_data['user'] = user_data

            if user.user_type == 'doctor':
                profile = DoctorProfile.objects.filter(user=user).first()
                if not profile:
                    return Response({"error": "Doctor profile not found."}, status=404)
                serializer = DoctorProfileSerializer(profile, data=combined_data, partial=True)

            elif user.user_type == 'patient':
                profile = PatientProfile.objects.filter(user=user).first()
                if not profile:
                    return Response({"error": "Patient profile not found."}, status=404)
                serializer = PatientProfileSerializer(profile, data=combined_data, partial=True)

            else:
                return Response({"error": "Invalid user type."}, status=400)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Profile updated successfully.",
                    "user": UserSerializer(user).data,
                    "profile": serializer.data
                })

            return Response({"error": "Invalid data", "details": serializer.errors}, status=400)

        except Exception as e:
            logger.error(f"PUT error: {str(e)}")
            return Response({"error": "An error occurred while updating profile."},status=500)

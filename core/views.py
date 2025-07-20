from django.shortcuts import render


# Create your views here.
from django.shortcuts import render
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from.models import Users,DoctorProfile
from.serializers import UsersSerializer,DoctorProfileSerializer,DoctorSummarySerializer
from django.shortcuts import get_object_or_404

# class DoctorSearchView(generics.RetrieveAPIView):
#     queryset = Users.objects.all()
#     serializer_class = DoctorSummarySerializer
#     lookup_field = 'username'  # يمكنك تغييره إلى 'pk' أو أي حقل آخر
    
#     # أو يمكنك استخدام هذه الطريقة للتحكم الكامل
#     def get_object(self):
#         user_email= self.kwargs.get('email')
#         return get_object_or_404( Users, email=user_email)   
class DoctorSearchView(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = DoctorSummarySerializer
    lookup_field = 'username'
    
    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(Users, username=username)
# View لملخص الأطباء
class DoctorSummaryView(APIView):
    def get(self, request):
        try:
            
            doctors = Users.objects.filter(user_type='doctor').select_related('doctor_profile')
            serializer = DoctorSummarySerializer(doctors, many=True)
            
            return Response({
                "status": "success",
                "doctors": serializer.data
            })
            
        except Exception as e:
            return Response({"error": str(e)}, status=400)
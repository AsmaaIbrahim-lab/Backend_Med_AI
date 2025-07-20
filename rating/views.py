from rest_framework import generics, permissions
from .models import Review
from .serializers import  ReviewSerializer
from rest_framework.exceptions import ValidationError

class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # التأكد من أن المستخدم الحالي هو مريض
        if not hasattr(self.request.user, 'patient_profile'):
            raise ValidationError("Only patients can submit reviews")
        
        # تعيين المريض الحالي تلقائياً
        serializer.save(patient=self.request.user)
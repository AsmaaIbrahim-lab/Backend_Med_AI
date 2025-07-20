from django.urls import path
from .views import ReviewCreateView

urlpatterns = [
    # إنشاء تقييم جديد (POST فقط)
    path('create/', ReviewCreateView.as_view(), name='review-create'),
    
    # (اختياري) إضافة endpoints أخرى مثل عرض التقييمات
    # path('list/', ReviewListView.as_view(), name='review-list'),
]
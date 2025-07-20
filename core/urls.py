from django.urls import path
from .views import DoctorSearchView,DoctorSummaryView
urlpatterns=[
    path('DoctorSearchView/<str:username>/', DoctorSearchView.as_view(), name='DoctorSearchView'),
    path('DoctorSummaryView/', DoctorSummaryView.as_view(), name='DoctorSummaryView'),

]
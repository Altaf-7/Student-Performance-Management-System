from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('offering/<int:pk>/', views.subject_offering_detail, name='offering_detail'),
    path('offering/<int:pk>/lecture/new/', views.lecture_create, name='lecture_create'),
]

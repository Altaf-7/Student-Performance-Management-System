from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.redirect_to_dashboard, name='redirect'),
    path('student/', views.student_dashboard, name='student'),
    path('faculty/', views.faculty_dashboard, name='faculty'),
    path('admin-home/', views.admin_dashboard, name='admin_home'),
]

from django.urls import path
from django.views.generic import TemplateView
from accounts.decorators import student_required

app_name = 'students'

urlpatterns = [
    path('dashboard/', student_required(TemplateView.as_view(template_name='student/dashboard.html')), name='dashboard'),
]

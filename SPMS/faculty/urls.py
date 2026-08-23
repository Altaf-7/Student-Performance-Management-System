from django.urls import path
from django.views.generic import TemplateView
from accounts.decorators import faculty_required

app_name = 'faculty'

urlpatterns = [
    path('dashboard/', faculty_required(TemplateView.as_view(template_name='faculty/dashboard.html')), name='dashboard'),
]

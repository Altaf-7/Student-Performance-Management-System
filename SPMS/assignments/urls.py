from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('offering/<int:pk>/new/', views.assignment_create, name='create'),
    path('<int:pk>/submit/', views.assignment_submit, name='submit'),
    path('<int:pk>/submissions/', views.assignment_submissions, name='submissions'),
    path('submission/<int:pk>/grade/', views.submission_grade, name='grade'),
]

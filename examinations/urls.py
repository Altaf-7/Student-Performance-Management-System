from django.urls import path
from . import views

app_name = 'examinations'

urlpatterns = [
    path('offering/<int:pk>/new/', views.exam_create, name='create'),
    path('<int:pk>/results/', views.exam_results, name='results'),
]

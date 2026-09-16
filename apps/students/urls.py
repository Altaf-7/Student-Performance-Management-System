from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    path("", views.StudentListView.as_view(), name="student_list"),
    path("add/", views.StudentCreateView.as_view(), name="student_add"),
    path("<int:pk>/", views.StudentDetailView.as_view(), name="student_detail"),
    path("<int:pk>/edit/", views.StudentUpdateView.as_view(), name="student_edit"),
    path("<int:pk>/deactivate/", views.StudentDeactivateView.as_view(), name="student_deactivate"),
    path("<int:pk>/activate/", views.StudentActivateView.as_view(), name="student_activate"),
    path("<int:pk>/delete/", views.StudentDeleteView.as_view(), name="student_delete"),
]

from django.urls import path

from . import views

app_name = "faculty"

urlpatterns = [
    path("", views.FacultyListView.as_view(), name="faculty_list"),
    path("add/", views.FacultyCreateView.as_view(), name="faculty_add"),
    path("<int:pk>/", views.FacultyDetailView.as_view(), name="faculty_detail"),
    path("<int:pk>/edit/", views.FacultyUpdateView.as_view(), name="faculty_edit"),
    path("<int:pk>/deactivate/", views.FacultyDeactivateView.as_view(), name="faculty_deactivate"),
    path("<int:pk>/activate/", views.FacultyActivateView.as_view(), name="faculty_activate"),
    path("<int:pk>/delete/", views.FacultyDeleteView.as_view(), name="faculty_delete"),
]

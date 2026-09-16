from django.urls import path

from . import views

app_name = "academics"

urlpatterns = [
    path("departments/", views.DepartmentListView.as_view(), name="department_list"),
    path("departments/add/", views.DepartmentCreateView.as_view(), name="department_add"),
    path("departments/<int:pk>/edit/", views.DepartmentUpdateView.as_view(), name="department_edit"),
    path("departments/<int:pk>/delete/", views.DepartmentDeleteView.as_view(), name="department_delete"),

    path("semesters/", views.SemesterListView.as_view(), name="semester_list"),
    path("semesters/add/", views.SemesterCreateView.as_view(), name="semester_add"),
    path("semesters/<int:pk>/edit/", views.SemesterUpdateView.as_view(), name="semester_edit"),
    path("semesters/<int:pk>/delete/", views.SemesterDeleteView.as_view(), name="semester_delete"),

    path("courses/", views.CourseListView.as_view(), name="course_list"),
    path("courses/add/", views.CourseCreateView.as_view(), name="course_add"),
    path("courses/<int:pk>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("courses/<int:pk>/edit/", views.CourseUpdateView.as_view(), name="course_edit"),
    path("courses/<int:pk>/delete/", views.CourseDeleteView.as_view(), name="course_delete"),

    path("enrollments/", views.EnrollmentListView.as_view(), name="enrollment_list"),
    path("enrollments/add/", views.EnrollmentCreateView.as_view(), name="enrollment_add"),
    path("enrollments/<int:pk>/delete/", views.EnrollmentDeleteView.as_view(), name="enrollment_delete"),
]

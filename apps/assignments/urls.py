from django.urls import path

from . import views

app_name = "assignments"

urlpatterns = [
    path("", views.AssignmentListView.as_view(), name="assignment_list"),
    path("add/", views.AssignmentCreateView.as_view(), name="assignment_add"),
    path("<int:pk>/", views.AssignmentDetailView.as_view(), name="assignment_detail"),
    path("<int:pk>/edit/", views.AssignmentUpdateView.as_view(), name="assignment_edit"),
    path("<int:pk>/delete/", views.AssignmentDeleteView.as_view(), name="assignment_delete"),
    path("submission/<int:pk>/grade/", views.GradeSubmissionView.as_view(), name="grade_submission"),

    path("my/", views.MyAssignmentsView.as_view(), name="my_assignments"),
    path("my/<int:pk>/submit/", views.SubmitAssignmentView.as_view(), name="submit_assignment"),
]

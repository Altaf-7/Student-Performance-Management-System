from django.urls import path

from . import views

app_name = "examinations"

urlpatterns = [
    path("", views.ExaminationListView.as_view(), name="examination_list"),
    path("add/", views.ExaminationCreateView.as_view(), name="examination_add"),
    path("<int:pk>/edit/", views.ExaminationUpdateView.as_view(), name="examination_edit"),
    path("<int:pk>/delete/", views.ExaminationDeleteView.as_view(), name="examination_delete"),
    path("<int:pk>/results/", views.EnterResultsView.as_view(), name="enter_results"),

    path("my-results/", views.MyResultsView.as_view(), name="my_results"),
    path("marksheet/<int:student_id>/<int:semester_id>/", views.MarksheetView.as_view(), name="marksheet"),
]

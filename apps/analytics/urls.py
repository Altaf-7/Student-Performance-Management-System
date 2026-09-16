from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("at-risk/", views.AtRiskStudentsView.as_view(), name="at_risk"),
    path("admin/", views.AdminAnalyticsView.as_view(), name="admin_analytics"),
    path("student/", views.StudentAnalyticsView.as_view(), name="student_analytics"),
]

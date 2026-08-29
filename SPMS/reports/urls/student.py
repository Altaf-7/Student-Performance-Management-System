from django.urls import path
from reports.views import student as views

app_name = 'student_reports'

urlpatterns = [
    path('reports/', views.StudentReportDashboardView.as_view(), name='dashboard'),
    path('reports/attendance/', views.StudentAttendanceReportView.as_view(), name='attendance'),
    path('reports/assignments/', views.StudentAssignmentReportView.as_view(), name='assignments'),
    path('reports/exams/', views.StudentExamReportView.as_view(), name='exams'),
    path('reports/semesters/', views.StudentSemesterReportView.as_view(), name='semesters'),
    path('analytics/', views.StudentAnalyticsView.as_view(), name='analytics'),
]

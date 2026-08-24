from django.urls import path
from reports.views import faculty as views

app_name = 'faculty_reports'

urlpatterns = [
    path('reports/', views.FacultyReportDashboardView.as_view(), name='dashboard'),
    path('reports/attendance/', views.FacultyAttendanceReportView.as_view(), name='attendance'),
    path('reports/assignments/', views.FacultyAssignmentReportView.as_view(), name='assignments'),
    path('reports/exams/', views.FacultyExamReportView.as_view(), name='exams'),
    path('reports/students/', views.FacultyStudentPerformanceView.as_view(), name='students'),
]

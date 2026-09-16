from django.urls import path
from reports.views import admin as views

app_name = 'admin_reports'

urlpatterns = [
    path('reports/', views.AdminReportDashboardView.as_view(), name='dashboard'),
    path('reports/enrollment/', views.EnrollmentReportView.as_view(), name='enrollment'),
    path('reports/departments/', views.DepartmentReportView.as_view(), name='departments'),
    path('reports/courses/', views.CourseReportView.as_view(), name='courses'),
    path('reports/batches/', views.BatchReportView.as_view(), name='batches'),
    path('reports/semesters/', views.SemesterReportView.as_view(), name='semesters'),
    path('reports/offerings/', views.SubjectOfferingReportView.as_view(), name='offerings'),
    
    path('analytics/', views.AdminAnalyticsView.as_view(), name='analytics'),
    path('analytics/at-risk/', views.AcademicMonitoringView.as_view(), name='at_risk'),
    path('analytics/at-risk/export/', views.ExportAtRiskCSVView.as_view(), name='export_at_risk'),
]

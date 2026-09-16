from django.urls import path
from students import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.StudentDashboardView.as_view(), name='dashboard'),
    path('profile/', views.StudentProfileView.as_view(), name='profile'),
    path('course/', views.StudentCourseView.as_view(), name='course'),
    path('semesters/', views.SemesterListView.as_view(), name='semesters'),
    path('semesters/<int:pk>/', views.SemesterDetailView.as_view(), name='semester_detail'),
    path('subjects/', views.SubjectListView.as_view(), name='subjects'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
    path('attendance/', views.AttendanceSummaryView.as_view(), name='attendance_summary'),
    path('attendance/<int:offering_id>/', views.SubjectAttendanceView.as_view(), name='subject_attendance'),
    path('assignments/', views.AssignmentListView.as_view(), name='assignments'),
    path('assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('assignments/<int:pk>/submit/', views.AssignmentSubmitView.as_view(), name='assignment_submit'),
    path('assignments/<int:pk>/download/', views.DownloadAssignmentAttachmentView.as_view(), name='download_assignment_attachment'),
    path('submissions/<int:pk>/download/', views.DownloadSubmissionView.as_view(), name='download_submission'),
    path('exams/', views.ExamListView.as_view(), name='exams'),
    path('exams/<int:pk>/', views.ExamDetailView.as_view(), name='exam_detail'),
    path('results/', views.ResultListView.as_view(), name='results'),
    path('semester-report/', views.SemesterReportView.as_view(), name='semester_report'),
    path('performance/', views.PerformanceView.as_view(), name='performance'),
]

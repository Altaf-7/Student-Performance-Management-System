from django.urls import path
from faculty import views

app_name = 'faculty'

urlpatterns = [
    path('dashboard/', views.FacultyDashboardView.as_view(), name='dashboard'),
    path('profile/', views.FacultyProfileView.as_view(), name='profile'),
    
    # Subjects & Students
    path('subjects/', views.SubjectOfferingListView.as_view(), name='subjects'),
    path('subjects/<int:pk>/', views.SubjectOfferingDetailView.as_view(), name='subject_detail'),
    path('subjects/<int:pk>/students/', views.StudentListView.as_view(), name='students'),
    
    # Lectures
    path('subjects/<int:offering_id>/lectures/', views.LectureListView.as_view(), name='lectures'),
    path('subjects/<int:offering_id>/lectures/create/', views.LectureCreateView.as_view(), name='lecture_create'),
    path('lectures/<int:pk>/', views.LectureDetailView.as_view(), name='lecture_detail'),
    path('lectures/<int:pk>/edit/', views.LectureUpdateView.as_view(), name='lecture_update'),
    path('lectures/<int:pk>/delete/', views.LectureDeleteView.as_view(), name='lecture_delete'),
    
    # Attendance
    path('lectures/<int:lecture_id>/attendance/', views.AttendanceEntryView.as_view(), name='attendance_entry'),
    path('subjects/<int:offering_id>/attendance/', views.AttendanceSummaryView.as_view(), name='attendance_summary'),
    
    # Assignments
    path('assignments/', views.AssignmentListView.as_view(), name='assignments'),
    path('assignments/create/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('assignments/<int:pk>/edit/', views.AssignmentUpdateView.as_view(), name='assignment_update'),
    path('assignments/<int:pk>/delete/', views.AssignmentDeleteView.as_view(), name='assignment_delete'),
    path('assignments/<int:assignment_id>/submissions/', views.SubmissionListView.as_view(), name='submissions'),
    path('submissions/<int:pk>/', views.SubmissionDetailView.as_view(), name='submission_detail'),
    path('submissions/<int:pk>/download/', views.DownloadSubmissionView.as_view(), name='download_submission'),
    path('assignments/<int:pk>/download/', views.DownloadAssignmentAttachmentView.as_view(), name='download_assignment_attachment'),
    
    # Exams
    path('exams/', views.ExamListView.as_view(), name='exams'),
    path('exams/create/', views.ExamCreateView.as_view(), name='exam_create'),
    path('exams/<int:pk>/', views.ExamDetailView.as_view(), name='exam_detail'),
    path('exams/<int:pk>/edit/', views.ExamUpdateView.as_view(), name='exam_update'),
    path('exams/<int:pk>/delete/', views.ExamDeleteView.as_view(), name='exam_delete'),
    path('exams/<int:exam_id>/results/', views.ExamResultEntryView.as_view(), name='exam_results'),
    path('exams/<int:exam_id>/publish/', views.ExamPublishView.as_view(), name='exam_publish'),
    
    # Performance
    path('performance/', views.FacultyPerformanceView.as_view(), name='performance'),
]


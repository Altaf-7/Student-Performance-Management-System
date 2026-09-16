from django.urls import path
from spms_admin import views

app_name = 'spms_admin'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.AdminDashboardView.as_view(), name='dashboard'),
    
    # Users
    path('users/', views.UserListView.as_view(), name='users'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/status/', views.UserStatusUpdateView.as_view(), name='user_status'),
    
    # Students
    path('students/', views.StudentListView.as_view(), name='students'),
    path('students/create/', views.StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    
    # Faculty
    path('faculty/', views.FacultyListView.as_view(), name='faculty_list'),
    path('faculty/create/', views.FacultyCreateView.as_view(), name='faculty_create'),
    path('faculty/<int:pk>/', views.FacultyDetailView.as_view(), name='faculty_detail'),
    
    # Departments
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),

    # Courses
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    path('courses/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),

    # Batches
    path('batches/', views.CourseBatchListView.as_view(), name='batch_list'),
    path('batches/create/', views.CourseBatchCreateView.as_view(), name='batch_create'),
    path('batches/<int:pk>/edit/', views.CourseBatchUpdateView.as_view(), name='batch_update'),
    path('batches/<int:pk>/delete/', views.CourseBatchDeleteView.as_view(), name='batch_delete'),

    # Semesters
    path('semesters/', views.SemesterListView.as_view(), name='semester_list'),
    path('semesters/create/', views.SemesterCreateView.as_view(), name='semester_create'),
    path('semesters/<int:pk>/edit/', views.SemesterUpdateView.as_view(), name='semester_update'),
    path('semesters/<int:pk>/delete/', views.SemesterDeleteView.as_view(), name='semester_delete'),

    # Subjects
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/create/', views.SubjectCreateView.as_view(), name='subject_create'),
    path('subjects/<int:pk>/edit/', views.SubjectUpdateView.as_view(), name='subject_update'),
    path('subjects/<int:pk>/delete/', views.SubjectDeleteView.as_view(), name='subject_delete'),

    # Offerings
    path('offerings/', views.SubjectOfferingListView.as_view(), name='offering_list'),
    path('offerings/create/', views.SubjectOfferingCreateView.as_view(), name='offering_create'),
    path('offerings/<int:pk>/edit/', views.SubjectOfferingUpdateView.as_view(), name='offering_update'),
    path('offerings/<int:pk>/delete/', views.SubjectOfferingDeleteView.as_view(), name='offering_delete'),
    
    # Reports & Profile
    path('profile/', views.AdminProfileView.as_view(), name='profile'),
    path('reports/', views.AdminReportsView.as_view(), name='reports'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.students.api import StudentViewSet
from apps.faculty.api import FacultyViewSet
from apps.academics.api import DepartmentViewSet, SemesterViewSet, CourseViewSet, EnrollmentViewSet
from apps.attendance.api import AttendanceViewSet
from apps.assignments.api import AssignmentViewSet, AssignmentSubmissionViewSet
from apps.examinations.api import ExaminationViewSet, ExamResultViewSet
from apps.notifications.api import NotificationViewSet
from apps.analytics.api import AnalyticsAPIView

router = DefaultRouter()
router.register("students", StudentViewSet, basename="api-students")
router.register("faculty", FacultyViewSet, basename="api-faculty")
router.register("departments", DepartmentViewSet, basename="api-departments")
router.register("semesters", SemesterViewSet, basename="api-semesters")
router.register("courses", CourseViewSet, basename="api-courses")
router.register("enrollments", EnrollmentViewSet, basename="api-enrollments")
router.register("attendance", AttendanceViewSet, basename="api-attendance")
router.register("assignments", AssignmentViewSet, basename="api-assignments")
router.register("submissions", AssignmentSubmissionViewSet, basename="api-submissions")
router.register("examinations", ExaminationViewSet, basename="api-examinations")
router.register("results", ExamResultViewSet, basename="api-results")
router.register("notifications", NotificationViewSet, basename="api-notifications")

urlpatterns = [
    path("analytics/", AnalyticsAPIView.as_view(), name="api-analytics"),
    path("", include(router.urls)),
]

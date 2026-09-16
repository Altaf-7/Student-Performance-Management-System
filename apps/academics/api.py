from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.api_permissions import IsAdminRole
from .models import Department, Semester, Course, Enrollment
from .serializers import DepartmentSerializer, SemesterSerializer, CourseSerializer, EnrollmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["department", "semester", "faculty", "status"]
    search_fields = ["course_code", "course_name"]

    def get_queryset(self):
        qs = Course.objects.select_related("department", "semester", "faculty")
        user = self.request.user
        if user.is_admin_role:
            return qs
        if user.is_faculty_role:
            return qs.filter(faculty=user)
        return qs.filter(enrollments__student=user).distinct()

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            from apps.accounts.api_permissions import IsAdminRole as _Admin
            return [IsAuthenticated(), _Admin()]
        return [IsAuthenticated()]


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filterset_fields = ["course", "semester", "status", "student"]

    def get_queryset(self):
        return Enrollment.objects.select_related("student", "course", "semester")

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.api_permissions import IsFacultyOrAdminOrReadOnlyStudent
from .models import Assignment, AssignmentSubmission
from .serializers import AssignmentSerializer, AssignmentSubmissionSerializer


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated, IsFacultyOrAdminOrReadOnlyStudent]
    filterset_fields = ["course"]

    def get_queryset(self):
        qs = Assignment.objects.select_related("course")
        user = self.request.user
        if user.is_admin_role:
            return qs
        if user.is_faculty_role:
            return qs.filter(course__faculty=user)
        return qs.filter(course__enrollments__student=user).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["assignment", "status"]

    def get_queryset(self):
        qs = AssignmentSubmission.objects.select_related("assignment", "student")
        user = self.request.user
        if user.is_admin_role:
            return qs
        if user.is_faculty_role:
            return qs.filter(assignment__course__faculty=user)
        return qs.filter(student=user)

    def perform_create(self, serializer):
        if not self.request.user.is_student_role:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only students can submit assignments.")
        serializer.save(student=self.request.user)

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.api_permissions import IsFacultyOrAdmin
from .models import Examination, ExamResult
from .serializers import ExaminationSerializer, ExamResultSerializer


class ExaminationViewSet(viewsets.ModelViewSet):
    serializer_class = ExaminationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["course", "semester", "exam_type", "is_published"]

    def get_queryset(self):
        qs = Examination.objects.select_related("course", "semester")
        user = self.request.user
        if user.is_admin_role:
            return qs
        if user.is_faculty_role:
            return qs.filter(course__faculty=user)
        return qs.filter(course__enrollments__student=user, is_published=True).distinct()

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsFacultyOrAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ExamResultViewSet(viewsets.ModelViewSet):
    serializer_class = ExamResultSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["examination", "course", "student"]

    def get_queryset(self):
        qs = ExamResult.objects.select_related("student", "examination", "course")
        user = self.request.user
        if user.is_admin_role:
            return qs
        if user.is_faculty_role:
            return qs.filter(course__faculty=user)
        return qs.filter(student=user, examination__is_published=True)

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsFacultyOrAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(entered_by=self.request.user)

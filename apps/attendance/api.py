from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.api_permissions import IsFacultyOrAdminOrReadOnlyStudent
from .models import Attendance
from .serializers import AttendanceSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsFacultyOrAdminOrReadOnlyStudent]
    filterset_fields = ["course", "student", "date", "status"]

    def get_queryset(self):
        qs = Attendance.objects.select_related("student", "course")
        user = self.request.user
        if user.is_admin_role:
            return qs
        if user.is_faculty_role:
            return qs.filter(course__faculty=user)
        return qs.filter(student=user)

    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)

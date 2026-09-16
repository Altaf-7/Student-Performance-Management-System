from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.api_permissions import IsAdminRole
from .models import StudentProfile
from .serializers import StudentProfileSerializer


class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filterset_fields = ["department", "semester", "academic_status"]
    search_fields = ["student_id", "user__first_name", "user__last_name", "user__email"]

    def get_queryset(self):
        return StudentProfile.objects.select_related("user", "department", "semester")

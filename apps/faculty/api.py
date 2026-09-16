from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.api_permissions import IsAdminRole
from .models import FacultyProfile
from .serializers import FacultyProfileSerializer


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FacultyProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filterset_fields = ["department", "designation"]
    search_fields = ["faculty_id", "user__first_name", "user__last_name"]

    def get_queryset(self):
        return FacultyProfile.objects.select_related("user", "department")

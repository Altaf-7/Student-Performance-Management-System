from rest_framework import serializers

from apps.accounts.serializers import UserSummarySerializer
from .models import FacultyProfile


class FacultyProfileSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = FacultyProfile
        fields = ["id", "faculty_id", "user", "department", "department_name", "designation", "is_active"]

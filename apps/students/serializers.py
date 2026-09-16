from rest_framework import serializers

from apps.accounts.serializers import UserSummarySerializer
from .models import StudentProfile


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    semester_name = serializers.CharField(source="semester.name", read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            "id", "student_id", "user", "date_of_birth", "gender", "address",
            "department", "department_name", "semester", "semester_name",
            "enrollment_year", "academic_status",
        ]

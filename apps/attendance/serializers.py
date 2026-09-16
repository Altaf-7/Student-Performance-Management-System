from rest_framework import serializers

from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    course_code = serializers.CharField(source="course.course_code", read_only=True)

    class Meta:
        model = Attendance
        fields = ["id", "student", "student_name", "course", "course_code", "date", "status", "marked_by"]
        read_only_fields = ["marked_by"]

    def get_student_name(self, obj):
        return obj.student.get_full_name()

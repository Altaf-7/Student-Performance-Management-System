from rest_framework import serializers

from .models import Examination, ExamResult


class ExaminationSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="course.course_code", read_only=True)

    class Meta:
        model = Examination
        fields = ["id", "name", "exam_type", "course", "course_code", "semester", "academic_year", "exam_date", "maximum_marks", "description", "is_published"]


class ExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = ExamResult
        fields = ["id", "student", "student_name", "examination", "course", "maximum_marks", "obtained_marks", "grade", "remarks"]
        read_only_fields = ["grade"]

    def get_student_name(self, obj):
        return obj.student.get_full_name()

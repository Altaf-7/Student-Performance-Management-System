from rest_framework import serializers

from .models import Assignment, AssignmentSubmission


class AssignmentSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="course.course_code", read_only=True)

    class Meta:
        model = Assignment
        fields = ["id", "title", "description", "course", "course_code", "attachment", "due_date", "maximum_marks", "created_by"]
        read_only_fields = ["created_by"]


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentSubmission
        fields = ["id", "assignment", "student", "student_name", "file", "submitted_at", "status", "marks_obtained", "feedback"]
        read_only_fields = ["student", "status"]

    def get_student_name(self, obj):
        return obj.student.get_full_name()

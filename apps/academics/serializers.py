from rest_framework import serializers

from .models import Department, Semester, Course, Enrollment


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "code", "head_of_department", "description", "contact_email"]


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ["id", "name", "semester_number", "academic_year", "start_date", "end_date", "is_active"]


class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    faculty_name = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "course_code", "course_name", "description", "credits", "department", "department_name", "semester", "faculty", "faculty_name", "status"]

    def get_faculty_name(self, obj):
        return obj.faculty.get_full_name() if obj.faculty else None


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    course_code = serializers.CharField(source="course.course_code", read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "student", "student_name", "course", "course_code", "academic_year", "semester", "enrollment_date", "status"]

    def get_student_name(self, obj):
        return obj.student.get_full_name()

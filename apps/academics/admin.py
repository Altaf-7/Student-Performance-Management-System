from django.contrib import admin

from .models import Department, Semester, Course, Enrollment, GradeScale


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "head_of_department", "contact_email", "created_at")
    search_fields = ("name", "code")
    list_filter = ("created_at",)
    autocomplete_fields = ("head_of_department",)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("name", "semester_number", "academic_year", "start_date", "end_date", "is_active")
    list_filter = ("academic_year", "is_active")
    search_fields = ("name", "academic_year")
    ordering = ("-academic_year", "semester_number")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_code", "course_name", "department", "semester", "faculty", "credits", "status")
    list_filter = ("department", "semester", "status")
    search_fields = ("course_code", "course_name")
    autocomplete_fields = ("faculty",)
    fieldsets = (
        (None, {"fields": ("course_code", "course_name", "description")}),
        ("Academic", {"fields": ("department", "semester", "credits", "faculty", "status")}),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "semester", "academic_year", "status", "enrollment_date")
    list_filter = ("status", "semester", "academic_year")
    search_fields = ("student__username", "student__first_name", "student__last_name", "course__course_code")
    autocomplete_fields = ("student", "course")
    readonly_fields = ("enrollment_date",)


@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display = ("grade", "min_percentage", "max_percentage", "grade_point")
    ordering = ("-min_percentage",)

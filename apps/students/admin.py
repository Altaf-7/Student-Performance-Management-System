from django.contrib import admin

from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("student_id", "user", "department", "semester", "enrollment_year", "academic_status")
    list_filter = ("department", "semester", "academic_status")
    search_fields = ("student_id", "user__username", "user__first_name", "user__last_name", "user__email")
    autocomplete_fields = ("user", "department", "semester")

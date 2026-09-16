from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "date", "status", "marked_by")
    list_filter = ("status", "date", "course")
    search_fields = ("student__username", "student__first_name", "student__last_name", "course__course_code")
    autocomplete_fields = ("student", "course", "marked_by")
    date_hierarchy = "date"

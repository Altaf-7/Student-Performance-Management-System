from django.contrib import admin

from .models import FacultyProfile


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ("faculty_id", "user", "department", "designation", "is_active")
    list_filter = ("department", "designation", "is_active")
    search_fields = ("faculty_id", "user__username", "user__first_name", "user__last_name", "user__email")
    autocomplete_fields = ("user", "department")

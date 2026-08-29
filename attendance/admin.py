from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'lecture', 'status', 'marked_by', 'marked_at')
    list_filter = ('status', 'lecture__subject_offering')
    autocomplete_fields = ['student']

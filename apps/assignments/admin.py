from django.contrib import admin

from .models import Assignment, AssignmentSubmission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "due_date", "maximum_marks", "created_by")
    list_filter = ("course", "due_date")
    search_fields = ("title", "course__course_code")
    autocomplete_fields = ("course", "created_by")


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "student", "status", "marks_obtained", "submitted_at")
    list_filter = ("status", "assignment__course")
    search_fields = ("student__username", "assignment__title")
    autocomplete_fields = ("assignment", "student", "graded_by")
    readonly_fields = ("submitted_at",)

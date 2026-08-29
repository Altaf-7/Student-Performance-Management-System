from django.contrib import admin
from .models import Assignment, AssignmentSubmission


class AssignmentSubmissionInline(admin.TabularInline):
    model = AssignmentSubmission
    extra = 0


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject_offering', 'max_marks', 'due_date', 'created_by')
    list_filter = ('subject_offering',)
    inlines = [AssignmentSubmissionInline]


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'marks', 'is_late', 'is_graded')
    list_filter = ('assignment__subject_offering',)
    autocomplete_fields = ['student']

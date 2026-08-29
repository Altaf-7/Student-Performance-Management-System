from django.contrib import admin
<<<<<<< HEAD
from .models import Exam, ExamResult


class ExamResultInline(admin.TabularInline):
    model = ExamResult
    extra = 0


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'subject_offering', 'term', 'category', 'exam_date', 'max_marks')
    list_filter = ('term', 'category', 'subject_offering')
    inlines = [ExamResultInline]


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'attempt_number', 'attempt_type', 'marks_obtained', 'grade', 'pass_status', 'is_latest')
    list_filter = ('attempt_type', 'is_latest', 'exam__subject_offering')
    autocomplete_fields = ['student']
=======

# Register your models here.
>>>>>>> origin/main

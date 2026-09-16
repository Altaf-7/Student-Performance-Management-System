from django.contrib import admin

from .models import Examination, ExamResult


@admin.register(Examination)
class ExaminationAdmin(admin.ModelAdmin):
    list_display = ("name", "exam_type", "course", "semester", "exam_date", "maximum_marks", "is_published")
    list_filter = ("exam_type", "is_published", "semester")
    search_fields = ("name", "course__course_code")
    autocomplete_fields = ("course", "semester", "created_by")


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ("student", "examination", "course", "obtained_marks", "maximum_marks", "grade")
    list_filter = ("grade", "course")
    search_fields = ("student__username", "examination__name")
    autocomplete_fields = ("student", "examination", "course", "entered_by")

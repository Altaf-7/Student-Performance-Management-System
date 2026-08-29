from django.contrib import admin
<<<<<<< HEAD
from .models import Department, Course, CourseBatch, Semester, Subject, SubjectOffering, Lecture


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'duration_years', 'total_semesters')
    list_filter = ('department',)
    search_fields = ('code', 'name')


@admin.register(CourseBatch)
class CourseBatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'start_year', 'end_year')
    list_filter = ('course',)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('course_batch', 'number', 'is_active', 'start_date', 'end_date')
    list_filter = ('course_batch__course', 'is_active')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credits')
    search_fields = ('code', 'name')


@admin.register(SubjectOffering)
class SubjectOfferingAdmin(admin.ModelAdmin):
    list_display = ('subject', 'semester', 'faculty', 'is_active')
    list_filter = ('semester__course_batch__course', 'is_active')
    autocomplete_fields = ['subject', 'faculty']


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('subject_offering', 'date', 'topic', 'created_by')
    list_filter = ('subject_offering',)
    date_hierarchy = 'date'
=======

# Register your models here.
>>>>>>> origin/main

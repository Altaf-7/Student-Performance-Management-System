from django.contrib import admin
<<<<<<< HEAD
from .models import StudentProfile, StudentCourse, StudentSemester, SemesterResult, StudentGraduation


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'user', 'phone')
    search_fields = ('roll_number', 'user__first_name', 'user__last_name', 'user__username')
    autocomplete_fields = ['user']


@admin.register(StudentCourse)
class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_batch', 'admission_year', 'completion_year', 'status')
    list_filter = ('status', 'course_batch__course')
    autocomplete_fields = ['student']


@admin.register(StudentSemester)
class StudentSemesterAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'student_course')
    list_filter = ('semester__course_batch__course',)
    autocomplete_fields = ['student']


@admin.register(SemesterResult)
class SemesterResultAdmin(admin.ModelAdmin):
    list_display = ('student_semester', 'total_marks', 'obtained_marks', 'sgpa', 'status', 'declared_date')
    list_filter = ('status',)


@admin.register(StudentGraduation)
class StudentGraduationAdmin(admin.ModelAdmin):
    list_display = ('student', 'student_course', 'graduation_date', 'final_cgpa')
=======

# Register your models here.
>>>>>>> origin/main

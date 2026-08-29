from django.contrib import admin
<<<<<<< HEAD
from .models import FacultyProfile


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department', 'designation')
    list_filter = ('department',)
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__username')
    autocomplete_fields = ['user']
=======

# Register your models here.
>>>>>>> origin/main

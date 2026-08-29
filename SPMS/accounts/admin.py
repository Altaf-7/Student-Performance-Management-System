from django.contrib import admin
<<<<<<< HEAD
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('SPMS role', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('SPMS role', {'fields': ('role', 'phone', 'email', 'first_name', 'last_name')}),
    )


admin.site.register(User, UserAdmin)
admin.site.site_header = "SPMS Administration"
admin.site.site_title = "SPMS Admin"
admin.site.index_title = "Student Performance Management System"
=======

# Register your models here.
>>>>>>> origin/main

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class SPMSUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_active", "is_staff", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    fieldsets = UserAdmin.fieldsets + (
        ("SPMS Role & Profile", {"fields": ("role", "phone", "profile_photo")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("SPMS Role & Profile", {"fields": ("role", "phone", "email")}),
    )

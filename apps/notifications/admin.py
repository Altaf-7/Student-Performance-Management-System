from django.contrib import admin

from .models import Notification, Announcement


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "kind", "title", "is_read", "created_at")
    list_filter = ("kind", "is_read")
    search_fields = ("recipient__username", "title")
    autocomplete_fields = ("recipient",)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "priority", "target_audience", "created_at")
    list_filter = ("priority", "target_audience")
    search_fields = ("title", "description")
    autocomplete_fields = ("author", "department", "semester")

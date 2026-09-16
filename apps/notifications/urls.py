from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notification_list"),
    path("<int:pk>/read/", views.MarkNotificationReadView.as_view(), name="mark_read"),
    path("<int:pk>/delete/", views.DeleteNotificationView.as_view(), name="delete"),
    path("mark-all-read/", views.MarkAllReadView.as_view(), name="mark_all_read"),

    path("announcements/", views.AnnouncementListView.as_view(), name="announcement_list"),
    path("announcements/add/", views.AnnouncementCreateView.as_view(), name="announcement_add"),
    path("announcements/<int:pk>/delete/", views.AnnouncementDeleteView.as_view(), name="announcement_delete"),
]

from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path("mark/", views.MarkAttendanceSelectView.as_view(), name="mark_select"),
    path("mark/<int:course_id>/<str:date_str>/", views.MarkAttendanceSheetView.as_view(), name="mark_sheet"),
    path("history/", views.AttendanceHistoryView.as_view(), name="history"),
    path("my/", views.MyAttendanceView.as_view(), name="my_attendance"),
]

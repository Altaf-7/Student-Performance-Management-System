from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.SPMSLoginView.as_view(), name="login"),
    path("logout/", views.SPMSLogoutView.as_view(), name="logout"),
    path("redirect/", views.role_redirect, name="role_redirect"),

    path("password-reset/", views.SPMSPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", views.SPMSPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", views.SPMSPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", views.SPMSPasswordResetCompleteView.as_view(), name="password_reset_complete"),

    path("password-change/", views.SPMSPasswordChangeView.as_view(), name="password_change"),
    path("password-change/done/", views.SPMSPasswordChangeDoneView.as_view(), name="password_change_done"),

    path("profile/", views.ProfileView.as_view(), name="profile"),

    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/faculty/", views.faculty_dashboard, name="faculty_dashboard"),
    path("dashboard/student/", views.student_dashboard, name="student_dashboard"),
]

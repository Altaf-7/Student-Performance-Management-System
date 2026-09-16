from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from apps.accounts.permissions import FacultyRequiredMixin
from .forms import AnnouncementForm
from .models import Notification, Announcement


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return redirect(request.META.get("HTTP_REFERER", "notifications:notification_list"))


class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
        return redirect(request.META.get("HTTP_REFERER", "notifications:notification_list"))


class DeleteNotificationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.delete()
        return redirect(request.META.get("HTTP_REFERER", "notifications:notification_list"))


class AnnouncementListView(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = "notifications/announcement_list.html"
    context_object_name = "announcements"
    paginate_by = 15

    def get_queryset(self):
        qs = Announcement.objects.select_related("author", "department", "semester")
        user = self.request.user
        if user.is_admin_role:
            return qs
        if user.is_faculty_role:
            return qs.filter(Q(target_audience=Announcement.Audience.FACULTY) | Q(target_audience=Announcement.Audience.ALL_STUDENTS))
        # student: all-students, or their department, or their semester
        profile = getattr(user, "student_profile", None)
        q = Q(target_audience=Announcement.Audience.ALL_STUDENTS)
        if profile:
            q |= Q(target_audience=Announcement.Audience.DEPARTMENT, department=profile.department)
            q |= Q(target_audience=Announcement.Audience.SEMESTER, semester=profile.semester)
        return qs.filter(q)


class AnnouncementCreateView(FacultyRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = "notifications/announcement_form.html"
    success_url = reverse_lazy("notifications:announcement_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Announcement published.")
        return super().form_valid(form)


class AnnouncementDeleteView(FacultyRequiredMixin, DeleteView):
    model = Announcement
    template_name = "academics/confirm_delete.html"
    success_url = reverse_lazy("notifications:announcement_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not (self.request.user.is_admin_role or obj.author_id == self.request.user.id):
            raise PermissionDenied
        return obj

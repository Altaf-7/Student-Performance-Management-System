from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View

from apps.accounts.permissions import AdminRequiredMixin
from apps.academics.models import Department, Semester
from .forms import StudentCreateForm, StudentEditForm
from .models import StudentProfile


class StudentListView(AdminRequiredMixin, ListView):
    model = StudentProfile
    template_name = "students/student_list.html"
    context_object_name = "students"
    paginate_by = 15

    def get_queryset(self):
        qs = StudentProfile.objects.select_related("user", "department", "semester")
        q = self.request.GET.get("q")
        dept = self.request.GET.get("department")
        sem = self.request.GET.get("semester")
        status = self.request.GET.get("status")
        if q:
            qs = qs.filter(
                Q(student_id__icontains=q) | Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) | Q(user__email__icontains=q)
            )
        if dept:
            qs = qs.filter(department_id=dept)
        if sem:
            qs = qs.filter(semester_id=sem)
        if status:
            qs = qs.filter(academic_status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["departments"] = Department.objects.all()
        ctx["semesters"] = Semester.objects.all()
        ctx["status_choices"] = StudentProfile.AcademicStatus.choices
        return ctx


class StudentCreateView(AdminRequiredMixin, CreateView):
    model = StudentProfile
    form_class = StudentCreateForm
    template_name = "students/student_form.html"
    success_url = reverse_lazy("students:student_list")

    def form_valid(self, form):
        messages.success(self.request, "Student created successfully.")
        return super().form_valid(form)


class StudentUpdateView(AdminRequiredMixin, UpdateView):
    model = StudentProfile
    form_class = StudentEditForm
    template_name = "students/student_form.html"
    success_url = reverse_lazy("students:student_list")

    def form_valid(self, form):
        messages.success(self.request, "Student updated successfully.")
        return super().form_valid(form)


class StudentDetailView(AdminRequiredMixin, DetailView):
    model = StudentProfile
    template_name = "students/student_detail.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.analytics.services import get_student_dashboard_context
        ctx["dashboard"] = get_student_dashboard_context(self.object.user)
        return ctx


class StudentDeactivateView(AdminRequiredMixin, View):
    def post(self, request, pk):
        profile = get_object_or_404(StudentProfile, pk=pk)
        profile.user.is_active = False
        profile.user.save()
        profile.academic_status = StudentProfile.AcademicStatus.DEACTIVATED
        profile.save()
        messages.success(request, f"{profile.user.get_full_name()} has been deactivated.")
        return redirect("students:student_list")


class StudentActivateView(AdminRequiredMixin, View):
    def post(self, request, pk):
        profile = get_object_or_404(StudentProfile, pk=pk)
        profile.user.is_active = True
        profile.user.save()
        profile.academic_status = StudentProfile.AcademicStatus.ACTIVE
        profile.save()
        messages.success(request, f"{profile.user.get_full_name()} has been reactivated.")
        return redirect("students:student_list")


class StudentDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        profile = get_object_or_404(StudentProfile, pk=pk)
        name = profile.user.get_full_name()
        profile.user.delete()  # cascades to profile
        messages.success(request, f"{name} has been permanently deleted.")
        return redirect("students:student_list")

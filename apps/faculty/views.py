from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View

from apps.accounts.permissions import AdminRequiredMixin
from apps.academics.models import Department
from .forms import FacultyCreateForm, FacultyEditForm
from .models import FacultyProfile


class FacultyListView(AdminRequiredMixin, ListView):
    model = FacultyProfile
    template_name = "faculty/faculty_list.html"
    context_object_name = "faculty_members"
    paginate_by = 15

    def get_queryset(self):
        qs = FacultyProfile.objects.select_related("user", "department")
        q = self.request.GET.get("q")
        dept = self.request.GET.get("department")
        if q:
            qs = qs.filter(
                Q(faculty_id__icontains=q) | Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) | Q(user__email__icontains=q)
            )
        if dept:
            qs = qs.filter(department_id=dept)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["departments"] = Department.objects.all()
        return ctx


class FacultyCreateView(AdminRequiredMixin, CreateView):
    model = FacultyProfile
    form_class = FacultyCreateForm
    template_name = "faculty/faculty_form.html"
    success_url = reverse_lazy("faculty:faculty_list")

    def form_valid(self, form):
        messages.success(self.request, "Faculty member created successfully.")
        return super().form_valid(form)


class FacultyUpdateView(AdminRequiredMixin, UpdateView):
    model = FacultyProfile
    form_class = FacultyEditForm
    template_name = "faculty/faculty_form.html"
    success_url = reverse_lazy("faculty:faculty_list")

    def form_valid(self, form):
        messages.success(self.request, "Faculty member updated successfully.")
        return super().form_valid(form)


class FacultyDetailView(AdminRequiredMixin, DetailView):
    model = FacultyProfile
    template_name = "faculty/faculty_detail.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["courses"] = self.object.user.courses_taught.select_related("department", "semester")
        return ctx


class FacultyDeactivateView(AdminRequiredMixin, View):
    def post(self, request, pk):
        profile = get_object_or_404(FacultyProfile, pk=pk)
        profile.user.is_active = False
        profile.user.save()
        profile.is_active = False
        profile.save()
        messages.success(request, f"{profile.user.get_full_name()} has been deactivated.")
        return redirect("faculty:faculty_list")


class FacultyActivateView(AdminRequiredMixin, View):
    def post(self, request, pk):
        profile = get_object_or_404(FacultyProfile, pk=pk)
        profile.user.is_active = True
        profile.user.save()
        profile.is_active = True
        profile.save()
        messages.success(request, f"{profile.user.get_full_name()} has been reactivated.")
        return redirect("faculty:faculty_list")


class FacultyDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        profile = get_object_or_404(FacultyProfile, pk=pk)
        name = profile.user.get_full_name()
        profile.user.delete()
        messages.success(request, f"{name} has been permanently deleted.")
        return redirect("faculty:faculty_list")

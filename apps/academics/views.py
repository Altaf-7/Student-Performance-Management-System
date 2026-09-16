from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from apps.accounts.permissions import AdminRequiredMixin
from .forms import DepartmentForm, SemesterForm, CourseForm, EnrollmentForm
from .models import Department, Semester, Course, Enrollment


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------
class DepartmentListView(AdminRequiredMixin, ListView):
    model = Department
    template_name = "academics/department_list.html"
    context_object_name = "departments"
    paginate_by = 15

    def get_queryset(self):
        qs = Department.objects.select_related("head_of_department")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q))
        return qs


class DepartmentCreateView(AdminRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = "academics/department_form.html"
    success_url = reverse_lazy("academics:department_list")

    def form_valid(self, form):
        messages.success(self.request, "Department created.")
        return super().form_valid(form)


class DepartmentUpdateView(AdminRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = "academics/department_form.html"
    success_url = reverse_lazy("academics:department_list")

    def form_valid(self, form):
        messages.success(self.request, "Department updated.")
        return super().form_valid(form)


class DepartmentDeleteView(AdminRequiredMixin, DeleteView):
    model = Department
    template_name = "academics/confirm_delete.html"
    success_url = reverse_lazy("academics:department_list")

    def form_valid(self, form):
        messages.success(self.request, "Department deleted.")
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Semesters
# ---------------------------------------------------------------------------
class SemesterListView(AdminRequiredMixin, ListView):
    model = Semester
    template_name = "academics/semester_list.html"
    context_object_name = "semesters"
    paginate_by = 15


class SemesterCreateView(AdminRequiredMixin, CreateView):
    model = Semester
    form_class = SemesterForm
    template_name = "academics/semester_form.html"
    success_url = reverse_lazy("academics:semester_list")

    def form_valid(self, form):
        messages.success(self.request, "Semester created.")
        return super().form_valid(form)


class SemesterUpdateView(AdminRequiredMixin, UpdateView):
    model = Semester
    form_class = SemesterForm
    template_name = "academics/semester_form.html"
    success_url = reverse_lazy("academics:semester_list")

    def form_valid(self, form):
        messages.success(self.request, "Semester updated.")
        return super().form_valid(form)


class SemesterDeleteView(AdminRequiredMixin, DeleteView):
    model = Semester
    template_name = "academics/confirm_delete.html"
    success_url = reverse_lazy("academics:semester_list")


# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = "academics/course_list.html"
    context_object_name = "courses"
    paginate_by = 15

    def get_queryset(self):
        qs = Course.objects.select_related("department", "semester", "faculty")
        user = self.request.user
        if user.is_faculty_role and not user.is_admin_role:
            qs = qs.filter(faculty=user)
        elif user.is_student_role:
            qs = qs.filter(enrollments__student=user).distinct()
        q = self.request.GET.get("q")
        dept = self.request.GET.get("department")
        sem = self.request.GET.get("semester")
        if q:
            qs = qs.filter(Q(course_name__icontains=q) | Q(course_code__icontains=q))
        if dept:
            qs = qs.filter(department_id=dept)
        if sem:
            qs = qs.filter(semester_id=sem)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["departments"] = Department.objects.all()
        ctx["semesters"] = Semester.objects.all()
        return ctx


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = "academics/course_detail.html"
    context_object_name = "course"


class CourseCreateView(AdminRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "academics/course_form.html"
    success_url = reverse_lazy("academics:course_list")

    def form_valid(self, form):
        messages.success(self.request, "Course created.")
        return super().form_valid(form)


class CourseUpdateView(AdminRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "academics/course_form.html"
    success_url = reverse_lazy("academics:course_list")

    def form_valid(self, form):
        messages.success(self.request, "Course updated.")
        return super().form_valid(form)


class CourseDeleteView(AdminRequiredMixin, DeleteView):
    model = Course
    template_name = "academics/confirm_delete.html"
    success_url = reverse_lazy("academics:course_list")


# ---------------------------------------------------------------------------
# Enrollments
# ---------------------------------------------------------------------------
class EnrollmentListView(AdminRequiredMixin, ListView):
    model = Enrollment
    template_name = "academics/enrollment_list.html"
    context_object_name = "enrollments"
    paginate_by = 20

    def get_queryset(self):
        qs = Enrollment.objects.select_related("student", "course", "semester")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(student__username__icontains=q) | Q(course__course_code__icontains=q))
        return qs


class EnrollmentCreateView(AdminRequiredMixin, CreateView):
    model = Enrollment
    form_class = EnrollmentForm
    template_name = "academics/enrollment_form.html"
    success_url = reverse_lazy("academics:enrollment_list")

    def form_valid(self, form):
        messages.success(self.request, "Student enrolled.")
        return super().form_valid(form)


class EnrollmentDeleteView(AdminRequiredMixin, DeleteView):
    model = Enrollment
    template_name = "academics/confirm_delete.html"
    success_url = reverse_lazy("academics:enrollment_list")

from datetime import date

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from apps.accounts.permissions import FacultyRequiredMixin, StudentRequiredMixin
from apps.academics.models import Course, Enrollment
from .forms import AttendanceDateCourseForm
from .models import Attendance
from .services import get_student_overall_attendance, get_student_course_attendance


def _faculty_owns_course(user, course):
    return user.is_admin_role or course.faculty_id == user.id


class MarkAttendanceSelectView(FacultyRequiredMixin, View):
    template_name = "attendance/mark_select.html"

    def get(self, request):
        form = AttendanceDateCourseForm(faculty_user=request.user, initial={"date": date.today()})
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = AttendanceDateCourseForm(request.POST, faculty_user=request.user)
        if form.is_valid():
            course = form.cleaned_data["course"]
            if not _faculty_owns_course(request.user, course):
                raise PermissionDenied("You cannot mark attendance for a course you do not teach.")
            d = form.cleaned_data["date"]
            return redirect(reverse("attendance:mark_sheet", args=[course.pk, d.isoformat()]))
        return render(request, self.template_name, {"form": form})


class MarkAttendanceSheetView(FacultyRequiredMixin, View):
    template_name = "attendance/mark_sheet.html"

    def get(self, request, course_id, date_str):
        course = get_object_or_404(Course, pk=course_id)
        if not _faculty_owns_course(request.user, course):
            raise PermissionDenied("You cannot mark attendance for a course you do not teach.")
        enrollments = Enrollment.objects.filter(course=course, status=Enrollment.Status.ACTIVE).select_related("student")
        existing = {a.student_id: a.status for a in Attendance.objects.filter(course=course, date=date_str)}
        rows = [{"student": e.student, "status": existing.get(e.student_id, Attendance.Status.PRESENT)} for e in enrollments]
        return render(request, self.template_name, {"course": course, "date": date_str, "rows": rows})

    def post(self, request, course_id, date_str):
        course = get_object_or_404(Course, pk=course_id)
        if not _faculty_owns_course(request.user, course):
            raise PermissionDenied("You cannot mark attendance for a course you do not teach.")
        enrollments = Enrollment.objects.filter(course=course, status=Enrollment.Status.ACTIVE)
        for enrollment in enrollments:
            status = request.POST.get(f"status_{enrollment.student_id}", Attendance.Status.ABSENT)
            if status not in Attendance.Status.values:
                continue
            Attendance.objects.update_or_create(
                student=enrollment.student, course=course, date=date_str,
                defaults={"status": status, "marked_by": request.user},
            )
        messages.success(request, f"Attendance saved for {course.course_code} on {date_str}.")
        return redirect(reverse("attendance:mark_select"))


class AttendanceHistoryView(FacultyRequiredMixin, ListView):
    model = Attendance
    template_name = "attendance/history.html"
    context_object_name = "records"
    paginate_by = 20

    def get_queryset(self):
        qs = Attendance.objects.select_related("student", "course")
        user = self.request.user
        if not user.is_admin_role:
            qs = qs.filter(course__faculty=user)
        course_id = self.request.GET.get("course")
        student_q = self.request.GET.get("q")
        status = self.request.GET.get("status")
        date_filter = self.request.GET.get("date")
        if course_id:
            qs = qs.filter(course_id=course_id)
        if student_q:
            qs = qs.filter(student__first_name__icontains=student_q) | qs.filter(student__last_name__icontains=student_q)
        if status:
            qs = qs.filter(status=status)
        if date_filter:
            qs = qs.filter(date=date_filter)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        courses = Course.objects.all() if user.is_admin_role else Course.objects.filter(faculty=user)
        ctx["courses"] = courses
        ctx["status_choices"] = Attendance.Status.choices
        return ctx


class MyAttendanceView(StudentRequiredMixin, View):
    template_name = "attendance/my_attendance.html"

    def get(self, request):
        data = get_student_overall_attendance(request.user)
        return render(request, self.template_name, {"data": data})

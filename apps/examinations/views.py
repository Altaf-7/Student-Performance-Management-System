from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from apps.accounts.permissions import AdminRequiredMixin, FacultyRequiredMixin, StudentRequiredMixin
from apps.academics.models import Enrollment, Semester
from apps.academics.services import calculate_cgpa, calculate_semester_gpa
from .forms import ExaminationForm
from .models import Examination, ExamResult


def _faculty_owns_exam(user, exam):
    return user.is_admin_role or exam.course.faculty_id == user.id


class ExaminationListView(FacultyRequiredMixin, ListView):
    model = Examination
    template_name = "examinations/examination_list.html"
    context_object_name = "examinations"
    paginate_by = 15

    def get_queryset(self):
        qs = Examination.objects.select_related("course", "semester")
        if not self.request.user.is_admin_role:
            qs = qs.filter(course__faculty=self.request.user)
        return qs


class ExaminationCreateView(FacultyRequiredMixin, CreateView):
    model = Examination
    form_class = ExaminationForm
    template_name = "examinations/examination_form.html"
    success_url = reverse_lazy("examinations:examination_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["faculty_user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Examination created.")
        return super().form_valid(form)


class ExaminationUpdateView(FacultyRequiredMixin, UpdateView):
    model = Examination
    form_class = ExaminationForm
    template_name = "examinations/examination_form.html"
    success_url = reverse_lazy("examinations:examination_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["faculty_user"] = self.request.user
        return kwargs

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not _faculty_owns_exam(self.request.user, obj):
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance.is_published:
            from apps.academics.models import Enrollment
            from apps.notifications.services import notify_many
            students = [e.student for e in Enrollment.objects.filter(course=form.instance.course).select_related("student")]
            notify_many(students, "RESULT_PUBLISHED", f"Results published: {form.instance.name}", "Check your results page for details.")
        return response


class ExaminationDeleteView(FacultyRequiredMixin, DeleteView):
    model = Examination
    template_name = "academics/confirm_delete.html"
    success_url = reverse_lazy("examinations:examination_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not _faculty_owns_exam(self.request.user, obj):
            raise PermissionDenied
        return obj


class EnterResultsView(FacultyRequiredMixin, View):
    template_name = "examinations/enter_results.html"

    def get(self, request, pk):
        exam = get_object_or_404(Examination, pk=pk)
        if not _faculty_owns_exam(request.user, exam):
            raise PermissionDenied
        enrollments = Enrollment.objects.filter(course=exam.course, status=Enrollment.Status.ACTIVE).select_related("student")
        existing = {r.student_id: r for r in ExamResult.objects.filter(examination=exam)}
        rows = [{"student": e.student, "result": existing.get(e.student_id)} for e in enrollments]
        return render(request, self.template_name, {"exam": exam, "rows": rows})

    def post(self, request, pk):
        exam = get_object_or_404(Examination, pk=pk)
        if not _faculty_owns_exam(request.user, exam):
            raise PermissionDenied
        enrollments = Enrollment.objects.filter(course=exam.course, status=Enrollment.Status.ACTIVE)
        errors = []
        for enrollment in enrollments:
            raw = request.POST.get(f"marks_{enrollment.student_id}", "").strip()
            if raw == "":
                continue
            try:
                obtained = Decimal(raw)
            except InvalidOperation:
                errors.append(f"Invalid marks for {enrollment.student}.")
                continue
            if obtained > exam.maximum_marks or obtained < 0:
                errors.append(f"Marks for {enrollment.student} must be between 0 and {exam.maximum_marks}.")
                continue
            remarks = request.POST.get(f"remarks_{enrollment.student_id}", "")
            ExamResult.objects.update_or_create(
                student=enrollment.student, examination=exam,
                defaults={
                    "course": exam.course, "maximum_marks": exam.maximum_marks,
                    "obtained_marks": obtained, "remarks": remarks, "entered_by": request.user,
                },
            )
        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            messages.success(request, "Results saved.")
        return redirect("examinations:enter_results", pk=exam.pk)


class MyResultsView(StudentRequiredMixin, View):
    template_name = "examinations/my_results.html"

    def get(self, request):
        results = ExamResult.objects.filter(student=request.user, examination__is_published=True).select_related(
            "examination", "course"
        ).order_by("-created_at")
        cgpa_data = calculate_cgpa(request.user)
        return render(request, self.template_name, {"results": results, "cgpa_data": cgpa_data})


class MarksheetView(View):
    template_name = "examinations/marksheet.html"

    def get(self, request, student_id, semester_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        student = get_object_or_404(User, pk=student_id, role="STUDENT")
        semester = get_object_or_404(Semester, pk=semester_id)

        if request.user.is_student_role and request.user.id != student.id:
            raise PermissionDenied("You can only view your own marksheet.")
        if request.user.is_faculty_role and not request.user.is_admin_role:
            teaches_student = Enrollment.objects.filter(student=student, course__faculty=request.user).exists()
            if not teaches_student:
                raise PermissionDenied("You may only view marksheets for your own students.")

        gpa_data = calculate_semester_gpa(student, semester)
        context = {"student": student, "semester": semester, "gpa_data": gpa_data}

        if request.GET.get("format") == "pdf":
            return self._render_pdf(context)
        return render(request, self.template_name, context)

    def _render_pdf(self, context):
        from .pdf import build_marksheet_pdf
        pdf_bytes = build_marksheet_pdf(context["student"], context["semester"], context["gpa_data"])
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        filename = f"marksheet_{context['student'].username}_{context['semester'].academic_year}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

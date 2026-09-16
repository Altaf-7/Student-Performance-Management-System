from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from apps.accounts.permissions import FacultyRequiredMixin, StudentRequiredMixin
from apps.academics.models import Enrollment
from .forms import AssignmentForm, SubmissionForm, GradeSubmissionForm
from .models import Assignment, AssignmentSubmission
from .services import determine_submission_status, grade_submission


def _faculty_owns_assignment(user, assignment):
    return user.is_admin_role or assignment.course.faculty_id == user.id


class AssignmentListView(FacultyRequiredMixin, ListView):
    model = Assignment
    template_name = "assignments/assignment_list.html"
    context_object_name = "assignments"
    paginate_by = 15

    def get_queryset(self):
        qs = Assignment.objects.select_related("course")
        user = self.request.user
        if not user.is_admin_role:
            qs = qs.filter(course__faculty=user)
        return qs


class AssignmentCreateView(FacultyRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = "assignments/assignment_form.html"
    success_url = reverse_lazy("assignments:assignment_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["faculty_user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        from apps.academics.models import Enrollment
        from apps.notifications.services import notify_many
        students = [e.student for e in Enrollment.objects.filter(course=self.object.course).select_related("student")]
        notify_many(students, "NEW_ASSIGNMENT", f"New assignment: {self.object.title}", f"Due {self.object.due_date:%Y-%m-%d %H:%M}")
        messages.success(self.request, "Assignment created and students notified.")
        return response


class AssignmentUpdateView(FacultyRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = "assignments/assignment_form.html"
    success_url = reverse_lazy("assignments:assignment_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["faculty_user"] = self.request.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not _faculty_owns_assignment(self.request.user, obj):
            raise PermissionDenied
        return obj


class AssignmentDeleteView(FacultyRequiredMixin, DeleteView):
    model = Assignment
    template_name = "academics/confirm_delete.html"
    success_url = reverse_lazy("assignments:assignment_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not _faculty_owns_assignment(self.request.user, obj):
            raise PermissionDenied
        return obj


class AssignmentDetailView(FacultyRequiredMixin, DetailView):
    model = Assignment
    template_name = "assignments/assignment_detail.html"
    context_object_name = "assignment"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not _faculty_owns_assignment(self.request.user, obj):
            raise PermissionDenied
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["submissions"] = self.object.submissions.select_related("student")
        return ctx


class GradeSubmissionView(FacultyRequiredMixin, View):
    template_name = "assignments/grade_submission.html"

    def get(self, request, pk):
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        if not _faculty_owns_assignment(request.user, submission.assignment):
            raise PermissionDenied
        form = GradeSubmissionForm(initial={"marks_obtained": submission.marks_obtained, "feedback": submission.feedback})
        return render(request, self.template_name, {"form": form, "submission": submission})

    def post(self, request, pk):
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        if not _faculty_owns_assignment(request.user, submission.assignment):
            raise PermissionDenied
        form = GradeSubmissionForm(request.POST)
        if form.is_valid():
            try:
                grade_submission(submission, form.cleaned_data["marks_obtained"], form.cleaned_data["feedback"], request.user)
            except ValueError as e:
                form.add_error("marks_obtained", str(e))
                return render(request, self.template_name, {"form": form, "submission": submission})
            from apps.notifications.services import notify
            notify(submission.student, "RESULT_PUBLISHED", f"Assignment graded: {submission.assignment.title}", f"You scored {submission.marks_obtained}/{submission.assignment.maximum_marks}")
            messages.success(request, "Submission graded.")
            return redirect("assignments:assignment_detail", pk=submission.assignment_id)
        return render(request, self.template_name, {"form": form, "submission": submission})


# ---------------------------------------------------------------------------
# Student-facing views
# ---------------------------------------------------------------------------
class MyAssignmentsView(StudentRequiredMixin, ListView):
    template_name = "assignments/my_assignments.html"
    context_object_name = "assignments"
    paginate_by = 15

    def get_queryset(self):
        course_ids = Enrollment.objects.filter(student=self.request.user).values_list("course_id", flat=True)
        qs = Assignment.objects.filter(course_id__in=course_ids).select_related("course")
        for a in qs:
            a.my_submission = AssignmentSubmission.objects.filter(assignment=a, student=self.request.user).first()
        return qs


class SubmitAssignmentView(StudentRequiredMixin, View):
    template_name = "assignments/submit_assignment.html"

    def _get_assignment(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        enrolled = Enrollment.objects.filter(student=request.user, course=assignment.course).exists()
        if not enrolled:
            raise PermissionDenied("You are not enrolled in this course.")
        return assignment

    def get(self, request, pk):
        assignment = self._get_assignment(request, pk)
        existing = AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).first()
        form = SubmissionForm(instance=existing)
        return render(request, self.template_name, {"form": form, "assignment": assignment, "existing": existing})

    def post(self, request, pk):
        assignment = self._get_assignment(request, pk)
        existing = AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).first()
        form = SubmissionForm(request.POST, request.FILES, instance=existing)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            if not submission.pk:
                submission.status = determine_submission_status(assignment)
            submission.full_clean()
            submission.save()
            messages.success(request, "Assignment submitted successfully.")
            return redirect("assignments:my_assignments")
        return render(request, self.template_name, {"form": form, "assignment": assignment, "existing": existing})

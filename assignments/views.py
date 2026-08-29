from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from academics.models import SubjectOffering
from .models import Assignment, AssignmentSubmission


@login_required
def assignment_create(request, pk):
    offering = get_object_or_404(SubjectOffering, pk=pk)
    profile = getattr(request.user, 'faculty_profile', None)
    if profile is None or offering.faculty_id != profile.id:
        messages.error(request, "Only the assigned faculty can create assignments.")
        return redirect('academics:offering_detail', pk=pk)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        max_marks = request.POST.get('max_marks')
        due_date = request.POST.get('due_date')
        if title and max_marks and due_date:
            Assignment.objects.create(
                subject_offering=offering,
                title=title,
                description=request.POST.get('description', ''),
                instructions=request.POST.get('instructions', ''),
                max_marks=int(max_marks),
                due_date=due_date,
                attachment=request.FILES.get('attachment'),
                created_by=request.user,
            )
            messages.success(request, "Assignment created.")
            return redirect('academics:offering_detail', pk=pk)
        messages.error(request, "Title, maximum marks, and due date are required.")

    return render(request, 'assignments/assignment_form.html', {'offering': offering})


@login_required
def assignment_submit(request, pk):
    assignment = get_object_or_404(Assignment.objects.select_related('subject_offering'), pk=pk)
    profile = getattr(request.user, 'student_profile', None)
    if profile is None:
        messages.error(request, "Only students can submit assignments.")
        return redirect('dashboard:redirect')

    submission = assignment.submissions.filter(student=profile).first()

    if request.method == 'POST':
        file = request.FILES.get('file')
        remarks = request.POST.get('remarks', '')
        if submission and submission.is_graded:
            messages.error(request, "This assignment has already been graded and cannot be resubmitted.")
        elif file or remarks:
            AssignmentSubmission.objects.update_or_create(
                assignment=assignment, student=profile,
                defaults={'file': file, 'remarks': remarks} if file else {'remarks': remarks},
            )
            messages.success(request, "Assignment submitted.")
            return redirect('dashboard:student')
        else:
            messages.error(request, "Attach a file or add remarks before submitting.")

    return render(
        request, 'assignments/assignment_submit.html',
        {'assignment': assignment, 'submission': submission, 'now': timezone.now()},
    )


@login_required
def assignment_submissions(request, pk):
    assignment = get_object_or_404(Assignment.objects.select_related('subject_offering'), pk=pk)
    profile = getattr(request.user, 'faculty_profile', None)
    if profile is None or assignment.subject_offering.faculty_id != profile.id:
        messages.error(request, "Only the assigned faculty can view submissions.")
        return redirect('dashboard:redirect')

    submissions = assignment.submissions.select_related('student__user').order_by('student__roll_number')
    return render(request, 'assignments/assignment_submissions.html', {'assignment': assignment, 'submissions': submissions})


@login_required
def submission_grade(request, pk):
    submission = get_object_or_404(
        AssignmentSubmission.objects.select_related('assignment__subject_offering', 'student__user'), pk=pk
    )
    profile = getattr(request.user, 'faculty_profile', None)
    if profile is None or submission.assignment.subject_offering.faculty_id != profile.id:
        messages.error(request, "Only the assigned faculty can grade this submission.")
        return redirect('dashboard:redirect')

    if request.method == 'POST':
        try:
            marks = Decimal(request.POST.get('marks', ''))
        except (InvalidOperation, TypeError):
            messages.error(request, "Enter a valid numeric mark.")
            return redirect('assignments:grade', pk=pk)

        if marks > submission.assignment.max_marks or marks < 0:
            messages.error(request, f"Marks must be between 0 and {submission.assignment.max_marks}.")
            return redirect('assignments:grade', pk=pk)

        submission.marks = marks
        submission.feedback = request.POST.get('feedback', '')
        submission.graded_by = request.user
        submission.graded_at = timezone.now()
        submission.save()
        messages.success(request, "Submission graded.")
        return redirect('assignments:submissions', pk=submission.assignment_id)

    return render(request, 'assignments/submission_grade.html', {'submission': submission})

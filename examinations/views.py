from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from academics.models import SubjectOffering
from students.models import StudentSemester
from .models import Exam, ExamResult


@login_required
def exam_create(request, pk):
    offering = get_object_or_404(SubjectOffering, pk=pk)
    profile = getattr(request.user, 'faculty_profile', None)
    if profile is None or offering.faculty_id != profile.id:
        messages.error(request, "Only the assigned faculty can schedule exams.")
        return redirect('academics:offering_detail', pk=pk)

    if request.method == 'POST':
        term = request.POST.get('term')
        category = request.POST.get('category')
        exam_date = request.POST.get('exam_date')
        max_marks = request.POST.get('max_marks')
        if term and category and exam_date and max_marks:
            Exam.objects.create(
                subject_offering=offering,
                term=term,
                category=category,
                name=request.POST.get('name', ''),
                exam_date=exam_date,
                max_marks=int(max_marks),
                created_by=request.user,
            )
            messages.success(request, "Exam scheduled.")
            return redirect('academics:offering_detail', pk=pk)
        messages.error(request, "All fields except label are required.")

    return render(request, 'examinations/exam_form.html', {
        'offering': offering, 'terms': Exam.Term.choices, 'categories': Exam.Category.choices,
    })


@login_required
def exam_results(request, pk):
    exam = get_object_or_404(Exam.objects.select_related('subject_offering'), pk=pk)
    profile = getattr(request.user, 'faculty_profile', None)
    if profile is None or exam.subject_offering.faculty_id != profile.id:
        messages.error(request, "Only the assigned faculty can enter results for this exam.")
        return redirect('dashboard:redirect')

    enrollments = (
        StudentSemester.objects.filter(semester=exam.subject_offering.semester)
        .select_related('student__user')
        .order_by('student__roll_number')
    )
    existing = {r.student_id: r for r in exam.results.filter(is_latest=True)}

    if request.method == 'POST':
        for enrollment in enrollments:
            sid = enrollment.student_id
            attendance_status = request.POST.get(f'attendance_{sid}', ExamResult.AttendanceStatus.PRESENT)
            marks_raw = request.POST.get(f'marks_{sid}', '').strip()
            marks = None
            if attendance_status == ExamResult.AttendanceStatus.PRESENT and marks_raw:
                try:
                    marks = Decimal(marks_raw)
                except InvalidOperation:
                    messages.error(request, f"Invalid marks for {enrollment.student}.")
                    continue
                if marks > exam.max_marks or marks < 0:
                    messages.error(request, f"Marks out of range for {enrollment.student}.")
                    continue

            prior = existing.get(sid)
            next_attempt = (prior.attempt_number + 1) if (prior and request.POST.get(f'retest_{sid}')) else (prior.attempt_number if prior else 1)
            attempt_type = ExamResult.AttemptType.RETEST if (prior and request.POST.get(f'retest_{sid}')) else (prior.attempt_type if prior else ExamResult.AttemptType.REGULAR)

            ExamResult.objects.update_or_create(
                exam=exam, student_id=sid, attempt_number=next_attempt,
                defaults={
                    'attendance_status': attendance_status,
                    'marks_obtained': marks,
                    'attempt_type': attempt_type,
                    'is_latest': True,
                    'entered_by': request.user,
                },
            )
        messages.success(request, "Results saved.")
        return redirect('academics:offering_detail', pk=exam.subject_offering_id)

    rows = [{'enrollment': e, 'result': existing.get(e.student_id)} for e in enrollments]
    return render(request, 'examinations/exam_results.html', {'exam': exam, 'rows': rows})

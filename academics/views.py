from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import SubjectOffering, Lecture


def _is_offering_faculty(request, offering):
    profile = getattr(request.user, 'faculty_profile', None)
    return profile is not None and offering.faculty_id == profile.id


@login_required
def subject_offering_detail(request, pk):
    offering = get_object_or_404(
        SubjectOffering.objects.select_related('subject', 'semester__course_batch__course', 'faculty__user'),
        pk=pk,
    )
    is_owner = _is_offering_faculty(request, offering)
    if not (is_owner or request.user.is_admin_role or request.user.is_student):
        messages.error(request, "You do not have access to this subject offering.")
        return redirect('dashboard:redirect')

    lectures = offering.lectures.all().order_by('-date')
    assignments = offering.assignments.all().order_by('-due_date')
    exams = offering.exams.all().order_by('-exam_date')

    context = {
        'offering': offering,
        'is_owner': is_owner,
        'lectures': lectures,
        'assignments': assignments,
        'exams': exams,
    }
    return render(request, 'academics/offering_detail.html', context)


@login_required
def lecture_create(request, pk):
    offering = get_object_or_404(SubjectOffering, pk=pk)
    if not _is_offering_faculty(request, offering):
        messages.error(request, "Only the assigned faculty can add lectures.")
        return redirect('academics:offering_detail', pk=pk)

    if request.method == 'POST':
        date = request.POST.get('date')
        topic = request.POST.get('topic', '')
        if date:
            lecture = Lecture.objects.create(
                subject_offering=offering, date=date, topic=topic, created_by=request.user
            )
            messages.success(request, "Lecture added. You can now mark attendance for it.")
            return redirect('attendance:mark', pk=lecture.pk)
        messages.error(request, "Date is required.")

    return render(request, 'academics/lecture_form.html', {'offering': offering})

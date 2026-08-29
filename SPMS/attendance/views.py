from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from academics.models import Lecture
from students.models import StudentSemester
from .models import Attendance


@login_required
def mark_attendance(request, pk):
    lecture = get_object_or_404(Lecture.objects.select_related('subject_offering'), pk=pk)
    profile = getattr(request.user, 'faculty_profile', None)
    if profile is None or lecture.subject_offering.faculty_id != profile.id:
        messages.error(request, "Only the assigned faculty can mark attendance for this lecture.")
        return redirect('dashboard:redirect')

    enrollments = (
        StudentSemester.objects.filter(semester=lecture.subject_offering.semester)
        .select_related('student__user')
        .order_by('student__roll_number')
    )
    existing = {a.student_id: a for a in lecture.attendance_records.all()}

    if request.method == 'POST':
        for enrollment in enrollments:
            status = request.POST.get(f'status_{enrollment.student_id}', Attendance.Status.ABSENT)
            Attendance.objects.update_or_create(
                lecture=lecture,
                student=enrollment.student,
                defaults={'status': status, 'marked_by': request.user},
            )
        messages.success(request, "Attendance saved.")
        return redirect('academics:offering_detail', pk=lecture.subject_offering_id)

    rows = [
        {'enrollment': e, 'current_status': existing.get(e.student_id).status if e.student_id in existing else Attendance.Status.PRESENT}
        for e in enrollments
    ]
    return render(request, 'attendance/mark_attendance.html', {'lecture': lecture, 'rows': rows})

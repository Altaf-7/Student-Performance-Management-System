from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Count, Q

from students.models import StudentCourse, StudentSemester, SemesterResult
from attendance.models import Attendance
from assignments.models import AssignmentSubmission
from examinations.models import ExamResult


@login_required
def redirect_to_dashboard(request):
    user = request.user
    if user.is_admin_role:
        return redirect('dashboard:admin_home')
    if user.is_faculty:
        return redirect('dashboard:faculty')
    return redirect('dashboard:student')


@login_required
def student_dashboard(request):
    profile = getattr(request.user, 'student_profile', None)
    if profile is None:
        return render(request, 'dashboard/no_profile.html', {'role': 'student'})

    current_course = (
        StudentCourse.objects.filter(student=profile, status=StudentCourse.Status.PURSUING)
        .select_related('course_batch__course')
        .first()
    )
    current_semester_enrollment = (
        StudentSemester.objects.filter(student=profile, semester__is_active=True)
        .select_related('semester', 'student_course')
        .order_by('-semester__number')
        .first()
    )

    subject_offerings = []
    attendance_summary = []
    assignment_rows = []
    if current_semester_enrollment:
        subject_offerings = list(
            current_semester_enrollment.semester.subject_offerings.select_related('subject', 'faculty__user')
        )
        for so in subject_offerings:
            total = Attendance.objects.filter(lecture__subject_offering=so, student=profile).count()
            present = Attendance.objects.filter(
                lecture__subject_offering=so, student=profile, status=Attendance.Status.PRESENT
            ).count()
            pct = round((present / total) * 100, 1) if total else None
            attendance_summary.append({'subject_offering': so, 'total': total, 'present': present, 'pct': pct})

            for a in so.assignments.all().order_by('-due_date'):
                submission = a.submissions.filter(student=profile).first()
                assignment_rows.append({'assignment': a, 'submission': submission})

    exam_results = (
        ExamResult.objects.filter(student=profile, is_latest=True)
        .select_related('exam__subject_offering__subject')
        .order_by('-exam__exam_date')[:15]
    )

    semester_results = (
        SemesterResult.objects.filter(student_semester__student=profile)
        .select_related('student_semester__semester')
        .order_by('-student_semester__semester__number')
    )

    context = {
        'profile': profile,
        'current_course': current_course,
        'current_semester_enrollment': current_semester_enrollment,
        'attendance_summary': attendance_summary,
        'assignment_rows': assignment_rows,
        'exam_results': exam_results,
        'semester_results': semester_results,
    }
    return render(request, 'dashboard/student_dashboard.html', context)


@login_required
def faculty_dashboard(request):
    profile = getattr(request.user, 'faculty_profile', None)
    if profile is None:
        return render(request, 'dashboard/no_profile.html', {'role': 'faculty'})

    subject_offerings = (
        profile.subject_offerings.filter(is_active=True)
        .select_related('subject', 'semester__course_batch__course')
        .annotate(
            student_count=Count('semester__enrolled_students', distinct=True),
        )
    )

    pending_grading = AssignmentSubmission.objects.filter(
        assignment__subject_offering__faculty=profile, marks__isnull=True
    ).select_related('assignment', 'student__user').order_by('-submitted_at')[:20]

    upcoming_exams = (
        profile.subject_offerings.filter(is_active=True)
        .values_list('exams', flat=True)
    )

    from examinations.models import Exam
    exams_needing_entry = (
        Exam.objects.filter(subject_offering__faculty=profile)
        .select_related('subject_offering__subject')
        .order_by('-exam_date')[:10]
    )

    context = {
        'profile': profile,
        'subject_offerings': subject_offerings,
        'pending_grading': pending_grading,
        'exams_needing_entry': exams_needing_entry,
    }
    return render(request, 'dashboard/faculty_dashboard.html', context)


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_role:
        return redirect('dashboard:redirect')

    from academics.models import Department, Course, SubjectOffering
    from students.models import StudentProfile
    from faculty.models import FacultyProfile

    stats = {
        'departments': Department.objects.count(),
        'courses': Course.objects.count(),
        'subject_offerings': SubjectOffering.objects.filter(is_active=True).count(),
        'students': StudentProfile.objects.count(),
        'faculty': FacultyProfile.objects.count(),
    }
    return render(request, 'dashboard/admin_dashboard.html', {'stats': stats})

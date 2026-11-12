from django.db.models import Count, Avg, F, Q, Sum
from academics.models import SubjectOffering
from attendance.models import Attendance
from assignments.models import Assignment, AssignmentSubmission
from examinations.models import Exam, ExamResult
from students.models import StudentSemester

def get_student_academic_overview(student):
    # Get active semester
    active_sem = StudentSemester.objects.filter(student=student, status='active').select_related('semester', 'semester__course_batch', 'semester__course_batch__course').first()
    
    overview = {
        'current_course': active_sem.semester.course_batch.course.name if active_sem else None,
        'current_batch': active_sem.semester.course_batch.academic_year if active_sem else None,
        'current_semester': active_sem.semester.semester_number if active_sem else None,
        'academic_status': active_sem.get_status_display() if active_sem else 'Inactive',
        'overall_attendance': 0,
        'assignment_submission_rate': 0,
        'exam_performance': 0,
        'latest_sgpa': None
    }
    
    if not active_sem:
        return overview

    # Attendance
    offerings = SubjectOffering.objects.filter(semester=active_sem.semester)
    attendance_stats = Attendance.objects.filter(
        student=student, 
        lecture__offering__in=offerings
    ).aggregate(
        total_lectures=Count('id'),
        present_count=Count('id', filter=Q(status='present'))
    )
    if attendance_stats['total_lectures'] > 0:
        overview['overall_attendance'] = round((attendance_stats['present_count'] / attendance_stats['total_lectures']) * 100, 1)

    # Assignments
    assignments = Assignment.objects.filter(offering__in=offerings)
    total_assignments = assignments.count()
    if total_assignments > 0:
        submissions = AssignmentSubmission.objects.filter(
            assignment__in=assignments,
            student=student
        ).count()
        overview['assignment_submission_rate'] = round((submissions / total_assignments) * 100, 1)

    # Exams
    published_results = ExamResult.objects.filter(
        student=student,
        exam__offering__in=offerings,
        exam__status='published',
        is_latest=True
    ).exclude(attendance_status='absent')
    
    if published_results.exists():
        total_obtained = sum(res.marks_obtained for res in published_results if res.marks_obtained is not None)
        total_max = sum(res.exam.total_marks for res in published_results if res.marks_obtained is not None)
        if total_max > 0:
            overview['exam_performance'] = round((total_obtained / total_max) * 100, 1)

    # Latest SGPA
    latest_report = student.semester_reports.order_by('-semester__semester_number').first()
    if latest_report:
        overview['latest_sgpa'] = latest_report.sgpa

    return overview

def get_student_attendance_report(student):
    active_sem = StudentSemester.objects.filter(student=student, status='active').first()
    if not active_sem:
        return []
    
    offerings = SubjectOffering.objects.filter(semester=active_sem.semester).select_related('subject')
    
    report = []
    for offering in offerings:
        stats = Attendance.objects.filter(
            student=student, 
            lecture__offering=offering
        ).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent'))
        )
        
        total = stats['total']
        present = stats['present']
        attendance_percentage = round((present / total) * 100, 1) if total > 0 else 0
        
        report.append({
            'subject': offering.subject,
            'total_lectures': total,
            'present': present,
            'absent': stats['absent'],
            'attendance_percentage': attendance_percentage
        })
        
    return report

def get_student_assignment_report(student):
    active_sem = StudentSemester.objects.filter(student=student, status='active').first()
    if not active_sem:
        return []

    offerings = SubjectOffering.objects.filter(semester=active_sem.semester).select_related('subject')
    assignments = Assignment.objects.filter(offering__in=offerings).select_related('offering__subject')
    submissions = AssignmentSubmission.objects.filter(student=student, assignment__in=assignments).select_related('assignment')
    
    sub_dict = {sub.assignment_id: sub for sub in submissions}
    
    report = []
    for assignment in assignments:
        sub = sub_dict.get(assignment.id)
        if sub:
            status = 'Late' if sub.is_late else 'Submitted'
            marks = sub.marks_obtained
            graded = sub.is_graded
        else:
            status = 'Not Submitted'
            marks = None
            graded = False
            
        report.append({
            'assignment': assignment,
            'subject': assignment.offering.subject,
            'status': status,
            'marks': marks,
            'max_marks': assignment.max_marks,
            'graded': graded
        })
        
    return report

def get_student_exam_report(student):
    results = ExamResult.objects.filter(
        student=student,
        exam__status='published',
        is_latest=True
    ).select_related('exam', 'exam__offering__subject').order_by('-exam__exam_date')
    return results

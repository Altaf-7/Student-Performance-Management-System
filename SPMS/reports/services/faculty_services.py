from django.db.models import Count, Avg, F, Q, Sum
from academics.models import SubjectOffering
from attendance.models import Attendance
from assignments.models import Assignment, AssignmentSubmission
from examinations.models import Exam, ExamResult

def get_faculty_overview(faculty):
    offerings = SubjectOffering.objects.filter(faculty=faculty).select_related('subject', 'semester', 'semester__course_batch', 'semester__course_batch__course')
    
    # We will build summary stats across all offerings
    total_students = 0
    total_lectures = 0
    total_assignments = Assignment.objects.filter(offering__in=offerings).count()
    total_exams = Exam.objects.filter(offering__in=offerings).count()
    
    for offering in offerings:
        total_students += offering.semester.students.filter(status='active').count()
        total_lectures += offering.lectures.count()
        
    return {
        'total_offerings': offerings.count(),
        'total_students': total_students,
        'total_lectures': total_lectures,
        'total_assignments': total_assignments,
        'total_exams': total_exams,
    }

def get_faculty_attendance_report(faculty):
    offerings = SubjectOffering.objects.filter(faculty=faculty).select_related('subject', 'semester', 'semester__course_batch')
    
    report = []
    for offering in offerings:
        lectures = offering.lectures.all()
        total_lectures = lectures.count()
        students = offering.semester.students.filter(status='active').select_related('student', 'student__user')
        total_students = students.count()
        
        if total_lectures == 0 or total_students == 0:
            report.append({
                'offering': offering,
                'total_students': total_students,
                'total_lectures': total_lectures,
                'average_attendance': 0,
                'below_threshold': 0,
                'above_threshold': 0
            })
            continue
            
        total_present_all = 0
        below_threshold = 0
        above_threshold = 0
        
        # Calculate per-student attendance
        # This could be heavily optimized with group_by, but doing Python-side iteration for accuracy
        # or we can use Subquery/OuterRef. Let's use aggregation.
        student_att = Attendance.objects.filter(
            lecture__offering=offering
        ).values('student').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present'))
        )
        
        for sa in student_att:
            total_present_all += sa['present']
            pct = (sa['present'] / total_lectures) * 100
            if pct < 75:
                below_threshold += 1
            elif pct >= 90:
                above_threshold += 1
                
        # Handle students with 0 attendance records
        students_with_records = len(student_att)
        students_without_records = total_students - students_with_records
        below_threshold += students_without_records # 0% attendance is below 75
        
        avg_att = (total_present_all / (total_students * total_lectures)) * 100
        
        report.append({
            'offering': offering,
            'total_students': total_students,
            'total_lectures': total_lectures,
            'average_attendance': round(avg_att, 1),
            'below_threshold': below_threshold,
            'above_threshold': above_threshold
        })
        
    return report

def get_faculty_assignment_report(faculty):
    offerings = SubjectOffering.objects.filter(faculty=faculty)
    assignments = Assignment.objects.filter(offering__in=offerings).select_related('offering', 'offering__subject', 'offering__semester')
    
    report = []
    for assignment in assignments:
        total_students = assignment.offering.semester.students.filter(status='active').count()
        if total_students == 0:
            continue
            
        submissions = AssignmentSubmission.objects.filter(assignment=assignment)
        total_subs = submissions.count()
        late_subs = submissions.filter(status='late').count()
        graded_subs = submissions.filter(marks_awarded__isnull=False)
        pending_grading = total_subs - graded_subs.count()
        
        avg_marks = graded_subs.aggregate(avg=Avg('marks_awarded'))['avg']
        
        report.append({
            'assignment': assignment,
            'total_students': total_students,
            'submitted': total_subs,
            'late': late_subs,
            'not_submitted': total_students - total_subs,
            'pending_grading': pending_grading,
            'submission_rate': round((total_subs / total_students) * 100, 1),
            'average_marks': round(avg_marks, 1) if avg_marks is not None else None
        })
        
    return report

def get_faculty_exam_report(faculty):
    offerings = SubjectOffering.objects.filter(faculty=faculty)
    exams = Exam.objects.filter(offering__in=offerings).select_related('offering', 'offering__subject')
    
    report = []
    for exam in exams:
        total_students = exam.offering.semester.students.filter(status='active').count()
        if total_students == 0:
            continue
            
        # Only use latest results
        results = ExamResult.objects.filter(exam=exam, is_latest=True).exclude(attendance_status='absent')
        total_results = results.count()
        
        passed = results.filter(result_status='Pass').count()
        failed = results.filter(result_status='Fail').count()
        avg_marks = results.aggregate(avg=Avg('marks_obtained'))['avg']
        
        pass_pct = round((passed / total_results) * 100, 1) if total_results > 0 else 0
        fail_pct = round((failed / total_results) * 100, 1) if total_results > 0 else 0
        
        report.append({
            'exam': exam,
            'total_students': total_students,
            'results_entered': total_results,
            'pending_results': total_students - ExamResult.objects.filter(exam=exam, is_latest=True).count(),
            'average_marks': round(avg_marks, 1) if avg_marks is not None else None,
            'pass_percentage': pass_pct,
            'fail_percentage': fail_pct
        })
        
    return report

def get_faculty_student_performance(faculty, offering_id):
    offering = SubjectOffering.objects.filter(faculty=faculty, id=offering_id).first()
    if not offering:
        return None
        
    students = offering.semester.students.filter(status='active').select_related('student', 'student__user')
    total_lectures = offering.lectures.count()
    
    # Prefetch assignments and exams
    assignments = Assignment.objects.filter(offering=offering)
    exams = Exam.objects.filter(offering=offering, status='published')
    
    report = []
    for s in students:
        student = s.student
        
        # Attendance
        present = Attendance.objects.filter(student=student, lecture__offering=offering, status='present').count()
        att_pct = round((present / total_lectures) * 100, 1) if total_lectures > 0 else 0
        
        # Assignments
        total_ass_marks = sum(a.maximum_marks for a in assignments)
        subs = AssignmentSubmission.objects.filter(student=student, assignment__in=assignments, marks_awarded__isnull=False)
        obt_ass_marks = sum(sub.marks_awarded for sub in subs)
        ass_pct = round((obt_ass_marks / total_ass_marks) * 100, 1) if total_ass_marks > 0 else 0
        
        # Exams
        total_exam_marks = sum(e.total_marks for e in exams)
        res = ExamResult.objects.filter(student=student, exam__in=exams, is_latest=True).exclude(marks_obtained=None)
        obt_exam_marks = sum(r.marks_obtained for r in res)
        exam_pct = round((obt_exam_marks / total_exam_marks) * 100, 1) if total_exam_marks > 0 else 0
        
        report.append({
            'student': student,
            'attendance_percentage': att_pct,
            'assignment_percentage': ass_pct,
            'exam_percentage': exam_pct,
        })
        
    return {
        'offering': offering,
        'student_data': report
    }

from django.db.models import Count, Avg, Q
from academics.models import Department, Course
from students.models import Student, StudentSemester
from attendance.models import Attendance
from examinations.models import ExamResult, SemesterReport
from assignments.models import AssignmentSubmission

# Thresholds as requested
ATTENDANCE_WARNING_THRESHOLD = 75.0
LOW_SGPA_THRESHOLD = 5.0
LOW_SUBMISSION_RATE_THRESHOLD = 60.0
FAILED_EXAMS_THRESHOLD = 2

def get_admin_analytics_data():
    # Enrollment Distribution by Department
    dept_distribution = Student.objects.values('course__department__name').annotate(count=Count('id'))
    dept_labels = [item['course__department__name'] if item['course__department__name'] else 'Unassigned' for item in dept_distribution]
    dept_data = [item['count'] for item in dept_distribution]
    
    # SGPA Distribution (Across all Semester Reports)
    sgpa_stats = SemesterReport.objects.aggregate(
        avg_sgpa=Avg('sgpa'),
        pass_count=Count('id', filter=Q(result_status='Pass')),
        fail_count=Count('id', filter=Q(result_status='Fail'))
    )
    
    return {
        'enrollment_chart': {
            'labels': dept_labels,
            'data': dept_data
        },
        'sgpa_stats': {
            'avg_sgpa': round(sgpa_stats['avg_sgpa'], 2) if sgpa_stats['avg_sgpa'] else 0,
            'pass_count': sgpa_stats['pass_count'],
            'fail_count': sgpa_stats['fail_count']
        }
    }

def get_at_risk_students():
    """
    Identifies students who may need academic attention based on defined thresholds.
    This demonstrates the Academic Monitoring logic.
    """
    active_students = StudentSemester.objects.filter(status='active').select_related('student', 'student__user', 'semester')
    
    at_risk_list = []
    
    for ss in active_students:
        student = ss.student
        reasons = []
        
        # 1. Attendance Check
        att_stats = Attendance.objects.filter(
            student=student,
            lecture__offering__semester=ss.semester
        ).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present'))
        )
        if att_stats['total'] > 0:
            att_pct = (att_stats['present'] / att_stats['total']) * 100
            if att_pct < ATTENDANCE_WARNING_THRESHOLD:
                reasons.append(f"Attendance {round(att_pct, 1)}% < {ATTENDANCE_WARNING_THRESHOLD}%")
                
        # 2. Latest SGPA Check
        latest_report = SemesterReport.objects.filter(student=student).order_by('-semester__semester_number').first()
        if latest_report and float(latest_report.sgpa) < LOW_SGPA_THRESHOLD:
            reasons.append(f"SGPA {latest_report.sgpa} < {LOW_SGPA_THRESHOLD}")
            
        # 3. Failed Exams Check
        failed_exams = ExamResult.objects.filter(
            student=student, 
            is_latest=True, 
            result_status='Fail'
        ).count()
        if failed_exams >= FAILED_EXAMS_THRESHOLD:
            reasons.append(f"Failed {failed_exams} exams")
            
        # 4. Low Submission Rate
        # Optional: implementation of assignment check
        
        if reasons:
            at_risk_list.append({
                'student': student,
                'semester': ss.semester,
                'reasons': reasons
            })
            
    return at_risk_list

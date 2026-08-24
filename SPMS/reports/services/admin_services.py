from django.db.models import Count, Avg, Q, F
from accounts.models import User
from academics.models import Department, Course, CourseBatch, Semester, SubjectOffering
from students.models import Student, StudentSemester
from attendance.models import Attendance
from examinations.models import ExamResult, SemesterReport

def get_admin_dashboard_overview():
    total_students = Student.objects.count()
    total_faculty = User.objects.filter(role='faculty').count()
    total_departments = Department.objects.count()
    total_courses = Course.objects.count()
    
    return {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_departments': total_departments,
        'total_courses': total_courses
    }

def get_enrollment_report():
    # Group students by Department, Course, Batch, Semester
    # This query uses values() and annotate() for grouping
    enrollments = StudentSemester.objects.filter(status='active').values(
        'semester__course_batch__course__department__name',
        'semester__course_batch__course__name',
        'semester__course_batch__academic_year',
        'semester__semester_number'
    ).annotate(
        total_students=Count('student', distinct=True)
    ).order_by(
        'semester__course_batch__course__department__name',
        'semester__course_batch__course__name',
        '-semester__course_batch__academic_year',
        'semester__semester_number'
    )
    return enrollments

def get_department_report():
    departments = Department.objects.annotate(
        total_courses=Count('courses', distinct=True),
        total_faculty=Count('user', filter=Q(user__role='faculty'), distinct=True),
    )
    
    # Calculate students per department
    # Need to go through Course -> CourseBatch -> Student (via student_profile)
    # This can be tricky with single query, so we'll do it python side for small numbers or subquery
    report = []
    for dept in departments:
        total_students = Student.objects.filter(course__department=dept).count()
        report.append({
            'department': dept,
            'total_courses': dept.total_courses,
            'total_faculty': dept.total_faculty,
            'total_students': total_students
        })
    return report

def get_course_report(filters=None):
    queryset = Course.objects.all()
    if filters and 'department_id' in filters and filters['department_id']:
        queryset = queryset.filter(department_id=filters['department_id'])
        
    courses = queryset.annotate(
        total_batches=Count('coursebatch', distinct=True)
    ).select_related('department')
    
    report = []
    for course in courses:
        total_students = Student.objects.filter(course=course).count()
        report.append({
            'course': course,
            'total_batches': course.total_batches,
            'total_students': total_students
        })
    return report

def get_batch_report(course_id=None):
    queryset = CourseBatch.objects.select_related('course', 'course__department')
    if course_id:
        queryset = queryset.filter(course_id=course_id)
        
    report = []
    for batch in queryset:
        total_students = Student.objects.filter(batch=batch).count()
        report.append({
            'batch': batch,
            'total_students': total_students
        })
    return report

def get_semester_report_admin(batch_id=None):
    queryset = Semester.objects.select_related('course_batch', 'course_batch__course')
    if batch_id:
        queryset = queryset.filter(course_batch_id=batch_id)
        
    report = []
    for semester in queryset:
        active_students = StudentSemester.objects.filter(semester=semester, status='active').count()
        
        # Performance
        sem_reports = SemesterReport.objects.filter(semester=semester)
        avg_sgpa = sem_reports.aggregate(avg=Avg('sgpa'))['avg']
        pass_count = sem_reports.filter(result_status='Pass').count()
        fail_count = sem_reports.filter(result_status='Fail').count()
        
        report.append({
            'semester': semester,
            'active_students': active_students,
            'avg_sgpa': round(avg_sgpa, 2) if avg_sgpa else None,
            'pass_count': pass_count,
            'fail_count': fail_count
        })
    return report

def get_offering_report(semester_id=None):
    queryset = SubjectOffering.objects.select_related('subject', 'semester', 'semester__course_batch', 'faculty', 'faculty__user')
    if semester_id:
        queryset = queryset.filter(semester_id=semester_id)
        
    report = []
    for offering in queryset:
        total_students = StudentSemester.objects.filter(semester=offering.semester, status='active').count()
        report.append({
            'offering': offering,
            'total_students': total_students
        })
    return report

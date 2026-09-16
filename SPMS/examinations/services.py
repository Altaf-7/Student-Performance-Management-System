def calculate_grade(marks, total_marks):
    """
    Calculate the grade based on standard percentage thresholds.
    """
    if marks is None or total_marks is None or total_marks <= 0:
        return None, None

    percentage = (marks / total_marks) * 100

    if percentage >= 90:
        return 'O', 'Pass'
    elif percentage >= 80:
        return 'A+', 'Pass'
    elif percentage >= 70:
        return 'A', 'Pass'
    elif percentage >= 60:
        return 'B+', 'Pass'
    elif percentage >= 50:
        return 'B', 'Pass'
    elif percentage >= 40:
        return 'C', 'Pass'
    else:
        return 'F', 'Fail'

def generate_semester_report(student, semester):
    """
    Generate or update the SemesterReport for a student.
    Uses simplified logic summing all published exam marks.
    """
    from examinations.models import ExamResult, SemesterReport
    from academics.models import SubjectOffering

    # Find all published exams for the student's semester
    results = ExamResult.objects.filter(
        student=student,
        exam__offering__semester=semester,
        exam__status='published',
        is_latest=True,
    ).exclude(attendance_status__in=['absent', 'medical_leave'])

    total_marks = 0
    obtained_marks = 0
    has_fail = False
    
    for result in results:
        total_marks += result.exam.total_marks
        if result.marks_obtained is not None:
            obtained_marks += result.marks_obtained
            if result.result_status == 'Fail':
                has_fail = True

    if total_marks == 0:
        return None

    percentage = (obtained_marks / total_marks) * 100
    sgpa = min(percentage / 10, 10.0)
    
    status = 'Fail' if has_fail else 'Pass'

    report, created = SemesterReport.objects.update_or_create(
        student=student,
        semester=semester,
        academic_year=semester.course_batch.academic_year,
        defaults={
            'total_marks': total_marks,
            'obtained_marks': obtained_marks,
            'sgpa': round(sgpa, 2),
            'result_status': status
        }
    )
    return report

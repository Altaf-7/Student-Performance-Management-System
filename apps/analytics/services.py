"""
Dashboard + chart data aggregation. Every number here comes from a real
database query - nothing is hard-coded, per project standards.
"""
from decimal import Decimal

from django.db.models import Avg, Count, Q
from django.utils import timezone

from apps.academics.models import Course, Department, Enrollment
from apps.academics.services import calculate_cgpa, calculate_semester_gpa
from apps.attendance.models import Attendance
from apps.attendance.services import get_student_overall_attendance
from apps.examinations.models import Examination, ExamResult
from apps.notifications.models import Announcement, Notification


def _user_model():
    from django.contrib.auth import get_user_model
    return get_user_model()


def get_admin_dashboard_context():
    User = _user_model()
    students = User.objects.filter(role="STUDENT")
    faculty = User.objects.filter(role="FACULTY")

    total_students = students.count()
    total_faculty = faculty.count()
    total_courses = Course.objects.count()
    total_departments = Department.objects.count()
    active_students = students.filter(is_active=True).count()

    avg_marks = ExamResult.objects.aggregate(a=Avg("obtained_marks"))["a"] or Decimal("0")

    attendance_agg = Attendance.objects.aggregate(
        present=Count("id", filter=Q(status=Attendance.Status.PRESENT)),
        late=Count("id", filter=Q(status=Attendance.Status.LATE)),
        absent=Count("id", filter=Q(status=Attendance.Status.ABSENT)),
    )
    from apps.attendance.services import calculate_attendance_percentage
    avg_attendance = calculate_attendance_percentage(
        attendance_agg["present"] or 0, attendance_agg["late"] or 0, attendance_agg["absent"] or 0
    )

    # Average GPA across all students who have at least one result.
    gpas = []
    for s in students.iterator():
        cgpa_data = calculate_cgpa(s)
        if cgpa_data["semesters"]:
            gpas.append(float(cgpa_data["cgpa"]))
    avg_gpa = round(sum(gpas) / len(gpas), 2) if gpas else 0

    from apps.analytics.risk_service import get_at_risk_students
    at_risk_count = len(get_at_risk_students(students))

    # Chart: average marks by subject (course)
    marks_by_course = list(
        ExamResult.objects.values("course__course_code")
        .annotate(avg_marks=Avg("obtained_marks"))
        .order_by("course__course_code")[:12]
    )

    # Chart: grade distribution
    grade_distribution = list(
        ExamResult.objects.values("grade").annotate(count=Count("id")).order_by("grade")
    )

    # Chart: attendance distribution (good/warning/critical) across students
    good = warning = critical = 0
    for s in students.iterator():
        band = get_student_overall_attendance(s)["overall_band"]
        if band == "GOOD":
            good += 1
        elif band == "WARNING":
            warning += 1
        else:
            critical += 1

    # Chart: pass/fail
    pass_count = ExamResult.objects.exclude(grade="F").count()
    fail_count = ExamResult.objects.filter(grade="F").count()

    # Chart: department-wise average performance
    dept_performance = list(
        ExamResult.objects.values("course__department__name")
        .annotate(avg_marks=Avg("obtained_marks"))
        .order_by("course__department__name")
    )

    # Chart: monthly attendance (present % per month)
    monthly_attendance = _monthly_attendance()

    # Chart: GPA distribution buckets
    gpa_buckets = {"0-4": 0, "4-6": 0, "6-8": 0, "8-10": 0}
    for g in gpas:
        if g < 4:
            gpa_buckets["0-4"] += 1
        elif g < 6:
            gpa_buckets["4-6"] += 1
        elif g < 8:
            gpa_buckets["6-8"] += 1
        else:
            gpa_buckets["8-10"] += 1

    recent_exams = Examination.objects.select_related("course").order_by("-exam_date")[:6]
    recent_announcements = Announcement.objects.select_related("author").order_by("-created_at")[:6]

    return {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_courses": total_courses,
        "total_departments": total_departments,
        "active_students": active_students,
        "avg_marks": round(float(avg_marks), 2),
        "avg_attendance": float(avg_attendance),
        "avg_gpa": avg_gpa,
        "at_risk_count": at_risk_count,
        "recent_exams": recent_exams,
        "recent_announcements": recent_announcements,
        "chart_marks_by_course": {
            "labels": [m["course__course_code"] for m in marks_by_course],
            "data": [round(float(m["avg_marks"] or 0), 2) for m in marks_by_course],
        },
        "chart_grade_distribution": {
            "labels": [g["grade"] for g in grade_distribution],
            "data": [g["count"] for g in grade_distribution],
        },
        "chart_attendance_distribution": {"labels": ["Good", "Warning", "Critical"], "data": [good, warning, critical]},
        "chart_pass_fail": {"labels": ["Pass", "Fail"], "data": [pass_count, fail_count]},
        "chart_department_performance": {
            "labels": [d["course__department__name"] for d in dept_performance],
            "data": [round(float(d["avg_marks"] or 0), 2) for d in dept_performance],
        },
        "chart_monthly_attendance": monthly_attendance,
        "chart_gpa_distribution": {"labels": list(gpa_buckets.keys()), "data": list(gpa_buckets.values())},
    }


def _monthly_attendance():
    from apps.attendance.services import calculate_attendance_percentage
    qs = (
        Attendance.objects.annotate(ym=_TruncMonth("date"))
        .values("ym")
        .annotate(
            present=Count("id", filter=Q(status=Attendance.Status.PRESENT)),
            late=Count("id", filter=Q(status=Attendance.Status.LATE)),
            absent=Count("id", filter=Q(status=Attendance.Status.ABSENT)),
        )
        .order_by("ym")
    )
    labels, data = [], []
    for row in qs:
        if row["ym"] is None:
            continue
        pct = calculate_attendance_percentage(row["present"], row["late"], row["absent"])
        labels.append(row["ym"].strftime("%b %Y"))
        data.append(float(pct))
    return {"labels": labels, "data": data}


def _TruncMonth(field):
    from django.db.models.functions import TruncMonth
    return TruncMonth(field)


def get_faculty_dashboard_context(faculty_user):
    courses = Course.objects.filter(faculty=faculty_user)
    course_ids = list(courses.values_list("id", flat=True))
    student_count = Enrollment.objects.filter(course_id__in=course_ids).values("student").distinct().count()

    today = timezone.now().date()
    attendance_marked_today = Attendance.objects.filter(course_id__in=course_ids, date=today).values("course").distinct().count()
    attendance_pending = courses.count() - attendance_marked_today

    from apps.assignments.models import AssignmentSubmission
    pending_grading = AssignmentSubmission.objects.filter(
        assignment__course_id__in=course_ids
    ).exclude(status=AssignmentSubmission.Status.GRADED).count()

    upcoming_exams = Examination.objects.filter(course_id__in=course_ids, exam_date__gte=today).order_by("exam_date")[:6]

    from apps.assignments.models import AssignmentSubmission as Sub
    recent_submissions = Sub.objects.filter(assignment__course_id__in=course_ids).select_related(
        "student", "assignment"
    ).order_by("-submitted_at")[:8]

    from django.contrib.auth import get_user_model
    User = get_user_model()
    students_in_courses = User.objects.filter(enrollments__course_id__in=course_ids).distinct()
    from apps.analytics.risk_service import get_at_risk_students
    at_risk = get_at_risk_students(students_in_courses)[:8]

    return {
        "courses": courses,
        "student_count": student_count,
        "attendance_pending": max(attendance_pending, 0),
        "pending_grading": pending_grading,
        "upcoming_exams": upcoming_exams,
        "recent_submissions": recent_submissions,
        "at_risk_students": at_risk,
    }


def get_student_dashboard_context(student_user):
    enrollments = Enrollment.objects.filter(student=student_user).select_related("course", "semester")
    cgpa_data = calculate_cgpa(student_user)
    attendance = get_student_overall_attendance(student_user)

    today = timezone.now()
    from apps.assignments.models import Assignment
    course_ids = enrollments.values_list("course_id", flat=True)
    upcoming_assignments = Assignment.objects.filter(course_id__in=course_ids, due_date__gte=today).order_by("due_date")[:6]
    upcoming_exams = Examination.objects.filter(course_id__in=course_ids, exam_date__gte=today.date()).order_by("exam_date")[:6]

    recent_results = ExamResult.objects.filter(student=student_user, examination__is_published=True).select_related(
        "examination", "course"
    ).order_by("-created_at")[:8]

    notifications = Notification.objects.filter(recipient=student_user).order_by("-created_at")[:8]

    from apps.analytics.risk_service import assess_student_risk
    risk = assess_student_risk(student_user)

    grade_counts = {}
    for r in ExamResult.objects.filter(student=student_user, examination__is_published=True):
        grade_counts[r.grade] = grade_counts.get(r.grade, 0) + 1

    return {
        "enrollments": enrollments,
        "cgpa": cgpa_data["cgpa"],
        "semester_gpas": cgpa_data["semesters"],
        "attendance": attendance,
        "upcoming_assignments": upcoming_assignments,
        "upcoming_exams": upcoming_exams,
        "recent_results": recent_results,
        "notifications": notifications,
        "risk": risk,
        "chart_grade_distribution": {"labels": list(grade_counts.keys()), "data": list(grade_counts.values())},
        "chart_gpa_trend": {
            "labels": [f"{s['semester'].name}" for s in cgpa_data["semesters"]],
            "data": [float(s["gpa"]) for s in cgpa_data["semesters"]],
        },
    }

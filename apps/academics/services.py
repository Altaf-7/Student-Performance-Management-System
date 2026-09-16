"""
Centralized academic-performance business logic.

Nothing in this file talks to templates or JavaScript - views call these
functions and pass plain results to templates. This keeps grade/GPA/CGPA
calculation in exactly one place, per project standards (see project spec
section 16/17).
"""
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Sum, F

from .models import GradeScale


def calculate_percentage(obtained_marks, maximum_marks) -> Decimal:
    obtained_marks = Decimal(str(obtained_marks))
    maximum_marks = Decimal(str(maximum_marks))
    if maximum_marks <= 0:
        return Decimal("0.00")
    pct = (obtained_marks / maximum_marks) * Decimal("100")
    return pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_grade(percentage) -> tuple[str, Decimal]:
    """Returns (grade_letter, grade_point) for a percentage using the
    configurable GradeScale table. Falls back to the documented default
    scale (see README) if no GradeScale rows exist yet."""
    percentage = Decimal(str(percentage))
    scale = GradeScale.objects.filter(
        min_percentage__lte=percentage, max_percentage__gte=percentage
    ).first()
    if scale:
        return scale.grade, scale.grade_point

    # Documented default scale, used only if the DB table is empty.
    default_bands = [
        (Decimal("90"), Decimal("100"), "A+", Decimal("10.0")),
        (Decimal("80"), Decimal("89.99"), "A", Decimal("9.0")),
        (Decimal("70"), Decimal("79.99"), "B+", Decimal("8.0")),
        (Decimal("60"), Decimal("69.99"), "B", Decimal("7.0")),
        (Decimal("50"), Decimal("59.99"), "C", Decimal("6.0")),
        (Decimal("40"), Decimal("49.99"), "D", Decimal("5.0")),
        (Decimal("0"), Decimal("39.99"), "F", Decimal("0.0")),
    ]
    for lo, hi, letter, gp in default_bands:
        if lo <= percentage <= hi:
            return letter, gp
    return "F", Decimal("0.0")


def calculate_course_result_for_student(student, course):
    """Aggregates all published exam results for a student in one course
    into a single overall percentage/grade for that course."""
    from apps.examinations.models import ExamResult

    results = ExamResult.objects.filter(
        student=student, course=course, examination__is_published=True
    )
    total_obtained = results.aggregate(s=Sum("obtained_marks"))["s"] or Decimal("0")
    total_max = results.aggregate(s=Sum("maximum_marks"))["s"] or Decimal("0")
    if total_max == 0:
        return None
    percentage = calculate_percentage(total_obtained, total_max)
    grade, grade_point = calculate_grade(percentage)
    return {
        "course": course,
        "percentage": percentage,
        "grade": grade,
        "grade_point": grade_point,
        "total_obtained": total_obtained,
        "total_max": total_max,
        "passed": grade != "F",
    }


def calculate_semester_gpa(student, semester):
    """Credit-weighted GPA for one semester:
    GPA = sum(grade_point * credits) / sum(credits)
    across all courses the student was enrolled in for that semester.
    """
    from .models import Enrollment

    enrollments = Enrollment.objects.filter(student=student, semester=semester).select_related("course")
    total_weighted = Decimal("0")
    total_credits = Decimal("0")
    course_breakdown = []

    for enrollment in enrollments:
        result = calculate_course_result_for_student(student, enrollment.course)
        credits = Decimal(str(enrollment.course.credits))
        if result is None:
            continue
        total_weighted += result["grade_point"] * credits
        total_credits += credits
        course_breakdown.append({**result, "credits": credits})

    gpa = (total_weighted / total_credits).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if total_credits > 0 else Decimal("0.00")
    return {"gpa": gpa, "courses": course_breakdown, "total_credits": total_credits}


def calculate_cgpa(student):
    """Credit-weighted CGPA across every semester the student has enrolled
    results for."""
    from .models import Semester, Enrollment

    semesters = Semester.objects.filter(enrollments__student=student).distinct()
    total_weighted = Decimal("0")
    total_credits = Decimal("0")
    semester_gpas = []

    for semester in semesters:
        sem_data = calculate_semester_gpa(student, semester)
        if sem_data["total_credits"] > 0:
            total_weighted += sem_data["gpa"] * sem_data["total_credits"]
            total_credits += sem_data["total_credits"]
        semester_gpas.append({"semester": semester, **sem_data})

    cgpa = (total_weighted / total_credits).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if total_credits > 0 else Decimal("0.00")
    semester_gpas.sort(key=lambda x: (x["semester"].academic_year, x["semester"].semester_number))
    return {"cgpa": cgpa, "semesters": semester_gpas}

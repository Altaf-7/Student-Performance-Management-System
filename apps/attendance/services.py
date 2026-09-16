"""
Attendance business logic - the single source of truth for how attendance
percentages and status bands are computed.

DOCUMENTED RULE for LATE:
  A LATE mark counts as HALF a present class when computing the
  attendance percentage. This is a common, transparent convention:
  the student showed up (unlike an absence) but missed part of the
  session. This is configurable in one place below if the institution
  wants a different policy.
LATE_WEIGHT = 0.5 (0.0 would treat LATE as absent, 1.0 would treat it as
  fully present).
"""
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings

LATE_WEIGHT = Decimal("0.5")


def calculate_attendance_percentage(present, late, absent) -> Decimal:
    total = present + late + absent
    if total == 0:
        return Decimal("0.00")
    effective_present = Decimal(present) + (Decimal(late) * LATE_WEIGHT)
    pct = (effective_present / Decimal(total)) * Decimal("100")
    return pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def attendance_band(percentage) -> str:
    """GOOD / WARNING / CRITICAL using the configurable thresholds in
    settings.ATTENDANCE_GOOD_THRESHOLD / ATTENDANCE_WARNING_THRESHOLD."""
    percentage = float(percentage)
    if percentage >= settings.ATTENDANCE_GOOD_THRESHOLD:
        return "GOOD"
    if percentage >= settings.ATTENDANCE_WARNING_THRESHOLD:
        return "WARNING"
    return "CRITICAL"


def get_student_course_attendance(student, course):
    from .models import Attendance

    qs = Attendance.objects.filter(student=student, course=course)
    present = qs.filter(status=Attendance.Status.PRESENT).count()
    late = qs.filter(status=Attendance.Status.LATE).count()
    absent = qs.filter(status=Attendance.Status.ABSENT).count()
    total = present + late + absent
    percentage = calculate_attendance_percentage(present, late, absent)
    return {
        "course": course, "present": present, "late": late, "absent": absent,
        "total": total, "percentage": percentage, "band": attendance_band(percentage),
    }


def get_student_overall_attendance(student):
    from apps.academics.models import Enrollment

    courses = [e.course for e in Enrollment.objects.filter(student=student).select_related("course")]
    per_course = [get_student_course_attendance(student, c) for c in courses]
    total_present = sum(c["present"] for c in per_course)
    total_late = sum(c["late"] for c in per_course)
    total_absent = sum(c["absent"] for c in per_course)
    overall_pct = calculate_attendance_percentage(total_present, total_late, total_absent)
    return {
        "overall_percentage": overall_pct,
        "overall_band": attendance_band(overall_pct),
        "per_course": per_course,
    }

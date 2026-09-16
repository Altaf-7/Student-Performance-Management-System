"""
Transparent, rule-based academic risk detection. No machine learning -
every flag is a documented threshold check so staff can see exactly why
a student was flagged.

RISK LEVELS AND THRESHOLDS (also mirrored in settings.py / .env):
  - LOW      : exactly one minor concern
                 (attendance between WARNING and GOOD thresholds, i.e.
                 75% <= attendance < 85% by default)
  - MEDIUM   : exactly one significant concern
                 (attendance < 75% OR GPA < 6.0 OR one failed course)
  - HIGH     : two significant concerns from:
                 attendance < 75%, GPA < 6.0, any failed course,
                 assignment completion < 60%
  - CRITICAL : three or more significant concerns, OR attendance < 50%,
               OR GPA < 4.0, OR 2+ failed courses

A student with no attendance records yet, or no published exam results
yet, is not penalized for that absence of data - attendance/GPA checks
only run once there is real data to judge (assignment completion and
failed-course checks are unaffected, since those already default safely
to "no concern" when there is nothing to grade).
"""
from apps.academics.services import calculate_cgpa
from apps.attendance.services import get_student_overall_attendance
from apps.assignments.services import assignment_completion_rate


def assess_student_risk(student):
    attendance = get_student_overall_attendance(student)
    attendance_pct = float(attendance["overall_percentage"])
    has_attendance_data = any(c["total"] > 0 for c in attendance["per_course"])

    cgpa_data = calculate_cgpa(student)
    cgpa = float(cgpa_data["cgpa"])
    has_result_data = len(cgpa_data["semesters"]) > 0

    failed_courses = []
    for sem in cgpa_data["semesters"]:
        for course_result in sem["courses"]:
            if not course_result["passed"]:
                failed_courses.append(course_result["course"])

    completion_rate = assignment_completion_rate(student)

    reasons = []
    significant_concerns = 0

    if has_attendance_data:
        if attendance_pct < 75:
            reasons.append(f"Attendance is {attendance_pct}%, below the 75% requirement.")
            significant_concerns += 1
        elif attendance_pct < 85:
            reasons.append(f"Attendance is {attendance_pct}%, in the warning band (75-85%).")

    if has_result_data and cgpa < 6.0:
        reasons.append(f"CGPA is {cgpa}, below the minimum expected 6.0.")
        significant_concerns += 1

    if failed_courses:
        reasons.append(f"{len(failed_courses)} failed course(s): " + ", ".join(c.course_code for c in failed_courses))
        significant_concerns += 1

    if completion_rate < 60:
        reasons.append(f"Assignment completion is only {completion_rate}%.")
        significant_concerns += 1

    critical_trigger = (
        (has_attendance_data and attendance_pct < 50)
        or (has_result_data and cgpa < 4.0)
        or len(failed_courses) >= 2
    )
    if critical_trigger:
        level = "CRITICAL"
    elif significant_concerns >= 2:
        level = "HIGH"
    elif significant_concerns == 1:
        level = "MEDIUM"
    elif reasons:
        level = "LOW"
    else:
        level = "NONE"

    recommendation = {
        "NONE": "No intervention needed.",
        "LOW": "Monitor attendance; encourage regular class participation.",
        "MEDIUM": "Advisor check-in recommended within two weeks.",
        "HIGH": "Schedule an advisor/mentor meeting and notify department.",
        "CRITICAL": "Immediate academic counseling and parent/guardian-level escalation via department head.",
    }[level]

    return {
        "student": student,
        "risk_level": level,
        "attendance_percentage": attendance_pct,
        "cgpa": cgpa,
        "failed_courses": failed_courses,
        "assignment_completion_rate": completion_rate,
        "reasons": reasons,
        "recommendation": recommendation,
    }


def get_at_risk_students(students_queryset):
    results = [assess_student_risk(s) for s in students_queryset]
    results = [r for r in results if r["risk_level"] != "NONE"]
    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    results.sort(key=lambda r: order[r["risk_level"]])
    return results

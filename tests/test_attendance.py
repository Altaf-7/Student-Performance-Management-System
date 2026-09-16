from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.academics.models import Department, Semester, Course, Enrollment
from apps.attendance.models import Attendance
from apps.attendance.services import calculate_attendance_percentage, attendance_band, get_student_course_attendance

User = get_user_model()


class AttendanceCalculationTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="Computer Science", code="CS")
        self.sem = Semester.objects.create(name="Semester 1", semester_number=1, academic_year="2025-2026",
                                            start_date="2025-08-01", end_date="2025-12-01")
        self.faculty = User.objects.create_user(username="fac1", password="x", role=User.Role.FACULTY)
        self.student = User.objects.create_user(username="stu1", password="x", role=User.Role.STUDENT)
        self.course = Course.objects.create(course_code="CS101", course_name="DS", credits=4,
                                             department=self.dept, semester=self.sem, faculty=self.faculty)
        Enrollment.objects.create(student=self.student, course=self.course, academic_year="2025-2026", semester=self.sem)

    def test_percentage_all_present(self):
        self.assertEqual(calculate_attendance_percentage(10, 0, 0), Decimal("100.00"))

    def test_percentage_with_late_weighted_half(self):
        # 8 present, 2 late, 0 absent -> (8 + 1)/10 = 90%
        self.assertEqual(calculate_attendance_percentage(8, 2, 0), Decimal("90.00"))

    def test_percentage_zero_sessions(self):
        self.assertEqual(calculate_attendance_percentage(0, 0, 0), Decimal("0.00"))

    def test_attendance_bands(self):
        self.assertEqual(attendance_band(90), "GOOD")
        self.assertEqual(attendance_band(80), "WARNING")
        self.assertEqual(attendance_band(50), "CRITICAL")

    def test_duplicate_attendance_prevented(self):
        Attendance.objects.create(student=self.student, course=self.course, date="2025-09-01",
                                   status=Attendance.Status.PRESENT, marked_by=self.faculty)
        with self.assertRaises(Exception):
            Attendance.objects.create(student=self.student, course=self.course, date="2025-09-01",
                                       status=Attendance.Status.ABSENT, marked_by=self.faculty)

    def test_get_student_course_attendance(self):
        for d, status in [("2025-09-01", Attendance.Status.PRESENT), ("2025-09-02", Attendance.Status.ABSENT)]:
            Attendance.objects.create(student=self.student, course=self.course, date=d, status=status, marked_by=self.faculty)
        result = get_student_course_attendance(self.student, self.course)
        self.assertEqual(result["present"], 1)
        self.assertEqual(result["absent"], 1)
        self.assertEqual(result["percentage"], Decimal("50.00"))

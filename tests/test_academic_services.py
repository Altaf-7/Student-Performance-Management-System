from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.academics.models import Department, Semester, Course, Enrollment
from apps.academics.services import calculate_percentage, calculate_grade, calculate_semester_gpa, calculate_cgpa
from apps.examinations.models import Examination, ExamResult

User = get_user_model()


class GradeCalculationTests(TestCase):
    def test_calculate_percentage(self):
        self.assertEqual(calculate_percentage(45, 50), Decimal("90.00"))
        self.assertEqual(calculate_percentage(0, 100), Decimal("0.00"))
        self.assertEqual(calculate_percentage(5, 0), Decimal("0.00"))

    def test_calculate_grade_bands(self):
        grade, gp = calculate_grade(95)
        self.assertEqual(grade, "A+")
        grade, gp = calculate_grade(35)
        self.assertEqual(grade, "F")
        self.assertEqual(gp, Decimal("0.0"))


class GPACalculationTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="Computer Science", code="CS")
        self.sem = Semester.objects.create(name="Semester 1", semester_number=1, academic_year="2025-2026",
                                            start_date="2025-08-01", end_date="2025-12-01")
        self.faculty = User.objects.create_user(username="fac1", password="x", role=User.Role.FACULTY)
        self.student = User.objects.create_user(username="stu1", password="x", role=User.Role.STUDENT)
        self.course1 = Course.objects.create(course_code="CS101", course_name="DS", credits=4,
                                              department=self.dept, semester=self.sem, faculty=self.faculty)
        self.course2 = Course.objects.create(course_code="CS102", course_name="DBMS", credits=3,
                                              department=self.dept, semester=self.sem, faculty=self.faculty)
        Enrollment.objects.create(student=self.student, course=self.course1, academic_year="2025-2026", semester=self.sem)
        Enrollment.objects.create(student=self.student, course=self.course2, academic_year="2025-2026", semester=self.sem)

    def _add_result(self, course, obtained, maximum=100):
        exam = Examination.objects.create(name=f"Exam {course.course_code}", exam_type="MIDTERM", course=course,
                                           semester=self.sem, academic_year="2025-2026", exam_date="2025-09-01",
                                           maximum_marks=maximum, is_published=True, created_by=self.faculty)
        return ExamResult.objects.create(student=self.student, examination=exam, course=course,
                                          maximum_marks=maximum, obtained_marks=obtained, entered_by=self.faculty)

    def test_semester_gpa_credit_weighted(self):
        self._add_result(self.course1, 90)  # 90% -> A+ -> 10.0 * 4 credits
        self._add_result(self.course2, 70)  # 70% -> B+ -> 8.0 * 3 credits
        data = calculate_semester_gpa(self.student, self.sem)
        expected = ((Decimal("10.0") * 4) + (Decimal("8.0") * 3)) / 7
        self.assertEqual(data["gpa"], expected.quantize(Decimal("0.01")))

    def test_obtained_marks_cannot_exceed_maximum(self):
        exam = Examination.objects.create(name="Bad Exam", exam_type="QUIZ", course=self.course1,
                                           semester=self.sem, academic_year="2025-2026", exam_date="2025-09-01",
                                           maximum_marks=50, is_published=True, created_by=self.faculty)
        with self.assertRaises(Exception):
            ExamResult.objects.create(student=self.student, examination=exam, course=self.course1,
                                       maximum_marks=50, obtained_marks=999, entered_by=self.faculty)

    def test_cgpa_across_semesters(self):
        self._add_result(self.course1, 90)
        self._add_result(self.course2, 70)
        data = calculate_cgpa(self.student)
        self.assertGreater(data["cgpa"], Decimal("0"))

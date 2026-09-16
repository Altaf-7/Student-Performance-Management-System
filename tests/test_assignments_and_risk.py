from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.academics.models import Department, Semester, Course, Enrollment
from apps.assignments.models import Assignment, AssignmentSubmission
from apps.assignments.services import determine_submission_status, grade_submission
from apps.analytics.risk_service import assess_student_risk

User = get_user_model()


class AssignmentWorkflowTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="Computer Science", code="CS")
        self.sem = Semester.objects.create(name="Semester 1", semester_number=1, academic_year="2025-2026",
                                            start_date="2025-08-01", end_date="2025-12-01")
        self.faculty = User.objects.create_user(username="fac1", password="Pass@1234", role=User.Role.FACULTY)
        self.student = User.objects.create_user(username="stu1", password="Pass@1234", role=User.Role.STUDENT)
        self.course = Course.objects.create(course_code="CS101", course_name="DS", credits=4,
                                             department=self.dept, semester=self.sem, faculty=self.faculty)
        Enrollment.objects.create(student=self.student, course=self.course, academic_year="2025-2026", semester=self.sem)
        self.assignment = Assignment.objects.create(
            title="HW1", course=self.course, due_date=timezone.now() + timedelta(days=3),
            maximum_marks=20, created_by=self.faculty,
        )

    def test_submission_status_before_due_date(self):
        status = determine_submission_status(self.assignment, timezone.now())
        self.assertEqual(status, AssignmentSubmission.Status.SUBMITTED)

    def test_submission_status_after_due_date(self):
        status = determine_submission_status(self.assignment, timezone.now() + timedelta(days=10))
        self.assertEqual(status, AssignmentSubmission.Status.LATE)

    def test_student_can_submit_assignment(self):
        self.client.login(username="stu1", password="Pass@1234")
        f = SimpleUploadedFile("hw1.txt", b"my homework content")
        response = self.client.post(reverse("assignments:submit_assignment", args=[self.assignment.pk]), {"file": f})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AssignmentSubmission.objects.filter(assignment=self.assignment, student=self.student).exists())

    def test_grading_rejects_marks_over_maximum(self):
        submission = AssignmentSubmission.objects.create(
            assignment=self.assignment, student=self.student,
            file=SimpleUploadedFile("hw1.txt", b"content"), status=AssignmentSubmission.Status.SUBMITTED,
        )
        with self.assertRaises(ValueError):
            grade_submission(submission, Decimal("999"), "too high", self.faculty)

    def test_student_cannot_grade_own_submission_via_api_permission(self):
        # Students are not faculty/admin, so grading view must 403 them.
        submission = AssignmentSubmission.objects.create(
            assignment=self.assignment, student=self.student,
            file=SimpleUploadedFile("hw1.txt", b"content"), status=AssignmentSubmission.Status.SUBMITTED,
        )
        self.client.login(username="stu1", password="Pass@1234")
        response = self.client.get(reverse("assignments:grade_submission", args=[submission.pk]))
        self.assertEqual(response.status_code, 403)


class RiskDetectionTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="Computer Science", code="CS")
        self.sem = Semester.objects.create(name="Semester 1", semester_number=1, academic_year="2025-2026",
                                            start_date="2025-08-01", end_date="2025-12-01")
        self.faculty = User.objects.create_user(username="fac1", password="x", role=User.Role.FACULTY)
        self.student = User.objects.create_user(username="stu1", password="x", role=User.Role.STUDENT)

    def test_student_with_no_data_is_not_flagged(self):
        result = assess_student_risk(self.student)
        self.assertEqual(result["risk_level"], "NONE")

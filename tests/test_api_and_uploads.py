from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.academics.models import Department, Semester, Course
from apps.assignments.models import validate_assignment_file

User = get_user_model()


class APIPermissionTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="Computer Science", code="CS")
        self.sem = Semester.objects.create(name="Semester 1", semester_number=1, academic_year="2025-2026",
                                            start_date="2025-08-01", end_date="2025-12-01")
        self.admin = User.objects.create_user(username="admin1", password="Pass@1234", role=User.Role.ADMIN, is_staff=True)
        self.student = User.objects.create_user(username="stu1", password="Pass@1234", role=User.Role.STUDENT)

    def test_anonymous_cannot_access_api(self):
        response = self.client.get("/api/students/")
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_access_student_admin_api(self):
        self.client.login(username="stu1", password="Pass@1234")
        response = self.client.get("/api/students/")
        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_department_via_api(self):
        self.client.login(username="admin1", password="Pass@1234")
        response = self.client.post("/api/departments/", {"name": "Physics", "code": "PHY", "description": "", "contact_email": ""})
        self.assertEqual(response.status_code, 201)

    def test_student_cannot_create_department_via_api(self):
        self.client.login(username="stu1", password="Pass@1234")
        response = self.client.post("/api/departments/", {"name": "Physics2", "code": "PHY2"})
        self.assertEqual(response.status_code, 403)


class FileValidationTests(TestCase):
    def test_rejects_disallowed_extension(self):
        bad_file = SimpleUploadedFile("virus.exe", b"binary content")
        with self.assertRaises(ValidationError):
            validate_assignment_file(bad_file)

    def test_accepts_allowed_extension(self):
        good_file = SimpleUploadedFile("homework.pdf", b"pdf content")
        try:
            validate_assignment_file(good_file)
        except ValidationError:
            self.fail("validate_assignment_file raised ValidationError for an allowed extension.")

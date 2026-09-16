from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin1", password="Pass@1234", role=User.Role.ADMIN, is_staff=True)
        self.faculty = User.objects.create_user(username="fac1", password="Pass@1234", role=User.Role.FACULTY)
        self.student = User.objects.create_user(username="stu1", password="Pass@1234", role=User.Role.STUDENT)

    def test_login_success(self):
        response = self.client.post(reverse("accounts:login"), {"username": "admin1", "password": "Pass@1234"})
        self.assertEqual(response.status_code, 302)

    def test_login_failure(self):
        response = self.client.post(reverse("accounts:login"), {"username": "admin1", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        self.client.login(username="admin1", password="Pass@1234")
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)

    def test_role_redirect_admin(self):
        self.client.login(username="admin1", password="Pass@1234")
        response = self.client.get(reverse("accounts:role_redirect"))
        self.assertRedirects(response, reverse("accounts:admin_dashboard"))

    def test_role_redirect_faculty(self):
        self.client.login(username="fac1", password="Pass@1234")
        response = self.client.get(reverse("accounts:role_redirect"))
        self.assertRedirects(response, reverse("accounts:faculty_dashboard"))

    def test_role_redirect_student(self):
        self.client.login(username="stu1", password="Pass@1234")
        response = self.client.get(reverse("accounts:role_redirect"))
        self.assertRedirects(response, reverse("accounts:student_dashboard"))

    def test_student_cannot_access_admin_student_list(self):
        self.client.login(username="stu1", password="Pass@1234")
        response = self.client.get(reverse("students:student_list"))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("students:student_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_faculty_cannot_access_admin_only_department_crud(self):
        self.client.login(username="fac1", password="Pass@1234")
        response = self.client.get(reverse("academics:department_list"))
        self.assertEqual(response.status_code, 403)

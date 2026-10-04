from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from students.models import Student

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a student user
        self.student_user = User.objects.create_user(
            email='student@test.com',
            password='testpassword123',
            role=User.RoleChoices.STUDENT
        )
        self.student_profile = Student.objects.create(
            user=self.student_user,
            enrollment_no='STU001'
        )

        # Create a faculty user
        self.faculty_user = User.objects.create_user(
            email='faculty@test.com',
            password='testpassword123',
            role=User.RoleChoices.FACULTY
        )

        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@test.com',
            password='testpassword123',
            role=User.RoleChoices.ADMIN
        )

    def test_successful_login(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'student@test.com',
            'password': 'testpassword123'
        })
        self.assertRedirects(response, reverse('students:dashboard'))

    def test_invalid_login(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'student@test.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], None, 'Please enter a correct email and password. Note that both fields may be case-sensitive.')

    def test_signup_redirects_to_login(self):
        response = self.client.get(reverse('accounts:signup'))
        self.assertRedirects(response, reverse('accounts:login'))

    def test_unauthenticated_access_denied(self):
        response = self.client.get(reverse('students:dashboard'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('students:dashboard')}")

    def test_student_cannot_access_faculty_pages(self):
        self.client.login(username='student@test.com', password='testpassword123')
        response = self.client.get(reverse('faculty:dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_access_admin_pages(self):
        self.client.login(username='student@test.com', password='testpassword123')
        response = self.client.get(reverse('spms_admin:dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_faculty_cannot_access_admin_pages(self):
        self.client.login(username='faculty@test.com', password='testpassword123')
        response = self.client.get(reverse('spms_admin:dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_admin_pages(self):
        self.client.login(username='admin@test.com', password='testpassword123')
        response = self.client.get(reverse('spms_admin:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='student@test.com', password='testpassword123')
        response = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('landing_page'))

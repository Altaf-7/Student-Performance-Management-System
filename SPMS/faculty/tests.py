<<<<<<< HEAD
from django.test import TestCase

# Create your tests here.
=======
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import datetime

from accounts.models import User
from academics.models import Department, Course, CourseBatch, Semester, Subject, SubjectOffering, Lecture
from faculty.models import Faculty
from students.models import Student, StudentCourse, StudentSemester
from assignments.models import Assignment, AssignmentSubmission
from examinations.models import Exam, ExamResult

class FacultyModuleTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # 1. Users
        self.faculty_user1 = User.objects.create_user(email='faculty1@example.com', password='password123', role=User.RoleChoices.FACULTY)
        self.faculty_user2 = User.objects.create_user(email='faculty2@example.com', password='password123', role=User.RoleChoices.FACULTY)
        self.student_user = User.objects.create_user(email='student@example.com', password='password123', role=User.RoleChoices.STUDENT)
        self.admin_user = User.objects.create_user(email='admin@example.com', password='password123', role=User.RoleChoices.ADMIN)
        
        # 2. Profiles
        self.dept = Department.objects.create(name='Computer Science', code='CS')
        self.faculty1 = Faculty.objects.create(user=self.faculty_user1, department=self.dept, designation='Professor')
        self.faculty2 = Faculty.objects.create(user=self.faculty_user2, department=self.dept, designation='Assistant Professor')
        self.student = Student.objects.create(user=self.student_user, enrollment_no='MCA001')
        
        # 3. Academics setup
        self.course = Course.objects.create(name='MCA', code='MCA', department=self.dept, duration_years=2)
        self.batch = CourseBatch.objects.create(course=self.course, academic_year='2023-2025')
        self.semester = Semester.objects.create(course_batch=self.batch, semester_number=1)
        self.subject = Subject.objects.create(name='DBMS', code='CS101')
        
        # 4. Student Enrollment
        StudentSemester.objects.create(student=self.student, semester=self.semester, academic_year='2023-2024')
        
        # 5. Offerings
        # Faculty 1 owns offering 1
        self.offering1 = SubjectOffering.objects.create(subject=self.subject, semester=self.semester, faculty=self.faculty1, credits=4)
        
        # Faculty 2 owns offering 2 (different subject)
        self.subject2 = Subject.objects.create(name='OS', code='CS102')
        self.offering2 = SubjectOffering.objects.create(subject=self.subject2, semester=self.semester, faculty=self.faculty2, credits=4)

        # 6. Sample Objects
        self.lecture1 = Lecture.objects.create(
            offering=self.offering1, 
            date=datetime.date.today(), 
            start_time=datetime.time(10, 0), 
            end_time=datetime.time(11, 0)
        )
        self.assignment1 = Assignment.objects.create(
            offering=self.offering1,
            title='Assig 1',
            maximum_marks=Decimal('10.00'),
            due_datetime=timezone.now() + datetime.timedelta(days=7)
        )
        self.exam1 = Exam.objects.create(
            offering=self.offering1,
            exam_term=Exam.ExamTerm.MID_SEM,
            exam_category=Exam.ExamCategory.WRITTEN,
            exam_date=datetime.date.today(),
            total_marks=Decimal('50.00')
        )

    # --- Authorization Tests ---
    
    def test_unauthenticated_user_access(self):
        """Unauthenticated user cannot access faculty pages."""
        response = self.client.get(reverse('faculty:dashboard'))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/login/?next={reverse('faculty:dashboard')}")

    def test_student_cannot_access_faculty(self):
        """Student cannot access faculty pages."""
        self.client.login(email='student@example.com', password='password123')
        response = self.client.get(reverse('faculty:dashboard'))
        self.assertEqual(response.status_code, 403) # PermissionDenied

    def test_faculty_can_access_own_pages(self):
        """Faculty can access their own pages."""
        self.client.login(email='faculty1@example.com', password='password123')
        response = self.client.get(reverse('faculty:dashboard'))
        self.assertEqual(response.status_code, 200)

    # --- Object-Level Security Tests ---
    
    def test_faculty_cannot_access_other_faculty_offering(self):
        """Faculty cannot access another faculty's offering detail."""
        self.client.login(email='faculty2@example.com', password='password123') # Faculty 2 logs in
        # Tries to access Faculty 1's offering
        response = self.client.get(reverse('faculty:subject_detail', args=[self.offering1.pk]))
        self.assertEqual(response.status_code, 404) # get_object_or_404 should fail due to queryset filtering

    def test_faculty_cannot_modify_other_faculty_lecture(self):
        self.client.login(email='faculty2@example.com', password='password123')
        response = self.client.get(reverse('faculty:lecture_detail', args=[self.lecture1.pk]))
        self.assertEqual(response.status_code, 404)
        
        response = self.client.post(reverse('faculty:lecture_delete', args=[self.lecture1.pk]))
        self.assertEqual(response.status_code, 404)

    def test_faculty_cannot_modify_other_faculty_assignment(self):
        self.client.login(email='faculty2@example.com', password='password123')
        response = self.client.get(reverse('faculty:assignment_detail', args=[self.assignment1.pk]))
        self.assertEqual(response.status_code, 404)

    def test_faculty_cannot_modify_other_faculty_exam(self):
        self.client.login(email='faculty2@example.com', password='password123')
        response = self.client.get(reverse('faculty:exam_detail', args=[self.exam1.pk]))
        self.assertEqual(response.status_code, 404)

    # --- Lecture Tests ---
    
    def test_create_lecture_own_offering(self):
        self.client.login(email='faculty1@example.com', password='password123')
        data = {
            'offering': self.offering1.pk,
            'date': (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
            'start_time': '12:00',
            'end_time': '13:00'
        }
        response = self.client.post(reverse('faculty:lecture_create'), data)
        self.assertRedirects(response, reverse('faculty:lectures'))
        self.assertEqual(Lecture.objects.filter(offering=self.offering1).count(), 2)

    def test_cannot_create_lecture_for_other_faculty(self):
        self.client.login(email='faculty1@example.com', password='password123')
        data = {
            'offering': self.offering2.pk, # Belongs to Faculty 2
            'date': (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
            'start_time': '12:00',
            'end_time': '13:00'
        }
        response = self.client.post(reverse('faculty:lecture_create'), data)
        # Form should be invalid because offering2 is not in the restricted queryset
        self.assertEqual(response.status_code, 200) 
        self.assertTrue('offering' in response.context['form'].errors)

    # --- Attendance Tests ---
    
    def test_bulk_attendance_entry(self):
        self.client.login(email='faculty1@example.com', password='password123')
        url = reverse('faculty:attendance_entry', args=[self.lecture1.pk])
        
        # Provide attendance for self.student
        data = {
            f'status_{self.student.id}': 'present'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('faculty:lecture_detail', args=[self.lecture1.pk]))
        
        # Verify in DB
        from attendance.models import Attendance
        att = Attendance.objects.get(lecture=self.lecture1, student=self.student)
        self.assertEqual(att.status, 'present')

    # --- Assignment Grading Tests ---
    
    def test_grade_valid_submission(self):
        self.client.login(email='faculty1@example.com', password='password123')
        submission = AssignmentSubmission.objects.create(
            assignment=self.assignment1,
            student=self.student,
            status=AssignmentSubmission.StatusChoices.SUBMITTED
        )
        url = reverse('faculty:submission_detail', args=[submission.pk])
        data = {
            'marks_awarded': '8.50',
            'feedback': 'Good job'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, url) # Success url points back to detail
        
        submission.refresh_from_db()
        self.assertEqual(submission.marks_awarded, Decimal('8.50'))
        self.assertIsNotNone(submission.graded_at)

    def test_marks_above_maximum_rejected(self):
        self.client.login(email='faculty1@example.com', password='password123')
        submission = AssignmentSubmission.objects.create(
            assignment=self.assignment1,
            student=self.student,
            status=AssignmentSubmission.StatusChoices.SUBMITTED
        )
        url = reverse('faculty:submission_detail', args=[submission.pk])
        # Maximum is 10.00
        data = {
            'marks_awarded': '11.00', 
            'feedback': ''
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('__all__' in response.context['form'].errors)

    # --- Exam Tests ---
    def test_bulk_exam_results(self):
        self.client.login(email='faculty1@example.com', password='password123')
        url = reverse('faculty:exam_results', args=[self.exam1.pk])
        
        data = {
            f'attendance_{self.student.id}': 'present',
            f'marks_{self.student.id}': '45.50'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('faculty:exam_detail', args=[self.exam1.pk]))
        
        # Verify
        res = ExamResult.objects.get(exam=self.exam1, student=self.student)
        self.assertEqual(res.marks_obtained, Decimal('45.50'))
        self.assertEqual(res.attendance_status, 'present')
>>>>>>> origin/main

from django.test import TestCase, Client
from django.urls import reverse
import datetime

from accounts.models import User
from academics.models import Department, Course, CourseBatch, Semester, Subject, SubjectOffering
from faculty.models import Faculty
from students.models import Student, StudentSemester
from assignments.models import Assignment, AssignmentSubmission
from examinations.models import Exam, ExamResult

class StudentModuleTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Users
        self.student_user1 = User.objects.create_user(email='student1@example.com', password='password123', role=User.RoleChoices.STUDENT)
        self.student_user2 = User.objects.create_user(email='student2@example.com', password='password123', role=User.RoleChoices.STUDENT)
        self.faculty_user = User.objects.create_user(email='faculty@example.com', password='password123', role=User.RoleChoices.FACULTY)
        
        # Profiles
        self.student1 = Student.objects.create(user=self.student_user1, enrollment_no='STU001')
        self.student2 = Student.objects.create(user=self.student_user2, enrollment_no='STU002')
        self.dept = Department.objects.create(name='CS', code='CS')
        self.faculty = Faculty.objects.create(user=self.faculty_user, department=self.dept)
        
        # Academics
        self.course = Course.objects.create(name='B.Tech', code='BT', department=self.dept, duration_years=4)
        self.batch = CourseBatch.objects.create(course=self.course, academic_year='2023-2027')
        self.semester = Semester.objects.create(course_batch=self.batch, semester_number=1)
        self.subject = Subject.objects.create(name='Maths', code='MA101')
        self.offering = SubjectOffering.objects.create(subject=self.subject, semester=self.semester, faculty=self.faculty, credits=4)
        
        # Enroll Student 1 in Semester 1
        StudentSemester.objects.create(student=self.student1, semester=self.semester, academic_year='2023-2024')
        # Student 2 is NOT enrolled in Semester 1
        
        # Assignment
        self.assignment = Assignment.objects.create(
            offering=self.offering, 
            title='HW1', 
            maximum_marks=10,
            due_datetime=timezone.now() + datetime.timedelta(days=2)
        )
        
        # Student 1 Submission
        self.submission1 = AssignmentSubmission.objects.create(
            assignment=self.assignment,
            student=self.student1
        )
        
        # Exam
        self.exam = Exam.objects.create(
            offering=self.offering,
            exam_category='mid_term',
            exam_term='theory',
            exam_date=datetime.date.today(),
            maximum_marks=50,
            status='published'
        )
        
        # Student 1 Result
        self.result1 = ExamResult.objects.create(
            exam=self.exam,
            student=self.student1,
            marks_obtained=40
        )
        
    def test_unauthenticated_user_cannot_access(self):
        response = self.client.get(reverse('students:dashboard'))
        self.assertEqual(response.status_code, 302)
        
    def test_faculty_cannot_access_student_pages(self):
        self.client.login(username='faculty@example.com', password='password123')
        response = self.client.get(reverse('students:dashboard'))
        self.assertEqual(response.status_code, 403)
        
    def test_student1_can_access_own_assignment(self):
        self.client.login(username='student1@example.com', password='password123')
        response = self.client.get(reverse('students:assignment_detail', args=[self.assignment.id]))
        self.assertEqual(response.status_code, 200)
        
    def test_student2_cannot_access_unrelated_assignment(self):
        # Student 2 is not enrolled in the semester offering this assignment
        self.client.login(username='student2@example.com', password='password123')
        response = self.client.get(reverse('students:assignment_detail', args=[self.assignment.id]))
        self.assertEqual(response.status_code, 403)
        
    def test_student2_cannot_submit_for_student1(self):
        self.client.login(username='student2@example.com', password='password123')
        response = self.client.post(reverse('students:assignment_submit', args=[self.assignment.id]), {
            'text_submission': 'Hacked'
        })
        self.assertEqual(response.status_code, 403)
        
    def test_student2_cannot_download_student1_submission(self):
        self.client.login(username='student2@example.com', password='password123')
        response = self.client.get(reverse('students:download_submission', args=[self.submission1.id]))
        self.assertEqual(response.status_code, 404)  # get_object_or_404 filters by student=request.user.student_profile
        
    def test_student2_cannot_view_student1_exam_result(self):
        self.client.login(username='student2@example.com', password='password123')
        response = self.client.get(reverse('students:exam_detail', args=[self.exam.id]))
        self.assertEqual(response.status_code, 403)

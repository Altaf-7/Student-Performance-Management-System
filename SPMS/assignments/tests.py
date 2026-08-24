from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime

from accounts.models import User
from academics.models import Department, Course, CourseBatch, Semester, Subject, SubjectOffering
from faculty.models import Faculty
from students.models import Student, StudentSemester
from assignments.models import Assignment, AssignmentSubmission

class AssignmentModelTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='CS', code='CS')
        self.course = Course.objects.create(name='B.Tech', code='BT', department=self.dept, duration_years=4)
        self.batch = CourseBatch.objects.create(course=self.course, academic_year='2023-2027')
        self.semester = Semester.objects.create(course_batch=self.batch, semester_number=1)
        self.subject = Subject.objects.create(name='Python', code='PY101')
        
        self.faculty_user = User.objects.create_user(email='fac@test.com', password='password', role=User.RoleChoices.FACULTY)
        self.faculty = Faculty.objects.create(user=self.faculty_user, department=self.dept)
        
        self.offering = SubjectOffering.objects.create(subject=self.subject, semester=self.semester, faculty=self.faculty, credits=4)
        
        self.student_user = User.objects.create_user(email='stu@test.com', password='password', role=User.RoleChoices.STUDENT)
        self.student = Student.objects.create(user=self.student_user, enrollment_no='STU001')
        StudentSemester.objects.create(student=self.student, semester=self.semester, academic_year='2023-2024')
        
    def test_assignment_due_date_must_be_future(self):
        # Using a past date should raise ValidationError
        past_date = timezone.now() - datetime.timedelta(days=1)
        assignment = Assignment(
            offering=self.offering,
            title='Test Assignment',
            maximum_marks=10,
            due_datetime=past_date
        )
        with self.assertRaises(ValidationError):
            assignment.clean()
            
    def test_submission_marks_cannot_exceed_maximum(self):
        assignment = Assignment.objects.create(
            offering=self.offering,
            title='Test Assignment',
            maximum_marks=10,
            due_datetime=timezone.now() + datetime.timedelta(days=1)
        )
        
        submission = AssignmentSubmission(
            assignment=assignment,
            student=self.student,
            marks_awarded=15  # Greater than maximum_marks
        )
        with self.assertRaises(ValidationError):
            submission.clean()

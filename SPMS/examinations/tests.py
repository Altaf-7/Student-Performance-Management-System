from django.test import TestCase
<<<<<<< HEAD

# Create your tests here.
=======
from django.core.exceptions import ValidationError
import datetime

from accounts.models import User
from academics.models import Department, Course, CourseBatch, Semester, Subject, SubjectOffering
from faculty.models import Faculty
from students.models import Student, StudentSemester
from examinations.models import Exam, ExamResult

class ExaminationsModelTests(TestCase):
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
        
        self.exam = Exam.objects.create(
            offering=self.offering,
            exam_category='mid_term',
            exam_term='theory',
            exam_date=datetime.date.today(),
            maximum_marks=50
        )
        
    def test_exam_result_marks_cannot_exceed_maximum(self):
        result = ExamResult(
            exam=self.exam,
            student=self.student,
            marks_obtained=60  # Greater than 50
        )
        with self.assertRaises(ValidationError):
            result.clean()
            
    def test_exam_result_marks_cannot_be_negative(self):
        result = ExamResult(
            exam=self.exam,
            student=self.student,
            marks_obtained=-5
        )
        with self.assertRaises(ValidationError):
            result.clean()
>>>>>>> origin/main

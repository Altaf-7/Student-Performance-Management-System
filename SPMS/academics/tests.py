from django.test import TestCase
from django.core.exceptions import ValidationError
from academics.models import Department, Course, CourseBatch, Semester, Subject, SubjectOffering
from faculty.models import Faculty
from accounts.models import User

class AcademicsModelTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='Computer Science', code='CS')
        self.course = Course.objects.create(name='B.Tech', code='BT', department=self.dept, duration_years=4)
        self.batch = CourseBatch.objects.create(course=self.course, academic_year='2023-2027')
        self.semester = Semester.objects.create(course_batch=self.batch, semester_number=1)
        self.subject = Subject.objects.create(name='Mathematics', code='MA101')
        
        self.faculty_user = User.objects.create_user(email='faculty@test.com', password='password123', role=User.RoleChoices.FACULTY)
        self.faculty = Faculty.objects.create(user=self.faculty_user, department=self.dept)

    def test_department_str(self):
        self.assertEqual(str(self.dept), 'Computer Science (CS)')

    def test_subject_offering_unique_constraint(self):
        # Create first offering
        SubjectOffering.objects.create(subject=self.subject, semester=self.semester, faculty=self.faculty, credits=4)
        
        # Creating a duplicate offering should raise ValidationError/IntegrityError
        duplicate_offering = SubjectOffering(subject=self.subject, semester=self.semester, faculty=self.faculty, credits=4)
        with self.assertRaises(Exception):
            duplicate_offering.save()

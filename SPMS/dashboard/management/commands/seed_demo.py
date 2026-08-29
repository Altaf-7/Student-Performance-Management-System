import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from academics.models import Department, Course, CourseBatch, Semester, Subject, SubjectOffering, Lecture
from faculty.models import FacultyProfile
from students.models import StudentProfile, StudentCourse, StudentSemester, SemesterResult
from assignments.models import Assignment, AssignmentSubmission
from examinations.models import Exam, ExamResult
from attendance.models import Attendance


class Command(BaseCommand):
    help = "Seeds the database with demo data: an admin, faculty, students, courses, subjects, and sample activity."

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        admin, _ = User.objects.get_or_create(
            username='admin', defaults={'email': 'admin@spms.edu', 'role': User.Role.ADMIN,
                                         'is_staff': True, 'is_superuser': True,
                                         'first_name': 'System', 'last_name': 'Admin'}
        )
        admin.set_password('admin12345')
        admin.save()

        dept, _ = Department.objects.get_or_create(code='CS', defaults={'name': 'Computer Science'})
        course, _ = Course.objects.get_or_create(
            code='BCA', defaults={'department': dept, 'name': 'Bachelor of Computer Applications',
                                   'duration_years': 3, 'total_semesters': 6}
        )
        batch, _ = CourseBatch.objects.get_or_create(
            course=course, start_year=2023, defaults={'name': 'BCA 2023-2026', 'end_year': 2026}
        )
        sem3, _ = Semester.objects.get_or_create(
            course_batch=batch, number=3, defaults={'name': 'Semester 3', 'is_active': True}
        )

        fac_user, _ = User.objects.get_or_create(
            username='faculty1', defaults={'email': 'faculty1@spms.edu', 'role': User.Role.FACULTY,
                                            'first_name': 'Anita', 'last_name': 'Sharma'}
        )
        fac_user.set_password('faculty12345')
        fac_user.save()
        faculty_profile, _ = FacultyProfile.objects.get_or_create(
            user=fac_user, defaults={'employee_id': 'EMP001', 'department': dept, 'designation': 'Assistant Professor'}
        )

        subject, _ = Subject.objects.get_or_create(code='CS301', defaults={'name': 'Database Management Systems', 'credits': 4})
        offering, _ = SubjectOffering.objects.get_or_create(
            subject=subject, semester=sem3, defaults={'faculty': faculty_profile, 'is_active': True}
        )

        students_data = [
            ('student1', 'Rahul', 'Verma', 'BCA23001'),
            ('student2', 'Priya', 'Nair', 'BCA23002'),
            ('student3', 'Karan', 'Mehta', 'BCA23003'),
        ]
        student_profiles = []
        for username, first, last, roll in students_data:
            u, _ = User.objects.get_or_create(
                username=username, defaults={'email': f'{username}@spms.edu', 'role': User.Role.STUDENT,
                                              'first_name': first, 'last_name': last}
            )
            u.set_password('student12345')
            u.save()
            sp, _ = StudentProfile.objects.get_or_create(user=u, defaults={'roll_number': roll})
            sc, _ = StudentCourse.objects.get_or_create(
                student=sp, course_batch=batch, admission_year=2023,
                defaults={'status': StudentCourse.Status.PURSUING}
            )
            StudentSemester.objects.get_or_create(student=sp, student_course=sc, semester=sem3)
            student_profiles.append(sp)

        # A couple of lectures with attendance
        today = timezone.now().date()
        for i in range(3):
            lecture, _ = Lecture.objects.get_or_create(
                subject_offering=offering, date=today - datetime.timedelta(days=7 * (3 - i)),
                defaults={'topic': f'DBMS Topic {i + 1}', 'created_by': fac_user}
            )
            for idx, sp in enumerate(student_profiles):
                status = Attendance.Status.PRESENT if (idx + i) % 3 != 0 else Attendance.Status.ABSENT
                Attendance.objects.get_or_create(lecture=lecture, student=sp, defaults={'status': status, 'marked_by': fac_user})

        # Sample assignment
        assignment, _ = Assignment.objects.get_or_create(
            subject_offering=offering, title='ER Diagram Assignment',
            defaults={
                'description': 'Design an ER diagram for a library management system.',
                'instructions': 'Submit as a single PDF.',
                'max_marks': 20,
                'due_date': timezone.now() + datetime.timedelta(days=5),
                'created_by': fac_user,
            }
        )
        AssignmentSubmission.objects.get_or_create(
            assignment=assignment, student=student_profiles[0],
            defaults={'remarks': 'Completed as instructed.', 'marks': Decimal('18'), 'feedback': 'Well done.', 'graded_by': fac_user}
        )

        # Sample exam + results
        exam, _ = Exam.objects.get_or_create(
            subject_offering=offering, term=Exam.Term.MID_SEM, category=Exam.Category.WRITTEN,
            defaults={'name': 'Mid-Sem Written', 'exam_date': today - datetime.timedelta(days=10),
                      'max_marks': 50, 'created_by': fac_user}
        )
        for idx, sp in enumerate(student_profiles):
            ExamResult.objects.get_or_create(
                exam=exam, student=sp, attempt_number=1,
                defaults={'marks_obtained': Decimal(35 + idx * 5), 'entered_by': fac_user}
            )

        self.stdout.write(self.style.SUCCESS(
            "Demo data ready.\n"
            "  Admin:    admin / admin12345\n"
            "  Faculty:  faculty1 / faculty12345\n"
            "  Students: student1 / student2 / student3, password: student12345"
        ))

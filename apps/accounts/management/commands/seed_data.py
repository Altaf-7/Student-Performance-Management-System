"""
python manage.py seed_data

Creates the Super Admin account, demo faculty/student accounts, and a full
set of internally-consistent realistic data (departments, semesters,
courses, enrollments, attendance, assignments, submissions, examinations,
results, announcements, notifications).

Safe to re-run: every object is created with get_or_create / update_or_create
keyed on a natural unique field, so re-running this command does not create
duplicates. The Super Admin account is a local DEVELOPMENT/DEMO credential
only - see README for details. The password is intentionally not printed
to stdout in this command's normal output.
"""
import random
from datetime import date, timedelta, datetime, time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.academics.models import Department, Semester, Course, Enrollment, GradeScale
from apps.students.models import StudentProfile
from apps.faculty.models import FacultyProfile
from apps.attendance.models import Attendance
from apps.assignments.models import Assignment, AssignmentSubmission
from apps.examinations.models import Examination, ExamResult
from apps.notifications.models import Announcement, Notification

User = get_user_model()
fake = None  # initialised lazily in handle() so `manage.py check` never needs Faker


DEPARTMENTS = [
    ("Computer Science", "CS"), ("Information Technology", "IT"), ("Data Science", "DS"),
    ("Artificial Intelligence", "AI"), ("Electronics", "EC"), ("Mechanical Engineering", "ME"),
    ("Electrical Engineering", "EE"), ("Mathematics", "MA"),
]

COURSES = [
    ("CS101", "Data Structures", "CS", 4), ("CS102", "Database Management Systems", "CS", 4),
    ("CS103", "Operating Systems", "CS", 3), ("CS104", "Computer Networks", "CS", 3),
    ("IT101", "Web Development", "IT", 3), ("AI101", "Machine Learning", "AI", 4),
    ("CS105", "Software Engineering", "CS", 3), ("IT102", "Cloud Computing", "IT", 3),
    ("AI102", "Artificial Intelligence", "AI", 4), ("CS106", "Computer Architecture", "CS", 3),
    ("DS101", "Data Analytics", "DS", 3), ("IT103", "Cyber Security", "IT", 3),
    ("CS107", "Object Oriented Programming", "CS", 3), ("CS108", "Algorithms", "CS", 4),
    ("MA101", "Statistics", "MA", 3),
]

GRADE_BANDS = [
    ("A+", 90, 100, 10.0), ("A", 80, 89.99, 9.0), ("B+", 70, 79.99, 8.0),
    ("B", 60, 69.99, 7.0), ("C", 50, 59.99, 6.0), ("D", 40, 49.99, 5.0), ("F", 0, 39.99, 0.0),
]

# Performance archetypes used to make seed data realistic and internally
# consistent (see project spec section 41).
PROFILES = {
    "excellent": {"attendance": (0.90, 0.99), "marks": (85, 98), "submit_rate": 0.98},
    "average": {"attendance": (0.78, 0.90), "marks": (60, 80), "submit_rate": 0.85},
    "weak": {"attendance": (0.65, 0.80), "marks": (42, 60), "submit_rate": 0.65},
    "at_risk": {"attendance": (0.35, 0.65), "marks": (15, 45), "submit_rate": 0.35},
}


class Command(BaseCommand):
    help = "Seeds the database with the Super Admin account and realistic demo data."

    def handle(self, *args, **options):
        global fake
        from faker import Faker
        fake = Faker()
        Faker.seed(42)
        random.seed(42)

        with transaction.atomic():
            self.create_superuser()
            self.create_grade_scale()
            departments = self.create_departments()
            semesters = self.create_semesters()
            faculty_users = self.create_faculty(departments)
            courses = self.create_courses(departments, semesters, faculty_users)
            students = self.create_students(departments, semesters)
            enrollments = self.create_enrollments(students, courses, semesters)
            self.create_attendance(enrollments)
            self.create_assignments_and_submissions(courses, enrollments)
            self.create_examinations_and_results(courses, semesters, enrollments, faculty_users)
            self.create_announcements(departments, semesters, faculty_users)
            self.create_notifications(students)

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
        self.stdout.write("Demo credentials are documented in README.md (DEVELOPMENT/DEMO ONLY).")

    # ------------------------------------------------------------------
    def create_superuser(self):
        if User.objects.filter(username="Kavya").exists():
            self.stdout.write("Super Admin 'Kavya' already exists - skipping.")
            return
        User.objects.create_superuser(
            username="Kavya", email="kavya@spms.local", password="Kavya 2004",
            first_name="Kavya", last_name="Admin", role=User.Role.SUPER_ADMIN,
        )
        self.stdout.write("Created Super Admin account.")

    def create_grade_scale(self):
        for grade, lo, hi, gp in GRADE_BANDS:
            GradeScale.objects.update_or_create(
                grade=grade, defaults={"min_percentage": lo, "max_percentage": hi, "grade_point": gp}
            )

    def create_departments(self):
        departments = {}
        for name, code in DEPARTMENTS:
            dept, _ = Department.objects.get_or_create(
                code=code, defaults={"name": name, "description": f"Department of {name}", "contact_email": f"{code.lower()}@spms.local"}
            )
            departments[code] = dept
        return departments

    def create_semesters(self):
        semesters = []
        year = "2025-2026"
        start = date(2025, 8, 1)
        for i in range(1, 7):
            sem_start = start + timedelta(days=(i - 1) * 60)
            sem_end = sem_start + timedelta(days=55)
            sem, _ = Semester.objects.get_or_create(
                semester_number=i, academic_year=year,
                defaults={"name": f"Semester {i}", "start_date": sem_start, "end_date": sem_end, "is_active": i == 3},
            )
            semesters.append(sem)
        return semesters

    # ------------------------------------------------------------------
    def create_faculty(self, departments):
        designations = list(FacultyProfile.Designation.values)
        dept_list = list(departments.values())
        faculty_users = []
        for i in range(1, 11):
            username = f"faculty{i}"
            password = "Faculty@2026"
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
            else:
                first, last = fake.first_name(), fake.last_name()
                user = User.objects.create_user(
                    username=username, password=password, first_name=first, last_name=last,
                    email=f"{username}@spms.local", role=User.Role.FACULTY, phone=fake.msisdn()[:15],
                )
            FacultyProfile.objects.get_or_create(
                user=user, defaults={
                    "faculty_id": f"FAC-{i:03d}", "department": random.choice(dept_list),
                    "designation": random.choice(designations),
                },
            )
            faculty_users.append(user)

        # Assign a head of department for each department
        for dept, fac in zip(departments.values(), faculty_users):
            if not dept.head_of_department:
                dept.head_of_department = fac
                dept.save()
        return faculty_users

    def create_courses(self, departments, semesters, faculty_users):
        courses = []
        for i, (code, name, dept_code, credits) in enumerate(COURSES):
            semester = semesters[i % len(semesters)]
            faculty = faculty_users[i % len(faculty_users)]
            course, _ = Course.objects.get_or_create(
                course_code=code, defaults={
                    "course_name": name, "description": f"{name} course covering core concepts and applications.",
                    "credits": credits, "department": departments[dept_code], "semester": semester,
                    "faculty": faculty, "status": Course.Status.ACTIVE,
                },
            )
            courses.append(course)
        return courses

    # ------------------------------------------------------------------
    def create_students(self, departments, semesters):
        dept_list = list(departments.values())
        archetype_cycle = (["excellent"] * 3 + ["average"] * 4 + ["weak"] * 2 + ["at_risk"] * 1)
        students = []
        for i in range(1, 51):
            username = f"student{i}"
            password = "Student@2026"
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
            else:
                first, last = fake.first_name(), fake.last_name()
                user = User.objects.create_user(
                    username=username, password=password, first_name=first, last_name=last,
                    email=f"{username}@spms.local", role=User.Role.STUDENT, phone=fake.msisdn()[:15],
                )
            semester = semesters[2] if i % 3 else random.choice(semesters[:4])
            profile, _ = StudentProfile.objects.get_or_create(
                user=user, defaults={
                    "student_id": f"STU-2026-{i:03d}", "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=24),
                    "gender": random.choice(["M", "F", "O"]), "address": fake.address().replace("\n", ", "),
                    "department": random.choice(dept_list), "semester": semester,
                    "enrollment_year": random.choice([2022, 2023, 2024, 2025]),
                    "academic_status": StudentProfile.AcademicStatus.ACTIVE,
                },
            )
            archetype = archetype_cycle[(i - 1) % len(archetype_cycle)]
            students.append({"user": user, "profile": profile, "archetype": archetype})
        return students

    def create_enrollments(self, students, courses, semesters):
        enrollments = []
        year = "2025-2026"
        for s in students:
            dept_courses = [c for c in courses if c.department == s["profile"].department]
            pool = dept_courses if len(dept_courses) >= 4 else courses
            chosen = random.sample(pool, k=min(5, len(pool)))
            for course in chosen:
                enrollment, _ = Enrollment.objects.get_or_create(
                    student=s["user"], course=course, academic_year=year,
                    defaults={"semester": course.semester, "status": Enrollment.Status.ACTIVE},
                )
                enrollments.append({"enrollment": enrollment, "student": s})
        return enrollments

    # ------------------------------------------------------------------
    def create_attendance(self, enrollments):
        today = timezone.now().date()
        session_dates = [today - timedelta(days=d) for d in range(1, 61) if (today - timedelta(days=d)).weekday() < 5][:30]
        bulk = []
        existing = set(Attendance.objects.values_list("student_id", "course_id", "date"))
        for item in enrollments:
            enrollment = item["enrollment"]
            archetype = item["student"]["archetype"]
            lo, hi = PROFILES[archetype]["attendance"]
            present_rate = random.uniform(lo, hi)
            marker = enrollment.course.faculty
            for d in session_dates:
                key = (enrollment.student_id, enrollment.course_id, d)
                if key in existing:
                    continue
                roll = random.random()
                if roll < present_rate:
                    status = Attendance.Status.PRESENT
                elif roll < present_rate + 0.07:
                    status = Attendance.Status.LATE
                else:
                    status = Attendance.Status.ABSENT
                bulk.append(Attendance(
                    student_id=enrollment.student_id, course_id=enrollment.course_id, date=d,
                    status=status, marked_by=marker,
                ))
                existing.add(key)
        Attendance.objects.bulk_create(bulk, batch_size=500, ignore_conflicts=True)
        self.stdout.write(f"Created {len(bulk)} attendance records.")

    def create_assignments_and_submissions(self, courses, enrollments):
        by_course = {}
        for item in enrollments:
            by_course.setdefault(item["enrollment"].course_id, []).append(item)

        now = timezone.now()
        assignments_created = 0
        submissions_created = 0
        for course in courses:
            faculty = course.faculty
            if not faculty:
                continue
            for j in range(1, 3):
                due = now - timedelta(days=20 - j * 15)
                assignment, created = Assignment.objects.get_or_create(
                    title=f"{course.course_code} Assignment {j}", course=course,
                    defaults={
                        "description": f"Assignment {j} for {course.course_name}. Complete and upload your work.",
                        "due_date": due, "maximum_marks": 20, "created_by": faculty,
                    },
                )
                if created:
                    assignments_created += 1
                for item in by_course.get(course.id, []):
                    student = item["student"]
                    archetype = student["archetype"]
                    if random.random() > PROFILES[archetype]["submit_rate"]:
                        continue
                    if AssignmentSubmission.objects.filter(assignment=assignment, student=student["user"]).exists():
                        continue
                    lo, hi = PROFILES[archetype]["marks"]
                    pct = random.uniform(lo, hi)
                    from decimal import Decimal
                    marks = Decimal("%.1f" % ((pct / 100) * float(assignment.maximum_marks)))
                    submitted_at = due - timedelta(hours=random.randint(1, 72))
                    status = AssignmentSubmission.Status.GRADED
                    from django.core.files.base import ContentFile
                    submission = AssignmentSubmission(
                        assignment=assignment, student=student["user"],
                        status=status, marks_obtained=marks, feedback="Good effort. Keep it up." if pct > 60 else "Needs improvement - please review the core concepts.",
                        graded_by=faculty, graded_at=submitted_at + timedelta(days=2),
                    )
                    file_content = (
                        f"Submission by {student['user'].get_full_name()} for {assignment.title}.\n"
                        f"Course: {course.course_code}\nSubmitted (seed data).\n"
                    ).encode()
                    submission.file.save(
                        f"{student['user'].username}_{assignment.id}.txt", ContentFile(file_content), save=False
                    )
                    submission.save()
                    AssignmentSubmission.objects.filter(pk=submission.pk).update(submitted_at=submitted_at)
                    submissions_created += 1
        self.stdout.write(f"Created {assignments_created} assignments and {submissions_created} submissions.")

    def create_examinations_and_results(self, courses, semesters, enrollments, faculty_users):
        by_course = {}
        for item in enrollments:
            by_course.setdefault(item["enrollment"].course_id, []).append(item)

        exams_created = 0
        results_created = 0
        for course in courses:
            faculty = course.faculty or faculty_users[0]
            for exam_type, offset, weight in [
                (Examination.ExamType.MIDTERM, 30, 0.4),
                (Examination.ExamType.END_TERM, 5, 0.6),
            ]:
                exam_date = timezone.now().date() - timedelta(days=offset)
                exam, created = Examination.objects.get_or_create(
                    name=f"{course.course_code} {exam_type.title()}", course=course, exam_type=exam_type,
                    defaults={
                        "semester": course.semester, "academic_year": "2025-2026", "exam_date": exam_date,
                        "maximum_marks": 100, "description": f"{exam_type.title()} examination for {course.course_name}.",
                        "is_published": True, "created_by": faculty,
                    },
                )
                if created:
                    exams_created += 1
                for item in by_course.get(course.id, []):
                    student = item["student"]
                    if ExamResult.objects.filter(student=student["user"], examination=exam).exists():
                        continue
                    lo, hi = PROFILES[student["archetype"]]["marks"]
                    pct = max(0, min(100, random.uniform(lo, hi) + random.uniform(-5, 5)))
                    from decimal import Decimal
                    obtained = Decimal("%.1f" % pct)
                    result = ExamResult(
                        student=student["user"], examination=exam, course=course, maximum_marks=100,
                        obtained_marks=obtained, remarks="", entered_by=faculty,
                    )
                    result.save()
                    results_created += 1
        self.stdout.write(f"Created {exams_created} examinations and {results_created} results.")

    # ------------------------------------------------------------------
    def create_announcements(self, departments, semesters, faculty_users):
        admin = User.objects.filter(role__in=[User.Role.SUPER_ADMIN, User.Role.ADMIN]).first()
        author = admin or faculty_users[0]
        items = [
            ("Welcome to Semester 2025-2026", "Classes begin Monday. Please check your course enrollments.", Announcement.Priority.NORMAL, Announcement.Audience.ALL_STUDENTS, None, None),
            ("Mid-term Examination Schedule Released", "Check the examinations page for your mid-term dates.", Announcement.Priority.HIGH, Announcement.Audience.ALL_STUDENTS, None, None),
            ("Faculty Meeting - Curriculum Review", "All faculty are requested to attend the curriculum review meeting.", Announcement.Priority.NORMAL, Announcement.Audience.FACULTY, None, None),
            ("Computer Science Department Update", "New lab equipment has been installed in Lab 3.", Announcement.Priority.LOW, Announcement.Audience.DEPARTMENT, departments.get("CS"), None),
        ]
        for title, desc, priority, audience, dept, sem in items:
            Announcement.objects.get_or_create(
                title=title, defaults={
                    "description": desc, "author": author, "priority": priority,
                    "target_audience": audience, "department": dept, "semester": sem,
                },
            )

    def create_notifications(self, students):
        created = 0
        for s in students[:15]:
            _, was_created = Notification.objects.get_or_create(
                recipient=s["user"], kind=Notification.Kind.ANNOUNCEMENT, title="Welcome to SPMS",
                defaults={"message": "Your account is set up. Explore your dashboard to get started.", "is_read": False},
            )
            if was_created:
                created += 1
            if s["archetype"] in ("weak", "at_risk"):
                _, was_created = Notification.objects.get_or_create(
                    recipient=s["user"], kind=Notification.Kind.ACADEMIC_WARNING, title="Attendance/GPA Warning",
                    defaults={"message": "Your recent performance needs attention. Please meet your advisor.", "is_read": False},
                )
                if was_created:
                    created += 1
        self.stdout.write(f"Created {created} notifications.")

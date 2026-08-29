# Student Performance Management System (SPMS)

A full-stack Student Performance Management System built with **Django**, **HTML5**, **CSS3 (Bootstrap 5)**, and **JavaScript**, implementing the architecture described in the project spec: Department → Course → Course Batch → Semester → Subject → Subject Offering → Lectures / Assignments / Exams → Student Performance.

## What's included

- **Role-based access** for Student, Faculty, and Administrator, backed by a custom `User` model with a `role` field.
- **Academic structure**: Departments, Courses, Course Batches, Semesters, Subjects, and Subject Offerings (a subject taught in a specific semester by a specific faculty member).
- **Attendance**: per-lecture attendance marking by faculty, with live attendance-percentage rollups on the student dashboard.
- **Assignments**: creation, file upload, submission, late-submission detection, grading, and feedback.
- **Examinations**: exam scheduling by term (Mid-Sem / End-Sem / Internal) and category (Written / Practical / Presentation / Viva), result entry with automatic grade and pass/fail calculation, and retest/attempt tracking (`is_latest` keeps the active result while preserving history).
- **Semester performance & graduation records**: models are in place for semester-level SGPA/result summaries and graduation records (manage these via the admin site; dashboards display them).
- **Django admin** is fully wired up for administrators to manage every entity (users, departments, courses, batches, semesters, subjects, offerings, students, faculty, assignments, exams, attendance).
- Clean Bootstrap 5 UI, mobile-responsive, with role-specific dashboards.

## Tech stack

- Backend: Python, Django, Django ORM, Django Authentication
- Database: SQLite by default (zero setup); MySQL supported via environment variables
- Frontend: HTML5, CSS3, Bootstrap 5, vanilla JavaScript (Bootstrap's bundle)

## Project structure

```
SPMS/
├── manage.py
├── config/            # settings, root urls
├── accounts/          # custom User model, login/logout
├── academics/         # Department, Course, CourseBatch, Semester, Subject, SubjectOffering, Lecture
├── students/          # StudentProfile, StudentCourse, StudentSemester, SemesterResult, StudentGraduation
├── faculty/           # FacultyProfile
├── assignments/       # Assignment, AssignmentSubmission
├── examinations/      # Exam, ExamResult
├── attendance/        # Attendance
├── dashboard/         # role-based dashboards + demo data seeder
├── templates/         # all HTML templates (Bootstrap 5)
├── static/            # project CSS
└── requirements.txt
```

## 1. Setup

```bash
cd SPMS
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure environment (optional)

Copy `.env.example` to `.env` and adjust as needed. By default the app runs on **SQLite** with no extra configuration.

```bash
cp .env.example .env
```

To use **MySQL** instead (as in the original spec), set in `.env`:

```
DB_ENGINE=mysql
DB_NAME=student_performance
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

Then install the MySQL driver and create the database first:

```bash
pip install mysqlclient   # requires MySQL client dev headers on your system
mysql -u root -p -e "CREATE DATABASE student_performance;"
```

## 3. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## 4. Create data

Either create your own superuser and add records through `/admin/`:

```bash
python manage.py createsuperuser
```

...or load ready-to-use demo data (an admin, one faculty member, three students, a subject offering with lectures/attendance/an assignment/an exam already in it):

```bash
python manage.py seed_demo
```

This prints the demo login credentials when it finishes:

| Role    | Username  | Password       |
|---------|-----------|----------------|
| Admin   | admin     | admin12345     |
| Faculty | faculty1  | faculty12345   |
| Student | student1 / student2 / student3 | student12345 |

## 5. Run the server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** and log in. You'll be routed to the dashboard for your role automatically.

## How the roles work

- **Administrator** (`role=ADMIN` or `is_superuser`): lands on an overview page and manages every academic entity through the Django admin at `/admin/` — departments, courses, batches, semesters, subjects, subject offerings, users, student/faculty profiles, and academic records.
- **Faculty**: sees their assigned Subject Offerings, can add lectures and mark attendance, create assignments and grade submissions, and schedule exams and enter results.
- **Student**: sees attendance percentage per subject, assignment status (not submitted / submitted / graded) with the ability to submit files, exam results, and semester performance.

## Notes on the implementation

- Authentication data (`accounts.User`) is kept separate from role-specific data (`students.StudentProfile`, `faculty.FacultyProfile`), as described in the spec.
- A student's course enrollment history is preserved via `StudentCourse` records rather than overwritten, so a student can have multiple enrollments over time (e.g. graduated from one course, pursuing another).
- A missing `AssignmentSubmission` row represents "not submitted" — no redundant status field is stored for that case.
- `ExamResult.is_latest` tracks the active attempt while keeping prior attempts (regular/retest/improvement) for academic history.
- Grade and pass/fail status on exam results are calculated automatically on save.

## Possible next steps

- REST API via Django REST Framework
- CGPA calculation and transcript/PDF generation
- Email/notification integration for deadlines and results
- Graphical analytics dashboards

# Student Performance Management System (SPMS)

A full-stack, server-rendered Student Performance Management System built with
Django, Django REST Framework, and PostgreSQL. Every dashboard statistic, chart,
CRUD screen, and permission check is backed by real database queries and
server-side enforcement — there is no mock data, no dead buttons, and no
frontend-only access control.

## Overview

SPMS covers the full academic lifecycle: departments, semesters, courses and
enrollments; attendance; assignments and submissions; examinations, results,
grading and GPA/CGPA; rule-based at-risk detection; notifications and
announcements; and a REST API for every major resource. Four roles are
supported — **Super Admin**, **Admin**, **Faculty**, and **Student** — each
with its own dashboard and server-enforced permissions. There is no Parent
role anywhere in the system.

## Features

- Custom user model with role-based authentication (login, logout, password
  reset/change, profile with photo upload)
- Role-based dashboard redirect and server-side permission mixins/decorators
  (frontend hiding is cosmetic only — every restricted view returns a real
  403 to unauthorized roles)
- Full CRUD with search, filtering and pagination for Departments, Semesters,
  Courses, Enrollments, Students, and Faculty
- Attendance marking (faculty), history, and per-student summaries with a
  documented LATE-weighting rule and configurable GOOD/WARNING/CRITICAL
  thresholds
- Assignments: creation with file attachment, student submission with file
  validation (extension + size), late detection, faculty grading with
  feedback
- Examinations: creation, results entry with max-marks validation, automatic
  grade calculation from a configurable `GradeScale` table
- Centralized academic-performance service: `calculate_percentage()`,
  `calculate_grade()`, `calculate_semester_gpa()`, `calculate_cgpa()` — all
  credit-weighted, all in one place (`apps/academics/services.py`)
- Professional PDF marksheets (ReportLab) with real per-course grade/GPA data
- Rule-based, threshold-documented academic risk detection (no ML) —
  `apps/analytics/risk_service.py`
- Admin/Faculty/Student dashboards with real Chart.js visualizations sourced
  entirely from PostgreSQL aggregate queries
- Database-backed notifications (read/unread, mark-all-read, delete) and
  announcements with audience targeting (all students / department /
  semester / faculty)
- Full DRF API (13 resources) with role-scoped querysets and real permission
  classes
- Customized Django Admin for every model
- Custom 403 / 404 / 500 error pages
- Responsive Bootstrap 5 UI (sidebar collapses on mobile, tables scroll)
- `seed_data` management command that creates the Super Admin account and
  realistic, internally-consistent demo data
- Automated test suite (32 tests) covering auth, permissions, GPA/grade
  math, attendance math, file validation, risk detection, and API
  permissions

## Tech Stack

- Python 3.12+, Django 6.1, Django REST Framework
- PostgreSQL (via `psycopg`) — no SQLite fallback, ever
- Server-rendered Django templates: HTML5, CSS3, vanilla JavaScript,
  Bootstrap 5, Bootstrap Icons, Chart.js (via CDN)
- ReportLab for PDF generation
- Pillow for image handling
- Faker for realistic seed data

## Architecture

```
spms/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── config/                  # settings, root urls, wsgi/asgi, api_urls (DRF router)
│
├── apps/
│   ├── accounts/            # custom User model, auth views, permissions, error views, seed_data command
│   ├── students/             # StudentProfile, CRUD, API
│   ├── faculty/               # FacultyProfile, CRUD, API
│   ├── academics/            # Department, Semester, Course, Enrollment, GradeScale, GPA/CGPA services
│   ├── attendance/           # Attendance model, marking views, percentage/band services
│   ├── assignments/          # Assignment, AssignmentSubmission, submission/grading services
│   ├── examinations/         # Examination, ExamResult, marksheet PDF builder
│   ├── analytics/            # dashboard aggregation services, risk_service (rule-based)
│   └── notifications/        # Notification, Announcement
│
├── templates/                # base.html, includes/ (sidebar, navbar, messages, pagination), per-app templates
├── static/                   # css/main.css, js/main.js
├── media/                    # profile photos, assignment attachments/submissions
└── tests/                    # top-level automated test suite
```

Business logic lives in `services.py` files, not in templates, views, or
JavaScript — grade/GPA/CGPA math, attendance percentage, assignment
completion rate, and risk assessment are each defined exactly once and
reused everywhere they're needed (dashboards, PDFs, APIs).

## Installation

### 1. Prerequisites

- Python 3.12+
- PostgreSQL 14+ running locally (or reachable via network)

### 2. Clone and set up a virtual environment

```bash
python -m venv venv
```

Activate it:

- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the PostgreSQL database

```sql
CREATE DATABASE spms;
```

(Run this inside `psql`, or via `createdb spms` from the shell, using a
Postgres role that can create databases.)

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set at least `DB_USER`, `DB_PASSWORD`, and `SECRET_KEY`.
See the table below for every variable.

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | — (set your own) |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `127.0.0.1,localhost` |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | PostgreSQL connection | `spms` / `postgres` / — / `127.0.0.1` / `5432` |
| `ATTENDANCE_GOOD_THRESHOLD` | % at/above which attendance is "Good" | `85` |
| `ATTENDANCE_WARNING_THRESHOLD` | % at/above which attendance is "Warning" (below is "Critical") | `75` |
| `RISK_MIN_GPA` / `RISK_MIN_ATTENDANCE` | Documented reference thresholds used by the risk service | `6.0` / `75.0` |
| `EMAIL_*` | SMTP settings for password-reset emails (console backend is used automatically while `DEBUG=True`) | — |

### 6. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Seed realistic demo data (creates the Super Admin account)

```bash
python manage.py seed_data
```

This is safe to re-run — it will not create duplicate departments, courses,
or accounts. It creates:

- The Super Admin account (see **Demo Credentials** below)
- 8 departments, 6 semesters, 15 courses
- 10 faculty accounts and 50 student accounts, with realistic performance
  archetypes (excellent / average / weak / at-risk) so dashboards and
  charts look like a real institution, not empty placeholders
- Thousands of attendance records, dozens of assignments and hundreds of
  graded submissions, dozens of examinations and hundreds of results —
  all internally consistent (a student only has attendance/assignments/
  results for courses they're actually enrolled in)

### 8. Run the automated tests

```bash
python manage.py test tests
```

### 9. Run the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/**.

## Demo Credentials — DEVELOPMENT / DEMO ONLY

These accounts are created by `seed_data` for local development and
demonstration purposes only. **Do not use these credentials, or this seed
command, in a production deployment.**

| Role | Username | Password |
|---|---|---|
| Super Admin | `Kavya` | `Kavya 2004` |
| Faculty (example) | `faculty1` | `Faculty@2026` |
| Student (example) | `student1` | `Student@2026` |

`seed_data` creates `faculty1`–`faculty10` and `student1`–`student50`, all
sharing the same respective demo passwords above.

The Super Admin can log into both the SPMS dashboard (`/`) and the Django
admin (`/admin/`).

## Django Admin

Visit `/admin/` and log in with the Super Admin account. Every model
(Users, Departments, Semesters, Courses, Enrollments, Attendance,
Assignments, Submissions, Examinations, Results, Grade Scale,
Announcements, Notifications) is registered with search, filtering, and
autocomplete configured.

## API Endpoints

Base path: `/api/`. All endpoints require authentication and enforce
role-scoped querysets (a student can never see another student's data; a
faculty member can never see another faculty member's course data).

```
GET/POST      /api/students/            (admin only)
GET           /api/students/<id>/
GET/POST      /api/faculty/             (admin only)
GET/POST      /api/departments/         (admin only)
GET/POST      /api/semesters/           (admin only)
GET/POST      /api/courses/             (read: any role, scoped; write: admin)
GET/POST      /api/enrollments/         (admin only)
GET/POST      /api/attendance/          (read: scoped; write: faculty/admin)
GET/POST      /api/assignments/         (read: scoped; write: faculty/admin)
GET/POST      /api/submissions/         (students create their own; faculty/admin see their courses')
GET/POST      /api/examinations/        (read: scoped, students see published only; write: faculty/admin)
GET/POST      /api/results/             (read: scoped, students see published only; write: faculty/admin)
GET           /api/notifications/       (own notifications only)
GET           /api/analytics/           (role-scoped dashboard summary)
```

Standard DRF pagination (`PAGE_SIZE = 20`), filtering (`django-filter`),
search and ordering are enabled on every ViewSet where relevant.

## Testing

```bash
python manage.py test tests
```

The suite (32 tests) covers: login/logout/role-redirect, server-side
permission enforcement (403s for unauthorized roles and anonymous
redirects), GPA/CGPA/grade calculation, attendance percentage and band
calculation (including the duplicate-attendance database constraint),
assignment submission/late-detection/grading (including the "marks cannot
exceed maximum" rule), rule-based risk detection, file upload validation,
and DRF API permission scoping.

## Media & Static Files

- `STATIC_URL = "static/"`, served from `static/` in development
- `MEDIA_URL = "/media/"`, served from `media/` in development
  (`MEDIA_ROOT`) — profile photos, assignment attachments and student
  submissions are stored here
- In production, configure your web server (nginx, etc.) to serve both
  directories directly; `DEBUG=False` disables Django's built-in static/
  media serving

## Security

- CSRF protection on every form
- Django's built-in password hashing (PBKDF2) and validators
- Custom `User` model with role-based, server-side permission mixins and
  decorators (`apps/accounts/permissions.py`) — every admin/faculty/
  student-only view enforces its role at the view layer, not just in the
  template
- File upload validation: extension allow-list and size limit for both
  profile photos and assignment files
- `SECRET_KEY`, database credentials, and all other secrets are read from
  environment variables (`.env`, never committed — see `.gitignore`)
- `DEBUG` is environment-controlled; secure cookie flags and
  `X_FRAME_OPTIONS` are automatically enabled when `DEBUG=False`

## Deployment Notes

This project ships with Django's development server for local use only.
For production:

1. Set `DEBUG=False` and a strong, unique `SECRET_KEY`.
2. Set `ALLOWED_HOSTS` to your real domain(s).
3. Run `python manage.py collectstatic` and serve `staticfiles/` and
   `media/` via a proper web server or object storage.
4. Run Django behind a production WSGI/ASGI server (gunicorn/uvicorn) with
   nginx or similar in front.
5. Point `DATABASES` at a managed/production PostgreSQL instance via
   environment variables — never SQLite.
6. Configure real SMTP credentials for password-reset email delivery.
7. Do **not** run `seed_data` against a production database — it is a
   development/demo tool only.

## Troubleshooting

- **`connection to server ... failed`** — PostgreSQL isn't running, or
  `DB_HOST`/`DB_PORT`/`DB_USER`/`DB_PASSWORD` in `.env` don't match your
  local setup. Confirm with `psql -h 127.0.0.1 -U <DB_USER> -d spms`.
- **`relation "..." does not exist`** — migrations haven't been applied.
  Run `python manage.py migrate`.
- **Login works but dashboard is empty** — you haven't run
  `python manage.py seed_data` yet, or you're logged in as a brand-new
  account with no enrollments/attendance/results yet (this is expected —
  the risk service and dashboards intentionally don't flag students with
  no data yet as "at risk").
- **File upload rejected** — check the extension against
  `ALLOWED_ASSIGNMENT_EXTENSIONS` / `ALLOWED_IMAGE_EXTENSIONS` in
  `config/settings.py`, and the size against `MAX_UPLOAD_SIZE_MB`.
- **Static files missing styling** — run `python manage.py collectstatic`
  in production, or confirm `static/` exists in development
  (`STATICFILES_DIRS`).

## Future Improvements

- WebSocket-based live notifications (ASGI is already configured)
- Bulk CSV import/export for students, faculty, and results
- Configurable grading scales per department (currently one global
  `GradeScale` table)
- Parent/guardian portal (explicitly out of scope for this build per
  project requirements)
- Automated email digests for at-risk student alerts

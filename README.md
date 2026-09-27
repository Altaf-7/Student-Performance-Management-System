# STUDENT PERFORMANCE MANAGEMENT SYSTEM

A web-based **Student Performance Management System** built using the **Django stack** to manage students, faculty, courses, subjects, attendance, assignments, examinations, results, and academic performance.

The system is designed as a centralized academic management platform where students, faculty, and administrators interact with different parts of the academic lifecycle.

---

## 📌 Overview

The **Student Performance Management System (SPMS)** provides a structured platform for managing academic activities and tracking student performance throughout their course.

The system follows a layered academic structure:

```text
Department
    ↓
Course
    ↓
Course Batch
    ↓
Semester
    ↓
Subject
    ↓
Subject Offering
    ↓
Lectures / Assignments / Exams
    ↓
Student Performance
    ↓
Semester Result
    ↓
Graduation
```

The application separates authentication data from role-specific information and maintains historical academic records without unnecessarily overwriting previous data.

---

## 🎯 Objectives

* Manage student academic information
* Manage departments and courses
* Manage course batches and semesters
* Manage subjects and their offerings
* Assign faculty to subjects
* Record lecture schedules
* Track student attendance
* Create and manage assignments
* Handle assignment submissions and grading
* Schedule examinations
* Record examination results
* Support retests and improvement attempts
* Generate semester-level performance records
* Maintain graduation information
* Provide role-based access for students, faculty, and administrators

---

## 🛠️ Technology Stack

### Backend

* **Python**
* **Django**
* Django ORM
* Django Authentication & Authorization

### Database

* **MySQL**

### Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap

### Development Tools

* Git
* GitHub
* VS Code
* MySQL CLI

---

## 👥 User Roles

The system supports three primary types of users:

### Student

Students can:

* View their profile
* View enrolled courses
* View semester information
* View subjects
* View lecture schedules
* View attendance
* View assignments
* Submit assignments
* View assignment marks and feedback
* View examination schedules
* View examination results
* View semester performance
* View academic history

### Faculty

Faculty can:

* Manage assigned subjects
* View students
* Schedule/manage lectures
* Mark attendance
* Create assignments
* Review submissions
* Award assignment marks
* Provide feedback
* Create examinations
* Enter examination marks
* View student performance

### Administrator

Administrators can manage:

* Users
* Students
* Faculty
* Departments
* Courses
* Course batches
* Semesters
* Subjects
* Subject offerings
* Academic records
* Administrative operations

---

# 🏗️ System Architecture

The application follows Django's MVC-like architecture, implemented through Django's **MTV (Model-Template-View)** pattern.

```text
                 ┌──────────────────────┐
                 │      Web Browser     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │    Django URLs       │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │    Django Views      │
                 └──────────┬───────────┘
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
        ┌──────────────────┐  ┌──────────────────┐
        │ Django Templates │  │ Django Models    │
        │ HTML/CSS/JS      │  │ Business Logic   │
        └──────────────────┘  └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │      MySQL       │
                              └──────────────────┘
```

---

# 🗄️ Database Design

The database is designed around normalized entities and relationships.

## Core Academic Structure

```text
Department
    │
    └── Course
          │
          └── Course_Batch
                │
                └── Semester
                      │
                      └── Subject_Offering
                            │
                            ├── Lecture
                            ├── Assignment
                            └── Exam
```

---

## Authentication Layer

```text
Users
 ├── Student
 ├── Faculty
 └── Admin
```

The authentication layer stores common user information, while role-specific tables contain additional information related to each user type.

---

## Student Academic History

A student is not directly tied to a single course permanently.

Instead:

```text
Student
   │
   └── Student_Course
          │
          ├── Course
          ├── Admission Year
          ├── Completion Year
          └── Status
```

This allows a student to have multiple academic records.

For example:

```text
Student
 ├── BCA 2021 → Graduated
 └── MCA 2025 → Pursuing
```

This preserves historical academic information instead of overwriting the previous course.

---

# 📚 Subject Management

Subjects are separated from their actual academic offerings.

```text
Subject
   │
   └── Subject_Offering
          │
          ├── Semester
          └── Faculty
```

### Subject

Represents the reusable definition of a subject.

Example:

```text
DBMS
CS501
Database Management Systems
```

### Subject Offering

Represents a particular instance of that subject being taught during a specific semester and batch.

This prevents duplication of subject information across different academic years.

---

# 📝 Assignments

Assignments belong to a specific `Subject_Offering`.

```text
Subject_Offering
       │
       └── Assignment
                │
                └── Assignment_Submission
                         │
                         └── Student
```

The system supports:

* Assignment title
* Description
* Instructions
* Maximum marks
* Assignment files
* Assignment status
* Submission time
* Late submission detection
* Marks
* Feedback
* Grading timestamp

A missing submission row represents:

```text
Student → Not Submitted
```

rather than storing a redundant `not_submitted` status.

---

# 📝 Examinations

Examinations are associated with a `Subject_Offering`.

The examination model separates:

### Exam Term

```text
mid_sem
end_sem
internal
```

### Exam Category

```text
written
practical
presentation
viva
```

This allows combinations such as:

```text
Mid-Sem Written
Mid-Sem Practical
End-Sem Written
End-Sem Practical
Internal Written
Internal Viva
```

Multiple internal examinations can also exist for the same subject.

---

# 📊 Examination Results

The system maintains individual examination results for students.

Results support:

* Regular attempts
* Retests
* Improvement attempts
* Multiple attempts
* Present
* Absent
* Medical leave
* Marks
* Grade
* Pass/fail status

The latest attempt can be identified using the `is_latest` field.

Example:

```text
Regular Attempt
       ↓
    Failed
       ↓
    Retest
       ↓
  Passed
```

The original attempt remains available for academic history while the latest attempt becomes the active result.

---

# 📅 Attendance

Attendance is associated with individual lectures.

```text
Student
   │
   └── Attendance
          │
          └── Lecture
                 │
                 └── Subject_Offering
```

Each student can have only one attendance record per lecture.

```text
UNIQUE(student_id, lecture_id)
```

Possible attendance states include:

```text
present
absent
```

The design also ensures that attendance can be validated against the student's academic enrollment.

---

# 🎓 Semester Performance

Student semester performance is maintained through:

```text
Student
   │
   └── Student_Semester
          │
          └── Semester_Result
```

The semester result contains:

* Total marks
* Obtained marks
* SGPA
* Result status
* Declaration date

The result acts as a semester-level academic snapshot.

---

# 🎓 Graduation

Graduation information is maintained separately.

```text
Student
   │
   └── Student_Graduation
          ├── Graduation Date
          ├── Final CGPA
          └── Remarks
```

A student can have only one graduation record.

---

# 🔐 Data Integrity

The database makes extensive use of MySQL constraints.

### Primary Keys

Every major entity has a unique identifier.

```sql
PRIMARY KEY
```

### Foreign Keys

Relationships between entities are enforced using:

```sql
FOREIGN KEY
```

### Unique Constraints

Used to prevent duplicate records.

Examples:

```sql
UNIQUE (student_id, lecture_id)
```

```sql
UNIQUE (assignment_id, student_id)
```

### Check Constraints

Used for validating domain rules.

Examples:

```sql
CHECK (maximum_marks > 0)
```

```sql
CHECK (obtained_marks <= total_marks)
```

### Triggers

Triggers are used where validation depends on data from another table or where derived values need to be maintained automatically.

Examples:

* Assignment submission status
* Assignment marks validation
* Examination marks validation
* Automatic grade calculation
* Automatic result status
* Latest examination attempt tracking

---

# 📁 Suggested Django Project Structure

```text
SMPS/
│
├── manage.py
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── academics/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── students/
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── faculty/
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── assignments/
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── examinations/
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── attendance/
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── templates/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone <repository-url>
cd student-performance-management-system
```

## 2. Create Virtual Environment

### Windows/Linux/macOS

```bash
uv venv
venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=student_performance
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

---

## 5. Create Database

Create the MySQL database:

```sql
CREATE DATABASE student_performance;
```

---

## 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 7. Create Admin User

```bash
python manage.py createsuperuser
```

---

## 8. Start Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# 🔑 Authentication & Authorization

Django authentication is used to manage user login and access control.

The application separates:

```text
Authentication
       ↓
Authorization
       ↓
Role-specific functionality
```

Access to resources should be controlled according to the user's role.

Example:

```text
Student
 ├── View attendance
 ├── Submit assignment
 └── View results

Faculty
 ├── Mark attendance
 ├── Create assignment
 └── Enter marks

Admin
 ├── Manage users
 ├── Manage courses
 └── Manage academic structure
```

---

# 📈 Performance Management

The system can provide students with an overall academic dashboard containing:

* Attendance percentage
* Assignment performance
* Examination marks
* Subject-wise performance
* Semester marks
* SGPA
* Academic status
* Historical performance

Example:

```text
Student Dashboard
│
├── Attendance
│
├── Assignments
│   ├── Submitted
│   ├── Pending
│   └── Marks
│
├── Examinations
│   ├── Upcoming
│   └── Results
│
└── Semester Performance
    ├── Total Marks
    ├── Obtained Marks
    └── SGPA
```

---

# 🔮 Future Enhancements

Possible future improvements include:

* CGPA calculation
* Academic transcript generation
* Performance analytics
* Graphical performance dashboards
* Attendance shortage alerts
* Assignment deadline notifications
* Email notifications
* PDF report generation
* Student ranking
* Faculty performance analytics
* Advanced RBAC
* REST API using Django REST Framework
* Mobile application support
* Cloud file storage
* Automated academic reports

---

# 🧪 Testing

The project should include tests for:

* Authentication
* Authorization
* Student registration
* Course enrollment
* Assignment submission
* Late submission detection
* Marks validation
* Examination result calculation
* Attendance
* Semester result generation

Run tests using:

```bash
python manage.py test
```

---

# 🔒 Security Considerations

The application should follow Django security best practices.

Important considerations include:

* Password hashing through Django authentication
* CSRF protection
* Authentication-required views
* Role-based authorization
* Input validation
* ORM-based database queries
* Secure file uploads
* Environment variables for secrets
* Production `DEBUG=False`
* Secure database credentials
* HTTPS in production

---

# 🚀 Deployment

For production deployment, the application can be hosted using a setup such as:

```text
                 Internet
                    │
                    ▼
              Web Server
                    │
                    ▼
             Django / WSGI
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       MySQL             File Storage
```

Production configuration should include:

```text
DEBUG=False
ALLOWED_HOSTS=...
SECRET_KEY=<secure-secret>
```

Static files should be collected using:

```bash
python manage.py collectstatic
```

---

# 📜 License

This project is developed for academic and educational purposes.

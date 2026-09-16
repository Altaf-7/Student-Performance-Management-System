# Testing Strategy

## Overview
The Student Performance Management System (SPMS) incorporates a comprehensive testing strategy that focuses on security, authorization, and data integrity. Tests are organized modularly within each Django app's `tests.py` file.

## Test Areas

### 1. Authentication (`accounts/tests.py`)
- Verifies successful and failed login attempts.
- Ensures roles (Student, Faculty, Admin) are assigned correctly during registration.
- Validates that unauthenticated users are redirected to login.

### 2. Authorization and IDOR (`faculty/tests.py`, `students/tests.py`)
- **Role Isolation:** Tests that students cannot access faculty dashboards and vice-versa.
- **Object-Level Authorization:** Tests that a faculty member can only edit/delete their own lectures, assignments, and exams. Tests that students can only view their own assignments and exam results.
- **File Download Authorization:** Tests that users cannot download attachments or submissions belonging to other users.

### 3. Data Integrity & Constraints (`academics/tests.py`, `assignments/tests.py`, `examinations/tests.py`)
- Validates model `clean()` methods.
- Ensures assignment due dates are in the future.
- Ensures exam marks obtained do not exceed the maximum marks and are not negative.
- Ensures `UniqueConstraint` functions as expected (e.g., no duplicate Subject Offerings).

## Running Tests
To run the entire test suite:
```bash
python manage.py test
```

To run tests for a specific app:
```bash
python manage.py test <app_name>
```
For example:
```bash
python manage.py test faculty
```

# Security Policy and Guidelines

## Authentication and Sessions
- All roles (Student, Faculty, Admin) authenticate via a single, centralized `/login/` endpoint.
- Session cookies are protected in production with `SESSION_COOKIE_SECURE=True`.
- CSRF cookies are protected in production with `CSRF_COOKIE_SECURE=True`.

## Authorization (RBAC and IDOR Prevention)
- **Role-Based Access Control (RBAC):** Views use custom mixins (`FacultyRequiredMixin`, `StudentRequiredMixin`) and decorators (`@student_required`, `@faculty_required`) to restrict access based on user roles.
- **Insecure Direct Object Reference (IDOR) Protection:** All detail, update, and delete views enforce object-level authorization by validating the object against the `request.user`'s profile (e.g., `offering__faculty=request.user.faculty_profile` or `student=request.user.student_profile`).

## Data Integrity and Model Constraints
- Database-level `clean()` methods ensure logical consistency:
  - Attendance percentages cannot exceed 100%.
  - Exam results cannot exceed `maximum_marks` and cannot be negative.
  - Assignment due dates cannot be in the past when creating them.
- `UniqueConstraint` prevents duplicate records, such as duplicate `SubjectOffering` or `StudentSemester` entries.

## Sensitive File Handling
- Media files, especially student assignment submissions, are **not** served directly via public URLs in production.
- File downloads are brokered through authorization-checked Django views (`DownloadSubmissionView`, `DownloadAssignmentAttachmentView`), which verify that the user has the right to access the specific file.

## Environment Configuration
- Sensitive keys like `SECRET_KEY` are stored in environment variables.
- `DEBUG` mode is conditionally disabled based on environment variables.
- Production uses HTTP Strict Transport Security (HSTS) with `SECURE_HSTS_SECONDS=31536000`, `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`, and `SECURE_HSTS_PRELOAD=True`.
- Standard security headers like `X-Frame-Options` (DENY) and `X-Content-Type-Options` (nosniff) are enabled.

import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def assignment_file_path(instance, filename):
    return f"assignments/{instance.course.course_code}/{filename}"


def submission_file_path(instance, filename):
    return f"submissions/{instance.assignment.id}/{instance.student.username}/{filename}"


def validate_assignment_file(f):
    ext = os.path.splitext(f.name)[1].lower()
    if ext not in settings.ALLOWED_ASSIGNMENT_EXTENSIONS:
        raise ValidationError(f"Unsupported file type '{ext}'.")
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if f.size > max_bytes:
        raise ValidationError(f"File too large. Max size is {settings.MAX_UPLOAD_SIZE_MB}MB.")


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course = models.ForeignKey("academics.Course", on_delete=models.CASCADE, related_name="assignments")
    attachment = models.FileField(upload_to=assignment_file_path, blank=True, null=True, validators=[validate_assignment_file])
    due_date = models.DateTimeField()
    maximum_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignments_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-due_date"]

    def __str__(self):
        return f"{self.title} ({self.course.course_code})"


class AssignmentSubmission(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUBMITTED = "SUBMITTED", "Submitted"
        LATE = "LATE", "Late"
        GRADED = "GRADED", "Graded"

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignment_submissions",
        limit_choices_to={"role": "STUDENT"},
    )
    file = models.FileField(upload_to=submission_file_path, validators=[validate_assignment_file])
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SUBMITTED)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="submissions_graded",
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(fields=["assignment", "student"], name="unique_submission_per_student")
        ]

    def clean(self):
        if self.marks_obtained is not None and self.marks_obtained > self.assignment.maximum_marks:
            raise ValidationError("Marks obtained cannot exceed the assignment's maximum marks.")

    def __str__(self):
        return f"{self.student} - {self.assignment}"

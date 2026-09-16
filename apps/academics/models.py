from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=15, unique=True)
    head_of_department = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="headed_departments", limit_choices_to={"role": "FACULTY"},
    )
    description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Semester(models.Model):
    name = models.CharField(max_length=50)
    semester_number = models.PositiveSmallIntegerField()
    academic_year = models.CharField(max_length=20, help_text="e.g. 2025-2026")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-academic_year", "semester_number"]
        constraints = [
            models.UniqueConstraint(fields=["semester_number", "academic_year"], name="unique_semester_per_year")
        ]

    def __str__(self):
        return f"{self.name} ({self.academic_year})"


class Course(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        ARCHIVED = "ARCHIVED", "Archived"

    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    credits = models.PositiveSmallIntegerField(default=3)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="courses")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="courses")
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="courses_taught", limit_choices_to={"role": "FACULTY"},
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["course_code"]
        indexes = [models.Index(fields=["department", "semester"])]

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        DROPPED = "DROPPED", "Dropped"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments",
        limit_choices_to={"role": "STUDENT"},
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    academic_year = models.CharField(max_length=20)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="enrollments")
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["-enrollment_date"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course", "academic_year"], name="unique_enrollment_per_year")
        ]
        indexes = [models.Index(fields=["student", "course"])]

    def __str__(self):
        return f"{self.student} -> {self.course}"


class GradeScale(models.Model):
    """Configurable grading bands. Business logic that consumes this
    (percentage -> grade -> grade point) lives in services.py, never in
    templates or JS, per project standards."""

    grade = models.CharField(max_length=5, unique=True)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=1)

    class Meta:
        ordering = ["-min_percentage"]

    def __str__(self):
        return f"{self.grade} ({self.min_percentage}-{self.max_percentage}%) = {self.grade_point}"

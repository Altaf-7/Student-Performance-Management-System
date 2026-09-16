from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class StudentProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    class AcademicStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ON_LEAVE = "ON_LEAVE", "On Leave"
        GRADUATED = "GRADUATED", "Graduated"
        DEACTIVATED = "DEACTIVATED", "Deactivated"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    student_id = models.CharField(
        max_length=20, unique=True,
        validators=[RegexValidator(r"^[A-Z0-9\-]+$", "Student ID may only contain uppercase letters, digits and hyphens.")],
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    address = models.TextField(blank=True)
    department = models.ForeignKey("academics.Department", on_delete=models.SET_NULL, null=True, related_name="students")
    semester = models.ForeignKey("academics.Semester", on_delete=models.SET_NULL, null=True, related_name="students")
    enrollment_year = models.PositiveIntegerField()
    academic_status = models.CharField(max_length=15, choices=AcademicStatus.choices, default=AcademicStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["student_id"]
        indexes = [models.Index(fields=["department", "semester"])]

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"

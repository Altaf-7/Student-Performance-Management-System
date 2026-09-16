from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class FacultyProfile(models.Model):
    class Designation(models.TextChoices):
        PROFESSOR = "PROFESSOR", "Professor"
        ASSOCIATE_PROFESSOR = "ASSOCIATE_PROFESSOR", "Associate Professor"
        ASSISTANT_PROFESSOR = "ASSISTANT_PROFESSOR", "Assistant Professor"
        LECTURER = "LECTURER", "Lecturer"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="faculty_profile")
    faculty_id = models.CharField(
        max_length=20, unique=True,
        validators=[RegexValidator(r"^[A-Z0-9\-]+$", "Faculty ID may only contain uppercase letters, digits and hyphens.")],
    )
    department = models.ForeignKey("academics.Department", on_delete=models.SET_NULL, null=True, related_name="faculty_members")
    designation = models.CharField(max_length=25, choices=Designation.choices, default=Designation.ASSISTANT_PROFESSOR)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["faculty_id"]

    def __str__(self):
        return f"{self.faculty_id} - {self.user.get_full_name() or self.user.username}"

    @property
    def workload(self):
        return self.user.courses_taught.count()

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model. Authentication data is kept separate from
    role-specific profile data (see students.StudentProfile / faculty.FacultyProfile)."""

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        FACULTY = 'FACULTY', 'Faculty'
        STUDENT = 'STUDENT', 'Student'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_faculty(self):
        return self.role == self.Role.FACULTY

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

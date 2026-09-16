from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


def profile_photo_path(instance, filename):
    return f"profile_photos/{instance.username}/{filename}"


class User(AbstractUser):
    """Custom user with a role. Role drives dashboard routing and
    backend permission checks throughout the system."""

    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        ADMIN = "ADMIN", "Admin"
        FACULTY = "FACULTY", "Faculty"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to=profile_photo_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN or self.is_superuser

    @property
    def is_admin_role(self):
        return self.role in (self.Role.SUPER_ADMIN, self.Role.ADMIN) or self.is_superuser

    @property
    def is_faculty_role(self):
        return self.role == self.Role.FACULTY

    @property
    def is_student_role(self):
        return self.role == self.Role.STUDENT

    def get_dashboard_url(self):
        if self.is_admin_role:
            return reverse("accounts:admin_dashboard")
        if self.is_faculty_role:
            return reverse("accounts:faculty_dashboard")
        return reverse("accounts:student_dashboard")

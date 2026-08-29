from django.db import models
from django.conf import settings


class FacultyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_profile')
    employee_id = models.CharField(max_length=30, unique=True)
    department = models.ForeignKey('academics.Department', on_delete=models.SET_NULL, null=True, related_name='faculty_members')
    designation = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.employee_id})"

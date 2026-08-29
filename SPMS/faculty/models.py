from django.db import models
from django.conf import settings

<<<<<<< HEAD

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
=======
class Faculty(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_profile')
    department = models.ForeignKey('academics.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='faculties')
    designation = models.CharField(max_length=100)
    specialization = models.CharField(max_length=150, blank=True, null=True)
    qualification = models.CharField(max_length=150, blank=True, null=True)
    office_email = models.EmailField(blank=True, null=True)
    office_contact = models.CharField(max_length=20, blank=True, null=True)
    date_of_join = models.DateField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} - {self.designation}"
>>>>>>> origin/main

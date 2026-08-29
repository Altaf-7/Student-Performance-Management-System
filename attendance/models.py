from django.db import models
from django.conf import settings


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'

    lecture = models.ForeignKey('academics.Lecture', on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ABSENT)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('lecture', 'student')
        ordering = ['-lecture__date']

    def __str__(self):
        return f"{self.student} - {self.lecture} - {self.get_status_display()}"

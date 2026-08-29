from django.db import models
<<<<<<< HEAD
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
=======
from django.core.exceptions import ValidationError

class Attendance(models.Model):
    class StatusChoices(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendances')
    lecture = models.ForeignKey('academics.Lecture', on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=10, choices=StatusChoices.choices)
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'lecture'], name='unique_attendance')
        ]

    def clean(self):
        # Validate that student is enrolled in the subject offering of the lecture
        if self.student_id and self.lecture_id:
            # We can check if the student has an active StudentSemester for the lecture's semester
            from students.models import StudentSemester
            is_enrolled = StudentSemester.objects.filter(
                student=self.student,
                semester=self.lecture.offering.semester,
                status__in=[StudentSemester.StatusChoices.ACTIVE, StudentSemester.StatusChoices.BACKLOG]
            ).exists()
            
            if not is_enrolled:
                raise ValidationError("Student is not enrolled in the semester for this lecture.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.enrollment_no} - {self.lecture.date} - {self.status}"
>>>>>>> origin/main

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class Assignment(models.Model):
    subject_offering = models.ForeignKey('academics.SubjectOffering', on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    max_marks = models.PositiveIntegerField()
    due_date = models.DateTimeField()
    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.title} ({self.subject_offering})"

    def clean(self):
        if self.max_marks is not None and self.max_marks <= 0:
            raise ValidationError({'max_marks': 'Maximum marks must be greater than 0.'})

    @property
    def is_past_due(self):
        return timezone.now() > self.due_date


class AssignmentSubmission(models.Model):
    """A missing row for a (assignment, student) pair means 'not submitted' -
    no redundant status field is stored for that case."""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='assignment_submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    remarks = models.TextField(blank=True)

    marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions')
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student} -> {self.assignment}"

    def clean(self):
        if self.marks is not None and self.marks > self.assignment.max_marks:
            raise ValidationError({'marks': 'Marks cannot exceed the assignment maximum marks.'})

    @property
    def is_late(self):
        return self.submitted_at > self.assignment.due_date

    @property
    def is_graded(self):
        return self.marks is not None

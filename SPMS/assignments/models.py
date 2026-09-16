from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import CheckConstraint, Q

import os

def validate_pdf(value):
    ext = os.path.splitext(value.name)[1]
    if ext.lower() != '.pdf':
        raise ValidationError('Unsupported file extension. Only PDF files are allowed.')

class Assignment(models.Model):
    class StatusChoices(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        CLOSED = 'closed', 'Closed'

    offering = models.ForeignKey('academics.SubjectOffering', on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    maximum_marks = models.DecimalField(max_digits=5, decimal_places=2)
    assigned_at = models.DateTimeField(default=timezone.now)
    due_datetime = models.DateTimeField()
    file_attachment = models.FileField(upload_to='assignments/', blank=True, null=True, validators=[validate_pdf])
    status = models.CharField(max_length=15, choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            CheckConstraint(
                condition=Q(maximum_marks__gt=0),
                name='check_assignment_maximum_marks'
            )
        ]

    def clean(self):
        if self.assigned_at and self.due_datetime and self.due_datetime < self.assigned_at:
            raise ValidationError("Due datetime cannot be before assigned datetime.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.offering.subject.code})"

class AssignmentSubmission(models.Model):
    class StatusChoices(models.TextChoices):
        SUBMITTED = 'submitted', 'Submitted'
        LATE = 'late', 'Late'

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    submission_file = models.FileField(upload_to='submissions/', blank=True, null=True, validators=[validate_pdf])
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    graded_at = models.DateTimeField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=StatusChoices.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['assignment', 'student'], name='unique_assignment_submission')
        ]

    def clean(self):
        if self.marks_awarded is not None and self.assignment_id:
            if self.marks_awarded > self.assignment.maximum_marks:
                raise ValidationError("Marks awarded cannot exceed assignment maximum marks.")
            if self.marks_awarded < 0:
                raise ValidationError("Marks awarded cannot be negative.")

    def save(self, *args, **kwargs):
        # Automatically determine status on creation
        if not self.pk and not self.status:
            # We use timezone.now() if submitted_at isn't set yet (since it's auto_now_add)
            current_time = timezone.now()
            if current_time > self.assignment.due_datetime:
                self.status = self.StatusChoices.LATE
            else:
                self.status = self.StatusChoices.SUBMITTED
        
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.enrollment_no} - {self.assignment.title}"

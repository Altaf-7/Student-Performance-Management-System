from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        LOW_ATTENDANCE = "LOW_ATTENDANCE", "Low Attendance"
        NEW_ASSIGNMENT = "NEW_ASSIGNMENT", "New Assignment"
        ASSIGNMENT_DEADLINE = "ASSIGNMENT_DEADLINE", "Assignment Deadline"
        EXAM_ANNOUNCEMENT = "EXAM_ANNOUNCEMENT", "Exam Announcement"
        RESULT_PUBLISHED = "RESULT_PUBLISHED", "Result Published"
        ACADEMIC_WARNING = "ACADEMIC_WARNING", "Academic Warning"
        ANNOUNCEMENT = "ANNOUNCEMENT", "New Announcement"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=25, choices=Kind.choices)
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipient", "is_read"])]

    def __str__(self):
        return f"{self.recipient} - {self.title}"


class Announcement(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        NORMAL = "NORMAL", "Normal"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    class Audience(models.TextChoices):
        ALL_STUDENTS = "ALL_STUDENTS", "All Students"
        DEPARTMENT = "DEPARTMENT", "Specific Department"
        SEMESTER = "SEMESTER", "Specific Semester"
        FACULTY = "FACULTY", "Faculty"

    title = models.CharField(max_length=200)
    description = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="announcements")
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    target_audience = models.CharField(max_length=15, choices=Audience.choices, default=Audience.ALL_STUDENTS)
    department = models.ForeignKey("academics.Department", on_delete=models.CASCADE, null=True, blank=True, related_name="announcements")
    semester = models.ForeignKey("academics.Semester", on_delete=models.CASCADE, null=True, blank=True, related_name="announcements")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

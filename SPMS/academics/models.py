from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import CheckConstraint, Q

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    duration_years = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.code})"

class CourseBatch(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='batches')
    academic_year = models.CharField(max_length=9, help_text="e.g. 2023-2024")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'academic_year'], name='unique_course_batch')
        ]

    def __str__(self):
        return f"{self.course.code} Batch {self.academic_year}"

class Semester(models.Model):
    course_batch = models.ForeignKey(CourseBatch, on_delete=models.CASCADE, related_name='semesters')
    semester_number = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course_batch', 'semester_number'], name='unique_semester')
        ]

    def clean(self):
        if self.course_batch_id:
            max_semesters = self.course_batch.course.duration_years * 2
            if self.semester_number > max_semesters:
                raise ValidationError(f"Semester number cannot exceed {max_semesters} for this course.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course_batch} - Sem {self.semester_number}"

class Subject(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class SubjectOffering(models.Model):
    class SubjectType(models.TextChoices):
        CORE = 'core', 'Core'
        ELECTIVE = 'elective', 'Elective'
        LAB = 'lab', 'Lab'
        PROJECT = 'project', 'Project'

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='offerings')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subject_offerings')
    faculty = models.ForeignKey('faculty.Faculty', on_delete=models.SET_NULL, null=True, blank=True, related_name='subject_offerings')
    subject_type = models.CharField(max_length=20, choices=SubjectType.choices, default=SubjectType.CORE)
    credits = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.subject.code} - {self.semester}"

class Lecture(models.Model):
    offering = models.ForeignKey(SubjectOffering, on_delete=models.CASCADE, related_name='lectures')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['offering', 'date', 'start_time'], name='unique_lecture_slot'),
            CheckConstraint(
                condition=Q(end_time__gt=models.F('start_time')),
                name='check_start_end_time'
            )
        ]

    def __str__(self):
        return f"{self.offering.subject.code} Lecture on {self.date} at {self.start_time}"

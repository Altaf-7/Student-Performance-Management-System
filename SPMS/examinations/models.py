from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import CheckConstraint, Q

class Exam(models.Model):
    class ExamTerm(models.TextChoices):
        MID_SEM = 'mid_sem', 'Mid Semester'
        END_SEM = 'end_sem', 'End Semester'
        INTERNAL = 'internal', 'Internal'

    class ExamCategory(models.TextChoices):
        WRITTEN = 'written', 'Written'
        PRACTICAL = 'practical', 'Practical'
        PRESENTATION = 'presentation', 'Presentation'
        VIVA = 'viva', 'Viva'

    class StatusChoices(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    offering = models.ForeignKey('academics.SubjectOffering', on_delete=models.CASCADE, related_name='exams')
    exam_term = models.CharField(max_length=20, choices=ExamTerm.choices)
    exam_category = models.CharField(max_length=20, choices=ExamCategory.choices)
    exam_date = models.DateField()
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.SCHEDULED)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['offering', 'exam_term', 'exam_category', 'exam_date'],
                name='unique_exam_schedule'
            )
        ]

    def __str__(self):
        return f"{self.offering.subject.code} - {self.exam_term} ({self.exam_category})"

class ExamResult(models.Model):
    class AttemptType(models.TextChoices):
        REGULAR = 'regular', 'Regular'
        RETEST = 'retest', 'Retest'
        IMPROVEMENT = 'improvement', 'Improvement'

    class AttendanceStatus(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        MEDICAL_LEAVE = 'medical_leave', 'Medical Leave'

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='exam_results')
    attempt_type = models.CharField(max_length=20, choices=AttemptType.choices, default=AttemptType.REGULAR)
    attempt_number = models.PositiveIntegerField(default=1)
    attendance_status = models.CharField(max_length=20, choices=AttendanceStatus.choices)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    grade = models.CharField(max_length=5, blank=True, null=True)
    result_status = models.CharField(max_length=20, blank=True, null=True) # e.g. Pass/Fail
    is_latest = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['exam', 'student', 'attempt_number'],
                name='unique_exam_attempt'
            )
        ]

    def clean(self):
        if self.attendance_status in [self.AttendanceStatus.ABSENT, self.AttendanceStatus.MEDICAL_LEAVE]:
            if self.marks_obtained is not None:
                raise ValidationError("Marks must be null if student was absent or on medical leave.")
        else:
            if self.marks_obtained is None:
                raise ValidationError("Marks must be provided if student was present.")
            if self.exam_id and self.marks_obtained > self.exam.total_marks:
                raise ValidationError("Obtained marks cannot exceed exam total marks.")
            if self.marks_obtained < 0:
                raise ValidationError("Obtained marks cannot be negative.")

    def save(self, *args, **kwargs):
        self.clean()
        # Optional: simple grade logic could go here if not handled by an external service
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.enrollment_no} - {self.exam}"

class SemesterReport(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='semester_reports')
    semester = models.ForeignKey('academics.Semester', on_delete=models.CASCADE, related_name='semester_reports')
    academic_year = models.CharField(max_length=9)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2)
    obtained_marks = models.DecimalField(max_digits=6, decimal_places=2)
    sgpa = models.DecimalField(max_digits=4, decimal_places=2) # 0.00 to 10.00
    result_status = models.CharField(max_length=20) # Pass/Fail/Promoted with Backlog
    declared_on = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'semester', 'academic_year'], name='unique_semester_report'),
            CheckConstraint(condition=Q(total_marks__gt=0), name='check_total_marks_positive'),
            CheckConstraint(condition=Q(obtained_marks__gte=0), name='check_obtained_marks_non_negative'),
            CheckConstraint(condition=Q(obtained_marks__lte=models.F('total_marks')), name='check_marks_validity'),
            CheckConstraint(condition=Q(sgpa__gte=0, sgpa__lte=10), name='check_sgpa_range')
        ]

    def __str__(self):
        return f"Report: {self.student.enrollment_no} - {self.semester}"

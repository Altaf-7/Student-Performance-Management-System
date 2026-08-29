from django.db import models
<<<<<<< HEAD
from django.conf import settings
from django.core.exceptions import ValidationError


class Exam(models.Model):
    class Term(models.TextChoices):
        MID_SEM = 'MID_SEM', 'Mid-Sem'
        END_SEM = 'END_SEM', 'End-Sem'
        INTERNAL = 'INTERNAL', 'Internal'

    class Category(models.TextChoices):
        WRITTEN = 'WRITTEN', 'Written'
        PRACTICAL = 'PRACTICAL', 'Practical'
        PRESENTATION = 'PRESENTATION', 'Presentation'
        VIVA = 'VIVA', 'Viva'

    subject_offering = models.ForeignKey('academics.SubjectOffering', on_delete=models.CASCADE, related_name='exams')
    term = models.CharField(max_length=10, choices=Term.choices)
    category = models.CharField(max_length=15, choices=Category.choices)
    name = models.CharField(max_length=150, blank=True, help_text="e.g. 'Internal Test 2' (optional label)")
    exam_date = models.DateField()
    max_marks = models.PositiveIntegerField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-exam_date']

    def __str__(self):
        label = self.name or f"{self.get_term_display()} {self.get_category_display()}"
        return f"{label} - {self.subject_offering}"

    def clean(self):
        if self.max_marks is not None and self.max_marks <= 0:
            raise ValidationError({'max_marks': 'Maximum marks must be greater than 0.'})


class ExamResult(models.Model):
    class AttendanceStatus(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        MEDICAL_LEAVE = 'MEDICAL_LEAVE', 'Medical Leave'

    class AttemptType(models.TextChoices):
        REGULAR = 'REGULAR', 'Regular'
        RETEST = 'RETEST', 'Retest'
        IMPROVEMENT = 'IMPROVEMENT', 'Improvement'

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='exam_results')
    attempt_number = models.PositiveSmallIntegerField(default=1)
    attempt_type = models.CharField(max_length=15, choices=AttemptType.choices, default=AttemptType.REGULAR)

    attendance_status = models.CharField(max_length=15, choices=AttendanceStatus.choices, default=AttendanceStatus.PRESENT)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=5, blank=True)
    pass_status = models.BooleanField(null=True, blank=True)
    is_latest = models.BooleanField(default=True)

    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    entered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attempt_number']
        unique_together = ('exam', 'student', 'attempt_number')

    def __str__(self):
        return f"{self.student} - {self.exam} (Attempt {self.attempt_number})"

    def clean(self):
        if self.marks_obtained is not None and self.marks_obtained > self.exam.max_marks:
            raise ValidationError({'marks_obtained': 'Marks cannot exceed the exam maximum marks.'})

    def save(self, *args, **kwargs):
        # Auto pass/fail + grade calculation, and keep only one "latest" attempt per student/exam.
        if self.attendance_status != self.AttendanceStatus.PRESENT:
            self.pass_status = False
            self.grade = self.grade or 'AB'
        elif self.marks_obtained is not None:
            percentage = (self.marks_obtained / self.exam.max_marks) * 100
            self.pass_status = percentage >= 40
            self.grade = self._grade_for_percentage(percentage)

        super().save(*args, **kwargs)

        if self.is_latest:
            ExamResult.objects.filter(
                exam=self.exam, student=self.student
            ).exclude(pk=self.pk).update(is_latest=False)

    @staticmethod
    def _grade_for_percentage(pct):
        if pct >= 90:
            return 'A+'
        if pct >= 80:
            return 'A'
        if pct >= 70:
            return 'B+'
        if pct >= 60:
            return 'B'
        if pct >= 50:
            return 'C'
        if pct >= 40:
            return 'D'
        return 'F'
=======
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
        RESULTS_PENDING = 'results_pending', 'Results Pending'
        PUBLISHED = 'published', 'Published'
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
>>>>>>> origin/main

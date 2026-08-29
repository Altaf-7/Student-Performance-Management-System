from django.db import models
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

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Examination(models.Model):
    class ExamType(models.TextChoices):
        MIDTERM = "MIDTERM", "Midterm"
        END_TERM = "END_TERM", "End-term"
        QUIZ = "QUIZ", "Quiz"
        PRACTICAL = "PRACTICAL", "Practical"
        INTERNAL = "INTERNAL", "Internal Assessment"

    name = models.CharField(max_length=150)
    exam_type = models.CharField(max_length=15, choices=ExamType.choices)
    course = models.ForeignKey("academics.Course", on_delete=models.CASCADE, related_name="examinations")
    semester = models.ForeignKey("academics.Semester", on_delete=models.CASCADE, related_name="examinations")
    academic_year = models.CharField(max_length=20)
    exam_date = models.DateField()
    maximum_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="examinations_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-exam_date"]
        indexes = [models.Index(fields=["course", "semester"])]

    def __str__(self):
        return f"{self.name} - {self.course.course_code}"


class ExamResult(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exam_results",
        limit_choices_to={"role": "STUDENT"},
    )
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE, related_name="results")
    course = models.ForeignKey("academics.Course", on_delete=models.CASCADE, related_name="exam_results")
    maximum_marks = models.DecimalField(max_digits=6, decimal_places=2)
    obtained_marks = models.DecimalField(max_digits=6, decimal_places=2)
    grade = models.CharField(max_length=5, blank=True)
    remarks = models.TextField(blank=True)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="results_entered")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "examination"], name="unique_result_per_exam")
        ]
        indexes = [models.Index(fields=["student", "course"])]

    def clean(self):
        if self.obtained_marks is not None and self.maximum_marks is not None:
            if self.obtained_marks > self.maximum_marks:
                raise ValidationError("Obtained marks cannot exceed maximum marks.")
            if self.obtained_marks < 0:
                raise ValidationError("Obtained marks cannot be negative.")

    def save(self, *args, **kwargs):
        from apps.academics.services import calculate_percentage, calculate_grade
        self.full_clean()
        pct = calculate_percentage(self.obtained_marks, self.maximum_marks)
        self.grade, _ = calculate_grade(pct)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.examination} - {self.obtained_marks}/{self.maximum_marks}"

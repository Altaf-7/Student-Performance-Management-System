from django.db import models
from django.conf import settings


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=30, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['roll_number']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.roll_number})"


class StudentCourse(models.Model):
    """A student's enrollment in a course. A student can have multiple of these over time
    (e.g. graduated from one course, pursuing another), preserving academic history."""

    class Status(models.TextChoices):
        PURSUING = 'PURSUING', 'Pursuing'
        GRADUATED = 'GRADUATED', 'Graduated'
        DROPPED = 'DROPPED', 'Dropped'

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='course_history')
    course_batch = models.ForeignKey('academics.CourseBatch', on_delete=models.CASCADE, related_name='enrolled_students')
    admission_year = models.PositiveIntegerField()
    completion_year = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PURSUING)

    class Meta:
        ordering = ['-admission_year']

    def __str__(self):
        return f"{self.student} - {self.course_batch.course} ({self.get_status_display()})"


class StudentSemester(models.Model):
    """Links a student's course enrollment to a specific semester they are/were enrolled in."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='semester_enrollments')
    student_course = models.ForeignKey(StudentCourse, on_delete=models.CASCADE, related_name='semesters')
    semester = models.ForeignKey('academics.Semester', on_delete=models.CASCADE, related_name='enrolled_students')

    class Meta:
        unique_together = ('student', 'semester')
        ordering = ['semester__number']

    def __str__(self):
        return f"{self.student} - {self.semester}"


class SemesterResult(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PASS_ = 'PASS', 'Pass'
        FAIL = 'FAIL', 'Fail'

    student_semester = models.OneToOneField(StudentSemester, on_delete=models.CASCADE, related_name='result')
    total_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    obtained_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    sgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    declared_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Result: {self.student_semester}"


class StudentGraduation(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='graduations')
    student_course = models.OneToOneField(StudentCourse, on_delete=models.CASCADE, related_name='graduation')
    graduation_date = models.DateField()
    final_cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Graduation - {self.student}"

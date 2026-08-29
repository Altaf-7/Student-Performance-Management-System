from django.db import models
from django.conf import settings

<<<<<<< HEAD

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
=======
class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    enrollment_no = models.CharField(max_length=50, unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    class GenderChoices(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'
        
    gender = models.CharField(max_length=1, choices=GenderChoices.choices, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_contact = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} ({self.enrollment_no})"

class StudentCourse(models.Model):
    class StatusChoices(models.TextChoices):
        PURSUING = 'pursuing', 'Pursuing'
        GRADUATED = 'graduated', 'Graduated'
        DROPPED = 'dropped', 'Dropped'
        DETAINED = 'detained', 'Detained'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='courses_enrolled')
    course = models.ForeignKey('academics.Course', on_delete=models.CASCADE, related_name='students')
    course_batch = models.ForeignKey('academics.CourseBatch', on_delete=models.CASCADE, related_name='students')
    admission_year = models.IntegerField()
    completion_year = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PURSUING)

    def __str__(self):
        return f"{self.student.enrollment_no} - {self.course.code}"

class StudentSemester(models.Model):
    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        BACKLOG = 'backlog', 'Backlog'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='semesters')
    semester = models.ForeignKey('academics.Semester', on_delete=models.CASCADE, related_name='students')
    academic_year = models.CharField(max_length=9)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'semester', 'academic_year'], name='unique_student_semester')
        ]

    def __str__(self):
        return f"{self.student.enrollment_no} - {self.semester}"

class StudentGraduation(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='graduation_record')
    graduation_date = models.DateField()
    final_cgpa = models.DecimalField(max_digits=4, decimal_places=2) # e.g. 10.00
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Graduation: {self.student.enrollment_no}"
>>>>>>> origin/main

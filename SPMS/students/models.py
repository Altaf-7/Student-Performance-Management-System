from django.db import models
from django.conf import settings

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

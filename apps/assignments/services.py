"""Assignment business logic kept out of views/templates."""
from django.utils import timezone

from .models import AssignmentSubmission


def determine_submission_status(assignment, submission_time=None) -> str:
    """A submission is LATE if made after the assignment due date,
    otherwise SUBMITTED. Grading later moves it to GRADED."""
    submission_time = submission_time or timezone.now()
    if submission_time > assignment.due_date:
        return AssignmentSubmission.Status.LATE
    return AssignmentSubmission.Status.SUBMITTED


def grade_submission(submission, marks_obtained, feedback, grader):
    if marks_obtained > submission.assignment.maximum_marks:
        raise ValueError("Marks obtained cannot exceed the assignment's maximum marks.")
    submission.marks_obtained = marks_obtained
    submission.feedback = feedback
    submission.graded_by = grader
    submission.graded_at = timezone.now()
    submission.status = AssignmentSubmission.Status.GRADED
    submission.full_clean()
    submission.save()
    return submission


def assignment_completion_rate(student):
    """Fraction of a student's assigned work that has been submitted
    (submitted/late/graded) vs the total assignments across their
    enrolled courses. Used by the risk-detection service."""
    from apps.academics.models import Enrollment

    course_ids = Enrollment.objects.filter(student=student).values_list("course_id", flat=True)
    total = 0
    completed = 0
    from .models import Assignment
    for assignment in Assignment.objects.filter(course_id__in=course_ids):
        total += 1
        if AssignmentSubmission.objects.filter(assignment=assignment, student=student).exclude(
            status=AssignmentSubmission.Status.PENDING
        ).exists():
            completed += 1
    if total == 0:
        return 100.0
    return round((completed / total) * 100, 2)

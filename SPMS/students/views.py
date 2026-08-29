<<<<<<< HEAD
from django.shortcuts import render

# Create your views here.
=======
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.http import FileResponse, Http404
from django.views.generic import TemplateView, DetailView, ListView
from django.utils.decorators import method_decorator
from accounts.decorators import student_required
from students.models import Student, StudentCourse, StudentSemester
from academics.models import Semester, SubjectOffering
from attendance.models import Attendance
from assignments.models import Assignment, AssignmentSubmission
from examinations.models import Exam, ExamResult, SemesterReport
from students.forms import AssignmentSubmissionForm, StudentProfileUpdateForm
from django.views.generic.edit import FormMixin, UpdateView
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect

@method_decorator(student_required, name='dispatch')
class StudentDashboardView(TemplateView):
    template_name = 'student/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        context['student'] = student
        
        # Determine current active semester
        active_sem = StudentSemester.objects.filter(student=student, status='active').first()
        context['active_semester'] = active_sem
        
        # Dashboard stats to be expanded in later tasks
        return context

@method_decorator(student_required, name='dispatch')
class StudentProfileView(UpdateView):
    template_name = 'student/profile.html'
    form_class = StudentProfileUpdateForm
    
    def get_object(self):
        return self.request.user.student_profile
        
    def get_success_url(self):
        messages.success(self.request, "Profile updated successfully.")
        return reverse('students:profile')

@method_decorator(student_required, name='dispatch')
class StudentCourseView(ListView):
    template_name = 'student/course.html'
    context_object_name = 'student_courses'
    
    def get_queryset(self):
        return StudentCourse.objects.filter(
            student=self.request.user.student_profile
        ).select_related('course', 'course__department', 'course_batch')

@method_decorator(student_required, name='dispatch')
class SemesterListView(ListView):
    template_name = 'student/semesters.html'
    context_object_name = 'student_semesters'
    
    def get_queryset(self):
        return StudentSemester.objects.filter(
            student=self.request.user.student_profile
        ).select_related('semester', 'semester__course_batch__course')

@method_decorator(student_required, name='dispatch')
class SemesterDetailView(DetailView):
    template_name = 'student/semester_detail.html'
    context_object_name = 'student_semester'
    
    def get_object(self):
        return get_object_or_404(
            StudentSemester.objects.select_related('semester', 'semester__course_batch__course'),
            id=self.kwargs['pk'],
            student=self.request.user.student_profile
        )
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        semester = self.object.semester
        
        context['offerings'] = SubjectOffering.objects.filter(
            semester=semester
        ).select_related('subject', 'faculty', 'faculty__user')
        
        return context

@method_decorator(student_required, name='dispatch')
class SubjectListView(ListView):
    template_name = 'student/subjects.html'
    context_object_name = 'offerings'
    
    def get_queryset(self):
        student = self.request.user.student_profile
        active_sem = StudentSemester.objects.filter(student=student, status='active').first()
        if active_sem:
            return SubjectOffering.objects.filter(
                semester=active_sem.semester
            ).select_related('subject', 'faculty', 'faculty__user')
        return SubjectOffering.objects.none()

@method_decorator(student_required, name='dispatch')
class SubjectDetailView(DetailView):
    template_name = 'student/subject_detail.html'
    context_object_name = 'offering'
    
    def get_object(self):
        student = self.request.user.student_profile
        # A student can view an offering if they are enrolled in the semester of the offering
        offering = get_object_or_404(
            SubjectOffering.objects.select_related('subject', 'faculty', 'faculty__user', 'semester'),
            id=self.kwargs['pk']
        )
        is_enrolled = StudentSemester.objects.filter(student=student, semester=offering.semester).exists()
        if not is_enrolled:
            raise PermissionDenied("You are not enrolled in the semester for this subject.")
        return offering

@method_decorator(student_required, name='dispatch')
class AttendanceSummaryView(TemplateView):
    template_name = 'student/attendance_summary.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        # Determine all current offerings the student is enrolled in
        active_sem = StudentSemester.objects.filter(student=student, status='active').first()
        if not active_sem:
            context['attendance_data'] = []
            return context
            
        offerings = SubjectOffering.objects.filter(semester=active_sem.semester).select_related('subject')
        
        attendance_data = []
        for offering in offerings:
            total_lectures = offering.lectures.count()
            attended_lectures = Attendance.objects.filter(
                student=student, 
                lecture__offering=offering, 
                status=Attendance.StatusChoices.PRESENT
            ).count()
            
            percentage = (attended_lectures / total_lectures * 100) if total_lectures > 0 else 0
            attendance_data.append({
                'offering': offering,
                'total_lectures': total_lectures,
                'attended_lectures': attended_lectures,
                'percentage': round(percentage, 2)
            })
            
        context['attendance_data'] = attendance_data
        return context

@method_decorator(student_required, name='dispatch')
class SubjectAttendanceView(ListView):
    template_name = 'student/subject_attendance.html'
    context_object_name = 'attendances'
    
    def get_queryset(self):
        student = self.request.user.student_profile
        offering = get_object_or_404(SubjectOffering, id=self.kwargs['offering_id'])
        
        # Verify enrollment
        is_enrolled = StudentSemester.objects.filter(student=student, semester=offering.semester).exists()
        if not is_enrolled:
            raise PermissionDenied("You are not enrolled in the semester for this subject.")
            
        return Attendance.objects.filter(
            student=student, 
            lecture__offering=offering
        ).select_related('lecture').order_by('-lecture__date', '-lecture__start_time')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offering'] = get_object_or_404(SubjectOffering.objects.select_related('subject'), id=self.kwargs['offering_id'])
        return context

@method_decorator(student_required, name='dispatch')
class AssignmentListView(ListView):
    template_name = 'student/assignments.html'
    context_object_name = 'assignments'
    
    def get_queryset(self):
        student = self.request.user.student_profile
        active_sem = StudentSemester.objects.filter(student=student, status='active').first()
        if not active_sem:
            return Assignment.objects.none()
            
        return Assignment.objects.filter(
            offering__semester=active_sem.semester,
            status__in=[Assignment.StatusChoices.ACTIVE, Assignment.StatusChoices.CLOSED]
        ).select_related('offering', 'offering__subject').order_by('due_datetime')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        # Pre-fetch submissions for fast lookup in template
        submissions = AssignmentSubmission.objects.filter(student=student)
        context['submitted_assignment_ids'] = list(submissions.values_list('assignment_id', flat=True))
        context['submissions_dict'] = {sub.assignment_id: sub for sub in submissions}
        return context

@method_decorator(student_required, name='dispatch')
class AssignmentDetailView(DetailView):
    template_name = 'student/assignment_detail.html'
    context_object_name = 'assignment'
    
    def get_object(self):
        student = self.request.user.student_profile
        assignment = get_object_or_404(
            Assignment.objects.select_related('offering', 'offering__subject', 'offering__faculty', 'offering__faculty__user'),
            id=self.kwargs['pk']
        )
        # Ensure student is enrolled
        if not StudentSemester.objects.filter(student=student, semester=assignment.offering.semester).exists():
            raise PermissionDenied("You are not enrolled in the subject for this assignment.")
        return assignment
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        context['submission'] = AssignmentSubmission.objects.filter(assignment=self.object, student=student).first()
        context['form'] = AssignmentSubmissionForm()
        return context

@method_decorator(student_required, name='dispatch')
class AssignmentSubmitView(UpdateView): # Using UpdateView logic manually in post
    def post(self, request, *args, **kwargs):
        student = request.user.student_profile
        assignment = get_object_or_404(Assignment, id=self.kwargs['pk'])
        
        if not StudentSemester.objects.filter(student=student, semester=assignment.offering.semester).exists():
            raise PermissionDenied("Unauthorized access.")
            
        if assignment.status != Assignment.StatusChoices.ACTIVE:
            messages.error(request, "This assignment is closed for submission.")
            return redirect('students:assignment_detail', pk=assignment.id)
            
        submission = AssignmentSubmission.objects.filter(assignment=assignment, student=student).first()
        if submission:
            messages.error(request, "You have already submitted this assignment.")
            return redirect('students:assignment_detail', pk=assignment.id)
            
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = assignment
            sub.student = student
            # Status (SUBMITTED/LATE) will be calculated in model's save method
            sub.save()
            messages.success(request, "Assignment submitted successfully!")
        else:
            for error in form.errors.values():
                messages.error(request, error)
                
        return redirect('students:assignment_detail', pk=assignment.id)

@method_decorator(student_required, name='dispatch')
class DownloadSubmissionView(TemplateView):
    def get(self, request, pk, *args, **kwargs):
        student = self.request.user.student_profile
        submission = get_object_or_404(AssignmentSubmission, pk=pk, student=student)
        if not submission.submission_file:
            raise Http404("No file attached to this submission.")
        return FileResponse(submission.submission_file.open(), as_attachment=True, filename=submission.submission_file.name.split('/')[-1])

@method_decorator(student_required, name='dispatch')
class DownloadAssignmentAttachmentView(TemplateView):
    def get(self, request, pk, *args, **kwargs):
        student = self.request.user.student_profile
        assignment = get_object_or_404(Assignment, pk=pk)
        
        # Check authorization
        if not StudentSemester.objects.filter(student=student, semester=assignment.offering.semester).exists():
            raise PermissionDenied("You are not enrolled in the subject for this assignment.")
            
        if not assignment.file_attachment:
            raise Http404("No file attached to this assignment.")
        return FileResponse(assignment.file_attachment.open(), as_attachment=True, filename=assignment.file_attachment.name.split('/')[-1])

@method_decorator(student_required, name='dispatch')
class ExamListView(ListView):
    template_name = 'student/exams.html'
    context_object_name = 'exams'
    
    def get_queryset(self):
        student = self.request.user.student_profile
        active_sem = StudentSemester.objects.filter(student=student, status='active').first()
        if not active_sem:
            return Exam.objects.none()
            
        return Exam.objects.filter(
            offering__semester=active_sem.semester
        ).select_related('offering', 'offering__subject').order_by('exam_date')

@method_decorator(student_required, name='dispatch')
class ExamDetailView(DetailView):
    template_name = 'student/exam_detail.html'
    context_object_name = 'exam'
    
    def get_object(self):
        student = self.request.user.student_profile
        exam = get_object_or_404(
            Exam.objects.select_related('offering', 'offering__subject'),
            id=self.kwargs['pk']
        )
        if not StudentSemester.objects.filter(student=student, semester=exam.offering.semester).exists():
            raise PermissionDenied("Unauthorized access.")
        return exam
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        context['result'] = ExamResult.objects.filter(exam=self.object, student=student, is_latest=True).first()
        return context

@method_decorator(student_required, name='dispatch')
class ResultListView(ListView):
    template_name = 'student/results.html'
    context_object_name = 'results'
    
    def get_queryset(self):
        return ExamResult.objects.filter(
            student=self.request.user.student_profile,
            exam__status='published',
            is_latest=True
        ).select_related('exam', 'exam__offering', 'exam__offering__subject', 'exam__offering__semester').order_by('-exam__exam_date')

@method_decorator(student_required, name='dispatch')
class SemesterReportView(ListView):
    template_name = 'student/semester_reports.html'
    context_object_name = 'reports'
    
    def get_queryset(self):
        return SemesterReport.objects.filter(
            student=self.request.user.student_profile
        ).select_related('semester', 'semester__course_batch', 'semester__course_batch__course').order_by('-semester__semester_number')

@method_decorator(student_required, name='dispatch')
class PerformanceView(TemplateView):
    template_name = 'student/performance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        context['reports'] = SemesterReport.objects.filter(student=student).order_by('semester__semester_number')
        
        # Calculate overall SGPA average roughly if reports exist
        if context['reports'].exists():
            total_sgpa = sum(report.sgpa for report in context['reports'])
            context['overall_sgpa'] = total_sgpa / context['reports'].count()
            
        return context
>>>>>>> origin/main

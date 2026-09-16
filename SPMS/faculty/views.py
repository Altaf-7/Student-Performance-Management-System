from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.http import FileResponse, Http404
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Avg, Q
from django.contrib import messages
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from academics.models import SubjectOffering, Lecture, Semester
from students.models import StudentSemester, Student
from attendance.models import Attendance
from assignments.models import Assignment, AssignmentSubmission
from examinations.models import Exam, ExamResult
from examinations.services import calculate_grade, generate_semester_report
from faculty.forms import FacultyProfileForm, LectureForm, AssignmentForm, AssignmentGradingForm, ExamForm

class FacultyRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.RoleChoices.FACULTY

class FacultyDashboardView(FacultyRequiredMixin, TemplateView):
    template_name = 'faculty/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = self.request.user.faculty_profile
        
        # Stats
        offerings = SubjectOffering.objects.filter(faculty=faculty)
        context['assigned_subjects_count'] = offerings.count()
        
        # Get all students enrolled in semesters associated with these offerings
        semester_ids = offerings.values_list('semester_id', flat=True).distinct()
        students_count = StudentSemester.objects.filter(
            semester_id__in=semester_ids, 
            status__in=[StudentSemester.StatusChoices.ACTIVE, StudentSemester.StatusChoices.BACKLOG]
        ).values('student').distinct().count()
        context['total_students'] = students_count
        
        # Upcoming Exams
        upcoming_exams = Exam.objects.filter(
            offering__faculty=faculty, 
            exam_date__gte=timezone.now().date()
        ).order_by('exam_date')[:5]
        context['upcoming_exams'] = upcoming_exams

        # Pending Grading
        # Count submissions that don't have marks_awarded
        pending_grading = AssignmentSubmission.objects.filter(
            assignment__offering__faculty=faculty,
            marks_awarded__isnull=True
        ).count()
        context['pending_grading'] = pending_grading

        # Active Assignments
        active_assignments = Assignment.objects.filter(
            offering__faculty=faculty,
            status=Assignment.StatusChoices.ACTIVE
        ).count()
        context['active_assignments'] = active_assignments
        
        return context

class FacultyProfileView(FacultyRequiredMixin, UpdateView):
    template_name = 'faculty/profile.html'
    form_class = FacultyProfileForm
    success_url = reverse_lazy('faculty:profile')
    
    def get_object(self):
        return self.request.user.faculty_profile

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)

class DownloadSubmissionView(FacultyRequiredMixin, View):
    def get(self, request, pk):
        submission = get_object_or_404(AssignmentSubmission, pk=pk, assignment__offering__faculty=self.request.user.faculty_profile)
        if not submission.submission_file:
            raise Http404("No file attached to this submission.")
        return FileResponse(submission.submission_file.open(), as_attachment=True, filename=submission.submission_file.name.split('/')[-1])

class DownloadAssignmentAttachmentView(FacultyRequiredMixin, View):
    def get(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk, offering__faculty=self.request.user.faculty_profile)
        if not assignment.file_attachment:
            raise Http404("No file attached to this assignment.")
        return FileResponse(assignment.file_attachment.open(), as_attachment=True, filename=assignment.file_attachment.name.split('/')[-1])

# ==========================================
# SUBJECTS & STUDENTS
# ==========================================

class SubjectOfferingListView(FacultyRequiredMixin, ListView):
    template_name = 'faculty/subjects.html'
    context_object_name = 'offerings'
    
    def get_queryset(self):
        return SubjectOffering.objects.filter(faculty=self.request.user.faculty_profile).select_related('subject', 'semester__course_batch__course')

class SubjectOfferingDetailView(FacultyRequiredMixin, DetailView):
    template_name = 'faculty/subject_detail.html'
    context_object_name = 'offering'
    
    def get_queryset(self):
        return SubjectOffering.objects.filter(faculty=self.request.user.faculty_profile).select_related('subject', 'semester__course_batch__course')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offering = self.object
        context['students_count'] = StudentSemester.objects.filter(
            semester=offering.semester, 
            status__in=[StudentSemester.StatusChoices.ACTIVE, StudentSemester.StatusChoices.BACKLOG]
        ).count()
        context['recent_lectures'] = offering.lectures.order_by('-date', '-start_time')[:5]
        context['recent_assignments'] = offering.assignments.order_by('-assigned_at')[:5]
        context['upcoming_exams'] = offering.exams.order_by('exam_date')[:5]
        return context

class StudentListView(FacultyRequiredMixin, ListView):
    template_name = 'faculty/students.html'
    context_object_name = 'students'
    
    def get_queryset(self):
        offering_id = self.kwargs.get('pk')
        self.offering = get_object_or_404(SubjectOffering, pk=offering_id, faculty=self.request.user.faculty_profile)
        
        # Get students enrolled in the offering's semester
        student_semesters = StudentSemester.objects.filter(
            semester=self.offering.semester,
            status__in=[StudentSemester.StatusChoices.ACTIVE, StudentSemester.StatusChoices.BACKLOG]
        ).select_related('student__user')
        
        return student_semesters
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offering'] = self.offering
        return context

# ==========================================
# LECTURES
# ==========================================

class LectureListView(FacultyRequiredMixin, ListView):
    template_name = 'faculty/lectures.html'
    context_object_name = 'lectures'
    
    def get_queryset(self):
        offering_id = self.kwargs.get('offering_id')
        return Lecture.objects.filter(
            offering_id=offering_id,
            offering__faculty=self.request.user.faculty_profile
        ).order_by('-date', '-start_time')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offering'] = get_object_or_404(SubjectOffering, pk=self.kwargs.get('offering_id'), faculty=self.request.user.faculty_profile)
        return context

class LectureCreateView(FacultyRequiredMixin, CreateView):
    template_name = 'faculty/lecture_form.html'
    form_class = LectureForm
    
    def get_success_url(self):
        return reverse_lazy('faculty:lectures', kwargs={'offering_id': self.kwargs.get('offering_id')})
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offering'] = get_object_or_404(SubjectOffering, pk=self.kwargs.get('offering_id'), faculty=self.request.user.faculty_profile)
        return context
        
    def form_valid(self, form):
        offering = get_object_or_404(SubjectOffering, pk=self.kwargs.get('offering_id'), faculty=self.request.user.faculty_profile)
        form.instance.offering = offering
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Lecture created successfully.")
            return response
        except IntegrityError:
            form.add_error(None, "A lecture already exists for this slot.")
            return self.form_invalid(form)

class LectureDetailView(FacultyRequiredMixin, DetailView):
    template_name = 'faculty/lecture_detail.html'
    context_object_name = 'lecture'
    
    def get_queryset(self):
        return Lecture.objects.filter(offering__faculty=self.request.user.faculty_profile).select_related('offering__subject')

class LectureUpdateView(FacultyRequiredMixin, UpdateView):
    template_name = 'faculty/lecture_form.html'
    form_class = LectureForm
    
    def get_queryset(self):
        return Lecture.objects.filter(offering__faculty=self.request.user.faculty_profile)
        
    def get_success_url(self):
        messages.success(self.request, "Lecture updated successfully.")
        return reverse_lazy('faculty:lecture_detail', kwargs={'pk': self.object.pk})
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offering'] = self.object.offering
        return context

class LectureDeleteView(FacultyRequiredMixin, DeleteView):
    template_name = 'faculty/lecture_confirm_delete.html'
    
    def get_queryset(self):
        return Lecture.objects.filter(offering__faculty=self.request.user.faculty_profile)
    
    def get_success_url(self):
        return reverse_lazy('faculty:lectures', kwargs={'offering_id': self.object.offering.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Lecture deleted successfully.")
        return super().delete(request, *args, **kwargs)

# ==========================================
# ATTENDANCE
# ==========================================

class AttendanceEntryView(FacultyRequiredMixin, View):
    template_name = 'faculty/attendance_entry.html'
    
    def get_lecture(self, lecture_id):
        return get_object_or_404(Lecture, pk=lecture_id, offering__faculty=self.request.user.faculty_profile)
        
    def get_eligible_students(self, lecture):
        student_semesters = StudentSemester.objects.filter(
            semester=lecture.offering.semester,
            status__in=[StudentSemester.StatusChoices.ACTIVE, StudentSemester.StatusChoices.BACKLOG]
        ).select_related('student__user')
        return [ss.student for ss in student_semesters]

    def get(self, request, lecture_id):
        lecture = self.get_lecture(lecture_id)
        students = self.get_eligible_students(lecture)
        
        # Get existing attendance
        existing_attendances = {
            att.student_id: att.status 
            for att in Attendance.objects.filter(lecture=lecture)
        }
        
        student_data = []
        for student in students:
            student_data.append({
                'student': student,
                'status': existing_attendances.get(student.id, '')
            })
            
        context = {
            'lecture': lecture,
            'student_data': student_data,
        }
        return render(request, self.template_name, context)
        
    def post(self, request, lecture_id):
        lecture = self.get_lecture(lecture_id)
        students = self.get_eligible_students(lecture)
        valid_student_ids = {student.id for student in students}
        
        try:
            with transaction.atomic():
                for student in students:
                    status = request.POST.get(f'status_{student.id}')
                    if status in [Attendance.StatusChoices.PRESENT, Attendance.StatusChoices.ABSENT]:
                        Attendance.objects.update_or_create(
                            student=student,
                            lecture=lecture,
                            defaults={'status': status}
                        )
            messages.success(request, "Attendance saved successfully.")
        except Exception as e:
            messages.error(request, f"Error saving attendance: {e}")
            
        return redirect('faculty:lecture_detail', pk=lecture.id)

class AttendanceSummaryView(FacultyRequiredMixin, TemplateView):
    template_name = 'faculty/attendance_summary.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offering_id = self.kwargs.get('offering_id')
        offering = get_object_or_404(SubjectOffering, pk=offering_id, faculty=self.request.user.faculty_profile)
        
        students = [ss.student for ss in StudentSemester.objects.filter(
            semester=offering.semester,
            status__in=[StudentSemester.StatusChoices.ACTIVE, StudentSemester.StatusChoices.BACKLOG]
        ).select_related('student__user')]
        
        total_lectures = Lecture.objects.filter(offering=offering).count()
        
        summary_data = []
        if total_lectures > 0:
            for student in students:
                present_count = Attendance.objects.filter(
                    lecture__offering=offering,
                    student=student,
                    status=Attendance.StatusChoices.PRESENT
                ).count()
                absent_count = Attendance.objects.filter(
                    lecture__offering=offering,
                    student=student,
                    status=Attendance.StatusChoices.ABSENT
                ).count()
                
                attendance_percentage = (present_count / total_lectures) * 100 if total_lectures > 0 else 0
                
                summary_data.append({
                    'student': student,
                    'present': present_count,
                    'absent': absent_count,
                    'percentage': round(attendance_percentage, 2)
                })
        
        context['offering'] = offering
        context['summary_data'] = summary_data
        context['total_lectures'] = total_lectures
        return context

# ==========================================
# ASSIGNMENTS
# ==========================================

class AssignmentListView(FacultyRequiredMixin, ListView):
    template_name = 'faculty/assignments.html'
    context_object_name = 'assignments'
    
    def get_queryset(self):
        return Assignment.objects.filter(offering__faculty=self.request.user.faculty_profile).select_related('offering__subject').order_by('-assigned_at')

class AssignmentCreateView(FacultyRequiredMixin, CreateView):
    template_name = 'faculty/assignment_form.html'
    form_class = AssignmentForm
    success_url = reverse_lazy('faculty:assignments')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['faculty'] = self.request.user.faculty_profile
        return kwargs
        
    def get_initial(self):
        initial = super().get_initial()
        offering_id = self.request.GET.get('offering')
        if offering_id:
            initial['offering'] = offering_id
        return initial
        
    def form_valid(self, form):
        messages.success(self.request, "Assignment created successfully.")
        return super().form_valid(form)

class AssignmentDetailView(FacultyRequiredMixin, DetailView):
    template_name = 'faculty/assignment_detail.html'
    context_object_name = 'assignment'
    
    def get_queryset(self):
        return Assignment.objects.filter(offering__faculty=self.request.user.faculty_profile).select_related('offering__subject')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment = self.object
        submissions = assignment.submissions.all()
        
        # Calculate total eligible students
        total_enrolled = StudentSemester.objects.filter(
            semester=assignment.offering.semester,
            status__in=[StudentSemester.StatusChoices.ACTIVE, StudentSemester.StatusChoices.BACKLOG]
        ).count()
        
        submitted = submissions.filter(status=AssignmentSubmission.StatusChoices.SUBMITTED).count()
        late = submissions.filter(status=AssignmentSubmission.StatusChoices.LATE).count()
        
        total_submissions = submitted + late
        not_submitted = total_enrolled - total_submissions
        if not_submitted < 0:
            not_submitted = 0
            
        graded = submissions.filter(marks_awarded__isnull=False).count()
        pending_grading = total_submissions - graded
        
        context['stats'] = {
            'total_enrolled': total_enrolled,
            'submitted': submitted,
            'late': late,
            'not_submitted': not_submitted,
            'graded': graded,
            'pending_grading': pending_grading,
        }
        
        # Calculate average marks
        graded_submissions = submissions.filter(marks_awarded__isnull=False)
        if graded_submissions.exists():
            context['average_marks'] = round(graded_submissions.aggregate(Avg('marks_awarded'))['marks_awarded__avg'], 2)
        else:
            context['average_marks'] = None
            
        return context

class AssignmentUpdateView(FacultyRequiredMixin, UpdateView):
    template_name = 'faculty/assignment_form.html'
    form_class = AssignmentForm
    
    def get_queryset(self):
        return Assignment.objects.filter(offering__faculty=self.request.user.faculty_profile)
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['faculty'] = self.request.user.faculty_profile
        return kwargs
        
    def get_success_url(self):
        messages.success(self.request, "Assignment updated successfully.")
        return reverse_lazy('faculty:assignment_detail', kwargs={'pk': self.object.pk})

class AssignmentDeleteView(FacultyRequiredMixin, DeleteView):
    template_name = 'faculty/assignment_confirm_delete.html'
    success_url = reverse_lazy('faculty:assignments')
    
    def get_queryset(self):
        return Assignment.objects.filter(offering__faculty=self.request.user.faculty_profile)
        
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Assignment deleted successfully.")
        return super().delete(request, *args, **kwargs)

class SubmissionListView(FacultyRequiredMixin, ListView):
    template_name = 'faculty/submissions.html'
    context_object_name = 'submissions'
    
    def get_queryset(self):
        assignment_id = self.kwargs.get('assignment_id')
        self.assignment = get_object_or_404(Assignment, pk=assignment_id, offering__faculty=self.request.user.faculty_profile)
        return AssignmentSubmission.objects.filter(assignment=self.assignment).select_related('student__user').order_by('-submitted_at')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = self.assignment
        return context

class SubmissionDetailView(FacultyRequiredMixin, UpdateView):
    template_name = 'faculty/submission_detail.html'
    form_class = AssignmentGradingForm
    
    def get_queryset(self):
        return AssignmentSubmission.objects.filter(assignment__offering__faculty=self.request.user.faculty_profile).select_related('assignment', 'student__user')
        
    def form_valid(self, form):
        # The graded_at logic could be handled here or by model triggers
        # By default we just update it if we're awarding marks.
        if form.instance.marks_awarded is not None:
            form.instance.graded_at = timezone.now()
            
        messages.success(self.request, "Grade saved successfully.")
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('faculty:submission_detail', kwargs={'pk': self.object.pk})

# ==========================================
# EXAMS & RESULTS
# ==========================================

class ExamListView(FacultyRequiredMixin, ListView):
    template_name = 'faculty/exams.html'
    context_object_name = 'exams'
    
    def get_queryset(self):
        return Exam.objects.filter(offering__faculty=self.request.user.faculty_profile).select_related('offering__subject').order_by('-exam_date')

class ExamCreateView(FacultyRequiredMixin, CreateView):
    template_name = 'faculty/exam_form.html'
    form_class = ExamForm
    success_url = reverse_lazy('faculty:exams')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['faculty'] = self.request.user.faculty_profile
        return kwargs
        
    def get_initial(self):
        initial = super().get_initial()
        offering_id = self.request.GET.get('offering')
        if offering_id:
            initial['offering'] = offering_id
        return initial
        
    def form_valid(self, form):
        messages.success(self.request, "Exam created successfully.")
        return super().form_valid(form)

class ExamDetailView(FacultyRequiredMixin, DetailView):
    template_name = 'faculty/exam_detail.html'
    context_object_name = 'exam'
    
    def get_queryset(self):
        return Exam.objects.filter(offering__faculty=self.request.user.faculty_profile).select_related('offering__subject')

class ExamUpdateView(FacultyRequiredMixin, UpdateView):
    template_name = 'faculty/exam_form.html'
    form_class = ExamForm
    
    def get_queryset(self):
        return Exam.objects.filter(offering__faculty=self.request.user.faculty_profile)
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['faculty'] = self.request.user.faculty_profile
        return kwargs
        
    def get_success_url(self):
        messages.success(self.request, "Exam updated successfully.")
        return reverse_lazy('faculty:exam_detail', kwargs={'pk': self.object.pk})

class ExamDeleteView(FacultyRequiredMixin, DeleteView):
    template_name = 'faculty/exam_confirm_delete.html'
    success_url = reverse_lazy('faculty:exams')
    
    def get_queryset(self):
        return Exam.objects.filter(offering__faculty=self.request.user.faculty_profile)
        
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Exam deleted successfully.")
        return super().delete(request, *args, **kwargs)

class ExamResultEntryView(FacultyRequiredMixin, View):
    template_name = 'faculty/exam_results.html'
    
    def get_exam(self, exam_id):
        return get_object_or_404(Exam, pk=exam_id, offering__faculty=self.request.user.faculty_profile)
        
    def get_eligible_students(self, exam):
        student_semesters = StudentSemester.objects.filter(
            semester=exam.offering.semester,
            status__in=[StudentSemester.StatusChoices.ACTIVE, StudentSemester.StatusChoices.BACKLOG]
        ).select_related('student__user')
        return [ss.student for ss in student_semesters]

    def get(self, request, exam_id):
        exam = self.get_exam(exam_id)
        students = self.get_eligible_students(exam)
        
        # Get existing results
        existing_results = {
            res.student_id: res 
            for res in ExamResult.objects.filter(exam=exam, is_latest=True)
        }
        
        student_data = []
        for student in students:
            result = existing_results.get(student.id)
            student_data.append({
                'student': student,
                'attendance_status': result.attendance_status if result else ExamResult.AttendanceStatus.PRESENT,
                'marks_obtained': result.marks_obtained if result else '',
                'grade': result.grade if result else ''
            })
            
        context = {
            'exam': exam,
            'student_data': student_data,
            'attendance_choices': ExamResult.AttendanceStatus.choices,
        }
        return render(request, self.template_name, context)
        
    def post(self, request, exam_id):
        exam = self.get_exam(exam_id)
        students = self.get_eligible_students(exam)
        
        try:
            with transaction.atomic():
                for student in students:
                    att_status = request.POST.get(f'attendance_{student.id}')
                    marks = request.POST.get(f'marks_{student.id}')
                    
                    if att_status:
                        # Convert empty string marks to None
                        marks_val = float(marks) if marks else None
                        
                        # Validate based on attendance
                        if att_status in [ExamResult.AttendanceStatus.ABSENT, ExamResult.AttendanceStatus.MEDICAL_LEAVE]:
                            marks_val = None
                        elif marks_val is not None and marks_val > float(exam.total_marks):
                            raise ValueError(f"Marks for {student.enrollment_no} exceed total marks.")
                            
                        if att_status == ExamResult.AttendanceStatus.PRESENT and marks_val is None:
                            continue # Ignore empty entries for present students unless they want to grade them later
                            
                        # Calculate grade and status
                        grade, status = calculate_grade(marks_val, float(exam.total_marks))
                            
                        # Update or Create
                        # Assuming regular attempts for simplicity, a more complex system would handle attempt numbers
                        # but we update the existing 'latest' attempt or create first attempt
                        obj, created = ExamResult.objects.update_or_create(
                            exam=exam,
                            student=student,
                            attempt_number=1, # simplified
                            defaults={
                                'attendance_status': att_status,
                                'marks_obtained': marks_val,
                                'attempt_type': ExamResult.AttemptType.REGULAR,
                                'is_latest': True,
                                'grade': grade,
                                'result_status': status
                            }
                        )
                
                if exam.status == Exam.StatusChoices.COMPLETED:
                    exam.status = Exam.StatusChoices.RESULTS_PENDING
                    exam.save()
                    
            messages.success(request, "Exam results saved successfully.")
        except ValueError as ve:
            messages.error(request, str(ve))
        except Exception as e:
            messages.error(request, f"Error saving results: {e}")
            
        return redirect('faculty:exam_detail', pk=exam.id)

# ==========================================
# PERFORMANCE
# ==========================================

class FacultyPerformanceView(FacultyRequiredMixin, TemplateView):
    template_name = 'faculty/performance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # We can build a basic summary here, e.g. average marks per assignment for this faculty
        faculty = self.request.user.faculty_profile
        
        context['offerings'] = SubjectOffering.objects.filter(faculty=faculty).select_related('subject')
        return context


class ExamPublishView(FacultyRequiredMixin, View):
    def post(self, request, exam_id):
        exam = get_object_or_404(Exam, pk=exam_id, offering__faculty=self.request.user.faculty_profile)
        if exam.status == Exam.StatusChoices.RESULTS_PENDING:
            exam.status = Exam.StatusChoices.PUBLISHED
            exam.save()
            messages.success(request, 'Results published successfully. Students can now view their grades.')
        else:
            messages.error(request, 'Exam results are not pending or have already been published.')
        return redirect('faculty:exam_detail', pk=exam.id)


from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from accounts.decorators import student_required
from django.utils.decorators import method_decorator
from reports.services.student_services import (
    get_student_academic_overview,
    get_student_attendance_report,
    get_student_assignment_report,
    get_student_exam_report
)

class StudentReportMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'student'

@method_decorator(student_required, name='dispatch')
class StudentReportDashboardView(StudentReportMixin, TemplateView):
    template_name = 'reports/student/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        context['overview'] = get_student_academic_overview(student)
        return context

@method_decorator(student_required, name='dispatch')
class StudentAttendanceReportView(StudentReportMixin, TemplateView):
    template_name = 'reports/student/attendance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        context['attendance_report'] = get_student_attendance_report(student)
        return context

@method_decorator(student_required, name='dispatch')
class StudentAssignmentReportView(StudentReportMixin, TemplateView):
    template_name = 'reports/student/assignments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        report = get_student_assignment_report(student)
        context['assignment_report'] = report
        
        # Summary stats
        total = len(report)
        submitted = sum(1 for r in report if r['status'] in ['Submitted', 'Late'])
        late = sum(1 for r in report if r['status'] == 'Late')
        not_submitted = total - submitted
        graded = sum(1 for r in report if r['graded'])
        pending_grading = submitted - graded
        
        context['summary'] = {
            'total': total,
            'submitted': submitted,
            'late': late,
            'not_submitted': not_submitted,
            'graded': graded,
            'pending_grading': pending_grading,
            'submission_rate': round((submitted / total) * 100, 1) if total > 0 else 0
        }
        return context

@method_decorator(student_required, name='dispatch')
class StudentExamReportView(StudentReportMixin, TemplateView):
    template_name = 'reports/student/exams.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        results = get_student_exam_report(student)
        context['exam_results'] = results
        
        total = len(results)
        passed = sum(1 for r in results if r.result_status == 'Pass')
        failed = sum(1 for r in results if r.result_status == 'Fail')
        
        marks_obtained = sum(r.marks_obtained for r in results if r.marks_obtained is not None)
        marks_total = sum(r.exam.total_marks for r in results if r.marks_obtained is not None)
        
        context['summary'] = {
            'total': total,
            'passed': passed,
            'failed': failed,
            'average_percentage': round((marks_obtained / marks_total) * 100, 1) if marks_total > 0 else 0,
        }
        return context

@method_decorator(student_required, name='dispatch')
class StudentSemesterReportView(StudentReportMixin, TemplateView):
    template_name = 'reports/student/semesters.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        context['reports'] = student.semester_reports.order_by('-semester__semester_number')
        return context

@method_decorator(student_required, name='dispatch')
class StudentAnalyticsView(StudentReportMixin, TemplateView):
    template_name = 'reports/student/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        # Prepare Chart Data
        semesters = student.semester_reports.order_by('semester__semester_number')
        sgpa_labels = [f"Sem {s.semester.semester_number}" for s in semesters]
        sgpa_data = [float(s.sgpa) for s in semesters]
        
        attendance = get_student_attendance_report(student)
        att_labels = [a['subject'].code for a in attendance]
        att_data = [a['attendance_percentage'] for a in attendance]
        
        context['chart_data'] = {
            'sgpa_labels': sgpa_labels,
            'sgpa_data': sgpa_data,
            'att_labels': att_labels,
            'att_data': att_data,
        }
        return context

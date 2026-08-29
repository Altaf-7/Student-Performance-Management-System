from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from accounts.decorators import faculty_required
from django.utils.decorators import method_decorator
from academics.models import SubjectOffering
from reports.services.faculty_services import (
    get_faculty_overview,
    get_faculty_attendance_report,
    get_faculty_assignment_report,
    get_faculty_exam_report,
    get_faculty_student_performance
)

class FacultyReportMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'faculty'

@method_decorator(faculty_required, name='dispatch')
class FacultyReportDashboardView(FacultyReportMixin, TemplateView):
    template_name = 'reports/faculty/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = self.request.user.faculty_profile
        context['overview'] = get_faculty_overview(faculty)
        return context

@method_decorator(faculty_required, name='dispatch')
class FacultyAttendanceReportView(FacultyReportMixin, TemplateView):
    template_name = 'reports/faculty/attendance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = self.request.user.faculty_profile
        context['reports'] = get_faculty_attendance_report(faculty)
        return context

@method_decorator(faculty_required, name='dispatch')
class FacultyAssignmentReportView(FacultyReportMixin, TemplateView):
    template_name = 'reports/faculty/assignments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = self.request.user.faculty_profile
        context['reports'] = get_faculty_assignment_report(faculty)
        return context

@method_decorator(faculty_required, name='dispatch')
class FacultyExamReportView(FacultyReportMixin, TemplateView):
    template_name = 'reports/faculty/exams.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = self.request.user.faculty_profile
        context['reports'] = get_faculty_exam_report(faculty)
        return context

@method_decorator(faculty_required, name='dispatch')
class FacultyStudentPerformanceView(FacultyReportMixin, TemplateView):
    template_name = 'reports/faculty/students.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = self.request.user.faculty_profile
        
        offering_id = self.request.GET.get('offering_id')
        context['offerings'] = SubjectOffering.objects.filter(faculty=faculty).select_related('subject', 'semester', 'semester__course_batch')
        
        if offering_id:
            context['performance_data'] = get_faculty_student_performance(faculty, offering_id)
            context['selected_offering_id'] = int(offering_id)
            
        return context

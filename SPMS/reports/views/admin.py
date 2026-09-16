import csv
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import UserPassesTestMixin
from accounts.decorators import admin_required
from django.utils.decorators import method_decorator
from reports.services.admin_services import (
    get_admin_dashboard_overview,
    get_enrollment_report,
    get_department_report,
    get_course_report,
    get_batch_report,
    get_semester_report_admin,
    get_offering_report
)
from reports.services.analytics_services import (
    get_admin_analytics_data,
    get_at_risk_students
)

class AdminReportMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.role == 'admin' or self.request.user.is_superuser)

@method_decorator(admin_required, name='dispatch')
class AdminReportDashboardView(AdminReportMixin, TemplateView):
    template_name = 'reports/admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['overview'] = get_admin_dashboard_overview()
        return context

@method_decorator(admin_required, name='dispatch')
class EnrollmentReportView(AdminReportMixin, TemplateView):
    template_name = 'reports/admin/enrollment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enrollments'] = get_enrollment_report()
        return context

@method_decorator(admin_required, name='dispatch')
class DepartmentReportView(AdminReportMixin, TemplateView):
    template_name = 'reports/admin/departments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reports'] = get_department_report()
        return context

@method_decorator(admin_required, name='dispatch')
class CourseReportView(AdminReportMixin, TemplateView):
    template_name = 'reports/admin/courses.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Handle GET filter
        dept_id = self.request.GET.get('department_id')
        filters = {}
        if dept_id:
            filters['department_id'] = dept_id
        context['reports'] = get_course_report(filters)
        return context

@method_decorator(admin_required, name='dispatch')
class BatchReportView(AdminReportMixin, TemplateView):
    template_name = 'reports/admin/batches.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reports'] = get_batch_report()
        return context

@method_decorator(admin_required, name='dispatch')
class SemesterReportView(AdminReportMixin, TemplateView):
    template_name = 'reports/admin/semesters.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reports'] = get_semester_report_admin()
        return context

@method_decorator(admin_required, name='dispatch')
class SubjectOfferingReportView(AdminReportMixin, TemplateView):
    template_name = 'reports/admin/offerings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reports'] = get_offering_report()
        return context

@method_decorator(admin_required, name='dispatch')
class AdminAnalyticsView(AdminReportMixin, TemplateView):
    template_name = 'reports/admin/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['analytics'] = get_admin_analytics_data()
        return context

@method_decorator(admin_required, name='dispatch')
class AcademicMonitoringView(AdminReportMixin, TemplateView):
    template_name = 'reports/admin/at_risk.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['at_risk_students'] = get_at_risk_students()
        return context

@method_decorator(admin_required, name='dispatch')
class ExportAtRiskCSVView(AdminReportMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="at_risk_students.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Enrollment No', 'Student Name', 'Course', 'Semester', 'Risk Factors'])
        
        at_risk = get_at_risk_students()
        for item in at_risk:
            writer.writerow([
                item['student'].enrollment_no,
                item['student'].user.get_full_name(),
                item['student'].course.name,
                item['semester'].semester_number,
                "; ".join(item['reasons'])
            ])
            
        return response

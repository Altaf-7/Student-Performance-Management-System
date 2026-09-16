from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views import View

from apps.accounts.permissions import AdminRequiredMixin, FacultyRequiredMixin, StudentRequiredMixin
from apps.academics.models import Course, Semester
from .risk_service import get_at_risk_students, assess_student_risk
from .services import get_admin_dashboard_context, get_student_dashboard_context

User = get_user_model()


class AtRiskStudentsView(FacultyRequiredMixin, View):
    template_name = "analytics/at_risk.html"

    def get(self, request):
        if request.user.is_admin_role:
            students = User.objects.filter(role="STUDENT", is_active=True)
        else:
            course_ids = Course.objects.filter(faculty=request.user).values_list("id", flat=True)
            students = User.objects.filter(role="STUDENT", enrollments__course_id__in=course_ids).distinct()
        results = get_at_risk_students(students)
        return render(request, self.template_name, {"results": results})


class AdminAnalyticsView(AdminRequiredMixin, View):
    template_name = "analytics/admin_analytics.html"

    def get(self, request):
        context = get_admin_dashboard_context()
        return render(request, self.template_name, context)


class StudentAnalyticsView(StudentRequiredMixin, View):
    template_name = "analytics/student_analytics.html"

    def get(self, request):
        context = get_student_dashboard_context(request.user)
        return render(request, self.template_name, context)

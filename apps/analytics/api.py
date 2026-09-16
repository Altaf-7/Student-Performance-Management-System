from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import get_admin_dashboard_context, get_faculty_dashboard_context, get_student_dashboard_context


class AnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_admin_role:
            data = get_admin_dashboard_context()
            data.pop("recent_exams", None)
            data.pop("recent_announcements", None)
        elif user.is_faculty_role:
            data = get_faculty_dashboard_context(user)
            data = {
                "student_count": data["student_count"],
                "attendance_pending": data["attendance_pending"],
                "pending_grading": data["pending_grading"],
            }
        else:
            data = get_student_dashboard_context(user)
            data = {
                "cgpa": str(data["cgpa"]),
                "attendance": {"overall_percentage": str(data["attendance"]["overall_percentage"]), "overall_band": data["attendance"]["overall_band"]},
                "chart_grade_distribution": data["chart_grade_distribution"],
                "chart_gpa_trend": data["chart_gpa_trend"],
            }
        return Response(data)

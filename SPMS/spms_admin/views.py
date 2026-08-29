from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.urls import reverse

from spms_admin.mixins import AdminRequiredMixin
from accounts.models import User
from students.models import Student, StudentCourse, StudentSemester
from faculty.models import Faculty
from academics.models import Department, Course, CourseBatch, Semester, Subject, SubjectOffering
from assignments.models import Assignment
from examinations.models import Exam
from django.db import transaction
from django.db.models import ProtectedError
from django.utils.crypto import get_random_string
from .forms import StudentCreateForm, FacultyCreateForm

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'spms_admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Users stats
        context['total_users'] = User.objects.count()
        context['total_students'] = Student.objects.count()
        context['total_faculty'] = Faculty.objects.count()
        
        # Academic stats
        context['total_departments'] = Department.objects.count()
        context['total_courses'] = Course.objects.count()
        context['active_batches'] = CourseBatch.objects.count()
        context['active_offerings'] = SubjectOffering.objects.count()
        
        # Activity stats
        context['upcoming_exams'] = Exam.objects.filter(status='scheduled').count()
        context['active_assignments'] = Assignment.objects.filter(status='active').count()
        
        # Recent users
        context['recent_students'] = Student.objects.select_related('user').order_by('-user__date_joined')[:5]
        context['recent_faculty'] = Faculty.objects.select_related('user', 'department').order_by('-user__date_joined')[:5]
        
        return context

class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'spms_admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().order_by('-date_joined')
        
        # Search
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(email__icontains=q) | qs.filter(first_name__icontains=q) | qs.filter(last_name__icontains=q)
            
        # Filter
        role = self.request.GET.get('role')
        if role:
            qs = qs.filter(role=role)
            
        status = self.request.GET.get('status')
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['role_filter'] = self.request.GET.get('role', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class UserDetailView(AdminRequiredMixin, DetailView):
    model = User
    template_name = 'spms_admin/user_detail.html'
    context_object_name = 'target_user'


class UserStatusUpdateView(AdminRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        
        if user == request.user:
            messages.error(request, "You cannot change your own status.")
            return redirect('spms_admin:user_detail', pk=pk)
            
        action = request.POST.get('action')
        if action == 'activate':
            user.is_active = True
            user.save()
            messages.success(request, f"User {user.email} activated successfully.")
        elif action == 'deactivate':
            user.is_active = False
            user.save()
            messages.success(request, f"User {user.email} deactivated successfully.")
            
        return redirect('spms_admin:user_detail', pk=pk)

# ==========================================
# STUDENT MANAGEMENT
# ==========================================

class StudentListView(AdminRequiredMixin, ListView):
    model = Student
    template_name = 'spms_admin/student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    
    def get_queryset(self):
        qs = super().get_queryset().select_related('user').order_by('-user__date_joined')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(user__first_name__icontains=q) | qs.filter(user__last_name__icontains=q) | qs.filter(enrollment_no__icontains=q)
        return qs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class StudentDetailView(AdminRequiredMixin, DetailView):
    model = Student
    template_name = 'spms_admin/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = self.object.courses_enrolled.select_related('course', 'course_batch').all()
        context['semesters'] = self.object.semesters.select_related('semester__course_batch').all()
        return context

class StudentCreateView(AdminRequiredMixin, View):
    def get(self, request):
        form = StudentCreateForm()
        return render(request, 'spms_admin/student_form.html', {'form': form})
        
    def post(self, request):
        form = StudentCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Create User
                    temp_password = get_random_string(10)
                    user = User.objects.create_user(
                        email=form.cleaned_data['email'],
                        password=temp_password,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        contact_number=form.cleaned_data['contact_number'],
                        role=User.RoleChoices.STUDENT
                    )
                    
                    # 2. Create Student Profile
                    student = Student.objects.create(
                        user=user,
                        enrollment_no=form.cleaned_data['enrollment_no'],
                        date_of_birth=form.cleaned_data['date_of_birth'],
                        gender=form.cleaned_data['gender'],
                        address=form.cleaned_data['address'],
                        guardian_name=form.cleaned_data['guardian_name'],
                        guardian_contact=form.cleaned_data['guardian_contact'],
                        emergency_contact=form.cleaned_data['emergency_contact']
                    )
                    
                    # 3. Create StudentCourse
                    StudentCourse.objects.create(
                        student=student,
                        course=form.cleaned_data['course'],
                        course_batch=form.cleaned_data['batch'],
                        admission_year=form.cleaned_data['admission_year'],
                        status=StudentCourse.StatusChoices.PURSUING
                    )
                    
                    # 4. Create StudentSemester
                    StudentSemester.objects.create(
                        student=student,
                        semester=form.cleaned_data['semester'],
                        academic_year=form.cleaned_data['batch'].academic_year, # using batch academic year for now
                        status=StudentSemester.StatusChoices.ACTIVE
                    )
                    
                messages.success(request, f"{user.email}|{temp_password}", extra_tags="credentials_modal")
                return redirect('spms_admin:students')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        
        return render(request, 'spms_admin/student_form.html', {'form': form})

# ==========================================
# FACULTY MANAGEMENT
# ==========================================

class FacultyListView(AdminRequiredMixin, ListView):
    model = Faculty
    template_name = 'spms_admin/faculty_list.html'
    context_object_name = 'faculties'
    paginate_by = 20
    
    def get_queryset(self):
        qs = super().get_queryset().select_related('user', 'department').order_by('-user__date_joined')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(user__first_name__icontains=q) | qs.filter(user__last_name__icontains=q) | qs.filter(user__email__icontains=q)
        return qs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class FacultyDetailView(AdminRequiredMixin, DetailView):
    model = Faculty
    template_name = 'spms_admin/faculty_detail.html'
    context_object_name = 'faculty'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offerings'] = self.object.subject_offerings.select_related('subject', 'semester__course_batch').all()
        return context

class FacultyCreateView(AdminRequiredMixin, View):
    def get(self, request):
        form = FacultyCreateForm()
        return render(request, 'spms_admin/faculty_form.html', {'form': form})
        
    def post(self, request):
        form = FacultyCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    temp_password = get_random_string(10)
                    user = User.objects.create_user(
                        email=form.cleaned_data['email'],
                        password=temp_password,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        contact_number=form.cleaned_data['contact_number'],
                        role=User.RoleChoices.FACULTY
                    )
                    
                    faculty = Faculty.objects.create(
                        user=user,
                        department=form.cleaned_data['department'],
                        designation=form.cleaned_data['designation'],
                        specialization=form.cleaned_data['specialization'],
                        qualification=form.cleaned_data['qualification'],
                        office_email=form.cleaned_data['office_email'],
                        office_contact=form.cleaned_data['office_contact'],
                        date_of_join=form.cleaned_data['date_of_join']
                    )
                    
                messages.success(request, f"{user.email}|{temp_password}", extra_tags="credentials_modal")
                return redirect('spms_admin:faculty_list')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        
        return render(request, 'spms_admin/faculty_form.html', {'form': form})

# ==========================================
# ACADEMIC STRUCTURE MANAGEMENT
# ==========================================

class ProtectedDeleteMixin:
    """Mixin to handle ProtectedError when deleting objects."""
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, "Cannot delete this item because it is referenced by other records (e.g. Students or Faculty).")
            return redirect(self.success_url)

# Department
class DepartmentListView(AdminRequiredMixin, ListView):
    model = Department
    template_name = 'spms_admin/generic_list.html'
    context_object_name = 'objects'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Departments'
        context['page_subtitle'] = 'Manage academic departments'
        context['create_url'] = reverse('spms_admin:department_create')
        context['columns'] = ['Name', 'Code', 'Contact', 'Email']
        context['fields'] = ['name', 'code', 'contact', 'email']
        context['edit_url_name'] = 'spms_admin:department_update'
        context['delete_url_name'] = 'spms_admin:department_delete'
        return context

class DepartmentCreateView(AdminRequiredMixin, CreateView):
    model = Department
    fields = '__all__'
    template_name = 'spms_admin/generic_form.html'
    success_url = reverse_lazy('spms_admin:department_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Department'
        context['back_url'] = reverse('spms_admin:department_list')
        return context

class DepartmentUpdateView(AdminRequiredMixin, UpdateView):
    model = Department
    fields = '__all__'
    template_name = 'spms_admin/generic_form.html'
    success_url = reverse_lazy('spms_admin:department_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Department'
        context['back_url'] = reverse('spms_admin:department_list')
        return context

class DepartmentDeleteView(AdminRequiredMixin, ProtectedDeleteMixin, DeleteView):
    model = Department
    template_name = 'spms_admin/generic_confirm_delete.html'
    success_url = reverse_lazy('spms_admin:department_list')

# Course
class CourseListView(AdminRequiredMixin, ListView):
    model = Course
    template_name = 'spms_admin/generic_list.html'
    context_object_name = 'objects'
    
    def get_queryset(self):
        return super().get_queryset().select_related('department')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Courses'
        context['page_subtitle'] = 'Manage academic courses'
        context['create_url'] = reverse('spms_admin:course_create')
        context['columns'] = ['Code', 'Name', 'Department', 'Duration (Years)']
        context['fields'] = ['code', 'name', 'department', 'duration_years']
        context['edit_url_name'] = 'spms_admin:course_update'
        context['delete_url_name'] = 'spms_admin:course_delete'
        return context

class CourseCreateView(AdminRequiredMixin, CreateView):
    model = Course
    fields = '__all__'
    template_name = 'spms_admin/generic_form.html'
    success_url = reverse_lazy('spms_admin:course_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Course'
        context['back_url'] = reverse('spms_admin:course_list')
        return context

class CourseUpdateView(AdminRequiredMixin, UpdateView):
    model = Course
    fields = '__all__'
    template_name = 'spms_admin/generic_form.html'
    success_url = reverse_lazy('spms_admin:course_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Course'
        context['back_url'] = reverse('spms_admin:course_list')
        return context

class CourseDeleteView(AdminRequiredMixin, ProtectedDeleteMixin, DeleteView):
    model = Course
    template_name = 'spms_admin/generic_confirm_delete.html'
    success_url = reverse_lazy('spms_admin:course_list')

# Course Batch
class CourseBatchListView(AdminRequiredMixin, ListView):
    model = CourseBatch
    template_name = 'spms_admin/generic_list.html'
    context_object_name = 'objects'
    
    def get_queryset(self):
        return super().get_queryset().select_related('course')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Course Batches'
        context['create_url'] = reverse('spms_admin:batch_create')
        context['columns'] = ['Course', 'Academic Year']
        context['fields'] = ['course', 'academic_year']
        context['edit_url_name'] = 'spms_admin:batch_update'
        context['delete_url_name'] = 'spms_admin:batch_delete'
        return context

class CourseBatchCreateView(AdminRequiredMixin, CreateView):
    model = CourseBatch
    fields = '__all__'
    template_name = 'spms_admin/generic_form.html'
    success_url = reverse_lazy('spms_admin:batch_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Course Batch'
        context['back_url'] = reverse('spms_admin:batch_list')
        return context

class CourseBatchUpdateView(AdminRequiredMixin, UpdateView):
    model = CourseBatch
    fields = '__all__'
    template_name = 'spms_admin/generic_form.html'
    success_url = reverse_lazy('spms_admin:batch_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Course Batch'
        context['back_url'] = reverse('spms_admin:batch_list')
        return context

class CourseBatchDeleteView(AdminRequiredMixin, ProtectedDeleteMixin, DeleteView):
    model = CourseBatch
    template_name = 'spms_admin/generic_confirm_delete.html'
    success_url = reverse_lazy('spms_admin:batch_list')

# Semester
class SemesterListView(AdminRequiredMixin, ListView):
    model = Semester
    template_name = 'spms_admin/generic_list.html'
    context_object_name = 'objects'
    
    def get_queryset(self):
        return super().get_queryset().select_related('course_batch__course')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Semesters'
        context['create_url'] = reverse('spms_admin:semester_create')
        context['columns'] = ['Course Batch', 'Semester Number']
        context['fields'] = ['course_batch', 'semester_number']
        context['edit_url_name'] = 'spms_admin:semester_update'
        context['delete_url_name'] = 'spms_admin:semester_delete'
        return context

class SemesterCreateView(AdminRequiredMixin, CreateView):
    model = Semester
    fields = '__all__'
    template_name = 'spms_admin/generic_form.html'
    success_url = reverse_lazy('spms_admin:semester_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Semester'
        context['back_url'] = reverse('spms_admin:semester_list')
        return context

class SemesterUpdateView(AdminRequiredMixin, UpdateView):
    model = Semester
    fields = '__all__'
    template_name = 'spms_admin/generic_form.html'
    success_url = reverse_lazy('spms_admin:semester_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Semester'
        context['back_url'] = reverse('spms_admin:semester_list')
        return context

class SemesterDeleteView(AdminRequiredMixin, ProtectedDeleteMixin, DeleteView):
    model = Semester
    template_name = 'spms_admin/generic_confirm_delete.html'
    success_url = reverse_lazy('spms_admin:semester_list')

# Subject
class SubjectListView(AdminRequiredMixin, ListView):
    model = Subject
    template_name = 'spms_admin/generic_list.html'
    context_object_name = 'objects'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Subjects'
        context['create_url'] = reverse('spms_admin:subject_create')
        context['columns'] = ['Code', 'Name']
        context['fields'] = ['code', 'name']
        context['edit_url_name'] = 'spms_admin:subject_update'
        context['delete_url_name'] = 'spms_admin:subject_delete'
        return context

class SubjectCreateView(AdminRequiredMixin, CreateView):
    model = Subject
    fields = '__all__'
    template_name = 'spms_admin/generic_form.html'
    success_url = reverse_lazy('spms_admin:subject_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Subject'
        context['back_url'] = reverse('spms_admin:subject_list')
        return context

class SubjectUpdateView(AdminRequiredMixin, UpdateView):
    model = Subject
    fields = '__all__'
    template_name = 'spms_admin/generic_form.html'
    success_url = reverse_lazy('spms_admin:subject_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Subject'
        context['back_url'] = reverse('spms_admin:subject_list')
        return context

class SubjectDeleteView(AdminRequiredMixin, ProtectedDeleteMixin, DeleteView):
    model = Subject
    template_name = 'spms_admin/generic_confirm_delete.html'
    success_url = reverse_lazy('spms_admin:subject_list')

# Subject Offering
class SubjectOfferingListView(AdminRequiredMixin, ListView):
    model = SubjectOffering
    template_name = 'spms_admin/generic_list.html'
    context_object_name = 'objects'
    
    def get_queryset(self):
        return super().get_queryset().select_related('subject', 'semester__course_batch', 'faculty__user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Subject Offerings'
        context['create_url'] = reverse('spms_admin:offering_create')
        context['columns'] = ['Subject', 'Semester', 'Faculty', 'Type', 'Credits']
        context['fields'] = ['subject', 'semester', 'faculty', 'subject_type', 'credits']
        context['edit_url_name'] = 'spms_admin:offering_update'
        context['delete_url_name'] = 'spms_admin:offering_delete'
        return context

class SubjectOfferingCreateView(AdminRequiredMixin, CreateView):
    model = SubjectOffering
    fields = '__all__'
    template_name = 'spms_admin/generic_form.html'
    success_url = reverse_lazy('spms_admin:offering_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Subject Offering'
        context['back_url'] = reverse('spms_admin:offering_list')
        return context

class SubjectOfferingUpdateView(AdminRequiredMixin, UpdateView):
    model = SubjectOffering
    fields = '__all__'
    template_name = 'spms_admin/generic_form.html'
    success_url = reverse_lazy('spms_admin:offering_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Subject Offering'
        context['back_url'] = reverse('spms_admin:offering_list')
        return context

class SubjectOfferingDeleteView(AdminRequiredMixin, ProtectedDeleteMixin, DeleteView):
    model = SubjectOffering
    template_name = 'spms_admin/generic_confirm_delete.html'
    success_url = reverse_lazy('spms_admin:offering_list')


# ==========================================
# ACCOUNT AND REPORTS
# ==========================================

class AdminProfileView(AdminRequiredMixin, TemplateView):
    template_name = 'spms_admin/admin_profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['admin_profile'] = self.request.user.admin_profile
        except:
            context['admin_profile'] = None
        return context

class AdminReportsView(AdminRequiredMixin, TemplateView):
    template_name = 'spms_admin/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Course distribution
        course_counts = []
        for course in Course.objects.all():
            course_counts.append({
                'course': course.code,
                'count': StudentCourse.objects.filter(course=course, status=StudentCourse.StatusChoices.PURSUING).count()
            })
            
        context['course_counts'] = course_counts
        return context


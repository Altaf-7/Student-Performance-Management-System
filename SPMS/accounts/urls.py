from django.urls import path
from django.contrib.auth import views as auth_views
from accounts.views import CustomLoginView, StudentSignUpView, FacultySignUpView
from django.views.generic import TemplateView
from accounts.decorators import admin_required

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/student/', StudentSignUpView.as_view(), name='signup'),
    path('register/faculty/', FacultySignUpView.as_view(), name='register_faculty'),
    
    # Password reset views
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='authentication/password_reset_form.html',
             success_url='/password-reset/done/',
             email_template_name='authentication/password_reset_email.html'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='authentication/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ), 
         name='password_reset_confirm'),
         
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), 
         name='password_reset_complete'),
         
    # Password change view (for authenticated users)
    path('change-password/', 
         auth_views.PasswordChangeView.as_view(
             template_name='authentication/change_password.html',
             success_url='/change-password/done/'
         ), 
         name='change_password'),
         
    path('change-password/done/', 
         auth_views.PasswordChangeDoneView.as_view(template_name='authentication/change_password_done.html'), 
         name='change_password_done'),
         
]

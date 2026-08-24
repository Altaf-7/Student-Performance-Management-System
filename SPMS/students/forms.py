from django import forms
from assignments.models import AssignmentSubmission
from students.models import Student

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submission_file']
        labels = {
            'submission_file': 'Upload PDF File'
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['submission_file'].widget.attrs.update({'accept': '.pdf'})

class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['address', 'guardian_name', 'guardian_contact', 'emergency_contact']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'placeholder': self.fields[field].label})

from django import forms
from faculty.models import Faculty
from academics.models import SubjectOffering, Lecture
from assignments.models import Assignment, AssignmentSubmission
from examinations.models import Exam

class FacultyProfileForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['office_email', 'office_contact', 'specialization', 'qualification']
        widgets = {
            'office_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'office_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")
            
        return cleaned_data

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'offering', 'description', 'instructions', 'maximum_marks', 'due_datetime', 'file_attachment', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'maximum_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'file_attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.faculty = kwargs.pop('faculty', None)
        super().__init__(*args, **kwargs)
        if self.faculty:
            self.fields['offering'].queryset = SubjectOffering.objects.filter(faculty=self.faculty)

class AssignmentGradingForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['marks_awarded', 'feedback']
        widgets = {
            'marks_awarded': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_marks_awarded(self):
        marks = self.cleaned_data.get('marks_awarded')
        if marks is not None:
            if marks < 0:
                raise forms.ValidationError("Marks cannot be negative.")
            if self.instance and self.instance.assignment and marks > self.instance.assignment.maximum_marks:
                raise forms.ValidationError(f"Marks cannot exceed maximum marks ({self.instance.assignment.maximum_marks}).")
        return marks

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['offering', 'exam_term', 'exam_category', 'exam_date', 'total_marks', 'description', 'status']
        widgets = {
            'offering': forms.Select(attrs={'class': 'form-control'}),
            'exam_term': forms.Select(attrs={'class': 'form-control'}),
            'exam_category': forms.Select(attrs={'class': 'form-control'}),
            'exam_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.faculty = kwargs.pop('faculty', None)
        super().__init__(*args, **kwargs)
        if self.faculty:
            self.fields['offering'].queryset = SubjectOffering.objects.filter(faculty=self.faculty)


    def clean_total_marks(self):
        total_marks = self.cleaned_data.get('total_marks')
        if total_marks and total_marks <= 0:
            raise forms.ValidationError('Total marks must be greater than 0.')
        return total_marks


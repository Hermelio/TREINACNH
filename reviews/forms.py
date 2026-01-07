"""
Forms for reviews app.
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML
from .models import Review, Report


class ReviewForm(forms.ModelForm):
    """Form for students to write reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} ★') for i in range(1, 6)], attrs={'class': 'form-check-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Conte sobre sua experiência...'}),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML('<h6 class="mb-3">Sua avaliação:</h6>'),
            Field('rating', css_class='mb-3'),
            HTML('<h6 class="mb-3 mt-4">Comentário (opcional):</h6>'),
            Field('comment', css_class='mb-3'),
            Submit('submit', 'Enviar Avaliação', css_class='btn btn-primary')
        )


class ReportForm(forms.ModelForm):
    """Form for reporting instructors"""
    
    class Meta:
        model = Report
        fields = ['reason', 'details', 'reporter_name', 'reporter_email']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Descreva a situação detalhadamente...'}),
            'reporter_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome'}),
            'reporter_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'}),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Pre-fill if user is logged in
        if user and user.is_authenticated:
            self.fields['reporter_name'].initial = user.get_full_name()
            self.fields['reporter_email'].initial = user.email
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML('<p class="alert alert-warning">Esta denúncia será analisada pela nossa equipe.</p>'),
            Field('reason', css_class='mb-3'),
            Field('details', css_class='mb-3'),
            HTML('<hr><h6 class="mb-3">Seus dados (para contato):</h6>'),
            Field('reporter_name', css_class='mb-3'),
            Field('reporter_email', css_class='mb-3'),
            Submit('submit', 'Enviar Denúncia', css_class='btn btn-danger')
        )

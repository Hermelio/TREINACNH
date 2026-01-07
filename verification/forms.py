"""
Forms for verification app.
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML
from .models import InstructorDocument


class DocumentUploadForm(forms.ModelForm):
    """Form for instructors to upload documents"""
    
    class Meta:
        model = InstructorDocument
        fields = ['doc_type', 'file']
        widgets = {
            'doc_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            HTML('<p class="text-muted mb-3">Envie seus documentos para verificação. Arquivos aceitos: PDF, JPG, PNG (máximo 10MB).</p>'),
            Field('doc_type', css_class='mb-3'),
            Field('file', css_class='mb-3'),
            Submit('submit', 'Enviar Documento', css_class='btn btn-primary')
        )


class DocumentReviewForm(forms.ModelForm):
    """Form for admin to review documents"""
    
    class Meta:
        model = InstructorDocument
        fields = ['status', 'notes']
        widgets = {
            'status': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações (opcional)'}),
        }

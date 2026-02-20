"""
Forms for verification app.
"""
from django import forms
from .models import InstructorDocument


class DocumentUploadForm(forms.ModelForm):
    """Formulário para instrutores enviarem documentos e selfie."""

    class Meta:
        model = InstructorDocument
        fields = ['doc_type', 'file', 'selfie']
        widgets = {
            'doc_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'selfie': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.jpg,.jpeg,.png',
            }),
        }
        labels = {
            'doc_type': 'Tipo de documento',
            'file':     'Arquivo do documento (PDF ou imagem)',
            'selfie':   'Selfie segurando o documento (opcional)',
        }
        help_texts = {
            'file':   'Formatos aceitos: PDF, JPG, PNG. Tamanho máximo: 10 MB.',
            'selfie': 'Foto do seu rosto segurando o documento — acelera a aprovação.',
        }

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if f and f.size > 10 * 1024 * 1024:
            raise forms.ValidationError('O arquivo não pode ultrapassar 10 MB.')
        return f

    def clean_selfie(self):
        s = self.cleaned_data.get('selfie')
        if s and s.size > 10 * 1024 * 1024:
            raise forms.ValidationError('A selfie não pode ultrapassar 10 MB.')
        return s


class DocumentReviewForm(forms.ModelForm):
    """Form for admin to review documents"""
    
    class Meta:
        model = InstructorDocument
        fields = ['status', 'notes']
        widgets = {
            'status': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações (opcional)'}),
        }

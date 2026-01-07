"""
Forms for marketplace app.
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML, Div
from .models import InstructorProfile, Lead, City, CategoryCNH


class InstructorProfileForm(forms.ModelForm):
    """Form for instructors to edit their professional profile"""
    
    class Meta:
        model = InstructorProfile
        fields = [
            'city', 'bio', 'neighborhoods_text', 'gender', 'age', 'years_experience',
            'has_own_car', 'car_model', 'categories', 'available_morning',
            'available_afternoon', 'available_evening', 'base_price_per_hour',
            'price_notes', 'is_visible'
        ]
        widgets = {
            'city': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Conte sobre sua experiência...'}),
            'neighborhoods_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Centro, Jardins, etc'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 18, 'max': 100}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 50}),
            'has_own_car': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'car_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Fiat Argo 2023'}),
            'categories': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'available_morning': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'available_afternoon': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'available_evening': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'base_price_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'price_notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Pacotes disponíveis'}),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_visible': 'Meu perfil está visível para alunos',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML('<h5 class="mb-3">Localização</h5>'),
            Field('city', css_class='mb-3'),
            Field('neighborhoods_text', css_class='mb-3'),
            
            HTML('<h5 class="mb-3 mt-4">Sobre Você</h5>'),
            Field('bio', css_class='mb-3'),
            Row(
                Column('gender', css_class='form-group col-md-4 mb-3'),
                Column('age', css_class='form-group col-md-4 mb-3'),
                Column('years_experience', css_class='form-group col-md-4 mb-3'),
            ),
            
            HTML('<h5 class="mb-3 mt-4">Veículo</h5>'),
            Field('has_own_car', css_class='mb-3'),
            Field('car_model', css_class='mb-3'),
            
            HTML('<h5 class="mb-3 mt-4">Categorias que Ensina</h5>'),
            Field('categories', css_class='mb-3'),
            
            HTML('<h5 class="mb-3 mt-4">Disponibilidade</h5>'),
            Div(
                Field('available_morning', wrapper_class='form-check'),
                Field('available_afternoon', wrapper_class='form-check'),
                Field('available_evening', wrapper_class='form-check'),
                css_class='mb-3'
            ),
            
            HTML('<h5 class="mb-3 mt-4">Preços (Opcional)</h5>'),
            Field('base_price_per_hour', css_class='mb-3'),
            Field('price_notes', css_class='mb-3'),
            
            HTML('<hr class="my-4">'),
            Field('is_visible', wrapper_class='form-check mb-3'),
            
            Submit('submit', 'Salvar Perfil', css_class='btn btn-primary btn-lg')
        )


class LeadForm(forms.ModelForm):
    """Form for students to request contact with instructor"""
    
    class Meta:
        model = Lead
        fields = ['contact_name', 'contact_phone', 'preferred_schedule', 'message']
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome completo'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+5511999999999'}),
            'preferred_schedule': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Selecione...'),
                ('Manhã', 'Manhã (6h-12h)'),
                ('Tarde', 'Tarde (12h-18h)'),
                ('Noite', 'Noite (18h-22h)'),
                ('Flexível', 'Horário flexível'),
            ]),
            'message': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Conte um pouco sobre o que você precisa (opcional)'
            }),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-fill if user is logged in
        if user and user.is_authenticated:
            self.fields['contact_name'].initial = user.get_full_name()
            if hasattr(user, 'profile') and user.profile.phone:
                self.fields['contact_phone'].initial = user.profile.phone
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML('<p class="text-muted mb-3">Preencha seus dados para que o instrutor entre em contato:</p>'),
            Field('contact_name', css_class='mb-3'),
            Field('contact_phone', css_class='mb-3'),
            Field('preferred_schedule', css_class='mb-3'),
            Field('message', css_class='mb-3'),
            Submit('submit', 'Solicitar Contato', css_class='btn btn-success btn-lg w-100')
        )


class InstructorSearchForm(forms.Form):
    """Form for filtering instructors"""
    gender = forms.ChoiceField(
        label='Gênero',
        required=False,
        choices=[('', 'Todos')] + list(InstructorProfile._meta.get_field('gender').choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    category = forms.ModelChoiceField(
        label='Categoria CNH',
        required=False,
        queryset=CategoryCNH.objects.all(),
        empty_label='Todas',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    has_own_car = forms.ChoiceField(
        label='Carro próprio',
        required=False,
        choices=[('', 'Tanto faz'), ('yes', 'Sim'), ('no', 'Não')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    availability = forms.ChoiceField(
        label='Disponibilidade',
        required=False,
        choices=[
            ('', 'Qualquer horário'),
            ('morning', 'Manhã'),
            ('afternoon', 'Tarde'),
            ('evening', 'Noite'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    verified_only = forms.BooleanField(
        label='Apenas verificados',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

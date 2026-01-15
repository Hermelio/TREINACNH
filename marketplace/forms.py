"""
Forms for marketplace app.
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML, Div
from .models import InstructorProfile, Lead, City, CategoryCNH, State, StudentLead


class InstructorProfileForm(forms.ModelForm):
    """Form for instructors to edit their professional profile"""
    
    class Meta:
        model = InstructorProfile
        fields = [
            'city', 'address_street', 'address_neighborhood', 'address_zip',
            'bio', 'neighborhoods_text', 'gender', 'age', 'years_experience',
            'has_own_car', 'car_model', 'categories', 'available_morning',
            'available_afternoon', 'available_evening', 'base_price_per_hour',
            'price_notes', 'is_visible'
        ]
        widgets = {
            'city': forms.Select(attrs={'class': 'form-select'}),
            'address_street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua e número'}),
            'address_neighborhood': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do bairro'}),
            'address_zip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
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
            Field('address_street', css_class='mb-3'),
            Row(
                Column('address_neighborhood', css_class='form-group col-md-6 mb-3'),
                Column('address_zip', css_class='form-group col-md-6 mb-3'),
            ),
            Field('neighborhoods_text', css_class='mb-3'),
            HTML('<p class="text-muted small"><i class="bi bi-info-circle"></i> Suas coordenadas serão calculadas automaticamente com base no endereço para aparecer no mapa.</p>'),
            
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


class StudentRegistrationForm(forms.ModelForm):
    """Form for student registration"""
    
    class Meta:
        model = StudentLead
        fields = [
            'photo', 'name', 'phone', 'email', 'state', 'city',
            'categories', 'has_theory', 'accept_whatsapp', 
            'accept_email', 'accept_terms'
        ]
        widgets = {
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu@email.com'
            }),
            'state': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_state'
            }),
            'city': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_city'
            }),
            'categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'has_theory': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'accept_whatsapp': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'accept_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'accept_terms': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'photo': 'Foto (Opcional)',
            'name': 'Nome Completo',
            'phone': 'WhatsApp',
            'email': 'E-mail',
            'state': 'Estado',
            'city': 'Cidade',
            'categories': 'Categorias Desejadas',
            'has_theory': 'Já concluí a parte teórica',
            'accept_whatsapp': 'Aceito receber mensagens via WhatsApp',
            'accept_email': 'Aceito receber mensagens via e-mail',
            'accept_terms': 'Li e aceito os Termos de Uso',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make photo optional
        self.fields['photo'].required = False
        
        # Make city initially empty (will be populated by JS based on state)
        self.fields['city'].queryset = City.objects.none()
        self.fields['city'].required = False
        
        # Set default values for consents
        self.fields['accept_whatsapp'].initial = True
        self.fields['accept_email'].initial = True
        
        # Make accept_terms required
        self.fields['accept_terms'].required = True
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            HTML('<h5 class="mb-3">Dados Pessoais</h5>'),
            Field('photo', css_class='mb-3'),
            Field('name', css_class='mb-3'),
            Field('phone', css_class='mb-3'),
            Field('email', css_class='mb-3'),
            
            HTML('<h5 class="mb-3 mt-4">Localização</h5>'),
            Row(
                Column('state', css_class='form-group col-md-6 mb-3'),
                Column('city', css_class='form-group col-md-6 mb-3'),
            ),
            
            HTML('<h5 class="mb-3 mt-4">Informações sobre a CNH</h5>'),
            Field('categories', css_class='mb-3'),
            Div(
                Field('has_theory', wrapper_class='form-check'),
                css_class='mb-3'
            ),
            
            HTML('<h5 class="mb-3 mt-4">Preferências de Contato</h5>'),
            Div(
                Field('accept_whatsapp', wrapper_class='form-check'),
                Field('accept_email', wrapper_class='form-check'),
                css_class='mb-3'
            ),
            
            HTML('<hr class="my-4">'),
            Div(
                Field('accept_terms', wrapper_class='form-check'),
                HTML('<small class="form-text text-muted d-block mt-2">Ao se cadastrar, você concorda com nossos <a href="/termos-de-uso" target="_blank">Termos de Uso</a> e <a href="/politica-de-privacidade" target="_blank">Política de Privacidade</a>.</small>'),
                css_class='mb-4'
            ),
            
            Submit('submit', 'Cadastrar', css_class='btn btn-success btn-lg w-100')
        )
    
    def clean_phone(self):
        """Clean and validate phone number"""
        phone = self.cleaned_data.get('phone')
        # Remove non-digits
        phone = ''.join(filter(str.isdigit, phone))
        
        if len(phone) < 10:
            raise forms.ValidationError('Telefone inválido. Digite um número válido.')
        
        return phone
    
    def clean_accept_terms(self):
        """Ensure terms are accepted"""
        accept_terms = self.cleaned_data.get('accept_terms')
        if not accept_terms:
            raise forms.ValidationError('Você deve aceitar os Termos de Uso para se cadastrar.')
        return accept_terms

"""
Forms for user registration, login, and profile management.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML
from .models import Profile, Address, RoleChoices


class UserRegistrationForm(UserCreationForm):
    """
    Extended user registration form with email, name, role and city selection.
    """
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'})
    )
    first_name = forms.CharField(
        required=True,
        label='Nome',
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome'})
    )
    last_name = forms.CharField(
        required=True,
        label='Sobrenome',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu sobrenome'})
    )
    role = forms.ChoiceField(
        required=True,
        label='Eu sou',
        choices=[(RoleChoices.STUDENT, 'Aluno'), (RoleChoices.INSTRUCTOR, 'Instrutor')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    preferred_state = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label='Seu estado',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_preferred_state'}),
        help_text='Selecione primeiro seu estado'
    )
    preferred_city = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label='Sua cidade',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_preferred_city'}),
        help_text='Selecione sua cidade para ver instrutores próximos'
    )
    cpf = forms.CharField(
        required=True,
        label='CPF',
        max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00000000000',
            'maxlength': '11',
            'pattern': '[0-9]{11}'
        }),
        help_text='Apenas números, sem pontos ou traços'
    )
    whatsapp_number = forms.CharField(
        required=True,
        label='WhatsApp',
        max_length=17,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+5511999999999'
        }),
        help_text='Número com código do país e DDD'
    )
    has_own_car = forms.BooleanField(
        required=False,
        label='Possui carro próprio',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Apenas para instrutores'
    )
    accept_whatsapp_messages = forms.BooleanField(
        required=False,
        initial=True,
        label='Aceito receber mensagens via WhatsApp',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    accept_terms = forms.BooleanField(
        required=True,
        label='Li e aceito os Termos de Uso',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'Você deve aceitar os termos de uso para continuar'}
    )
    accept_privacy = forms.BooleanField(
        required=True,
        label='Li e aceito a Política de Privacidade',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'Você deve aceitar a política de privacidade para continuar'}
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de usuário'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import here to avoid circular import
        from marketplace.models import City, State
        
        # Load all states
        self.fields['preferred_state'].queryset = State.objects.all().order_by('code')
        
        # Cities will be loaded dynamically via JavaScript, but set empty queryset
        self.fields['preferred_city'].queryset = City.objects.none()
        
        # If editing and has data, load the cities for that state
        if self.data.get('preferred_state'):
            try:
                state_id = int(self.data.get('preferred_state'))
                self.fields['preferred_city'].queryset = City.objects.filter(
                    state_id=state_id, is_active=True
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Senha'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirme a senha'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Update profile with all fields
            profile = user.profile
            profile.role = self.cleaned_data['role']
            profile.cpf = self.cleaned_data.get('cpf', '')
            profile.whatsapp_number = self.cleaned_data.get('whatsapp_number', '')
            profile.accept_whatsapp_messages = self.cleaned_data.get('accept_whatsapp_messages', True)
            profile.accept_terms = self.cleaned_data.get('accept_terms', False)
            profile.accept_privacy = self.cleaned_data.get('accept_privacy', False)
            
            if self.cleaned_data.get('preferred_city'):
                profile.preferred_city = self.cleaned_data['preferred_city']
            
            profile.save()
            
            # If instructor and has car info, save to InstructorProfile if it exists
            if profile.role == 'INSTRUCTOR':
                try:
                    from marketplace.models import InstructorProfile
                    # Store has_own_car temporarily for later use when creating InstructorProfile
                    profile._has_own_car = self.cleaned_data.get('has_own_car', False)
                except:
                    pass
        return user


class CustomLoginForm(AuthenticationForm):
    """Customized login form with Bootstrap styling"""
    username = forms.CharField(
        label='Usuário ou E-mail',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu usuário ou e-mail'})
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Sua senha'})
    )


class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile information"""
    first_name = forms.CharField(
        required=True,
        label='Nome',
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=True,
        label='Sobrenome',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Profile
        fields = ('phone', 'whatsapp_number', 'avatar')
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '11 99999-9999',
                'maxlength': '15',
                'inputmode': 'tel',
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '11 99999-9999',
                'maxlength': '15',
                'inputmode': 'tel',
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'd-none',
                'id': 'avatar-input',
                'accept': 'image/*',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

        # Strip +55 prefix so only local digits are shown in the input
        for field_name in ('phone', 'whatsapp_number'):
            value = getattr(self.instance, field_name, '') or ''
            if value.startswith('+55'):
                value = value[3:]
            self.fields[field_name].initial = value

    def _normalize_phone(self, value):
        """Strip spaces/dashes and ensure +55 prefix in E.164 format."""
        if not value:
            return value
        # Remove anything except digits and leading +
        digits = ''.join(c for c in value if c.isdigit())
        if not digits:
            return value
        # If the user typed the full number with country code already
        if value.lstrip().startswith('+55'):
            return '+55' + digits[2:] if digits.startswith('55') else '+55' + digits
        # Otherwise prepend +55
        if digits.startswith('55') and len(digits) >= 12:
            return '+' + digits
        return '+55' + digits

    def clean_phone(self):
        value = self.cleaned_data.get('phone', '').strip()
        if not value:
            return value
        return self._normalize_phone(value)

    def clean_whatsapp_number(self):
        value = self.cleaned_data.get('whatsapp_number', '').strip()
        if not value:
            return value
        return self._normalize_phone(value)
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Update user fields
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            profile.save()
        return profile


class AddressForm(forms.ModelForm):
    """Form for managing user addresses"""
    class Meta:
        model = Address
        fields = ('state', 'city', 'neighborhood', 'is_primary')
        widgets = {
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SP', 'maxlength': '2'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'São Paulo'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Centro (opcional)'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CompleteProfileForm(forms.Form):
    """
    Minimal form shown after Google login so the user can choose
    whether they are a student (Aluno) or instructor (Instrutor).
    """
    role = forms.ChoiceField(
        label='Como você vai usar o TreinaCNH?',
        choices=[
            (RoleChoices.STUDENT, 'Aluno — quero encontrar instrutores'),
            (RoleChoices.INSTRUCTOR, 'Instrutor — quero divulgar meu serviço'),
        ],
        widget=forms.RadioSelect,
        required=True,
    )

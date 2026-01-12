"""
Models for accounts app - User profiles, roles and addresses.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class RoleChoices(models.TextChoices):
    """User role options"""
    STUDENT = 'STUDENT', 'Aluno'
    INSTRUCTOR = 'INSTRUCTOR', 'Instrutor'
    ADMIN_SUPPORT = 'ADMIN_SUPPORT', 'Administrador/Suporte'


class Profile(models.Model):
    """
    Extended user profile with phone, role, and avatar.
    Created automatically when a User is created.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Usuário')
    
    # Phone validation (E.164 format)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Telefone deve estar no formato: '+5511999999999'. Até 15 dígitos permitidos."
    )
    phone = models.CharField('Telefone', validators=[phone_regex], max_length=17, blank=True)
    whatsapp_number = models.CharField(
        'WhatsApp', 
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        help_text='Número do WhatsApp (pode ser igual ao telefone)'
    )
    
    # Identity documents
    cpf = models.CharField(
        'CPF',
        max_length=11,
        blank=True,
        unique=True,
        null=True,
        help_text='CPF sem pontos ou traços (apenas números)'
    )
    birth_date = models.DateField(
        'Data de Nascimento',
        null=True,
        blank=True,
        help_text='Data de nascimento para validação'
    )
    
    # Multi-step verification
    email_verified = models.BooleanField(
        'Email Verificado',
        default=False,
        help_text='Email confirmado via token'
    )
    phone_verified = models.BooleanField(
        'Telefone Verificado',
        default=False,
        help_text='Telefone confirmado via SMS/WhatsApp'
    )
    identity_verified = models.BooleanField(
        'Identidade Verificada',
        default=False,
        help_text='Selfie + documento verificados'
    )
    
    # Trust and security
    trust_score = models.IntegerField(
        'Score de Confiança',
        default=50,
        help_text='Score de 0-100 baseado em verificações e reputação'
    )
    is_blocked = models.BooleanField(
        'Bloqueado',
        default=False,
        help_text='Usuário bloqueado por atividade suspeita'
    )
    block_reason = models.TextField(
        'Motivo do Bloqueio',
        blank=True,
        help_text='Razão do bloqueio'
    )
    
    role = models.CharField(
        'Perfil',
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.STUDENT
    )
    
    avatar = models.ImageField(
        'Foto de Perfil',
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        help_text='Foto do perfil (opcional)'
    )
    
    # Location for students
    preferred_city = models.ForeignKey(
        'marketplace.City',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_profiles',
        verbose_name='Cidade Preferida',
        help_text='Cidade onde o aluno busca instrutores'
    )
    
    # Preferences and Consents
    accept_whatsapp_messages = models.BooleanField(
        'Aceita Mensagens via WhatsApp',
        default=True,
        help_text='Permite receber mensagens via WhatsApp'
    )
    accept_terms = models.BooleanField(
        'Aceita Termos de Uso',
        default=False,
        help_text='Confirmação de aceite dos termos de uso'
    )
    accept_privacy = models.BooleanField(
        'Aceita Política de Privacidade',
        default=False,
        help_text='Confirmação de aceite da política de privacidade'
    )
    
    # Metadata
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"
    
    @property
    def is_instructor(self):
        """Check if user is an instructor"""
        return self.role == RoleChoices.INSTRUCTOR
    
    @property
    def is_student(self):
        """Check if user is a student"""
        return self.role == RoleChoices.STUDENT
    
    @property
    def is_admin_support(self):
        """Check if user is admin/support"""
        return self.role == RoleChoices.ADMIN_SUPPORT


class Address(models.Model):
    """
    Address/Location information for users.
    Can be extended with full address fields if needed.
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='addresses', verbose_name='Perfil')
    
    state = models.CharField('UF', max_length=2, help_text='Sigla do Estado (ex: SP, RJ)')
    city = models.CharField('Cidade', max_length=100)
    neighborhood = models.CharField('Bairro', max_length=100, blank=True)
    
    # Optional coordinates
    latitude = models.DecimalField('Latitude', max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField('Longitude', max_digits=9, decimal_places=6, blank=True, null=True)
    
    is_primary = models.BooleanField('Endereço Principal', default=False)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'
        ordering = ['-is_primary', '-created_at']
    
    def __str__(self):
        return f"{self.city}/{self.state}"
    
    def save(self, *args, **kwargs):
        """Ensure only one primary address per profile"""
        if self.is_primary:
            Address.objects.filter(profile=self.profile, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


# Signals to auto-create Profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create Profile when User is created"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save Profile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

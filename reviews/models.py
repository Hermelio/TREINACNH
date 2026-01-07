"""
Models for reviews app - Reviews and Reports.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from marketplace.models import InstructorProfile


class ReviewStatusChoices(models.TextChoices):
    """Review moderation status"""
    PUBLISHED = 'PUBLISHED', 'Publicado'
    PENDING = 'PENDING', 'Pendente'
    HIDDEN = 'HIDDEN', 'Oculto'


class Review(models.Model):
    """
    Student reviews for instructors.
    Can be created by logged-in users or anonymous.
    """
    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Instrutor'
    )
    
    author_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews_written',
        verbose_name='Autor (usuário)'
    )
    
    author_name = models.CharField(
        'Nome do Autor',
        max_length=100,
        blank=True,
        help_text='Usado se autor não estiver logado'
    )
    
    rating = models.PositiveIntegerField(
        'Avaliação',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='1 a 5 estrelas'
    )
    
    comment = models.TextField(
        'Comentário',
        max_length=1000,
        blank=True
    )
    
    status = models.CharField(
        'Status',
        max_length=20,
        choices=ReviewStatusChoices.choices,
        default=ReviewStatusChoices.PENDING
    )
    
    # Metadata
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    ip_address = models.GenericIPAddressField('IP', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instructor', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        author = self.author_user.get_full_name() if self.author_user else self.author_name
        return f"{author} → {self.instructor.user.get_full_name()} ({self.rating}★)"
    
    @property
    def display_name(self):
        """Get display name for review author"""
        if self.author_user:
            return self.author_user.get_full_name() or self.author_user.username
        return self.author_name or 'Anônimo'


class ReportStatusChoices(models.TextChoices):
    """Report investigation status"""
    OPEN = 'OPEN', 'Aberto'
    INVESTIGATING = 'INVESTIGATING', 'Em Investigação'
    CLOSED = 'CLOSED', 'Fechado'


class Report(models.Model):
    """
    Reports/complaints about instructors.
    """
    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='Instrutor'
    )
    
    reporter_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_made',
        verbose_name='Denunciante (usuário)'
    )
    
    reporter_name = models.CharField(
        'Nome do Denunciante',
        max_length=100,
        blank=True
    )
    
    reporter_email = models.EmailField(
        'E-mail do Denunciante',
        blank=True
    )
    
    reason = models.CharField(
        'Motivo',
        max_length=50,
        choices=[
            ('FRAUD', 'Fraude/Documentos Falsos'),
            ('INAPPROPRIATE', 'Comportamento Inadequado'),
            ('SCAM', 'Golpe/Cobrança Indevida'),
            ('OTHER', 'Outro'),
        ]
    )
    
    details = models.TextField(
        'Detalhes',
        max_length=2000,
        help_text='Descreva a situação'
    )
    
    status = models.CharField(
        'Status',
        max_length=20,
        choices=ReportStatusChoices.choices,
        default=ReportStatusChoices.OPEN
    )
    
    admin_notes = models.TextField(
        'Notas do Admin',
        blank=True,
        help_text='Observações da investigação'
    )
    
    # Metadata
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    ip_address = models.GenericIPAddressField('IP', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Denúncia'
        verbose_name_plural = 'Denúncias'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instructor', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        reporter = self.reporter_user.username if self.reporter_user else self.reporter_name
        return f"{reporter} → {self.instructor.user.get_full_name()} ({self.get_reason_display()})"

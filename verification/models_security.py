"""
Models for reporting and blacklist system.
"""
from django.db import models
from django.contrib.auth.models import User
from marketplace.models import InstructorProfile


class ReportTypeChoices(models.TextChoices):
    """Types of reports"""
    FAKE_PROFILE = 'FAKE_PROFILE', 'Perfil Falso'
    FAKE_DOCUMENT = 'FAKE_DOCUMENT', 'Documento Falso'
    SCAM = 'SCAM', 'Golpe/Fraude'
    HARASSMENT = 'HARASSMENT', 'Assédio'
    NO_SHOW = 'NO_SHOW', 'Não compareceu à aula'
    POOR_SERVICE = 'POOR_SERVICE', 'Serviço ruim'
    OTHER = 'OTHER', 'Outro'


class UserReport(models.Model):
    """
    Reports from users about instructors or students.
    """
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='verification_reports_made',
        verbose_name='Denunciante'
    )
    
    reported_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='verification_reports_received',
        verbose_name='Usuário Denunciado'
    )
    
    report_type = models.CharField(
        'Tipo de Denúncia',
        max_length=20,
        choices=ReportTypeChoices.choices
    )
    
    description = models.TextField(
        'Descrição',
        help_text='Detalhe o que aconteceu'
    )
    
    evidence = models.FileField(
        'Evidência',
        upload_to='reports/%Y/%m/',
        blank=True,
        null=True,
        help_text='Screenshot, foto ou documento comprobatório'
    )
    
    # Investigation
    status = models.CharField(
        'Status',
        max_length=20,
        choices=[
            ('PENDING', 'Pendente'),
            ('INVESTIGATING', 'Em Investigação'),
            ('RESOLVED', 'Resolvido'),
            ('DISMISSED', 'Arquivado')
        ],
        default='PENDING'
    )
    
    admin_notes = models.TextField(
        'Notas do Administrador',
        blank=True,
        help_text='Investigação e decisão'
    )
    
    investigated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investigations',
        verbose_name='Investigado por'
    )
    
    action_taken = models.CharField(
        'Ação Tomada',
        max_length=20,
        choices=[
            ('NONE', 'Nenhuma'),
            ('WARNING', 'Advertência'),
            ('SUSPENSION', 'Suspensão'),
            ('PERMANENT_BAN', 'Banimento Permanente')
        ],
        blank=True
    )
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Denúncia'
        verbose_name_plural = 'Denúncias'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reported_user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.reported_user.get_full_name()} ({self.get_status_display()})"


class DocumentBlacklist(models.Model):
    """
    Blacklist of fake, stolen or invalid documents.
    """
    document_type = models.CharField(
        'Tipo de Documento',
        max_length=20,
        choices=[
            ('CNH', 'CNH'),
            ('CPF', 'CPF'),
            ('RG', 'RG'),
            ('PHONE', 'Telefone'),
            ('EMAIL', 'Email')
        ]
    )
    
    document_number = models.CharField(
        'Número do Documento',
        max_length=50,
        help_text='Número sem formatação'
    )
    
    reason = models.CharField(
        'Motivo',
        max_length=20,
        choices=[
            ('FAKE', 'Documento Falso'),
            ('STOLEN', 'Documento Roubado'),
            ('DUPLICATED', 'Uso Duplicado'),
            ('FRAUD', 'Fraude Confirmada')
        ]
    )
    
    description = models.TextField(
        'Descrição',
        blank=True,
        help_text='Detalhes sobre o bloqueio'
    )
    
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blacklist_reports',
        verbose_name='Reportado por'
    )
    
    is_active = models.BooleanField(
        'Ativo',
        default=True,
        help_text='Blacklist ativo'
    )
    
    expires_at = models.DateTimeField(
        'Expira em',
        null=True,
        blank=True,
        help_text='Data de expiração (deixe em branco para permanente)'
    )
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Blacklist de Documento'
        verbose_name_plural = 'Blacklist de Documentos'
        ordering = ['-created_at']
        unique_together = [['document_type', 'document_number']]
        indexes = [
            models.Index(fields=['document_type', 'document_number', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_document_type_display()}: {self.document_number} ({self.get_reason_display()})"


class SuspiciousActivity(models.Model):
    """
    Log of suspicious activities for fraud detection.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='suspicious_activities',
        verbose_name='Usuário'
    )
    
    activity_type = models.CharField(
        'Tipo de Atividade',
        max_length=30,
        choices=[
            ('MULTIPLE_REJECTIONS', 'Múltiplas Rejeições'),
            ('RAPID_REGISTRATION', 'Cadastro Muito Rápido'),
            ('FAKE_DATA', 'Dados Falsos'),
            ('DUPLICATE_ACCOUNT', 'Conta Duplicada'),
            ('ABNORMAL_BEHAVIOR', 'Comportamento Anormal'),
            ('REPORTED_MULTIPLE', 'Múltiplas Denúncias')
        ]
    )
    
    description = models.TextField('Descrição')
    
    severity = models.CharField(
        'Severidade',
        max_length=10,
        choices=[
            ('LOW', 'Baixa'),
            ('MEDIUM', 'Média'),
            ('HIGH', 'Alta'),
            ('CRITICAL', 'Crítica')
        ]
    )
    
    auto_detected = models.BooleanField(
        'Detectado Automaticamente',
        default=True,
        help_text='Foi detectado pelo sistema ou reportado manualmente'
    )
    
    reviewed = models.BooleanField(
        'Revisado',
        default=False
    )
    
    created_at = models.DateTimeField('Detectado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Atividade Suspeita'
        verbose_name_plural = 'Atividades Suspeitas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'reviewed']),
            models.Index(fields=['severity', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} ({self.get_severity_display()})"

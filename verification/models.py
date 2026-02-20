"""
Models for verification app - Document verification and audit logs.
"""
from django.db import models
from django.contrib.auth.models import User
from marketplace.models import InstructorProfile

# Import security models
from .models_security import UserReport, DocumentBlacklist, SuspiciousActivity


class DocumentTypeChoices(models.TextChoices):
    """Document type options"""
    CNH = 'CNH', 'CNH (Carteira Nacional de Habilitação)'
    CERT_INSTRUTOR = 'CERT_INSTRUTOR', 'Certificado de Instrutor'
    DOC_VEICULO = 'DOC_VEICULO', 'Documento do Veículo'
    OTHER = 'OTHER', 'Outro'


class DocumentStatusChoices(models.TextChoices):
    """Document verification status"""
    PENDING = 'PENDING', 'Pendente'
    APPROVED = 'APPROVED', 'Aprovado'
    REJECTED = 'REJECTED', 'Rejeitado'


class InstructorDocument(models.Model):
    """
    Documents uploaded by instructors for verification.
    """
    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Instrutor'
    )
    
    # Selfie for identity verification
    selfie = models.ImageField(
        'Selfie',
        upload_to='selfies/%Y/%m/',
        blank=True,
        null=True,
        help_text='Foto do rosto para comparar com documento'
    )
    face_match = models.BooleanField(
        'Rosto Corresponde',
        null=True,
        blank=True,
        help_text='Selfie corresponde à foto do documento'
    )
    face_confidence = models.DecimalField(
        'Confiança da Comparação',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Confiança da comparação facial (0-100%)'
    )
    
    doc_type = models.CharField(
        'Tipo de Documento',
        max_length=20,
        choices=DocumentTypeChoices.choices
    )
    
    file = models.FileField(
        'Arquivo',
        upload_to='documents/%Y/%m/',
        help_text='PDF, JPG ou PNG (máx 10MB)'
    )
    
    status = models.CharField(
        'Status',
        max_length=20,
        choices=DocumentStatusChoices.choices,
        default=DocumentStatusChoices.PENDING
    )
    
    notes = models.TextField(
        'Observações',
        blank=True,
        help_text='Motivo da aprovação/rejeição'
    )
    
    # OCR Extracted Data (for CNH documents)
    extracted_cnh_number = models.CharField(
        'Número CNH Extraído',
        max_length=11,
        blank=True,
        help_text='Número da CNH extraído via OCR'
    )
    extracted_cpf = models.CharField(
        'CPF Extraído',
        max_length=11,
        blank=True,
        help_text='CPF extraído via OCR'
    )
    extracted_name = models.CharField(
        'Nome Extraído',
        max_length=200,
        blank=True,
        help_text='Nome completo extraído via OCR'
    )
    extracted_validity = models.DateField(
        'Validade Extraída',
        null=True,
        blank=True,
        help_text='Data de validade extraída via OCR'
    )
    ocr_confidence = models.DecimalField(
        'Confiança do OCR',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Confiança da extração (0-100%)'
    )
    
    # Validation Results
    cnh_valid = models.BooleanField(
        'CNH Válida',
        null=True,
        blank=True,
        help_text='Número da CNH passou na validação'
    )
    cpf_valid = models.BooleanField(
        'CPF Válido',
        null=True,
        blank=True,
        help_text='CPF passou na validação'
    )
    validity_ok = models.BooleanField(
        'Dentro da Validade',
        null=True,
        blank=True,
        help_text='Documento está dentro da validade'
    )
    
    # Review info
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_documents',
        verbose_name='Revisado por'
    )
    reviewed_at = models.DateTimeField('Revisado em', null=True, blank=True)
    
    # Timestamps
    uploaded_at = models.DateTimeField('Enviado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Documento de Instrutor'
        verbose_name_plural = 'Documentos de Instrutores'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['instructor', 'status']),
            models.Index(fields=['status', 'uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.get_doc_type_display()} - {self.instructor.user.get_full_name()} ({self.get_status_display()})"
    
    def approve(self, reviewer, notes=''):
        """Approve document and update instructor verification status"""
        self.status = DocumentStatusChoices.APPROVED
        self.reviewed_by = reviewer
        self.notes = notes
        from django.utils import timezone
        self.reviewed_at = timezone.now()
        self.save()
        
        # Check if all required documents are approved
        self._update_instructor_verification()
    
    def reject(self, reviewer, notes):
        """Reject document"""
        self.status = DocumentStatusChoices.REJECTED
        self.reviewed_by = reviewer
        self.notes = notes
        from django.utils import timezone
        self.reviewed_at = timezone.now()
        self.save()
        
        # Remove instructor verification
        self.instructor.is_verified = False
        self.instructor.save()
    
    def _update_instructor_verification(self):
        """Update instructor verification status based on approved documents"""
        # Check if CNH and CERT_INSTRUTOR are approved
        has_cnh = self.instructor.documents.filter(
            doc_type=DocumentTypeChoices.CNH,
            status=DocumentStatusChoices.APPROVED
        ).exists()
        
        has_cert = self.instructor.documents.filter(
            doc_type=DocumentTypeChoices.CERT_INSTRUTOR,
            status=DocumentStatusChoices.APPROVED
        ).exists()
        
        if has_cnh and has_cert:
            self.instructor.is_verified = True
            self.instructor.save()


class AuditLog(models.Model):
    """
    Audit log for tracking admin actions.
    """
    actor_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name='Usuário'
    )
    
    action = models.CharField('Ação', max_length=100)
    object_type = models.CharField('Tipo de Objeto', max_length=50)
    object_id = models.PositiveIntegerField('ID do Objeto')
    metadata = models.JSONField('Metadados', default=dict, blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    ip_address = models.GenericIPAddressField('IP', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['actor_user', 'created_at']),
            models.Index(fields=['object_type', 'object_id']),
        ]
    
    def __str__(self):
        actor = self.actor_user.username if self.actor_user else 'Sistema'
        return f"{actor} - {self.action} - {self.object_type}#{self.object_id}"
    
    @classmethod
    def log(cls, action, object_type, object_id, actor_user=None, metadata=None, ip_address=None):
        """Helper method to create audit log"""
        return cls.objects.create(
            action=action,
            object_type=object_type,
            object_id=object_id,
            actor_user=actor_user,
            metadata=metadata or {},
            ip_address=ip_address
        )


class PendingDocument(InstructorDocument):
    """
    Proxy model used exclusively for the admin approval queue.
    Shows only PENDING documents — no new DB table needed.
    """
    class Meta:
        proxy = True
        verbose_name = '⏳ Documento Pendente'
        verbose_name_plural = '⏳ Fila de Aprovação'
        ordering = ['uploaded_at']

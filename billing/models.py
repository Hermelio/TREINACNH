"""
Models for billing app - Plans, Subscriptions, Payments and Highlights.
"""
from django.db import models
from django.utils import timezone
from marketplace.models import InstructorProfile, City


class Plan(models.Model):
    """Subscription plans for instructors"""
    name = models.CharField('Nome', max_length=100, unique=True)
    description = models.TextField('Descrição', blank=True)
    price_monthly = models.DecimalField('Preço Mensal', max_digits=8, decimal_places=2)
    features = models.TextField('Recursos', help_text='Um recurso por linha')
    is_active = models.BooleanField('Ativo', default=True)
    
    # Display order
    order = models.PositiveIntegerField('Ordem', default=0)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Plano'
        verbose_name_plural = 'Planos'
        ordering = ['order', 'price_monthly']
    
    def __str__(self):
        return f"{self.name} - R$ {self.price_monthly}/mês"


class SubscriptionStatusChoices(models.TextChoices):
    """Subscription status"""
    ACTIVE = 'ACTIVE', 'Ativo'
    PAUSED = 'PAUSED', 'Pausado'
    CANCELED = 'CANCELED', 'Cancelado'


class Subscription(models.Model):
    """
    Instructor subscriptions with automatic payment integration.
    """
    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Instrutor'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name='Plano'
    )
    
    status = models.CharField(
        'Status',
        max_length=20,
        choices=SubscriptionStatusChoices.choices,
        default=SubscriptionStatusChoices.ACTIVE
    )
    
    start_date = models.DateField('Data de Início')
    end_date = models.DateField('Data de Término', null=True, blank=True)
    
    notes = models.TextField('Observações', blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.instructor.user.get_full_name()} - {self.plan.name}"
    
    @property
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != SubscriptionStatusChoices.ACTIVE:
            return False
        
        now = timezone.now().date()
        if self.end_date and self.end_date < now:
            return False
        
        return True


class PaymentMethodChoices(models.TextChoices):
    """Payment method options"""
    PIX = 'PIX', 'PIX'
    BOLETO = 'BOLETO', 'Boleto Bancário'
    CREDIT_CARD = 'CREDIT_CARD', 'Cartão de Crédito'
    DEBIT_CARD = 'DEBIT_CARD', 'Cartão de Débito'


class PaymentStatusChoices(models.TextChoices):
    """Payment status options"""
    PENDING = 'PENDING', 'Pendente'
    APPROVED = 'APPROVED', 'Aprovado'
    REJECTED = 'REJECTED', 'Rejeitado'
    CANCELLED = 'CANCELLED', 'Cancelado'
    REFUNDED = 'REFUNDED', 'Reembolsado'


class Payment(models.Model):
    """
    Payment records for subscriptions using Mercado Pago.
    """
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Assinatura'
    )
    
    amount = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    
    payment_method = models.CharField(
        'Método de Pagamento',
        max_length=20,
        choices=PaymentMethodChoices.choices,
        default=PaymentMethodChoices.PIX
    )
    
    status = models.CharField(
        'Status',
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.PENDING
    )
    
    # Mercado Pago IDs
    external_id = models.CharField(
        'ID Externo (MP)',
        max_length=255,
        unique=True,
        help_text='ID do pagamento no Mercado Pago'
    )
    preference_id = models.CharField(
        'ID da Preferência',
        max_length=255,
        blank=True,
        help_text='ID da preferência criada no Mercado Pago'
    )
    
    # Timestamps
    paid_at = models.DateTimeField('Pago em', null=True, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    # Additional info
    payment_details = models.JSONField(
        'Detalhes do Pagamento',
        default=dict,
        blank=True,
        help_text='JSON com informações completas do Mercado Pago'
    )
    
    notes = models.TextField('Observações', blank=True)
    
    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subscription', '-created_at']),
            models.Index(fields=['external_id']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Pagamento {self.external_id} - {self.get_status_display()} - R$ {self.amount}"
    
    @property
    def is_paid(self):
        """Check if payment is approved and paid"""
        return self.status == PaymentStatusChoices.APPROVED and self.paid_at is not None


class Highlight(models.Model):
    """
    Highlighted/featured instructors in specific cities.
    Manually managed by admin.
    """
    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name='highlights',
        verbose_name='Instrutor'
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='highlights',
        verbose_name='Cidade',
        help_text='Cidade onde o destaque será exibido'
    )
    
    weight = models.PositiveIntegerField(
        'Peso',
        default=1,
        help_text='Quanto maior, mais relevante. Usado para ordenação.'
    )
    
    start_date = models.DateField('Data de Início')
    end_date = models.DateField('Data de Término')
    
    is_active = models.BooleanField('Ativo', default=True)
    
    notes = models.TextField('Observações', blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Destaque'
        verbose_name_plural = 'Destaques'
        ordering = ['-weight', '-start_date']
        indexes = [
            models.Index(fields=['city', 'is_active', '-weight']),
        ]
    
    def __str__(self):
        return f"{self.instructor.user.get_full_name()} em {self.city} (Peso: {self.weight})"
    
    @property
    def is_current(self):
        """Check if highlight is currently active"""
        if not self.is_active:
            return False
        
        now = timezone.now().date()
        return self.start_date <= now <= self.end_date

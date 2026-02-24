"""
Admin configuration for billing app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Plan, Subscription, Payment, Highlight


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Admin for Plan model"""
    list_display = ('name', 'price_monthly', 'is_active', 'order', 'subscription_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    
    def subscription_count(self, obj):
        return obj.subscriptions.filter(status='ACTIVE').count()
    subscription_count.short_description = 'Assinaturas Ativas'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin for Subscription model"""
    list_display = ('instructor_name', 'plan', 'status', 'start_date', 'end_date', 'is_active_badge')
    list_filter = ('status', 'plan', 'start_date')
    search_fields = ('instructor__user__username', 'instructor__user__first_name', 'plan__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Assinatura', {
            'fields': ('instructor', 'plan', 'status')
        }),
        ('Período', {
            'fields': ('start_date', 'end_date')
        }),
        ('Observações', {
            'fields': ('notes',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def instructor_name(self, obj):
        return obj.instructor.user.get_full_name()
    instructor_name.short_description = 'Instrutor'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span class="badge-active">✓ Ativo</span>')
        return format_html('<span class="badge-inactive">✗ Inativo</span>')
    is_active_badge.short_description = 'Ativo agora'
    
    actions = ['activate_subscriptions', 'pause_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f'{updated} assinatura(s) ativada(s).')
    activate_subscriptions.short_description = 'Ativar assinaturas'
    
    def pause_subscriptions(self, request, queryset):
        updated = queryset.update(status='PAUSED')
        self.message_user(request, f'{updated} assinatura(s) pausada(s).')
    pause_subscriptions.short_description = 'Pausar assinaturas'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payment model"""
    list_display = ('external_id', 'subscription_instructor', 'amount', 'payment_method', 'payment_status_badge', 'paid_at', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('external_id', 'subscription__instructor__user__username', 'preference_id')
    readonly_fields = ('created_at', 'updated_at', 'external_id', 'preference_id', 'payment_details')
    
    fieldsets = (
        ('Pagamento', {
            'fields': ('subscription', 'amount', 'payment_method', 'status')
        }),
        ('Mercado Pago', {
            'fields': ('external_id', 'preference_id', 'payment_details'),
        }),
        ('Datas', {
            'fields': ('paid_at', 'created_at', 'updated_at')
        }),
        ('Observações', {
            'fields': ('notes',)
        }),
    )
    
    def subscription_instructor(self, obj):
        return obj.subscription.instructor.user.get_full_name()
    subscription_instructor.short_description = 'Instrutor'

    def payment_status_badge(self, obj):
        css_map = {'PAID': 'badge-paid', 'PENDING': 'badge-pending', 'FAILED': 'badge-failed', 'PROCESSING': 'badge-processing'}
        css = css_map.get(obj.status, 'badge-inactive')
        return format_html('<span class="{}">{}</span>', css, obj.get_status_display())
    payment_status_badge.short_description = 'Status'
    payment_status_badge.admin_order_field = 'status'
    
    def has_add_permission(self, request):
        # Payments are created automatically
        return False


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    """Admin for Highlight model"""
    list_display = ('instructor_name', 'city', 'weight', 'start_date', 'end_date', 'is_active', 'is_current_badge')
    list_filter = ('is_active', 'city__state', 'start_date')
    search_fields = ('instructor__user__username', 'city__name')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Destaque', {
            'fields': ('instructor', 'city', 'weight')
        }),
        ('Período', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('Observações', {
            'fields': ('notes',)
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def instructor_name(self, obj):
        return obj.instructor.user.get_full_name()
    instructor_name.short_description = 'Instrutor'
    
    def is_current_badge(self, obj):
        if obj.is_current:
            return format_html('<span class="badge-active">✓ Ativo agora</span>')
        return format_html('<span class="badge-inactive">Inativo</span>')
    is_current_badge.short_description = 'Status Atual'
    
    actions = ['activate_highlights', 'deactivate_highlights']
    
    def activate_highlights(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} destaque(s) ativado(s).')
    activate_highlights.short_description = 'Ativar destaques'
    
    def deactivate_highlights(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} destaque(s) desativado(s).')
    deactivate_highlights.short_description = 'Desativar destaques'

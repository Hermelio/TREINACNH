"""
Admin configuration for security and fraud prevention models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models_security import UserReport, DocumentBlacklist, SuspiciousActivity


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    """Admin for user reports and complaints"""
    list_display = (
        'report_type', 'reported_user_info', 'reporter_info', 
        'status_badge', 'severity_indicator', 'created_at', 'action_taken'
    )
    list_filter = ('status', 'report_type', 'action_taken', 'created_at')
    search_fields = (
        'reported_user__username', 'reported_user__email',
        'reporter__username', 'description'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Denúncia', {
            'fields': ('reporter', 'reported_user', 'report_type', 'description', 'evidence')
        }),
        ('Investigação', {
            'fields': ('status', 'admin_notes', 'investigated_by', 'action_taken')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def reported_user_info(self, obj):
        user = obj.reported_user
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>',
            user.get_full_name() or user.username,
            user.email
        )
    reported_user_info.short_description = 'Usuário Denunciado'
    
    def reporter_info(self, obj):
        return obj.reporter.get_full_name() or obj.reporter.username
    reporter_info.short_description = 'Denunciante'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': 'orange',
            'INVESTIGATING': 'blue',
            'RESOLVED': 'green',
            'DISMISSED': 'gray',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def severity_indicator(self, obj):
        """Show severity based on report type"""
        high_severity = ['FAKE_PROFILE', 'FAKE_DOCUMENT', 'SCAM']
        
        if obj.report_type in high_severity:
            return format_html('<span style="color: red;">⚠️ Alto Risco</span>')
        return format_html('<span style="color: orange;">⚠ Médio</span>')
    severity_indicator.short_description = 'Risco'
    
    actions = ['mark_as_investigating', 'mark_as_resolved', 'mark_as_dismissed']
    
    def mark_as_investigating(self, request, queryset):
        queryset.update(status='INVESTIGATING', investigated_by=request.user)
        self.message_user(request, f'{queryset.count()} denúncia(s) marcada(s) como em investigação')
    mark_as_investigating.short_description = 'Marcar como em investigação'
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='RESOLVED')
        self.message_user(request, f'{queryset.count()} denúncia(s) resolvida(s)')
    mark_as_resolved.short_description = 'Marcar como resolvido'
    
    def mark_as_dismissed(self, request, queryset):
        queryset.update(status='DISMISSED')
        self.message_user(request, f'{queryset.count()} denúncia(s) arquivada(s)')
    mark_as_dismissed.short_description = 'Arquivar denúncia'


@admin.register(DocumentBlacklist)
class DocumentBlacklistAdmin(admin.ModelAdmin):
    """Admin for document blacklist"""
    list_display = (
        'document_type', 'document_number_masked', 'reason_badge',
        'is_active', 'created_at', 'expires_at'
    )
    list_filter = ('document_type', 'reason', 'is_active', 'created_at')
    search_fields = ('document_number', 'description')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Documento', {
            'fields': ('document_type', 'document_number', 'reason', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at', 'reported_by')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def document_number_masked(self, obj):
        """Mask document number for privacy"""
        if len(obj.document_number) > 4:
            return f"***{obj.document_number[-4:]}"
        return "****"
    document_number_masked.short_description = 'Número'
    
    def reason_badge(self, obj):
        colors = {
            'FAKE': 'red',
            'STOLEN': 'orange',
            'DUPLICATED': 'blue',
            'FRAUD': 'darkred',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.reason, 'black'),
            obj.get_reason_display()
        )
    reason_badge.short_description = 'Motivo'
    
    actions = ['activate', 'deactivate']
    
    def activate(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} item(ns) ativado(s)')
    activate.short_description = 'Ativar blacklist'
    
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} item(ns) desativado(s)')
    deactivate.short_description = 'Desativar blacklist'


@admin.register(SuspiciousActivity)
class SuspiciousActivityAdmin(admin.ModelAdmin):
    """Admin for suspicious activity logs"""
    list_display = (
        'user_info', 'activity_type', 'severity_badge',
        'auto_detected', 'reviewed', 'created_at'
    )
    list_filter = ('severity', 'activity_type', 'reviewed', 'auto_detected', 'created_at')
    search_fields = ('user__username', 'user__email', 'description')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Atividade', {
            'fields': ('user', 'activity_type', 'description', 'severity')
        }),
        ('Detecção', {
            'fields': ('auto_detected', 'reviewed')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_info(self, obj):
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>',
            obj.user.get_full_name() or obj.user.username,
            obj.user.email
        )
    user_info.short_description = 'Usuário'
    
    def severity_badge(self, obj):
        colors = {
            'LOW': 'green',
            'MEDIUM': 'orange',
            'HIGH': 'red',
            'CRITICAL': 'darkred',
        }
        icons = {
            'LOW': '⚠',
            'MEDIUM': '⚠️',
            'HIGH': '🚨',
            'CRITICAL': '🔴',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            colors.get(obj.severity, 'black'),
            icons.get(obj.severity, '⚠'),
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severidade'
    
    actions = ['mark_reviewed', 'mark_unreviewed']
    
    def mark_reviewed(self, request, queryset):
        queryset.update(reviewed=True)
        self.message_user(request, f'{queryset.count()} atividade(s) marcada(s) como revisada(s)')
    mark_reviewed.short_description = 'Marcar como revisado'
    
    def mark_unreviewed(self, request, queryset):
        queryset.update(reviewed=False)
        self.message_user(request, f'{queryset.count()} atividade(s) marcada(s) como não revisada(s)')
    mark_unreviewed.short_description = 'Marcar como não revisado'

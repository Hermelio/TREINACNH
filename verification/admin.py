"""
Admin configuration for verification app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import InstructorDocument, AuditLog


@admin.register(InstructorDocument)
class InstructorDocumentAdmin(admin.ModelAdmin):
    """Admin for InstructorDocument with review functionality"""
    list_display = (
        'instructor_name', 'doc_type', 'status_badge', 
        'validation_results', 'uploaded_at', 'reviewed_by', 'file_link'
    )
    list_filter = ('status', 'doc_type', 'uploaded_at', 'cnh_valid', 'cpf_valid')
    search_fields = (
        'instructor__user__username', 'instructor__user__first_name', 
        'instructor__user__last_name', 'extracted_cnh_number', 'extracted_cpf'
    )
    readonly_fields = (
        'uploaded_at', 'updated_at', 'reviewed_at', 'file_preview',
        'extracted_cnh_number', 'extracted_cpf', 'extracted_name',
        'extracted_validity', 'ocr_confidence',
        'cnh_valid', 'cpf_valid', 'validity_ok'
    )
    
    fieldsets = (
        ('Documento', {
            'fields': ('instructor', 'doc_type', 'file', 'file_preview')
        }),
        ('Dados Extraídos via OCR', {
            'fields': (
                'extracted_cnh_number', 'extracted_cpf', 'extracted_name',
                'extracted_validity', 'ocr_confidence'
            ),
            'classes': ('collapse',),
            'description': 'Dados extraídos automaticamente do documento'
        }),
        ('Validação Automática', {
            'fields': ('cnh_valid', 'cpf_valid', 'validity_ok'),
            'classes': ('collapse',),
            'description': 'Resultados da validação algorítmica'
        }),
        ('Revisão Manual', {
            'fields': ('status', 'notes', 'reviewed_by', 'reviewed_at')
        }),
        ('Metadados', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def instructor_name(self, obj):
        return obj.instructor.user.get_full_name()
    instructor_name.short_description = 'Instrutor'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': 'orange',
            'APPROVED': 'green',
            'REJECTED': 'red',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def validation_results(self, obj):
        """Show validation icons"""
        if obj.doc_type != 'CNH':
            return '-'
        
        icons = []
        if obj.cnh_valid is True:
            icons.append('✅ CNH')
        elif obj.cnh_valid is False:
            icons.append('❌ CNH')
        
        if obj.cpf_valid is True:
            icons.append('✅ CPF')
        elif obj.cpf_valid is False:
            icons.append('❌ CPF')
        
        if obj.validity_ok is True:
            icons.append('✅ Validade')
        elif obj.validity_ok is False:
            icons.append('❌ Vencida')
        
        return ' | '.join(icons) if icons else 'Não validado'
    validation_results.short_description = 'Validação'
    
    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Ver arquivo</a>', obj.file.url)
        return '-'
    file_link.short_description = 'Arquivo'
    
    def file_preview(self, obj):
        if obj.file:
            if obj.file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                return format_html('<img src="{}" style="max-width: 400px; max-height: 400px;" />', obj.file.url)
            return format_html('<a href="{}" target="_blank">Baixar arquivo</a>', obj.file.url)
        return '-'
    file_preview.short_description = 'Preview'
    
    actions = ['approve_documents', 'reject_documents']
    
    def approve_documents(self, request, queryset):
        for doc in queryset:
            doc.approve(reviewer=request.user, notes='Aprovado em lote pelo admin')
            AuditLog.log(
                action='DOCUMENT_APPROVED',
                object_type='InstructorDocument',
                object_id=doc.pk,
                actor_user=request.user,
                metadata={'doc_type': doc.doc_type}
            )
        self.message_user(request, f'{queryset.count()} documento(s) aprovado(s).')
    approve_documents.short_description = 'Aprovar documentos selecionados'
    
    def reject_documents(self, request, queryset):
        for doc in queryset:
            doc.reject(reviewer=request.user, notes='Rejeitado em lote pelo admin')
            AuditLog.log(
                action='DOCUMENT_REJECTED',
                object_type='InstructorDocument',
                object_id=doc.pk,
                actor_user=request.user,
                metadata={'doc_type': doc.doc_type}
            )
        self.message_user(request, f'{queryset.count()} documento(s) rejeitado(s).')
    reject_documents.short_description = 'Rejeitar documentos selecionados'
    
    def save_model(self, request, obj, form, change):
        """Auto-set reviewer when status changes"""
        if change and 'status' in form.changed_data and obj.status != 'PENDING':
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
            
            # Log action
            action = 'DOCUMENT_APPROVED' if obj.status == 'APPROVED' else 'DOCUMENT_REJECTED'
            AuditLog.log(
                action=action,
                object_type='InstructorDocument',
                object_id=obj.pk,
                actor_user=request.user,
                metadata={'doc_type': obj.doc_type, 'notes': obj.notes}
            )
        
        super().save_model(request, obj, form, change)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin for AuditLog"""
    list_display = ('actor_user', 'action', 'object_type', 'object_id', 'created_at', 'ip_address')
    list_filter = ('action', 'object_type', 'created_at')
    search_fields = ('actor_user__username', 'action', 'object_type')
    readonly_fields = ('actor_user', 'action', 'object_type', 'object_id', 'metadata', 'created_at', 'ip_address')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

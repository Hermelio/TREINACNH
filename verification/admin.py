"""
Admin configuration for verification app — document review with approve/reject workflow.
"""
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import InstructorDocument, AuditLog, DocumentTypeChoices, DocumentStatusChoices


# ─── helpers ────────────────────────────────────────────────────────────────

def _is_image(path_or_name):
    return str(path_or_name).lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))


# ─── Inline used inside InstructorProfileAdmin (marketplace) ────────────────

class InstructorDocumentInline(admin.TabularInline):
    """Compact inline: all docs for one instructor, readable at a glance."""
    model = InstructorDocument
    extra = 0
    can_delete = False
    fields = ('doc_type', 'inline_preview', 'status', 'notes', 'uploaded_at', 'reviewed_by')
    readonly_fields = ('doc_type', 'inline_preview', 'uploaded_at', 'reviewed_by')
    show_change_link = True

    def inline_preview(self, obj):
        if not obj.file:
            return '—'
        if _is_image(obj.file.name):
            return format_html(
                '<a href="{url}" target="_blank">'
                '<img src="{url}" style="height:64px;width:64px;object-fit:cover;border-radius:6px;border:1px solid #ccc;">'
                '</a>',
                url=obj.file.url,
            )
        return format_html('<a href="{}" target="_blank">📄 Ver arquivo</a>', obj.file.url)
    inline_preview.short_description = 'Arquivo'


# ─── Main InstructorDocument admin ──────────────────────────────────────────

@admin.register(InstructorDocument)
class InstructorDocumentAdmin(admin.ModelAdmin):
    """Full document review admin with approve/reject buttons on the detail page."""

    # ── list ────────────────────────────────────────────────────────────────
    list_display = (
        'instructor_card', 'doc_type_badge', 'file_thumb',
        'selfie_thumb', 'ocr_summary', 'status_badge',
        'uploaded_at', 'reviewed_by',
    )
    list_filter = ('status', 'doc_type', 'uploaded_at')
    list_per_page = 25
    search_fields = (
        'instructor__user__first_name', 'instructor__user__last_name',
        'instructor__user__username', 'extracted_cnh_number', 'extracted_cpf',
    )
    ordering = ('status', '-uploaded_at')   # PENDING first (P < A/R alphabetically)

    # ── detail page ─────────────────────────────────────────────────────────
    readonly_fields = (
        'instructor_info_panel',
        'document_preview_panel',
        'selfie_preview_panel',
        'ocr_data_panel',
        'validation_panel',
        'review_history_panel',
        'uploaded_at', 'updated_at',
        # individual OCR fields kept for completeness but shown via panel
        'extracted_cnh_number', 'extracted_cpf', 'extracted_name',
        'extracted_validity', 'ocr_confidence',
        'cnh_valid', 'cpf_valid', 'validity_ok',
        'reviewed_by', 'reviewed_at',
    )

    fieldsets = (
        ('👤 Instrutor', {
            'fields': ('instructor_info_panel',),
        }),
        ('📄 Documento enviado', {
            'fields': ('instructor', 'doc_type', 'document_preview_panel', 'file'),
        }),
        ('🤳 Selfie', {
            'fields': ('selfie', 'selfie_preview_panel', 'face_match', 'face_confidence'),
        }),
        ('🔍 Dados extraídos via OCR', {
            'fields': ('ocr_data_panel',),
            'classes': ('collapse',),
        }),
        ('✅ Validação automática', {
            'fields': ('validation_panel',),
            'classes': ('collapse',),
        }),
        ('📝 Decisão do admin', {
            'fields': ('status', 'notes'),
            'description': (
                '⬇ Mude o status para <strong>Aprovado</strong> ou <strong>Rejeitado</strong> '
                'e clique em Salvar — ou use os botões rápidos abaixo.'
            ),
        }),
        ('🕑 Histórico de revisão', {
            'fields': ('review_history_panel', 'reviewed_by', 'reviewed_at',
                       'uploaded_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # ── custom actions ───────────────────────────────────────────────────────
    actions = ['action_approve', 'action_reject']

    # ── list display methods ─────────────────────────────────────────────────

    def instructor_card(self, obj):
        user = obj.instructor.user
        full_name = user.get_full_name() or user.username
        verified_icon = '✅' if obj.instructor.is_verified else '⏳'
        return format_html(
            '<strong>{} {}</strong><br/><small style="color:#888">{}</small>',
            verified_icon, full_name, user.email,
        )
    instructor_card.short_description = 'Instrutor'

    def doc_type_badge(self, obj):
        icons = {
            'CNH': '🪪',
            'CERT_INSTRUTOR': '📜',
            'DOC_VEICULO': '🚗',
            'OTHER': '📎',
        }
        icon = icons.get(obj.doc_type, '📎')
        return format_html('{} {}', icon, obj.get_doc_type_display())
    doc_type_badge.short_description = 'Tipo'

    def file_thumb(self, obj):
        if not obj.file:
            return '—'
        if _is_image(obj.file.name):
            return format_html(
                '<a href="{url}" target="_blank">'
                '<img src="{url}" style="height:56px;width:56px;object-fit:cover;'
                'border-radius:4px;border:1px solid #ddd;">'
                '</a>',
                url=obj.file.url,
            )
        return format_html('<a href="{}" target="_blank">📄 PDF</a>', obj.file.url)
    file_thumb.short_description = 'Doc'

    def selfie_thumb(self, obj):
        if not obj.selfie:
            return '—'
        return format_html(
            '<a href="{url}" target="_blank">'
            '<img src="{url}" style="height:56px;width:56px;object-fit:cover;'
            'border-radius:50%;border:2px solid #198754;">'
            '</a>',
            url=obj.selfie.url,
        )
    selfie_thumb.short_description = 'Selfie'

    def ocr_summary(self, obj):
        if obj.doc_type != 'CNH':
            return '—'
        parts = []
        if obj.extracted_name:
            parts.append(f'<span style="color:#383">👤 {obj.extracted_name[:22]}</span>')
        if obj.extracted_cnh_number:
            parts.append(f'CNH: {obj.extracted_cnh_number}')
        if obj.extracted_validity:
            color = '#383' if obj.validity_ok else '#c33'
            parts.append(f'<span style="color:{color}">Val: {obj.extracted_validity}</span>')
        return format_html('<small>{}</small>', ' | '.join(parts)) if parts else '—'
    ocr_summary.short_description = 'OCR'

    def status_badge(self, obj):
        cfg = {
            'PENDING':  ('#ff8c00', '⏳ Pendente'),
            'APPROVED': ('#1a7a3c', '✅ Aprovado'),
            'REJECTED': ('#b91c1c', '❌ Rejeitado'),
        }
        color, label = cfg.get(obj.status, ('#333', obj.get_status_display()))
        return format_html(
            '<span style="color:{};font-weight:700;white-space:nowrap;">{}</span>',
            color, label,
        )
    status_badge.short_description = 'Status'

    # ── readonly panel methods ───────────────────────────────────────────────

    def instructor_info_panel(self, obj):
        inst = obj.instructor
        user = inst.user
        name = user.get_full_name() or user.username
        city = inst.city.name if inst.city else '—'
        state = inst.city.state.code if inst.city else ''
        verified = '<span style="color:#1a7a3c;font-weight:700">✅ VERIFICADO</span>' if inst.is_verified \
                   else '<span style="color:#b91c1c;font-weight:700">⏳ NÃO VERIFICADO</span>'
        doc_counts = inst.documents.values('status').annotate(
            n=__import__('django.db.models', fromlist=['Count']).Count('id')
        )
        counts = {r['status']: r['n'] for r in doc_counts}
        pending  = counts.get('PENDING', 0)
        approved = counts.get('APPROVED', 0)
        rejected = counts.get('REJECTED', 0)
        avatar_html = ''
        if hasattr(user, 'profile') and user.profile.avatar:
            avatar_html = f'<img src="{user.profile.avatar.url}" style="width:56px;height:56px;border-radius:50%;object-fit:cover;float:left;margin-right:12px;">'
        return format_html(
            '<div style="background:#f8f9fa;border:1px solid #dee2e6;border-radius:8px;padding:16px;margin-bottom:4px;">'
            '{avatar}'
            '<div style="overflow:hidden;">'
            '<strong style="font-size:1.1em">{name}</strong>&nbsp;&nbsp;{verified}<br/>'
            '<small style="color:#666">{email} &mdash; {city}/{state}</small><br/><br/>'
            '<span style="background:#ffc107;color:#000;padding:2px 8px;border-radius:12px;font-size:.8em">⏳ {p} pendente(s)</span>&nbsp;'
            '<span style="background:#198754;color:#fff;padding:2px 8px;border-radius:12px;font-size:.8em">✅ {a} aprovado(s)</span>&nbsp;'
            '<span style="background:#dc3545;color:#fff;padding:2px 8px;border-radius:12px;font-size:.8em">❌ {r} rejeitado(s)</span>'
            '</div></div>',
            avatar=format_html(avatar_html),
            name=name, verified=format_html(verified),
            email=user.email, city=city, state=state,
            p=pending, a=approved, r=rejected,
        )
    instructor_info_panel.short_description = 'Informações do Instrutor'

    def document_preview_panel(self, obj):
        if not obj.file:
            return format_html('<em style="color:#999">Nenhum arquivo enviado</em>')
        if _is_image(obj.file.name):
            return format_html(
                '<a href="{url}" target="_blank">'
                '<img src="{url}" style="max-width:100%;max-height:420px;border-radius:8px;border:1px solid #dee2e6;display:block;">'
                '</a>'
                '<br/><a class="button" href="{url}" target="_blank">'
                '⬇ Abrir em nova aba</a>',
                url=obj.file.url,
            )
        return format_html(
            '<a class="button" href="{}" target="_blank">⬇ Baixar / Abrir PDF</a>',
            obj.file.url,
        )
    document_preview_panel.short_description = 'Preview do documento'

    def selfie_preview_panel(self, obj):
        if not obj.selfie:
            return format_html('<em style="color:#999">Selfie não enviada</em>')
        match_html = ''
        if obj.face_match is not None:
            icon = '✅' if obj.face_match else '❌'
            conf = f' ({obj.face_confidence}%)' if obj.face_confidence is not None else ''
            color = '#1a7a3c' if obj.face_match else '#b91c1c'
            match_html = f'<br/><span style="color:{color};font-weight:700">{icon} Correspondência facial{conf}</span>'
        return format_html(
            '<a href="{url}" target="_blank">'
            '<img src="{url}" style="max-width:300px;max-height:360px;border-radius:8px;border:2px solid #198754;">'
            '</a>{match}',
            url=obj.selfie.url,
            match=format_html(match_html),
        )
    selfie_preview_panel.short_description = 'Preview da selfie'

    def ocr_data_panel(self, obj):
        if obj.doc_type != 'CNH':
            return format_html('<em>OCR aplicável apenas para CNH</em>')
        rows = [
            ('Nome', obj.extracted_name),
            ('Número CNH', obj.extracted_cnh_number),
            ('CPF', obj.extracted_cpf),
            ('Validade', obj.extracted_validity),
            ('Confiança OCR', f'{obj.ocr_confidence}%' if obj.ocr_confidence is not None else None),
        ]
        html = '<table style="border-collapse:collapse;width:100%">'
        for label, value in rows:
            val = str(value) if value else '<span style="color:#aaa">—</span>'
            html += f'<tr><td style="padding:4px 12px 4px 0;color:#666;white-space:nowrap"><strong>{label}</strong></td><td>{val}</td></tr>'
        html += '</table>'
        return format_html(html)
    ocr_data_panel.short_description = 'Dados extraídos pelo OCR'

    def validation_panel(self, obj):
        checks = [
            ('CNH válida', obj.cnh_valid),
            ('CPF válido', obj.cpf_valid),
            ('Dentro da validade', obj.validity_ok),
        ]
        parts = []
        for label, result in checks:
            if result is True:
                parts.append(f'<span style="color:#1a7a3c">✅ {label}</span>')
            elif result is False:
                parts.append(f'<span style="color:#b91c1c">❌ {label}</span>')
            else:
                parts.append(f'<span style="color:#999">— {label} (não verificado)</span>')
        return format_html('<br/>'.join(parts))
    validation_panel.short_description = 'Resultado da validação'

    def review_history_panel(self, obj):
        if not obj.reviewed_by:
            return format_html('<em style="color:#999">Ainda não revisado</em>')
        reviewer = obj.reviewed_by.get_full_name() or obj.reviewed_by.username
        date = obj.reviewed_at.strftime('%d/%m/%Y %H:%M') if obj.reviewed_at else '—'
        return format_html(
            '<strong>{}</strong> em <strong>{}</strong>',
            reviewer, date,
        )
    review_history_panel.short_description = 'Revisado por'

    # ── custom URL actions (approve / reject buttons on change page) ─────────

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                '<int:pk>/approve/',
                self.admin_site.admin_view(self.approve_view),
                name='verification_instructordocument_approve',
            ),
            path(
                '<int:pk>/reject/',
                self.admin_site.admin_view(self.reject_view),
                name='verification_instructordocument_reject',
            ),
        ]
        return custom + urls

    def approve_view(self, request, pk):
        doc = get_object_or_404(InstructorDocument, pk=pk)
        notes = request.POST.get('notes', 'Aprovado pelo admin.')
        doc.approve(reviewer=request.user, notes=notes)
        AuditLog.log(
            action='DOCUMENT_APPROVED',
            object_type='InstructorDocument',
            object_id=doc.pk,
            actor_user=request.user,
            metadata={'doc_type': doc.doc_type, 'notes': notes},
        )
        inst_verified = doc.instructor.is_verified
        if inst_verified:
            messages.success(
                request,
                f'✅ Documento aprovado. Instrutor {doc.instructor.user.get_full_name()} recebeu o SELO VERIFICADO!'
            )
        else:
            messages.success(request, '✅ Documento aprovado. Aguardando outros documentos obrigatórios para verificação completa.')
        return HttpResponseRedirect(
            reverse('admin:verification_instructordocument_change', args=[pk])
        )

    def reject_view(self, request, pk):
        doc = get_object_or_404(InstructorDocument, pk=pk)
        notes = request.POST.get('notes', '') or 'Rejeitado pelo admin.'
        doc.reject(reviewer=request.user, notes=notes)
        AuditLog.log(
            action='DOCUMENT_REJECTED',
            object_type='InstructorDocument',
            object_id=doc.pk,
            actor_user=request.user,
            metadata={'doc_type': doc.doc_type, 'notes': notes},
        )
        messages.warning(
            request,
            f'❌ Documento rejeitado. Instrutor notificado para reenviar.'
        )
        return HttpResponseRedirect(
            reverse('admin:verification_instructordocument_change', args=[pk])
        )

    # ── change_view: inject approve / reject button URLs ─────────────────────

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        doc = get_object_or_404(InstructorDocument, pk=object_id)
        extra_context['approve_url'] = reverse('admin:verification_instructordocument_approve', args=[object_id])
        extra_context['reject_url']  = reverse('admin:verification_instructordocument_reject',  args=[object_id])
        extra_context['doc_is_pending'] = doc.status == 'PENDING'
        extra_context['doc_notes']   = doc.notes
        return super().change_view(request, object_id, form_url, extra_context)

    # ── override template to show quick_action_html ──────────────────────────
    change_form_template = 'admin/verification/instructordocument/change_form.html'

    # ── list bulk actions ─────────────────────────────────────────────────────

    def action_approve(self, request, queryset):
        count = 0
        for doc in queryset.filter(status='PENDING'):
            doc.approve(reviewer=request.user, notes='Aprovado em lote pelo admin')
            AuditLog.log('DOCUMENT_APPROVED', 'InstructorDocument', doc.pk,
                         actor_user=request.user, metadata={'doc_type': doc.doc_type})
            count += 1
        self.message_user(request, f'✅ {count} documento(s) aprovado(s).', messages.SUCCESS)
    action_approve.short_description = '✅ Aprovar documentos pendentes selecionados'

    def action_reject(self, request, queryset):
        count = 0
        for doc in queryset.filter(status='PENDING'):
            doc.reject(reviewer=request.user, notes='Rejeitado em lote pelo admin')
            AuditLog.log('DOCUMENT_REJECTED', 'InstructorDocument', doc.pk,
                         actor_user=request.user, metadata={'doc_type': doc.doc_type})
            count += 1
        self.message_user(request, f'❌ {count} documento(s) rejeitado(s).', messages.WARNING)
    action_reject.short_description = '❌ Rejeitar documentos pendentes selecionados'

    # ── save_model: auto-fill reviewer + audit when status edited via form ────

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status != 'PENDING':
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
            action = 'DOCUMENT_APPROVED' if obj.status == 'APPROVED' else 'DOCUMENT_REJECTED'
            super().save_model(request, obj, form, change)
            # trigger verification logic
            if obj.status == 'APPROVED':
                obj._update_instructor_verification()
            else:
                obj.instructor.is_verified = False
                obj.instructor.save()
            AuditLog.log(action, 'InstructorDocument', obj.pk,
                         actor_user=request.user,
                         metadata={'doc_type': obj.doc_type, 'notes': obj.notes})
            return
        super().save_model(request, obj, form, change)


# ─── AuditLog admin ─────────────────────────────────────────────────────────

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
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

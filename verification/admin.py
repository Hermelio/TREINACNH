"""
Admin de verificação — fila de aprovação de documentos dos instrutores.

Estrutura:
  ⏳ Fila de Aprovação  → apenas PENDING, para o time de revisão
  Documentos completos → todos os status
  Logs de Auditoria    → histórico imutável
"""
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import (
    InstructorDocument, AuditLog, PendingDocument,
    DocumentTypeChoices, DocumentStatusChoices,
)

# ─── Branding do admin ───────────────────────────────────────────────────────

admin.site.site_header = '🚗 TreinaCNH — Painel Administrativo'
admin.site.site_title  = 'TreinaCNH Admin'
admin.site.index_title = 'Central de Gerenciamento'


# ─── Helpers ────────────────────────────────────────────────────────────────

def _is_image(path_or_name):
    return str(path_or_name).lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))


# ─── Inline usado no InstructorProfileAdmin (marketplace/admin.py) ───────────

class InstructorDocumentInline(admin.TabularInline):
    """Inline compacto: todos os docs de um instrutor numa linha."""
    model            = InstructorDocument
    extra            = 0
    can_delete       = False
    show_change_link = True
    fields           = ('doc_type', 'inline_preview', 'status', 'notes', 'uploaded_at', 'reviewed_by')
    readonly_fields  = ('doc_type', 'inline_preview', 'uploaded_at', 'reviewed_by')
    verbose_name     = 'Documento enviado'
    verbose_name_plural = 'Documentos enviados'

    def inline_preview(self, obj):
        if not obj.file:
            return '—'
        if _is_image(obj.file.name):
            return format_html(
                '<a href="{url}" target="_blank">'
                '<img src="{url}" style="height:60px;width:60px;object-fit:cover;'
                'border-radius:6px;border:1px solid #ccc;">'
                '</a>',
                url=obj.file.url,
            )
        return format_html('<a href="{}" target="_blank">📄 Ver arquivo</a>', obj.file.url)
    inline_preview.short_description = 'Arquivo'


# ─── Mixin compartilhado: métodos de exibição e ações ────────────────────────

class _DocumentAdminMixin:
    """Métodos reutilizados por InstructorDocumentAdmin e PendingDocumentAdmin."""

    # ── colunas da lista ──────────────────────────────────────────────────────

    def instructor_card(self, obj):
        user = obj.instructor.user
        nome = user.get_full_name() or user.username
        icon = '✅' if obj.instructor.is_verified else '⏳'
        return format_html(
            '<strong>{} {}</strong><br/><small style="color:#777">{}</small>',
            icon, nome, user.email,
        )
    instructor_card.short_description = 'Instrutor'
    instructor_card.admin_order_field = 'instructor__user__first_name'

    def doc_type_badge(self, obj):
        icons = {'CNH': '🪪', 'CERT_INSTRUTOR': '📜', 'DOC_VEICULO': '🚗', 'OTHER': '📎'}
        return format_html('{} {}', icons.get(obj.doc_type, '📎'), obj.get_doc_type_display())
    doc_type_badge.short_description = 'Tipo'
    doc_type_badge.admin_order_field = 'doc_type'

    def file_thumb(self, obj):
        if not obj.file:
            return '—'
        if _is_image(obj.file.name):
            return format_html(
                '<a href="{url}" target="_blank">'
                '<img src="{url}" style="height:52px;width:52px;object-fit:cover;'
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
            '<img src="{url}" style="height:52px;width:52px;object-fit:cover;'
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
            parts.append(f'<b>{obj.extracted_name[:22]}</b>')
        if obj.extracted_cnh_number:
            parts.append(f'CNH {obj.extracted_cnh_number}')
        if obj.extracted_validity:
            color = '#1a7a3c' if obj.validity_ok else '#b91c1c'
            parts.append(f'<span style="color:{color}">Val: {obj.extracted_validity}</span>')
        return format_html('<small>{}</small>', ' | '.join(parts)) if parts else '—'
    ocr_summary.short_description = 'OCR'

    def status_badge(self, obj):
        cfg = {
            'PENDING':  ('#d97706', '#fff8e1', '⏳ Pendente'),
            'APPROVED': ('#1a7a3c', '#f0fdf4', '✅ Aprovado'),
            'REJECTED': ('#b91c1c', '#fff1f2', '❌ Rejeitado'),
        }
        c, bg, label = cfg.get(obj.status, ('#555', '#f5f5f5', obj.get_status_display()))
        return format_html(
            '<span style="color:{c};background:{bg};font-weight:700;white-space:nowrap;'
            'padding:3px 10px;border-radius:12px;font-size:.88em;">{l}</span>',
            c=c, bg=bg, l=label,
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def days_waiting(self, obj):
        """Dias desde o envio (só faz sentido para PENDING)."""
        if obj.status != 'PENDING':
            return '—'
        delta = (timezone.now() - obj.uploaded_at).days
        color = '#b91c1c' if delta >= 3 else ('#d97706' if delta >= 1 else '#1a7a3c')
        return format_html(
            '<span style="color:{};font-weight:700">{} dia(s)</span>', color, delta
        )
    days_waiting.short_description = '⏱ Aguardando'

    # ── painéis readonly no detalhe ───────────────────────────────────────────

    def instructor_info_panel(self, obj):
        inst  = obj.instructor
        user  = inst.user
        nome  = user.get_full_name() or user.username
        city  = inst.city.name if inst.city else '—'
        state = inst.city.state.code if inst.city else ''
        v_html = ('<span style="color:#1a7a3c;font-weight:700">✅ VERIFICADO</span>'
                  if inst.is_verified else
                  '<span style="color:#b91c1c;font-weight:700">⏳ NÃO VERIFICADO</span>')
        counts = dict(inst.documents.values_list('status').annotate(n=Count('id')))
        p = counts.get('PENDING', 0)
        a = counts.get('APPROVED', 0)
        r = counts.get('REJECTED', 0)
        avatar_html = ''
        if hasattr(user, 'profile') and user.profile.avatar:
            avatar_html = (
                f'<img src="{user.profile.avatar.url}" '
                f'style="width:52px;height:52px;border-radius:50%;object-fit:cover;'
                f'float:left;margin-right:14px;">'
            )
        return format_html(
            '<div style="background:#f8f9fa;border:1px solid #dee2e6;border-radius:8px;'
            'padding:16px;margin-bottom:4px;">'
            '{avatar}'
            '<div style="overflow:hidden;">'
            '<strong style="font-size:1.1em">{nome}</strong>&nbsp;&nbsp;{v}<br/>'
            '<small style="color:#666">{email} &mdash; {city}/{state}</small><br/><br/>'
            '<span style="background:#ffc107;color:#000;padding:2px 10px;border-radius:12px;font-size:.82em">⏳ {p} pendente(s)</span>&nbsp;'
            '<span style="background:#198754;color:#fff;padding:2px 10px;border-radius:12px;font-size:.82em">✅ {a} aprovado(s)</span>&nbsp;'
            '<span style="background:#dc3545;color:#fff;padding:2px 10px;border-radius:12px;font-size:.82em">❌ {r} rejeitado(s)</span>'
            '</div></div>',
            avatar=format_html(avatar_html),
            nome=nome, v=format_html(v_html),
            email=user.email, city=city, state=state,
            p=p, a=a, r=r,
        )
    instructor_info_panel.short_description = 'Informações do Instrutor'

    def document_preview_panel(self, obj):
        if not obj.file:
            return format_html('<em style="color:#999">Nenhum arquivo enviado</em>')
        if _is_image(obj.file.name):
            return format_html(
                '<a href="{url}" target="_blank">'
                '<img src="{url}" style="max-width:100%;max-height:420px;'
                'border-radius:8px;border:1px solid #dee2e6;display:block;">'
                '</a><br/>'
                '<a class="button" href="{url}" target="_blank">⬇ Abrir em nova aba</a>',
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
            icon  = '✅' if obj.face_match else '❌'
            conf  = f' ({obj.face_confidence}%)' if obj.face_confidence is not None else ''
            color = '#1a7a3c' if obj.face_match else '#b91c1c'
            match_html = (
                f'<br/><span style="color:{color};font-weight:700">'
                f'{icon} Correspondência facial{conf}</span>'
            )
        return format_html(
            '<a href="{url}" target="_blank">'
            '<img src="{url}" style="max-width:280px;max-height:340px;'
            'border-radius:8px;border:2px solid #198754;">'
            '</a>{match}',
            url=obj.selfie.url,
            match=format_html(match_html),
        )
    selfie_preview_panel.short_description = 'Preview da selfie'

    def ocr_data_panel(self, obj):
        if obj.doc_type != 'CNH':
            return format_html('<em>OCR aplicável apenas para CNH</em>')
        rows = [
            ('Nome',        obj.extracted_name),
            ('Número CNH',  obj.extracted_cnh_number),
            ('CPF',         obj.extracted_cpf),
            ('Validade',    obj.extracted_validity),
            ('Confiança OCR', f'{obj.ocr_confidence}%' if obj.ocr_confidence is not None else None),
        ]
        html = '<table style="border-collapse:collapse;width:100%">'
        for label, value in rows:
            val = str(value) if value else '<span style="color:#aaa">—</span>'
            html += (
                f'<tr>'
                f'<td style="padding:4px 14px 4px 0;color:#555;white-space:nowrap">'
                f'<strong>{label}</strong></td>'
                f'<td>{val}</td></tr>'
            )
        html += '</table>'
        return format_html(html)
    ocr_data_panel.short_description = 'Dados extraídos pelo OCR'

    def validation_panel(self, obj):
        checks = [
            ('CNH válida',         obj.cnh_valid),
            ('CPF válido',         obj.cpf_valid),
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
    validation_panel.short_description = 'Resultado da validação automática'

    def review_history_panel(self, obj):
        if not obj.reviewed_by:
            return format_html('<em style="color:#999">Ainda não revisado</em>')
        reviewer = obj.reviewed_by.get_full_name() or obj.reviewed_by.username
        date     = obj.reviewed_at.strftime('%d/%m/%Y %H:%M') if obj.reviewed_at else '—'
        status_map = {'APPROVED': ('✅', '#1a7a3c'), 'REJECTED': ('❌', '#b91c1c')}
        icon, color = status_map.get(obj.status, ('•', '#555'))
        notes_html  = format_html('<br/><em>"{}"</em>', obj.notes) if obj.notes else ''
        return format_html(
            '<span style="color:{c}">{icon} {status}</span> — '
            'por <strong>{reviewer}</strong> em <strong>{date}</strong>{notes}',
            c=color, icon=icon, status=obj.get_status_display(),
            reviewer=reviewer, date=date, notes=notes_html,
        )
    review_history_panel.short_description = 'Revisado por'

    # ── URLs customizadas: botões Aprovar / Rejeitar na página de detalhe ─────

    def get_urls(self):
        urls  = super().get_urls()
        app   = self.model._meta.app_label
        model = self.model._meta.model_name
        custom = [
            path(
                '<int:pk>/approve/',
                self.admin_site.admin_view(self.approve_view),
                name=f'{app}_{model}_approve',
            ),
            path(
                '<int:pk>/reject/',
                self.admin_site.admin_view(self.reject_view),
                name=f'{app}_{model}_reject',
            ),
        ]
        return custom + urls

    def approve_view(self, request, pk):
        if request.method != 'POST':
            return HttpResponseRedirect(
                reverse('admin:verification_instructordocument_change', args=[pk])
            )
        doc   = get_object_or_404(InstructorDocument, pk=pk)
        notes = (request.POST.get('notes') or '').strip() or 'Aprovado pelo admin.'
        doc.approve(reviewer=request.user, notes=notes)
        AuditLog.log(
            'DOCUMENT_APPROVED', 'InstructorDocument', doc.pk,
            actor_user=request.user,
            metadata={'doc_type': doc.doc_type, 'notes': notes},
        )
        if doc.instructor.is_verified:
            messages.success(
                request,
                f'✅ Documento aprovado — {doc.instructor.user.get_full_name()} '
                f'recebeu o SELO VERIFICADO! 🎉',
            )
        else:
            messages.success(
                request,
                '✅ Documento aprovado. Aguardando demais documentos obrigatórios.',
            )
        return HttpResponseRedirect(
            reverse('admin:verification_instructordocument_change', args=[doc.pk])
        )

    def reject_view(self, request, pk):
        if request.method != 'POST':
            return HttpResponseRedirect(
                reverse('admin:verification_instructordocument_change', args=[pk])
            )
        doc   = get_object_or_404(InstructorDocument, pk=pk)
        notes = (request.POST.get('notes') or '').strip()
        if not notes:
            messages.error(
                request,
                '⚠️ Informe o motivo da rejeição antes de prosseguir.',
            )
            return HttpResponseRedirect(
                reverse('admin:verification_instructordocument_change', args=[pk])
            )
        doc.reject(reviewer=request.user, notes=notes)
        AuditLog.log(
            'DOCUMENT_REJECTED', 'InstructorDocument', doc.pk,
            actor_user=request.user,
            metadata={'doc_type': doc.doc_type, 'notes': notes},
        )
        messages.warning(request, '❌ Documento rejeitado. Instrutor será notificado.')
        return HttpResponseRedirect(
            reverse('admin:verification_instructordocument_change', args=[doc.pk])
        )

    # ── change_view: injeta URLs dos botões no contexto do template ───────────

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        doc   = get_object_or_404(InstructorDocument, pk=object_id)
        app   = self.model._meta.app_label
        model = self.model._meta.model_name
        extra_context['approve_url']    = reverse(f'admin:{app}_{model}_approve', args=[object_id])
        extra_context['reject_url']     = reverse(f'admin:{app}_{model}_reject',  args=[object_id])
        extra_context['doc_is_pending'] = doc.status == 'PENDING'
        extra_context['doc_notes']      = doc.notes or ''
        return super().change_view(request, object_id, form_url, extra_context)

    # ── ações em massa ────────────────────────────────────────────────────────

    def action_approve(self, request, queryset):
        count = 0
        for doc in queryset.filter(status='PENDING'):
            doc.approve(reviewer=request.user, notes='Aprovado em lote pelo admin')
            AuditLog.log(
                'DOCUMENT_APPROVED', 'InstructorDocument', doc.pk,
                actor_user=request.user, metadata={'doc_type': doc.doc_type},
            )
            count += 1
        self.message_user(request, f'✅ {count} documento(s) aprovado(s).', messages.SUCCESS)
    action_approve.short_description = '✅ Aprovar documentos pendentes selecionados'

    def action_reject(self, request, queryset):
        count = 0
        for doc in queryset.filter(status='PENDING'):
            doc.reject(reviewer=request.user, notes='Rejeitado em lote pelo admin')
            AuditLog.log(
                'DOCUMENT_REJECTED', 'InstructorDocument', doc.pk,
                actor_user=request.user, metadata={'doc_type': doc.doc_type},
            )
            count += 1
        self.message_user(request, f'❌ {count} documento(s) rejeitado(s).', messages.WARNING)
    action_reject.short_description = '❌ Rejeitar documentos pendentes selecionados'

    # ── save_model: preenche revisor quando status é editado via formulário ───

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status != 'PENDING':
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
            super().save_model(request, obj, form, change)
            if obj.status == 'APPROVED':
                obj._update_instructor_verification()
            else:
                obj.instructor.is_verified = False
                obj.instructor.save()
            action = 'DOCUMENT_APPROVED' if obj.status == 'APPROVED' else 'DOCUMENT_REJECTED'
            AuditLog.log(
                action, 'InstructorDocument', obj.pk,
                actor_user=request.user,
                metadata={'doc_type': obj.doc_type, 'notes': obj.notes},
            )
            return
        super().save_model(request, obj, form, change)


# ─── Admin de todos os documentos (lista completa) ───────────────────────────

@admin.register(InstructorDocument)
class InstructorDocumentAdmin(_DocumentAdminMixin, admin.ModelAdmin):
    """Lista completa de documentos — todos os status."""

    change_form_template = 'admin/verification/instructordocument/change_form.html'

    list_display  = (
        'instructor_card', 'doc_type_badge', 'file_thumb',
        'selfie_thumb', 'ocr_summary', 'status_badge',
        'days_waiting', 'uploaded_at', 'reviewed_by',
    )
    list_filter   = ('status', 'doc_type', 'uploaded_at')
    list_per_page = 30
    search_fields = (
        'instructor__user__first_name', 'instructor__user__last_name',
        'instructor__user__username', 'extracted_cnh_number', 'extracted_cpf',
    )
    ordering = ('status', '-uploaded_at')   # PENDING aparece primeiro

    readonly_fields = (
        'instructor_info_panel',
        'document_preview_panel',
        'selfie_preview_panel',
        'ocr_data_panel',
        'validation_panel',
        'review_history_panel',
        'uploaded_at', 'updated_at',
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
                'Use os botões <strong>APROVAR / REJEITAR</strong> no topo da página, '
                'ou altere o status aqui e clique em Salvar.'
            ),
        }),
        ('🕑 Histórico de revisão', {
            'fields': ('review_history_panel', 'reviewed_by', 'reviewed_at',
                       'uploaded_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    actions = ['action_approve', 'action_reject']


# ─── ⏳ FILA DE APROVAÇÃO — tela principal do time de revisão ─────────────────

@admin.register(PendingDocument)
class PendingDocumentAdmin(_DocumentAdminMixin, admin.ModelAdmin):
    """
    Mostra apenas documentos PENDENTES.
    Esta é a tela que o time de revisão usa diariamente.
    Ordenação FIFO: os mais antigos aparecem primeiro.
    """

    change_form_template = 'admin/verification/instructordocument/change_form.html'

    list_display  = (
        'instructor_card', 'doc_type_badge', 'file_thumb',
        'selfie_thumb', 'ocr_summary', 'days_waiting', 'uploaded_at',
    )
    list_filter   = ('doc_type', 'uploaded_at')
    list_per_page = 25
    search_fields = (
        'instructor__user__first_name', 'instructor__user__last_name',
        'instructor__user__username',
    )
    ordering = ('uploaded_at',)   # FIFO — mais antigo primeiro

    readonly_fields = (
        'instructor_info_panel',
        'document_preview_panel',
        'selfie_preview_panel',
        'ocr_data_panel',
        'validation_panel',
        'uploaded_at', 'updated_at',
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
        ('📝 Observações para a decisão', {
            'fields': ('notes',),
            'description': (
                'Preencha o motivo e clique em '
                '<strong>✅ APROVAR</strong> ou <strong>❌ REJEITAR</strong> no topo da página.'
            ),
        }),
    )

    actions = ['action_approve', 'action_reject']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status='PENDING')

    def has_add_permission(self, request):
        return False   # instrutores enviam pelo portal

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ─── AuditLog admin ─────────────────────────────────────────────────────────

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display    = ('actor_user', 'action', 'object_type', 'object_id', 'created_at', 'ip_address')
    list_filter     = ('action', 'object_type', 'created_at')
    search_fields   = ('actor_user__username', 'action', 'object_type')
    readonly_fields = ('actor_user', 'action', 'object_type', 'object_id', 'metadata', 'created_at', 'ip_address')
    date_hierarchy  = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ─── Carrega admin de segurança (UserReport, DocumentBlacklist, etc.) ─────────
from . import admin_security  # noqa: F401, E402

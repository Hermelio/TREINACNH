"""
Admin configuration for marketplace app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path
from django.utils import timezone
from datetime import timedelta
import csv
from .models import (
    State, City, CategoryCNH, InstructorProfile, Lead, StudentLead,
    InstructorAvailability, Appointment, CityGeoCache
)
from .geocoding_service import GeocodingService
import threading


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    """Admin for State model"""
    list_display = ('code', 'name', 'city_count')
    search_fields = ('code', 'name')
    
    def city_count(self, obj):
        return obj.cities.count()
    city_count.short_description = 'Cidades'


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Admin for City model"""
    list_display = ('name', 'state', 'slug', 'is_active', 'instructor_count', 'geocoded_status', 'created_at')
    list_filter = ('state', 'is_active')
    search_fields = ('name', 'state__code')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    actions = ['geocode_selected_cities']
    
    def geocoded_status(self, obj):
        """Show if city is geocoded"""
        city_key = CityGeoCache.normalize_city_key(obj.name, obj.state.code)
        try:
            cache = CityGeoCache.objects.get(city_key=city_key)
            if cache.geocoded:
                return format_html('<span style="color: green;">✓ Geocodificado</span>')
            elif cache.failed:
                return format_html('<span style="color: red;">✗ Falhou</span>')
            else:
                return format_html('<span style="color: orange;">? Pendente</span>')
        except CityGeoCache.DoesNotExist:
            return format_html('<span style="color: gray;">○ Não processado</span>')
    geocoded_status.short_description = 'Geocoding'
    
    def geocode_selected_cities(self, request, queryset):
        """Action to geocode selected cities"""
        def geocode_cities():
            for city in queryset:
                GeocodingService.get_city_latlng(city.name, city.state.code)
        
        thread = threading.Thread(target=geocode_cities)
        thread.daemon = True
        thread.start()
        
        self.message_user(
            request,
            f"Iniciado geocoding de {queryset.count()} cidades em background.",
            messages.SUCCESS
        )
    geocode_selected_cities.short_description = "Geocodificar cidades selecionadas"


@admin.register(CityGeoCache)
class CityGeoCacheAdmin(admin.ModelAdmin):
    """Admin for CityGeoCache model"""
    list_display = ('city_name', 'state_code', 'geocoded', 'failed', 'latitude', 'longitude', 'provider', 'attempts', 'updated_at')
    list_filter = ('geocoded', 'failed', 'state_code', 'provider')
    search_fields = ('city_name', 'state_code', 'city_key')
    readonly_fields = ('city_key', 'created_at', 'updated_at', 'attempts')
    actions = ['retry_failed_geocoding']
    
    def retry_failed_geocoding(self, request, queryset):
        """Retry geocoding for failed entries"""
        def retry_geocode():
            for cache in queryset.filter(failed=True):
                # Reset failed status
                cache.failed = False
                cache.save()
                # Try again
                GeocodingService.get_city_latlng(cache.city_name, cache.state_code)
        
        thread = threading.Thread(target=retry_geocode)
        thread.daemon = True
        thread.start()
        
        self.message_user(
            request,
            f"Iniciado retry de geocoding para {queryset.filter(failed=True).count()} cidades.",
            messages.SUCCESS
        )
    retry_failed_geocoding.short_description = "Tentar geocodificar novamente"


@admin.register(CategoryCNH)
class CategoryCNHAdmin(admin.ModelAdmin):
    """Admin for CategoryCNH model"""
    list_display = ('code', 'label', 'instructor_count')
    
    def instructor_count(self, obj):
        return obj.instructors.count()
    instructor_count.short_description = 'Instrutores'


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    """Admin for InstructorProfile model"""
    list_display = (
        'user_full_name', 'user_cpf', 'city', 'user_phone',
        'verification_status', 'pioneer_badge', 'visible_badge',
        'trial_status_badge', 'completion_badge', 'created_at',
    )
    list_display_links = ('user_full_name',)
    list_per_page = 25
    list_filter = ('is_verified', 'is_visible', 'is_trial_active', 'gender', 'has_own_car', 'city__state', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'city__name', 'user__profile__cpf', 'user__profile__phone')
    readonly_fields = ('created_at', 'updated_at', 'profile_completion_score', 'user_cpf', 'verification_denied_at')
    filter_horizontal = ('categories',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Usuário', {
            'fields': ('user', 'user_cpf', 'city')
        }),
        ('Informações Profissionais', {
            'fields': ('bio', 'neighborhoods_text', 'years_experience', 'categories')
        }),
        ('Informações Pessoais', {
            'fields': ('gender', 'age')
        }),
        ('Veículo', {
            'fields': ('has_own_car', 'car_model')
        }),
        ('Disponibilidade', {
            'fields': ('available_morning', 'available_afternoon', 'available_evening')
        }),
        ('Preços', {
            'fields': ('base_price_per_hour', 'price_notes')
        }),
        ('Status', {
            'fields': ('is_visible', 'is_verified', 'profile_completion_score',
                       'verification_denied', 'verification_denied_at')
        }),
        ('⏱ Trial Gratuito', {
            'fields': ('is_trial_active', 'trial_start_date', 'trial_end_date'),
            'description': 'Edite diretamente as datas ou use as ações em massa na listagem para adicionar/remover dias.',
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = 'Instrutor'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def user_phone(self, obj):
        if hasattr(obj.user, 'profile') and obj.user.profile.phone:
            return obj.user.profile.phone
        return '-'
    user_phone.short_description = 'Telefone'

    def user_cpf(self, obj):
        if hasattr(obj.user, 'profile') and obj.user.profile.cpf:
            # Format CPF: XXX.XXX.XXX-XX
            cpf = obj.user.profile.cpf
            if len(cpf) == 11:
                return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
            return cpf
        return '-'
    user_cpf.short_description = 'CPF'

    def verification_status(self, obj):
        if obj.is_verified:
            return format_html('<span class="badge-verified">✓ Verificado</span>')
        return format_html('<span class="badge-pending">⏳ Pendente</span>')
    verification_status.short_description = 'Status'

    def pioneer_badge(self, obj):
        if getattr(obj, 'is_pioneer', False):
            return format_html('<span class="badge-pioneer">⭐ Pioneiro</span>')
        return '—'
    pioneer_badge.short_description = 'Pioneiro'

    def visible_badge(self, obj):
        if obj.is_visible:
            return format_html('<span class="badge-visible">👁 Visível</span>')
        return format_html('<span class="badge-hidden">🔒 Oculto</span>')
    visible_badge.short_description = 'Visibilidade'

    def completion_badge(self, obj):
        try:
            score = obj.profile_completion_score
            if isinstance(score, str):
                score = float(score.replace('%', '').strip())
            else:
                score = float(score)
        except (ValueError, AttributeError):
            score = 0
        css = 'badge-active' if score >= 80 else ('badge-pending' if score >= 50 else 'badge-failed')
        return format_html('<span class="{}">{}</span>', css, '{}%'.format(int(score)))
    completion_badge.short_description = 'Completude'

    actions = [
        'approve_instructors', 'mark_not_authorized',
        'make_unverified', 'make_visible', 'make_invisible', 'export_to_csv',
        'trial_add_7', 'trial_add_14', 'trial_add_30',
        'trial_sub_7', 'trial_sub_14',
        'trial_custom_days',
    ]

    def export_to_csv(self, request, queryset):
        """Export selected instructors to CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="instrutores_export.csv"'
        response.write('\ufeff')  # UTF-8 BOM for Excel compatibility
        
        writer = csv.writer(response)
        # Header
        writer.writerow([
            'ID', 'Nome Completo', 'Email', 'Telefone', 'WhatsApp', 'CPF',
            'Cidade', 'Estado', 'Gênero', 'Idade', 'Anos Experiência',
            'Categorias CNH', 'Possui Carro', 'Modelo Carro', 
            'Preço Base/Hora', 'Disponibilidade Manhã', 'Disponibilidade Tarde', 
            'Disponibilidade Noite', 'Verificado', 'Visível', 'Score Completude',
            'Data Cadastro'
        ])
        
        # Data rows
        for instructor in queryset.select_related('user', 'city', 'city__state').prefetch_related('categories'):
            profile = instructor.user.profile if hasattr(instructor.user, 'profile') else None
            writer.writerow([
                instructor.id,
                instructor.user.get_full_name() or instructor.user.username,
                instructor.user.email,
                profile.phone if profile else '',
                profile.whatsapp_number if profile else '',
                profile.cpf if profile else '',
                instructor.city.name if instructor.city else '',
                instructor.city.state.code if instructor.city else '',
                instructor.get_gender_display(),
                instructor.age or '',
                instructor.years_experience or '',
                ', '.join([cat.code for cat in instructor.categories.all()]),
                'Sim' if instructor.has_own_car else 'Não',
                instructor.car_model or '',
                instructor.base_price_per_hour or '',
                'Sim' if instructor.available_morning else 'Não',
                'Sim' if instructor.available_afternoon else 'Não',
                'Sim' if instructor.available_evening else 'Não',
                'Sim' if instructor.is_verified else 'Não',
                'Sim' if instructor.is_visible else 'Não',
                f'{instructor.profile_completion_score}%',
                instructor.created_at.strftime('%d/%m/%Y %H:%M'),
            ])
        
        self.message_user(request, f'{queryset.count()} instrutor(es) exportado(s) para CSV.')
        return response
    export_to_csv.short_description = '📥 Exportar selecionados para CSV'

    def approve_instructors(self, request, queryset):
        """
        Approve selected instructors after manual validation.
        This marks them as verified and activates their trial period if applicable.
        """
        count = 0
        for instructor in queryset:
            if not instructor.is_verified:
                instructor.is_verified = True
                # Activate trial if not already active and has no subscription
                if not instructor.is_trial_active and not instructor.has_active_subscription():
                    instructor.activate_trial()
                instructor.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} instrutor(es) aprovado(s) com sucesso! Trial de 14 dias ativado para novos instrutores.',
            messages.SUCCESS
        )
    approve_instructors.short_description = '✅ APROVAR INSTRUTORES (após validação manual dos dados)'

    def mark_not_authorized(self, request, queryset):
        """Mark instructors as not authorized by Detran. Hides profile and shows denial notice."""
        count = 0
        for instructor in queryset:
            instructor.is_verified = False
            instructor.is_visible = False
            instructor.verification_denied = True
            instructor.verification_denied_at = timezone.now()
            instructor.save(update_fields=[
                'is_verified', 'is_visible',
                'verification_denied', 'verification_denied_at',
            ])
            count += 1
        self.message_user(
            request,
            f'{count} instrutor(es) marcado(s) como Não Autorizado. '
            'Perfis ocultados. Instrutor(es) verão aviso no painel.',
            messages.WARNING,
        )
    mark_not_authorized.short_description = '🚫 Não autorizado (negado pelo Detran)'

    def make_unverified(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} instrutor(es) desmarcado(s) como verificado.')
    make_unverified.short_description = 'Remover verificação'

    def make_visible(self, request, queryset):
        updated = queryset.update(is_visible=True)
        self.message_user(request, f'{updated} instrutor(es) tornado(s) visível(is).')
    make_visible.short_description = 'Tornar visível'

    def make_invisible(self, request, queryset):
        updated = queryset.update(is_visible=False)
        self.message_user(request, f'{updated} instrutor(es) tornado(s) invisível(is).')
    make_invisible.short_description = 'Tornar invisível'

    # ---- Trial management helpers ----

    def trial_status_badge(self, obj):
        if not obj.is_trial_active:
            if obj.trial_end_date and obj.trial_end_date < timezone.now():
                return format_html('<span class="badge-trial-exp">⛔ Expirado</span>')
            return format_html('<span class="badge-inactive">— Sem trial</span>')
        if obj.trial_end_date:
            remaining = (obj.trial_end_date - timezone.now()).days
            if remaining < 0:
                return format_html('<span class="badge-trial-exp">⛔ Expirado</span>')
            css = 'badge-active' if remaining > 7 else ('badge-pending' if remaining > 2 else 'badge-failed')
            return format_html('<span class="{}">⏱ {} dia(s)</span>', css, remaining)
        return format_html('<span class="badge-trial">Ativo</span>')
    trial_status_badge.short_description = 'Trial'

    def _adjust_trial(self, request, queryset, days):
        updated = 0
        for instructor in queryset:
            if instructor.trial_end_date:
                instructor.trial_end_date = instructor.trial_end_date + timedelta(days=days)
            else:
                # Se ainda não tem trial, cria a partir de agora
                instructor.trial_start_date = timezone.now()
                instructor.trial_end_date = timezone.now() + timedelta(days=max(days, 0))
                instructor.is_trial_active = True
            # Reativa trial se foi adicionado dias e estava inativo/expirado
            if days > 0 and instructor.trial_end_date > timezone.now():
                instructor.is_trial_active = True
            instructor.save(update_fields=['trial_start_date', 'trial_end_date', 'is_trial_active'])
            updated += 1
        verb = f'+{days}' if days > 0 else str(days)
        self.message_user(
            request,
            f'{updated} instrutor(es) ajustado(s): {verb} dia(s) no trial.',
            messages.SUCCESS,
        )

    def trial_add_7(self, request, queryset):
        self._adjust_trial(request, queryset, 7)
    trial_add_7.short_description = '⏱ Trial: adicionar +7 dias'

    def trial_add_14(self, request, queryset):
        self._adjust_trial(request, queryset, 14)
    trial_add_14.short_description = '⏱ Trial: adicionar +14 dias'

    def trial_add_30(self, request, queryset):
        self._adjust_trial(request, queryset, 30)
    trial_add_30.short_description = '⏱ Trial: adicionar +30 dias'

    def trial_sub_7(self, request, queryset):
        self._adjust_trial(request, queryset, -7)
    trial_sub_7.short_description = '⏱ Trial: remover -7 dias'

    def trial_sub_14(self, request, queryset):
        self._adjust_trial(request, queryset, -14)
    trial_sub_14.short_description = '⏱ Trial: remover -14 dias'

    def trial_custom_days(self, request, queryset):
        """Ação com formulário intermediário para número personalizado de dias."""
        if 'apply' in request.POST:
            try:
                days = int(request.POST.get('days', 0))
            except (ValueError, TypeError):
                self.message_user(request, 'Valor inválido. Digite um número inteiro.', messages.ERROR)
                return
            self._adjust_trial(request, queryset, days)
            return

        # Monta o formulário intermediário inline
        ids = request.POST.getlist('_selected_action')
        names = ', '.join(
            inst.user.get_full_name() or inst.user.username
            for inst in queryset[:5]
        )
        extra = f' e mais {queryset.count() - 5}...' if queryset.count() > 5 else ''
        form_html = f"""
        <html><head><title>Ajustar Trial</title>
        <style>
            body {{font-family:Arial,sans-serif;margin:40px;color:#333}}
            .box {{background:#f8f9fa;border:1px solid #dee2e6;border-radius:8px;padding:30px;max-width:480px}}
            h2 {{margin-top:0;color:#495057}}
            label {{display:block;margin-bottom:6px;font-weight:bold}}
            input[type=number] {{width:120px;padding:8px;font-size:16px;border:1px solid #ced4da;border-radius:4px}}
            .hint {{color:#6c757d;font-size:13px;margin-top:4px}}
            .btns {{margin-top:20px}}
            .btn-primary {{background:#007bff;color:#fff;border:none;padding:10px 24px;border-radius:4px;font-size:15px;cursor:pointer}}
            .btn-cancel {{background:#6c757d;color:#fff;border:none;padding:10px 18px;border-radius:4px;font-size:15px;cursor:pointer;margin-left:10px;text-decoration:none}}
        </style></head><body>
        <div class="box">
            <h2>⏱ Ajustar Trial Personalizado</h2>
            <p>Instrutores selecionados: <strong>{names}{extra}</strong></p>
            <form method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="{self._get_csrf_token(request)}"/>
                <input type="hidden" name="action" value="trial_custom_days"/>
                {''.join(f'<input type="hidden" name="_selected_action" value="{i}"/>' for i in ids)}
                <label for="days">Dias a ajustar:</label>
                <input type="number" id="days" name="days" value="7" min="-365" max="365" required/>
                <div class="hint">Use número positivo para adicionar dias ou negativo para remover. Ex: 7 ou -7</div>
                <div class="btns">
                    <button type="submit" name="apply" value="1" class="btn-primary">✔ Aplicar</button>
                    <a href="../" class="btn-cancel">Cancelar</a>
                </div>
            </form>
        </div></body></html>"""
        return HttpResponse(form_html)
    trial_custom_days.short_description = '⏱ Trial: ajustar número personalizado de dias'

    def _get_csrf_token(self, request):
        from django.middleware.csrf import get_token
        return get_token(request)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """Admin for Lead model"""
    list_display = (
        'contact_name', 'instructor_name', 'city', 'status',
        'preferred_schedule', 'created_at'
    )
    list_filter = ('status', 'city__state', 'created_at')
    search_fields = ('contact_name', 'contact_phone', 'instructor__user__username', 'message')
    readonly_fields = ('created_at', 'updated_at', 'ip_address')
    
    fieldsets = (
        ('Relacionamentos', {
            'fields': ('student_user', 'instructor', 'city')
        }),
        ('Informações de Contato', {
            'fields': ('contact_name', 'contact_phone')
        }),
        ('Detalhes da Solicitação', {
            'fields': ('preferred_schedule', 'message', 'status')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    def instructor_name(self, obj):
        return obj.instructor.user.get_full_name()
    instructor_name.short_description = 'Instrutor'
    
    actions = ['mark_as_contacted', 'mark_as_closed', 'mark_as_spam']
    
    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(status='CONTACTED')
        self.message_user(request, f'{updated} lead(s) marcado(s) como contatado.')
    mark_as_contacted.short_description = 'Marcar como contatado'
    
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status='CLOSED')
        self.message_user(request, f'{updated} lead(s) marcado(s) como fechado.')
    mark_as_closed.short_description = 'Marcar como fechado'
    
    def mark_as_spam(self, request, queryset):
        updated = queryset.update(status='SPAM')
        self.message_user(request, f'{updated} lead(s) marcado(s) como spam.')
    mark_as_spam.short_description = 'Marcar como spam'


@admin.register(StudentLead)
class StudentLeadAdmin(admin.ModelAdmin):
    """Admin for StudentLead model"""
    list_display = (
        'name', 'get_city_display', 'state', 'get_categories_display', 'phone',
        'has_theory', 'is_contacted', 'notified_about_instructor',
        'has_instructor_badge', 'created_at'
    )
    list_filter = (
        'state', 'has_theory',
        'is_contacted', 'notified_about_instructor',
        'accept_whatsapp', 'accept_email', 'accept_terms'
    )
    search_fields = ('name', 'phone', 'email', 'city__name', 'external_id')
    readonly_fields = ('external_id', 'created_at', 'updated_at', 'has_instructor_in_state', 'whatsapp_link', 'email_verified')
    filter_horizontal = ('categories',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('external_id', 'photo', 'name', 'phone', 'email', 'email_verified', 'city', 'state')
        }),
        ('CNH', {
            'fields': ('categories', 'has_theory')
        }),
        ('Preferências LGPD', {
            'fields': ('accept_whatsapp', 'accept_email', 'accept_terms')
        }),
        ('Status de Contato', {
            'fields': ('is_contacted', 'contacted_at', 'notified_about_instructor', 'notified_at')
        }),
        ('Instrutor Disponível', {
            'fields': ('has_instructor_in_state', 'whatsapp_link'),
            'classes': ('collapse',)
        }),
        ('Dados Adicionais', {
            'fields': ('metadata', 'notes'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_city_display(self, obj):
        """Display city name"""
        return obj.city.name if obj.city else 'N/A'
    get_city_display.short_description = 'Cidade'
    get_city_display.admin_order_field = 'city__name'
    
    def get_categories_display(self, obj):
        """Display categories"""
        if obj.categories.exists():
            return ', '.join([cat.code for cat in obj.categories.all()])
        return 'N/A'
    get_categories_display.short_description = 'Categorias'
    
    def has_instructor_badge(self, obj):
        """Display if state has instructors available"""
        if obj.has_instructor_in_state:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Sim</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Não</span>'
        )
    has_instructor_badge.short_description = 'Instrutor Disponível'
    
    def whatsapp_link(self, obj):
        """Display WhatsApp link for easy contact"""
        if obj.phone and obj.accept_whatsapp:
            link = obj.get_whatsapp_link()
            return format_html(
                '<a href="{}" target="_blank" style="background: #25D366; color: white; padding: 5px 10px; text-decoration: none; border-radius: 5px;">📱 Enviar WhatsApp</a>',
                link
            )
        return '-'
    whatsapp_link.short_description = 'WhatsApp'
    
    actions = ['notify_about_instructors', 'mark_as_contacted', 'export_phones']
    
    def notify_about_instructors(self, request, queryset):
        """Notify students that have instructors in their state"""
        from django.utils import timezone
        
        # Filter only students with instructors available and not yet notified
        students_to_notify = queryset.filter(
            notified_about_instructor=False
        )
        
        count = 0
        for student in students_to_notify:
            if student.has_instructor_in_state:
                student.notified_about_instructor = True
                student.notified_at = timezone.now()
                student.save(update_fields=['notified_about_instructor', 'notified_at'])
                count += 1
        
        self.message_user(
            request,
            f'{count} aluno(s) marcado(s) como notificado(s). Use o link do WhatsApp para enviar mensagem.'
        )
    notify_about_instructors.short_description = 'Marcar como notificado sobre instrutores'
    
    def mark_as_contacted(self, request, queryset):
        """Mark students as contacted"""
        from django.utils import timezone
        
        updated = queryset.update(
            is_contacted=True,
            contacted_at=timezone.now()
        )
        self.message_user(request, f'{updated} aluno(s) marcado(s) como contatado.')
    mark_as_contacted.short_description = 'Marcar como contatado'
    
    def export_phones(self, request, queryset):
        """Export phone numbers for bulk messaging"""
        phones = [lead.phone for lead in queryset if lead.phone]
        phones_text = '\n'.join(phones)
        
        self.message_user(
            request,
            f'Telefones exportados ({len(phones)} números): {phones_text[:100]}...'
        )
    export_phones.short_description = 'Exportar telefones'


@admin.register(InstructorAvailability)
class InstructorAvailabilityAdmin(admin.ModelAdmin):
    """Admin for InstructorAvailability model"""
    list_display = ('instructor_name', 'weekday_display', 'start_time', 'end_time', 'is_active')
    list_filter = ('weekday', 'is_active', 'instructor__city__state')
    search_fields = ('instructor__user__first_name', 'instructor__user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def instructor_name(self, obj):
        return obj.instructor.user.get_full_name()
    instructor_name.short_description = 'Instrutor'
    
    def weekday_display(self, obj):
        return obj.get_weekday_display()
    weekday_display.short_description = 'Dia da Semana'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin for Appointment model"""
    list_display = (
        'appointment_date', 'start_time', 'instructor_name', 'student_name',
        'duration_hours', 'status_badge', 'created_at'
    )
    list_filter = ('is_confirmed', 'is_completed', 'is_cancelled', 'appointment_date', 'instructor__city__state')
    search_fields = (
        'instructor__user__first_name', 'instructor__user__last_name',
        'student_user__first_name', 'student_user__last_name',
        'lead__contact_name'
    )
    readonly_fields = ('created_at', 'updated_at', 'status_display')
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('lead', 'instructor', 'student_user')
        }),
        ('Data e Horário', {
            'fields': ('appointment_date', 'start_time', 'end_time', 'duration_hours')
        }),
        ('Status', {
            'fields': ('is_confirmed', 'is_completed', 'is_cancelled', 'cancellation_reason', 'status_display')
        }),
        ('Observações', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def instructor_name(self, obj):
        return obj.instructor.user.get_full_name()
    instructor_name.short_description = 'Instrutor'
    
    def student_name(self, obj):
        if obj.student_user:
            return obj.student_user.get_full_name()
        return obj.lead.contact_name
    student_name.short_description = 'Aluno'
    
    def status_badge(self, obj):
        if obj.is_cancelled:
            return format_html('<span style="color: red;">❌ Cancelado</span>')
        if obj.is_completed:
            return format_html('<span style="color: green;">✅ Concluído</span>')
        if obj.is_confirmed:
            return format_html('<span style="color: blue;">📅 Confirmado</span>')
        return format_html('<span style="color: orange;">⏳ Pendente</span>')
    status_badge.short_description = 'Status'
    
    actions = ['confirm_appointments', 'complete_appointments', 'cancel_appointments']
    
    def confirm_appointments(self, request, queryset):
        updated = queryset.filter(is_cancelled=False).update(is_confirmed=True)
        self.message_user(request, f'{updated} agendamento(s) confirmado(s).')
    confirm_appointments.short_description = 'Confirmar agendamentos'
    
    def complete_appointments(self, request, queryset):
        updated = queryset.filter(is_cancelled=False).update(is_completed=True, is_confirmed=True)
        self.message_user(request, f'{updated} agendamento(s) marcado(s) como concluído.')
    complete_appointments.short_description = 'Marcar como concluído'
    
    def cancel_appointments(self, request, queryset):
        updated = queryset.update(is_cancelled=True)
        self.message_user(request, f'{updated} agendamento(s) cancelado(s).')
    cancel_appointments.short_description = 'Cancelar agendamentos'


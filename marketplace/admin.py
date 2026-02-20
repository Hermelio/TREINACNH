"""
Admin configuration for marketplace app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.contrib import messages
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
        'user_full_name', 'city', 'gender', 'years_experience',
        'has_own_car', 'verification_badge', 'is_visible', 'completion_badge',
        'pending_docs_count', 'created_at',
    )
    list_filter = ('is_verified', 'is_visible', 'gender', 'has_own_car', 'city__state')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'city__name')
    readonly_fields = ('created_at', 'updated_at', 'profile_completion_score')
    filter_horizontal = ('categories',)

    fieldsets = (
        ('Usuário', {
            'fields': ('user', 'city')
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
            'fields': ('is_visible', 'is_verified', 'profile_completion_score')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_inline_instances(self, request, obj=None):
        """Load document inline only on existing objects (not on creation form)."""
        if obj is None:
            return []
        from verification.admin import InstructorDocumentInline
        return [InstructorDocumentInline(self.model, self.admin_site)]

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = 'Instrutor'

    def verification_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color:#1a7a3c;font-weight:700">✅ Verificado</span>')
        # Count pending docs
        pending = obj.documents.filter(status='PENDING').count() if hasattr(obj, 'documents') else 0
        if pending:
            return format_html(
                '<span style="color:#ff8c00;font-weight:700">⏳ {} pendente(s)</span>', pending
            )
        return format_html('<span style="color:#999">— Sem docs</span>')
    verification_badge.short_description = 'Verificação'

    def pending_docs_count(self, obj):
        count = obj.documents.filter(status='PENDING').count()
        if count:
            return format_html(
                '<span style="background:#ffc107;color:#000;padding:2px 10px;'
                'border-radius:12px;font-weight:700;">{}</span>', count
            )
        return format_html('<span style="color:#aaa">0</span>')
    pending_docs_count.short_description = '⏳ Pendentes'

    def completion_badge(self, obj):
        score = obj.profile_completion_score
        color = 'green' if score >= 80 else ('orange' if score >= 50 else 'red')
        return format_html(
            '<span style="color:{};font-weight:bold;">{:.0f}%</span>', color, score
        )
    completion_badge.short_description = 'Completude'

    actions = ['make_verified', 'make_unverified', 'make_visible', 'make_invisible']

    def make_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} instrutor(es) verificado(s).')
    make_verified.short_description = 'Marcar como verificado'

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


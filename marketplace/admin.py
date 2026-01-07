"""
Admin configuration for marketplace app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import State, City, CategoryCNH, InstructorProfile, Lead


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
    list_display = ('name', 'state', 'slug', 'is_active', 'instructor_count', 'created_at')
    list_filter = ('state', 'is_active')
    search_fields = ('name', 'state__code')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)


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
        'has_own_car', 'is_verified', 'is_visible', 'completion_badge', 'created_at'
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
    
    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = 'Instrutor'
    
    def completion_badge(self, obj):
        score = obj.profile_completion_score
        if score >= 80:
            color = 'green'
        elif score >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.0f}%</span>',
            color, score
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

"""
Admin configuration for reviews app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Review, Report


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin for Review with moderation"""
    list_display = ('display_name', 'instructor_name', 'rating_stars', 'status_badge', 'created_at')
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('author_name', 'author_user__username', 'instructor__user__first_name', 'instructor__user__last_name', 'comment')
    readonly_fields = ('created_at', 'updated_at', 'ip_address')
    
    fieldsets = (
        ('Avaliação', {
            'fields': ('instructor', 'author_user', 'author_name', 'rating', 'comment')
        }),
        ('Moderação', {
            'fields': ('status',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    def instructor_name(self, obj):
        return obj.instructor.user.get_full_name()
    instructor_name.short_description = 'Instrutor'
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: gold; font-size: 1.2em;">{}</span>', stars)
    rating_stars.short_description = 'Avaliação'
    
    def status_badge(self, obj):
        colors = {
            'PUBLISHED': 'green',
            'PENDING': 'orange',
            'HIDDEN': 'red',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    actions = ['publish_reviews', 'hide_reviews']
    
    def publish_reviews(self, request, queryset):
        updated = queryset.update(status='PUBLISHED')
        self.message_user(request, f'{updated} avaliação(ões) publicada(s).')
    publish_reviews.short_description = 'Publicar avaliações'
    
    def hide_reviews(self, request, queryset):
        updated = queryset.update(status='HIDDEN')
        self.message_user(request, f'{updated} avaliação(ões) ocultada(s).')
    hide_reviews.short_description = 'Ocultar avaliações'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin for Report/complaints"""
    list_display = ('reporter_display', 'instructor_name', 'reason', 'status_badge', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('reporter_name', 'reporter_user__username', 'instructor__user__first_name', 'details')
    readonly_fields = ('created_at', 'updated_at', 'ip_address')
    
    fieldsets = (
        ('Denúncia', {
            'fields': ('instructor', 'reason', 'details')
        }),
        ('Denunciante', {
            'fields': ('reporter_user', 'reporter_name', 'reporter_email')
        }),
        ('Investigação', {
            'fields': ('status', 'admin_notes')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    def reporter_display(self, obj):
        if obj.reporter_user:
            return obj.reporter_user.username
        return obj.reporter_name or 'Anônimo'
    reporter_display.short_description = 'Denunciante'
    
    def instructor_name(self, obj):
        return obj.instructor.user.get_full_name()
    instructor_name.short_description = 'Instrutor'
    
    def status_badge(self, obj):
        colors = {
            'OPEN': 'red',
            'INVESTIGATING': 'orange',
            'CLOSED': 'green',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    actions = ['mark_investigating', 'mark_closed']
    
    def mark_investigating(self, request, queryset):
        updated = queryset.update(status='INVESTIGATING')
        self.message_user(request, f'{updated} denúncia(s) em investigação.')
    mark_investigating.short_description = 'Marcar como "Em Investigação"'
    
    def mark_closed(self, request, queryset):
        updated = queryset.update(status='CLOSED')
        self.message_user(request, f'{updated} denúncia(s) fechada(s).')
    mark_closed.short_description = 'Fechar denúncias'

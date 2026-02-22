"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.http import HttpResponse
import csv
from .models import Profile, Address


class ProfileInline(admin.StackedInline):
    """Inline Profile in User admin"""
    model = Profile
    can_delete = False
    verbose_name = 'Perfil'
    verbose_name_plural = 'Perfil'
    fields = ('phone', 'whatsapp_number', 'role', 'avatar', 'avatar_preview')
    readonly_fields = ('avatar_preview',)

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:60px;width:60px;border-radius:50%;object-fit:cover;">',
                obj.avatar.url,
            )
        return '—'
    avatar_preview.short_description = 'Preview'


class UserAdmin(BaseUserAdmin):
    """Extended User admin with Profile inline"""
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role')
    actions = list(BaseUserAdmin.actions) + ['export_users_to_csv', 'export_students_to_csv']

    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except Exception:
            return '—'
    get_role.short_description = 'Perfil'

    def export_users_to_csv(self, request, queryset):
        """Export all selected users to CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="usuarios_todos_export.csv"'
        response.write('\ufeff')  # UTF-8 BOM for Excel compatibility
        
        writer = csv.writer(response)
        # Header
        writer.writerow([
            'ID', 'Username', 'Nome', 'Sobrenome', 'Email', 'Tipo Perfil',
            'Telefone', 'WhatsApp', 'CPF', 'Ativo', 'Staff', 'Superuser',
            'Último Login', 'Data Cadastro'
        ])
        
        # Data rows
        for user in queryset.select_related('profile'):
            profile = user.profile if hasattr(user, 'profile') else None
            writer.writerow([
                user.id,
                user.username,
                user.first_name or '',
                user.last_name or '',
                user.email,
                profile.get_role_display() if profile else 'Sem perfil',
                profile.phone if profile else '',
                profile.whatsapp_number if profile else '',
                profile.cpf if profile else '',
                'Sim' if user.is_active else 'Não',
                'Sim' if user.is_staff else 'Não',
                'Sim' if user.is_superuser else 'Não',
                user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Nunca',
                user.date_joined.strftime('%d/%m/%Y %H:%M'),
            ])
        
        self.message_user(request, f'{queryset.count()} usuário(s) exportado(s) para CSV.')
        return response
    export_users_to_csv.short_description = '📥 Exportar TODOS para CSV'

    def export_students_to_csv(self, request, queryset):
        """Export only students from selected users to CSV"""
        students = queryset.filter(profile__role='STUDENT')
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="alunos_export.csv"'
        response.write('\ufeff')  # UTF-8 BOM for Excel compatibility
        
        writer = csv.writer(response)
        # Header
        writer.writerow([
            'ID', 'Username', 'Nome Completo', 'Email', 
            'Telefone', 'WhatsApp', 'CPF', 'Ativo',
            'Último Login', 'Data Cadastro'
        ])
        
        # Data rows
        for user in students.select_related('profile'):
            profile = user.profile
            writer.writerow([
                user.id,
                user.username,
                user.get_full_name() or '-',
                user.email,
                profile.phone or '',
                profile.whatsapp_number or '',
                profile.cpf or '',
                'Sim' if user.is_active else 'Não',
                user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Nunca',
                user.date_joined.strftime('%d/%m/%Y %H:%M'),
            ])
        
        self.message_user(request, f'{students.count()} aluno(s) exportado(s) para CSV.')
        return response
    export_students_to_csv.short_description = '📥 Exportar somente ALUNOS para CSV'


# Unregister default User admin and register custom
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin direto de Profile — útil para busca rápida por papel."""
    list_display = ('user', 'role_badge', 'phone', 'whatsapp_number', 'avatar_preview')
    list_filter  = ('role',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone')
    readonly_fields = ('avatar_preview',)
    actions = ['export_to_csv']

    def role_badge(self, obj):
        colors = {'ADMIN': '#7c3aed', 'INSTRUCTOR': '#1d4ed8', 'STUDENT': '#065f46'}
        color = colors.get(obj.role, '#555')
        return format_html(
            '<span style="color:{};font-weight:700">{}</span>',
            color, obj.get_role_display(),
        )
    role_badge.short_description = 'Papel'
    role_badge.admin_order_field = 'role'

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:52px;width:52px;border-radius:50%;object-fit:cover;">',
                obj.avatar.url,
            )
        return '—'
    avatar_preview.short_description = 'Avatar'

    def export_to_csv(self, request, queryset):
        """Export selected profiles to CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="usuarios_export.csv"'
        response.write('\ufeff')  # UTF-8 BOM for Excel compatibility
        
        writer = csv.writer(response)
        # Header
        writer.writerow([
            'ID', 'Username', 'Nome Completo', 'Email', 'Tipo Perfil',
            'Telefone', 'WhatsApp', 'CPF', 'Ativo', 'Staff', 'Data Cadastro'
        ])
        
        # Data rows
        for profile in queryset.select_related('user'):
            writer.writerow([
                profile.user.id,
                profile.user.username,
                profile.user.get_full_name() or '-',
                profile.user.email,
                profile.get_role_display(),
                profile.phone or '',
                profile.whatsapp_number or '',
                profile.cpf or '',
                'Sim' if profile.user.is_active else 'Não',
                'Sim' if profile.user.is_staff else 'Não',
                profile.user.date_joined.strftime('%d/%m/%Y %H:%M'),
            ])
        
        self.message_user(request, f'{queryset.count()} usuário(s) exportado(s) para CSV.')
        return response
    export_to_csv.short_description = '📥 Exportar selecionados para CSV'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin for Address model"""
    list_display = ('profile', 'city', 'state', 'neighborhood', 'is_primary', 'created_at')
    list_filter = ('state', 'is_primary')
    search_fields = ('city', 'neighborhood', 'profile__user__username')
    readonly_fields = ('created_at',)


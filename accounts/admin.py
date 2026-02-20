"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
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

    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except Exception:
            return '—'
    get_role.short_description = 'Perfil'


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


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin for Address model"""
    list_display = ('profile', 'city', 'state', 'neighborhood', 'is_primary', 'created_at')
    list_filter = ('state', 'is_primary')
    search_fields = ('city', 'neighborhood', 'profile__user__username')
    readonly_fields = ('created_at',)


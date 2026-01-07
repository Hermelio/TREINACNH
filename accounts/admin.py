"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Address


class ProfileInline(admin.StackedInline):
    """Inline Profile in User admin"""
    model = Profile
    can_delete = False
    verbose_name = 'Perfil'
    verbose_name_plural = 'Perfil'
    fields = ('phone', 'whatsapp_number', 'role', 'avatar')


class UserAdmin(BaseUserAdmin):
    """Extended User admin with Profile inline"""
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role')
    
    def get_role(self, obj):
        """Get user role from profile"""
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else '-'
    get_role.short_description = 'Perfil'


# Unregister default User admin and register custom
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin for Address model"""
    list_display = ('profile', 'city', 'state', 'neighborhood', 'is_primary', 'created_at')
    list_filter = ('state', 'is_primary')
    search_fields = ('city', 'neighborhood', 'profile__user__username')
    readonly_fields = ('created_at',)

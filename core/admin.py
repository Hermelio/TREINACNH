"""
Admin configuration for core app.
"""
from django.contrib import admin
from .models import StaticPage, FAQEntry, HomeBanner, NewsArticle


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    """Admin for StaticPage model"""
    list_display = ('title', 'slug', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(FAQEntry)
class FAQEntryAdmin(admin.ModelAdmin):
    """Admin for FAQEntry model"""
    list_display = ('question', 'category', 'order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer')
    list_editable = ('order', 'is_active')


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    """Admin for HomeBanner model"""
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle')
    list_editable = ('order', 'is_active')
    readonly_fields = ('created_at',)


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    """Admin para Notícias"""
    list_display = ('title', 'source', 'category', 'published_date', 'is_featured', 'is_active')
    list_filter = ('category', 'source', 'is_featured', 'is_active', 'published_date')
    search_fields = ('title', 'summary', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'slug', 'category', 'published_date')
        }),
        ('Conteúdo', {
            'fields': ('summary', 'content')
        }),
        ('Fonte', {
            'fields': ('source', 'source_url', 'image_url')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

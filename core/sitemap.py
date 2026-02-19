from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from marketplace.models import InstructorProfile
from django.utils import timezone
from .models import NewsArticle, StaticPage


class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        # Apenas nomes de URLs que existem em core/urls.py
        return [
            'core:home',
            'core:about',
            'core:contact',
            'core:faq',
            'core:news_list',
        ]

    def location(self, item):
        return reverse(item)


class StaticPageSitemap(Sitemap):
    """Páginas do model StaticPage (termos, politica, etc.)"""
    priority = 0.4
    changefreq = 'yearly'

    def items(self):
        return StaticPage.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('core:static_page', kwargs={'slug': obj.slug})


class InstructorSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return InstructorProfile.objects.filter(
            is_active=True,
            latitude__isnull=False,
            longitude__isnull=False
        )

    def lastmod(self, obj):
        return getattr(obj, 'updated_at', timezone.now())


class NewsSitemap(Sitemap):
    """Sitemap para notícias/blog (NewsArticle)"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return NewsArticle.objects.filter(is_active=True).order_by('-published_date')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('core:news_detail', kwargs={'slug': obj.slug})


sitemaps = {
    'static': StaticViewSitemap,
    'paginas': StaticPageSitemap,
    'instrutores': InstructorSitemap,
    'noticias': NewsSitemap,
}

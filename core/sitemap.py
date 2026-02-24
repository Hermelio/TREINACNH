from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from marketplace.models import InstructorProfile
from django.utils import timezone
from .models import NewsArticle, StaticPage


class PriorityPagesSitemap(Sitemap):
    """Páginas que queremos como sitelinks — prioridade máxima."""
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return [
            'core:home',
            'marketplace:cities_list',
            'accounts:register',
            'billing:plans',
            'core:about',
            'core:faq',
        ]

    def location(self, item):
        return reverse(item)


class StaticViewSitemap(Sitemap):
    """Páginas estáticas de menor prioridade."""
    priority = 0.4
    changefreq = 'monthly'

    def items(self):
        return [
            'core:news_list',
            'core:contact',
        ]

    def location(self, item):
        return reverse(item)


class StaticPageSitemap(Sitemap):
    """Páginas do model StaticPage (termos, politica, etc.)"""
    priority = 0.3
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
        return InstructorProfile.objects.filter(is_visible=True, is_verified=True)

    def lastmod(self, obj):
        return getattr(obj, 'updated_at', timezone.now())


class NewsSitemap(Sitemap):
    """Sitemap para notícias/blog (NewsArticle)"""
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return NewsArticle.objects.filter(is_active=True).order_by('-published_date')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('core:news_detail', kwargs={'slug': obj.slug})


sitemaps = {
    'priority': PriorityPagesSitemap,
    'static': StaticViewSitemap,
    'paginas': StaticPageSitemap,
    'instrutores': InstructorSitemap,
    'noticias': NewsSitemap,
}

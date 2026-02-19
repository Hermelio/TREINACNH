from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from marketplace.models import InstructorProfile
from django.utils import timezone
from .models import NewsArticle


class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return [
            'core:home',
            'core:como_funciona',
            'core:sobre',
            'core:contato',
            'core:seja_instrutor',
            'core:termos',
            'core:news_list',
        ]

    def location(self, item):
        return reverse(item)


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
    'instrutores': InstructorSitemap,
    'noticias': NewsSitemap,
}

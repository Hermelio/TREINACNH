from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from marketplace.models import InstructorProfile
from reviews.models import Review
from django.utils import timezone

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
        ]

    def location(self, item):
        return reverse(item)

class InstructorSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return InstructorProfile.objects.filter(is_active=True, latitude__isnull=False, longitude__isnull=False)

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else timezone.now()

class BlogSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        # Ajuste para seu modelo de blog/post
        return []

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else timezone.now()

sitemaps = {
    'static': StaticViewSitemap,
    'instrutores': InstructorSitemap,
    'blog': BlogSitemap,
}

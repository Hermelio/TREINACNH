"""
Context processors for the core app.
Makes site configuration available to all templates.
"""
from django.conf import settings


def site_settings(request):
    """
    Adds site configuration to the template context.
    
    Available in all templates:
    - site_name: Nome do site
    - site_logo: Caminho da logo
    - site_url: URL do site
    """
    return {
        'site_name': getattr(settings, 'SITE_NAME', 'TREINACNH'),
        'site_logo': getattr(settings, 'SITE_LOGO', 'images/logo.png'),
        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
    }

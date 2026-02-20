"""
URL Configuration for TREINACNH project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from billing import views as billing_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    # Sitemap e robots.txt
    # (urls já adicionadas em core.urls)
    # Accounts URLs (DEVE VIR ANTES do allauth para pegar /contas/painel/)
    path('contas/', include('accounts.urls')),
    # Allauth URLs (apenas para social login)
    path('contas/', include('allauth.urls')),
    path('instrutores/', include('marketplace.urls')),
    path('verificacao/', include('verification.urls')),
    path('avaliacoes/', include('reviews.urls')),
    path('planos/', include('billing.urls')),
    # Webhook (outside billing app for clean URL)
    path('webhook/mercadopago/', billing_views.mercadopago_webhook, name='mercadopago_webhook'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Handlers de erro personalizados
from django.views.defaults import page_not_found, server_error  # noqa: E402
handler404 = page_not_found
handler500 = server_error
    
    # Debug toolbar (comentado)
    # import debug_toolbar
    # urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

# Admin site customization
admin.site.site_header = "TREINACNH - Administração"
admin.site.site_title = "TREINACNH Admin"
admin.site.index_title = "Painel de Controle"

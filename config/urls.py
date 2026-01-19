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
    # Allauth URLs (IMPORTANTE: antes das accounts!)
    path('contas/', include('allauth.urls')),
    path('contas/', include('accounts.urls')),
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
    
    # Debug toolbar (comentado)
    # import debug_toolbar
    # urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

# Admin site customization
admin.site.site_header = "TREINACNH - Administração"
admin.site.site_title = "TREINACNH Admin"
admin.site.index_title = "Painel de Controle"

from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'marketplace'
    verbose_name = 'Marketplace de Instrutores'
    
    def ready(self):
        """Import signals when app is ready"""
        import marketplace.signals  # noqa

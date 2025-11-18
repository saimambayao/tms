from django.apps import AppConfig


class UnifiedDbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.unified_db'
    verbose_name = 'Unified Database System'

    def ready(self):
        # Import models to ensure signals are registered
        try:
            from . import models
        except ImportError:
            pass

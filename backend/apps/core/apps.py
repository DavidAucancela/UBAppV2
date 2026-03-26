from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'

    def ready(self):
        """Aplica patches cuando la app está lista"""
        try:
            from . import patches_django
        except ImportError:
            pass
        try:
            from .signals import connect_audit_signals
            connect_audit_signals()
        except Exception:
            pass
























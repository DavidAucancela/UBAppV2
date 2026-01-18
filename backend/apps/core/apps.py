from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'

    def ready(self):
        """Aplica patches cuando la app está lista"""
        # Importar y aplicar patches para modelos de Django
        try:
            from . import patches_django
        except ImportError:
            pass
























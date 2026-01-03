from django.apps import AppConfig


class MetricasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.metricas'
    
    def ready(self):
        """Importa signals cuando la app está lista"""
        import apps.metricas.signals  # noqa

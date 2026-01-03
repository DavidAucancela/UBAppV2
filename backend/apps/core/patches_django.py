"""
Patches para modificar el comportamiento de modelos de Django
y que usen los nombres de tabla renombrados.

Estos patches se aplican ANTES de que Django cargue los modelos,
usando monkey patching en las clases de modelos directamente.
"""
import django
from django.apps import apps


def aplicar_patches_temprano():
    """Aplica patches directamente en las clases de modelos antes de que se carguen"""
    try:
        # Importar las clases de modelos directamente
        from django.contrib.admin.models import LogEntry
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.sessions.models import Session
        
        # Aplicar patches directamente en las clases Meta
        if hasattr(LogEntry, '_meta'):
            LogEntry._meta.db_table = 'logs'
            # Forzar actualización del nombre de tabla en la clase
            if hasattr(LogEntry._meta, 'original_attrs'):
                LogEntry._meta.original_attrs['db_table'] = 'logs'
        
        if hasattr(ContentType, '_meta'):
            ContentType._meta.db_table = 'tipo_contenido'
            if hasattr(ContentType._meta, 'original_attrs'):
                ContentType._meta.original_attrs['db_table'] = 'tipo_contenido'
        
        if hasattr(Session, '_meta'):
            Session._meta.db_table = 'sesiones_key'
            if hasattr(Session._meta, 'original_attrs'):
                Session._meta.original_attrs['db_table'] = 'sesiones_key'
        
    except (ImportError, AttributeError) as e:
        # Si los modelos aún no están disponibles, se aplicarán más tarde
        pass


def aplicar_patches():
    """Aplica patches para cambiar db_table de modelos de Django"""
    # Intentar aplicar patches temprano
    aplicar_patches_temprano()
    
    # Si los modelos ya están cargados, aplicar patches directamente
    try:
        if django.apps.apps.ready:
            try:
                LogEntry = apps.get_model('admin', 'LogEntry')
                if LogEntry and hasattr(LogEntry, '_meta'):
                    LogEntry._meta.db_table = 'logs'
            except (LookupError, AttributeError):
                pass
            
            try:
                ContentType = apps.get_model('contenttypes', 'ContentType')
                if ContentType and hasattr(ContentType, '_meta'):
                    ContentType._meta.db_table = 'tipo_contenido'
            except (LookupError, AttributeError):
                pass
            
            try:
                Session = apps.get_model('sessions', 'Session')
                if Session and hasattr(Session, '_meta'):
                    Session._meta.db_table = 'sesiones_key'
            except (LookupError, AttributeError):
                pass
    except Exception:
        pass


# Aplicar patches inmediatamente al importar el módulo
try:
    aplicar_patches_temprano()
except Exception:
    pass


"""
Settings para correr tests localmente.
- SQLite en memoria (no requiere PostgreSQL ni Redis)
- Patches de db_table desactivados (ver patches_django.py)
- Celery síncrono
"""
from settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Usar hasher rápido en tests — PBKDF2 toma ~4s por usuario en SQLite
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_RESULT_BACKEND = 'cache+memory://'
CELERY_BROKER_URL = 'memory://'

# Forzar config en el objeto Celery directamente — config_from_object se
# inicializa antes de que Django aplique test_settings, por lo que los
# settings Django solos no alcanzan a sobreescribir el broker ya cacheado.
try:
    from celery_app import app as _celery_app
    _celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=False,
        broker_url='memory://',
        result_backend='cache+memory://',
    )
except Exception:
    pass

# Saltarse las migraciones de busqueda/metricas (usan pgvector y PL/pgSQL).
# Django creará sus tablas directamente desde los modelos — SQLite acepta
# el tipo vector(1536) sin aplicar restricciones de tipo.
MIGRATION_MODULES = {
    'busqueda': None,
    'metricas': None,
}

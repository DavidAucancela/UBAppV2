"""
Settings de prueba que usa SQLite en memoria.
Permite ejecutar manage.py test sin necesitar privilegios CREATEDB
en la base de datos de producción (Supabase/Railway).
"""
from settings import *  # noqa: F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Deshabilitar migraciones lentas en tests (usa schema directo)
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Hasher más rápido para tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

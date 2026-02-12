from pathlib import Path
import os
from decouple import config
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

# Cargar variables del entorno
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'clave-por-defecto-solo-para-desarrollo')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',

    # servicios 
    'apps.core.apps.CoreConfig',  # Configuración personalizada para aplicar patches
    'apps.usuarios',
    'apps.archivos',
    'apps.busqueda',
    'apps.notificaciones',
    'apps.metricas',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'


# Database Configuration
# Usar DATABASE_URL si está disponible, sino usar variables individuales
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Parsear DATABASE_URL y agregar opciones SSL solo si es Supabase (no localhost)
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    
    # Detectar si es conexión local (Docker o localhost) o remota (Supabase)
    db_host = DATABASES['default'].get('HOST', '')
    is_local = db_host in ('localhost', '127.0.0.1', '::1', 'postgres')
    is_supabase = 'supabase.co' in str(db_host)
    
    # Configurar opciones
    if 'OPTIONS' not in DATABASES['default']:
        DATABASES['default']['OPTIONS'] = {}
    
    # SSL solo para Supabase; Docker (host "postgres") y localhost no usan SSL
    # Forzar sslmode disable en local/Docker para evitar "server does not support SSL, but SSL was required"
    if is_supabase and not is_local:
        DATABASES['default']['OPTIONS']['sslmode'] = 'require'
    else:
        DATABASES['default']['OPTIONS']['sslmode'] = 'disable'
    # Eliminar sslmode del nivel superior si dj_database_url lo puso (evita conflicto)
    DATABASES['default'].pop('sslmode', None)

    DATABASES['default']['OPTIONS']['connect_timeout'] = 10
    DATABASES['default']['ATOMIC_REQUESTS'] = True
else:
    # Usar configuración con variables individuales
    db_host = os.getenv('DB_HOST', 'localhost')
    # SSL solo para conexiones remotas (Supabase), no para localhost
    is_local = db_host in ('localhost', '127.0.0.1', '::1')
    
    db_options = {
        'connect_timeout': 10,  # Timeout de conexión en segundos
    }
    
    # SSL solo requerido para Supabase (conexiones remotas)
    if not is_local:
        db_options['sslmode'] = 'require'
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'UBAppDB'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'admin'),
            'HOST': db_host,
            'PORT': os.getenv('DB_PORT', '5435'),
            'OPTIONS': db_options,
            'CONN_MAX_AGE': 600,  # Mantener conexiones vivas por 10 minutos
            'ATOMIC_REQUESTS': True,  # Cada request en una transacción
        }
    }

# Información de diagnóstico de la base de datos
DB_CONFIG_INFO = {
    'host': DATABASES['default'].get('HOST', 'unknown'),
    'port': DATABASES['default'].get('PORT', 'unknown'),
    'name': DATABASES['default'].get('NAME', 'unknown'),
    'is_local': is_local if 'is_local' in locals() else db_host in ('localhost', '127.0.0.1', '::1'),
    'using_supabase': 'supabase.co' in str(db_host) if 'db_host' in locals() else False
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Manejador de excepciones centralizado
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
    # Rate Limiting / Throttling
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',             # 100 requests por hora para usuarios anónimos
        'user': '1000/hour',            # 1000 requests por hora para usuarios autenticados
        'busqueda': '60/minute',        # 60 búsquedas por minuto
        'busqueda_semantica': '30/minute',  # 30 búsquedas semánticas por minuto (costosas)
        'login': '5/minute',            # 5 intentos de login por minuto
        'registro': '3/hour',           # 3 registros por hora
        'importacion': '10/hour',       # 10 importaciones por hora
        'exportacion': '30/hour',       # 30 exportaciones por hora
        'burst': '60/minute',           # Ráfagas cortas
        'sustained': '10000/day',       # Uso sostenido diario
    },
}

# generar documentación automática de tu API REST en Django REST Framework (DRF).
SPECTACULAR_SETTINGS = {
    'TITLE': 'UBApp API - Sistema de Gestión de Envíos',
    'DESCRIPTION': '''
    API REST para el sistema de gestión de envíos UBApp.
    
    ## Características principales:
    
    - **Gestión de Usuarios**: Autenticación, autorización y gestión de perfiles
    - **Gestión de Envíos**: CRUD completo de envíos con productos
    - **Búsqueda Avanzada**: Búsqueda tradicional y semántica con IA
    - **Tarifas**: Cálculo automático de costos según categorías y pesos
    - **Notificaciones**: Sistema de notificaciones en tiempo real
    - **Importación Masiva**: Importación de envíos desde Excel
    
    ## Autenticación
    
    La API utiliza JWT (JSON Web Tokens) para autenticación. 
    Incluye el token en el header: `Authorization: Bearer <token>`
    
    ## Arquitectura
    
    La API sigue una arquitectura en capas:
    - **Presentación**: Views (HTTP handling)
    - **Lógica de Negocio**: Services (business rules)
    - **Acceso a Datos**: Repositories (database access)
    - **Semántica**: Embeddings e IA para búsquedas semánticas
    ''',
    'VERSION': '2.0.0',
    'CONTACT': {
        'name': 'Equipo UBApp',
        'email': 'soporte@ubapp.com',
    },
    'LICENSE': {
        'name': 'Proprietary',
    },
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayOperationId': True,
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2,
        'docExpansion': 'list',
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
    },
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': False,
        'hideHostname': False,
        'hideLoading': False,
        'hideSingleRequestSampleTab': False,
        'jsonSampleExpandLevel': 2,
        'nativeScrollbars': False,
        'noAutoAuth': False,
        'pathInMiddlePanel': False,
        'requiredPropsFirst': False,
        'scrollYOffset': 0,
        'sortPropsAlphabetically': False,
        'theme': {
            'colors': {
                'primary': {
                    'main': '#32329f'
                }
            }
        },
    },
    'TAGS': [
        {'name': 'autenticacion', 'description': 'Autenticación y autorización de usuarios'},
        {'name': 'usuarios', 'description': 'Gestión de usuarios y perfiles'},
        {'name': 'envios', 'description': 'Gestión de envíos y productos'},
        {'name': 'busqueda', 'description': 'Búsqueda tradicional y semántica'},
        {'name': 'tarifas', 'description': 'Gestión y cálculo de tarifas'},
        {'name': 'notificaciones', 'description': 'Sistema de notificaciones'},
        {'name': 'importacion', 'description': 'Importación masiva desde Excel'},
    ],
}

# gestión de los tokens del sistema
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS settings - Configuración segura (prioridad a .env)
# En desarrollo, puedes cambiar esto temporalmente
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Solo permitir todos los orígenes si DEBUG=True
CORS_ALLOW_CREDENTIALS = True

# Whitelist de orígenes: si CORS_ALLOWED_ORIGINS está en .env, se usa; si no, valores por defecto
_DEFAULT_CORS_ORIGINS = [
    'http://localhost:4200',
    'http://localhost:4201',
    'http://127.0.0.1:4200',
    'http://127.0.0.1:4201',
]
_ENV_CORS = [o.strip() for o in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()]
CORS_ALLOWED_ORIGINS = _ENV_CORS if _ENV_CORS else _DEFAULT_CORS_ORIGINS

# Headers permitidos
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF settings - Permitir peticiones desde el frontend (prioridad a .env)
_DEFAULT_CSRF_ORIGINS = [
    'http://localhost:4200',
    'http://localhost:4201',
    'http://127.0.0.1:4200',
    'http://127.0.0.1:4201',
]
_ENV_CSRF = [o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]
CSRF_TRUSTED_ORIGINS = _ENV_CSRF if _ENV_CSRF else _DEFAULT_CSRF_ORIGINS

# Cookies de seguridad
CSRF_COOKIE_HTTPONLY = not DEBUG  # HttpOnly en producción
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = not DEBUG  # HTTPS only en producción

# Headers de seguridad adicionales
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Custom User Model
AUTH_USER_MODEL = 'usuarios.Usuario'

# Configuración de Cache
# Redis para producción, LocMem para desarrollo
REDIS_URL = os.getenv('REDIS_URL', '')

if REDIS_URL:
    # Usar django-redis (soporta CLIENT_CLASS y OPTIONS); evita TypeError con redis-py
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'RETRY_ON_TIMEOUT': True,
                'MAX_CONNECTIONS': 50,
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True
                },
            },
            'KEY_PREFIX': 'ubapp',
            'TIMEOUT': 300,  # 5 minutos por defecto
        },
        # Caché separado para sesiones
        'sessions': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'KEY_PREFIX': 'ubapp_sessions',
            'TIMEOUT': 86400,  # 1 día
        },
        # Caché para rate limiting
        'throttle': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'KEY_PREFIX': 'ubapp_throttle',
            'TIMEOUT': 3600,  # 1 hora
        },
        # Caché para embeddings (larga duración)
        'embeddings': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'KEY_PREFIX': 'ubapp_embeddings',
            'TIMEOUT': 604800,  # 7 días
        },
    }
    # Usar cache para sesiones
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'sessions'
else:
    # Usar caché en memoria para desarrollo
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
            'TIMEOUT': 300,
        },
        'throttle': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'throttle-cache',
            'TIMEOUT': 3600,
        },
        'embeddings': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'embeddings-cache',
            'TIMEOUT': 3600,
        },
    }

# Configuración de caché para búsquedas semánticas
SEMANTIC_SEARCH_CACHE_TIMEOUT = int(os.getenv('SEMANTIC_CACHE_TIMEOUT', 3600))  # 1 hora
EMBEDDING_CACHE_TIMEOUT = int(os.getenv('EMBEDDING_CACHE_TIMEOUT', 604800))  # 7 días

# OpenAI
OPENAI_API_KEY = config('OPENAI_API_KEY')
OPENAI_EMBEDDING_MODEL = config('OPENAI_EMBEDDING_MODEL', default='text-embedding-3-small')
OPENAI_EMBEDDING_DIMENSIONS = config('OPENAI_EMBEDDING_DIMENSIONS', default=1536, cast=int)


DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@ubapp.com')


# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Para desarrollo, imprime en consola
# Para producción, usar:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
# EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
# EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d'
        },
        'detailed': {
            'format': '[{levelname}] {asctime} - {name}:{funcName}:{lineno} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'app.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'service_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'services.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'detailed',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps.core.base.base_service': {
            'handlers': ['service_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.usuarios.services': {
            'handlers': ['service_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.archivos.services': {
            'handlers': ['service_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.busqueda.services': {
            'handlers': ['service_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.busqueda.semantic': {
            'handlers': ['service_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# Crear directorio de logs si no existe
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Aplicar patches para tablas renombradas ANTES de que Django use los modelos
# Esto debe ejecutarse después de que Django esté configurado
try:
    # Aplicar patches directamente en las clases de modelos
    # Esto se ejecuta cuando settings.py se carga
    import django
    if django.setup.__module__ != 'builtins':  # Django ya está configurado
        try:
            from django.contrib.admin.models import LogEntry
            from django.contrib.contenttypes.models import ContentType
            from django.contrib.sessions.models import Session
            
            # Aplicar patches directamente
            LogEntry._meta.db_table = 'logs'
            ContentType._meta.db_table = 'tipo_contenido'
            Session._meta.db_table = 'sesiones_key'
        except (ImportError, AttributeError):
            # Los modelos aún no están disponibles, se aplicarán en apps.core
            pass
except Exception:
    # Si hay algún error, los patches se aplicarán en apps.core
    pass


# 🛠️ RECOMENDACIONES TÉCNICAS - QUÉ IMPLEMENTAR Y QUÉ ELIMINAR

**Fecha:** Enero 2025  
**Sistema:** UBApp - Backend Django + Frontend Angular  

---

## 🔴 QUÉ ELIMINAR O CORREGIR (CRÍTICO)

### 1. ELIMINAR: Conflictos de Merge

**Archivos a limpiar:**
```bash
# Backend - Archivos con conflictos
backend/settings.py
backend/urls.py
backend/apps/usuarios/views.py
backend/apps/usuarios/models.py
backend/apps/usuarios/serializers.py
backend/apps/archivos/views.py
backend/apps/archivos/models.py
backend/apps/busqueda/views.py
backend/apps/busqueda/models.py
# ... (total 59 archivos en backend)

# Frontend - Archivos con conflictos
frontend/src/app/app.routes.ts
frontend/src/app/services/auth.service.ts
frontend/src/app/services/api.service.ts
frontend/src/app/interceptors/auth.interceptor.ts
frontend/src/app/components/**/*.ts
# ... (total 135 archivos en frontend)
```

**Acción:** Resolver todos los conflictos eligiendo una versión consistente.

---

### 2. ELIMINAR: Sistema de Autenticación Duplicado

**Eliminar Token Authentication tradicional:**

```python
# backend/settings.py - ELIMINAR estas líneas:
'rest_framework.authtoken',  # ← ELIMINAR de INSTALLED_APPS
'rest_framework.authentication.TokenAuthentication',  # ← ELIMINAR
'rest_framework.authentication.BasicAuthentication',  # ← ELIMINAR (si no se usa)
```

**Mantener solo JWT:**
```python
# backend/settings.py - MANTENER:
'rest_framework_simplejwt',  # ← MANTENER
'rest_framework_simplejwt.authentication.JWTAuthentication',  # ← MANTENER
```

**Eliminar de requirements.txt (si no se usa):**
```python
# No eliminar, JWT lo requiere, pero Token auth ya no se usa
```

---

### 3. ELIMINAR: Configuraciones Inseguras

**Eliminar/MODIFICAR:**
```python
# backend/settings.py
CORS_ALLOW_ALL_ORIGINS = True  # ← CAMBIAR a False en producción

DEBUG = config('DEBUG', default=True, cast=bool)  # ← CAMBIAR default a False
```

**Reemplazar con:**
```python
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Solo en desarrollo

DEBUG = config('DEBUG', default=False, cast=bool)  # Seguro por defecto
```

---

### 4. ELIMINAR: Código Muerto/Comentado

**Buscar y eliminar:**
- Imports no utilizados
- Funciones comentadas
- Código duplicado
- Variables no usadas

**Herramienta:**
```bash
# Backend
flake8 --select=F401  # Imports no usados
pylint --disable=all --enable=unused-import

# Frontend
npm run lint  # Ya configurado
```

---

## ✅ QUÉ IMPLEMENTAR (NUEVO)

### 1. IMPLEMENTAR: Sistema de Logging Completo

**Archivo:** `backend/settings.py`

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Crear directorio de logs si no existe
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {funcName} {lineno} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'errors.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'security.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
```

**Agregar a .gitignore:**
```
logs/
*.log
```

---

### 2. IMPLEMENTAR: Manejo Centralizado de Errores

**Archivo:** `backend/apps/core/exceptions.py` (NUEVO)

```python
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('apps')

def custom_exception_handler(exc, context):
    """
    Manejo personalizado de excepciones para respuestas consistentes
    """
    # Obtener el handler estándar de DRF
    response = exception_handler(exc, context)
    
    # Si DRF no maneja la excepción, crear una respuesta personalizada
    if response is None:
        # Log del error
        logger.exception(f"Excepción no manejada: {type(exc).__name__}: {str(exc)}")
        
        # Crear respuesta de error genérica
        custom_response_data = {
            'error': True,
            'message': 'Ha ocurrido un error en el servidor',
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'details': str(exc) if logger.level == logging.DEBUG else None
        }
        response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        # Personalizar respuesta de DRF
        custom_response_data = {
            'error': True,
            'message': response.data.get('detail', 'Error en la solicitud'),
            'code': response.status_code,
            'data': response.data
        }
        response.data = custom_response_data
    
    return response
```

**Actualizar settings.py:**
```python
REST_FRAMEWORK = {
    # ... otras configuraciones ...
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}
```

---

### 3. IMPLEMENTAR: Validaciones de Modelos Mejoradas

**Archivo:** `backend/apps/archivos/models.py`

```python
from django.core.exceptions import ValidationError

class Envio(models.Model):
    # ... campos existentes ...
    
    def clean(self):
        """Validaciones a nivel de modelo"""
        errors = {}
        
        # Validar peso total
        if self.peso_total and self.peso_total <= 0:
            errors['peso_total'] = 'El peso total debe ser mayor a 0'
        
        # Validar valor total
        if self.valor_total and self.valor_total < 0:
            errors['valor_total'] = 'El valor total no puede ser negativo'
        
        # Validar que HAWB sea único (ya está en campo, pero validar aquí también)
        if self.hawb:
            qs = Envio.objects.filter(hawb=self.hawb)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                errors['hawb'] = 'Este HAWB ya existe'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Llamar clean antes de guardar"""
        self.full_clean()
        super().save(*args, **kwargs)

class Producto(models.Model):
    # ... campos existentes ...
    
    def clean(self):
        """Validaciones de producto"""
        errors = {}
        
        if self.peso <= 0:
            errors['peso'] = 'El peso debe ser mayor a 0'
        
        if self.cantidad <= 0:
            errors['cantidad'] = 'La cantidad debe ser mayor a 0'
        
        if self.valor < 0:
            errors['valor'] = 'El valor no puede ser negativo'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Tarifa(models.Model):
    # ... campos existentes ...
    
    def clean(self):
        """Validar que no haya solapamiento de rangos"""
        errors = {}
        
        if self.peso_maximo <= self.peso_minimo:
            errors['peso_maximo'] = 'El peso máximo debe ser mayor al peso mínimo'
        
        # Validar solapamiento con otras tarifas de la misma categoría
        if self.categoria:
            solapadas = Tarifa.objects.filter(
                categoria=self.categoria,
                activa=True
            ).exclude(
                peso_maximo__lte=self.peso_minimo
            ).exclude(
                peso_minimo__gte=self.peso_maximo
            )
            
            if self.pk:
                solapadas = solapadas.exclude(pk=self.pk)
            
            if solapadas.exists():
                errors['peso_minimo'] = 'Este rango de peso se solapa con otra tarifa activa'
        
        if self.precio_por_kg <= 0:
            errors['precio_por_kg'] = 'El precio por kg debe ser mayor a 0'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
```

---

### 4. IMPLEMENTAR: Optimización de Queries

**Archivo:** `backend/apps/archivos/views.py`

```python
class EnvioViewSet(viewsets.ModelViewSet):
    # ... código existente ...
    
    def get_queryset(self):
        """Optimizar queries con select_related y prefetch_related"""
        user = self.request.user
        
        # Base queryset optimizado
        queryset = Envio.objects.select_related(
            'comprador'
        ).prefetch_related(
            'productos'
        ).order_by('-fecha_emision')
        
        # Aplicar filtros de permisos
        if user.es_admin or user.es_gerente:
            return queryset
        
        if user.es_digitador:
            return queryset
        
        if user.es_comprador:
            return queryset.filter(comprador=user)
        
        return queryset.none()
```

**Archivo:** `backend/apps/usuarios/views.py`

```python
class UsuarioViewSet(viewsets.ModelViewSet):
    # ... código existente ...
    
    def get_queryset(self):
        """Optimizar queries"""
        user = self.request.user
        
        # Base queryset (sin optimización adicional necesaria para usuarios)
        queryset = Usuario.objects.all()
        
        # Aplicar filtros de permisos
        if user.es_admin:
            return queryset
        
        if user.es_gerente:
            return queryset.exclude(rol=1)
        
        if user.es_digitador:
            return queryset.filter(rol__in=[3, 4])
        
        return queryset.filter(id=user.id)
```

---

### 5. IMPLEMENTAR: Tests Básicos

**Archivo:** `backend/apps/usuarios/tests.py`

```python
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

Usuario = get_user_model()

@pytest.mark.django_db
class TestLoginView:
    """Tests para el endpoint de login"""
    
    def test_login_exitoso(self):
        """Test de login con credenciales válidas"""
        # Crear usuario de prueba
        usuario = Usuario.objects.create_user(
            username='testuser',
            password='Test123!@#',
            email='test@example.com',
            cedula='1234567890',
            nombre='Test User',
            rol=4  # Comprador
        )
        
        client = APIClient()
        response = client.post('/api/usuarios/auth/login/', {
            'username': 'testuser',
            'password': 'Test123!@#'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
        assert 'user' in response.data
    
    def test_login_credenciales_invalidas(self):
        """Test de login con credenciales inválidas"""
        client = APIClient()
        response = client.post('/api/usuarios/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data
    
    def test_login_bloqueo_intentos(self):
        """Test de bloqueo después de múltiples intentos fallidos"""
        Usuario.objects.create_user(
            username='testuser',
            password='Test123!@#',
            email='test@example.com',
            cedula='1234567890',
            nombre='Test User'
        )
        
        client = APIClient()
        
        # Intentar login 6 veces (más del límite de 5)
        for i in range(6):
            response = client.post('/api/usuarios/auth/login/', {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
        
        # El último intento debe estar bloqueado
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
```

**Archivo:** `backend/apps/archivos/tests.py`

```python
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.archivos.models import Envio, Producto, Tarifa

Usuario = get_user_model()

@pytest.mark.django_db
class TestEnvioViewSet:
    """Tests para el ViewSet de Envíos"""
    
    def test_comprador_solo_ve_sus_envios(self):
        """Test que compradores solo ven sus propios envíos"""
        # Crear dos compradores
        comprador1 = Usuario.objects.create_user(
            username='comprador1',
            password='Test123!@#',
            email='comp1@example.com',
            cedula='1111111111',
            nombre='Comprador 1',
            rol=4
        )
        
        comprador2 = Usuario.objects.create_user(
            username='comprador2',
            password='Test123!@#',
            email='comp2@example.com',
            cedula='2222222222',
            nombre='Comprador 2',
            rol=4
        )
        
        # Crear envíos para cada comprador
        envio1 = Envio.objects.create(
            hawb='HAWB001',
            peso_total=10.5,
            cantidad_total=1,
            valor_total=100.0,
            comprador=comprador1
        )
        
        envio2 = Envio.objects.create(
            hawb='HAWB002',
            peso_total=20.5,
            cantidad_total=2,
            valor_total=200.0,
            comprador=comprador2
        )
        
        # Login como comprador1
        client = APIClient()
        response = client.post('/api/usuarios/auth/login/', {
            'username': 'comprador1',
            'password': 'Test123!@#'
        })
        token = response.data['token']
        
        # Obtener envíos
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = client.get('/api/envios/envios/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['hawb'] == 'HAWB001'
```

---

### 6. IMPLEMENTAR: Variables de Entorno Obligatorias

**Archivo:** `backend/.env.example` (NUEVO)

```env
# Django Settings
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=equityDB
DB_USER=postgres
DB_PASSWORD=tu-password-segura
DB_HOST=localhost
DB_PORT=5432

# OpenAI (para búsqueda semántica)
OPENAI_API_KEY=sk-tu-api-key-aqui

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password
EMAIL_USE_TLS=True

# CORS (solo en desarrollo)
# CORS_ALLOW_ALL_ORIGINS=True
```

**Actualizar `backend/settings.py`:**

```python
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# Variables obligatorias - lanzan error si no están
SECRET_KEY = config('SECRET_KEY')
if not SECRET_KEY or SECRET_KEY == 'clave-por-defecto-solo-para-desarrollo':
    raise ValueError(
        "SECRET_KEY debe estar configurada en el archivo .env. "
        "Ver .env.example para referencia."
    )

DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
)

# Database - obligatorio
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# OpenAI - opcional (solo si se usa búsqueda semántica)
try:
    OPENAI_API_KEY = config('OPENAI_API_KEY')
except:
    OPENAI_API_KEY = None
    if not DEBUG:
        print("⚠️  WARNING: OPENAI_API_KEY no configurada. Búsqueda semántica no funcionará.")
```

---

### 7. IMPLEMENTAR: Rate Limiting

**Archivo:** `backend/apps/core/throttling.py` (NUEVO)

```python
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class LoginRateThrottle(UserRateThrottle):
    """Rate limiting para login"""
    scope = 'login'

class APIRateThrottle(UserRateThrottle):
    """Rate limiting general para API"""
    scope = 'api'
```

**Actualizar `backend/settings.py`:**

```python
REST_FRAMEWORK = {
    # ... otras configuraciones ...
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/minute',  # Máximo 5 intentos de login por minuto
        'api': '1000/hour',
    },
}
```

---

### 8. IMPLEMENTAR: Caché de Resultados

**Archivo:** `backend/settings.py`

```python
# Usar Redis para caché (recomendado) o memoria local (desarrollo)
if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        }
    }
```

**Ejemplo de uso en views:**

```python
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class EnvioViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))  # Cache 5 minutos
    def estadisticas(self, request):
        """Estadísticas con caché"""
        cache_key = f'envios_stats_{request.user.id}'
        stats = cache.get(cache_key)
        
        if stats is None:
            # Calcular estadísticas
            stats = {
                'total_envios': Envio.objects.count(),
                # ... más cálculos ...
            }
            cache.set(cache_key, stats, 60 * 5)  # Cache 5 minutos
        
        return Response(stats)
```

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: Críticos (Semana 1)
- [ ] Resolver todos los conflictos de merge
- [ ] Unificar autenticación (JWT)
- [ ] Crear `.env.example`
- [ ] Configurar variables de entorno obligatorias
- [ ] Ajustar CORS y DEBUG

### Fase 2: Alta Prioridad (Semana 2-3)
- [ ] Implementar logging completo
- [ ] Implementar manejo centralizado de errores
- [ ] Implementar tests básicos
- [ ] Agregar validaciones de modelos
- [ ] Optimizar queries

### Fase 3: Mejoras (Semana 4+)
- [ ] Implementar rate limiting
- [ ] Implementar caché
- [ ] Documentar API completamente
- [ ] Configurar CI/CD
- [ ] Agregar monitoreo (Sentry)

---

**Documento generado:** Enero 2025  
**Última actualización:** Enero 2025



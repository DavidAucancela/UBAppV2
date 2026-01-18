# 🔴 Reporte de Caída del Servidor
**Fecha del Incidente**: 6 de Enero de 2026  
**Hora Inicial**: 09:31:54  
**Hora Final**: 09:33:08  
**Duración Aproximada**: ~1 minuto 14 segundos  
**Severidad**: 🔴 CRÍTICA

---

## 📋 Resumen Ejecutivo

El servidor Django experimentó una caída completa debido a la pérdida de conectividad con la base de datos PostgreSQL alojada en Supabase. El incidente se manifestó como una cascada de errores de conexión que progresaron desde abortos de conexión hasta fallos de resolución DNS.

**Impacto**: 
- ❌ Todas las peticiones a la API fallaron con error 500
- ❌ El sistema quedó completamente inoperativo
- ❌ Múltiples endpoints afectados simultáneamente

---

## 🔍 Análisis Detallado del Incidente

### Cronología de Eventos

#### **Fase 1: Aborto de Conexión (09:31:54)**
```
[ERROR] 09:31:54 - Internal Server Error: /api/busqueda/semantica/historial/
psycopg2.OperationalError: connection to server at "db.gybrifikqkibwqpzjuxm.supabase.co" 
failed: Software caused connection abort (0x00002745/10053)
```

**Análisis**:
- Error código: `0x00002745/10053` (WSAECONNABORTED en Windows)
- La conexión TCP fue abortada abruptamente
- Posibles causas:
  - El servidor de Supabase cerró la conexión inesperadamente
  - Problema de red intermedia (firewall, router, ISP)
  - Timeout en el lado del servidor de Supabase

**Endpoints Afectados**:
- `/api/busqueda/semantica/historial/` (500 error)

---

#### **Fase 2: Timeout de Conexión (09:32:37)**
```
[ERROR] 09:32:37 - Internal Server Error: /api/envios/envios/
psycopg2.OperationalError: connection to server at "db.gybrifikqkibwqpzjuxm.supabase.co" 
failed: timeout expired
```

**Análisis**:
- El intento de reconexión falló por timeout
- El servidor de Supabase no respondió dentro del tiempo límite
- Indica que el servidor podría estar:
  - Sobrecargado
  - Inaccesible temporalmente
  - En proceso de reinicio

**Endpoints Afectados**:
- `/api/envios/envios/` (500 error)

---

#### **Fase 3: Fallo de Resolución DNS (09:33:00 - 09:33:08)**
```
[ERROR] 09:33:00 - Internal Server Error: /api/envios/productos/estadisticas/
psycopg2.OperationalError: could not translate host name 
"db.gybrifikqkibwqpzjuxm.supabase.co" to address: Host desconocido
```

**Análisis**:
- El sistema no pudo resolver el nombre DNS del servidor
- Error: "Host desconocido" (DNS lookup failure)
- Esto sugiere:
  - Problema temporal con el servicio DNS
  - El hostname de Supabase podría estar temporalmente no disponible
  - Posible problema de red local o ISP

**Endpoints Afectados**:
- `/api/envios/productos/estadisticas/`
- `/api/envios/envios/`
- `/api/envios/envios/estadisticas/`
- `/api/usuarios/estadisticas/`
- `/api/busqueda/historial/`

---

## 🎯 Causa Raíz Identificada

### **Causa Principal: Pérdida de Conectividad con Supabase PostgreSQL**

El incidente fue causado por una **pérdida completa de conectividad** entre el servidor Django y la base de datos PostgreSQL alojada en Supabase. La progresión de errores sugiere un problema en la infraestructura de Supabase o en la red de comunicación.

### Posibles Causas Específicas:

1. **Problema en Supabase** (Más Probable)
   - Mantenimiento no programado
   - Reinicio del servidor de base de datos
   - Sobrecarga del servicio
   - Problema de infraestructura en Supabase

2. **Problema de Red**
   - Interrupción temporal de la conexión a Internet
   - Problema con el proveedor de servicios de Internet (ISP)
   - Firewall o router bloqueando conexiones
   - Problema de routing de red

3. **Problema de DNS**
   - Fallo temporal del servicio DNS
   - Cache DNS corrupto
   - Problema con el resolver DNS local

4. **Límites de Conexión**
   - Supabase podría tener límites de conexiones concurrentes
   - Pool de conexiones agotado
   - Límite de rate limiting alcanzado

---

## 📊 Impacto del Incidente

### Endpoints Afectados (Total: 7)

| Endpoint | Hora del Error | Tipo de Error |
|----------|----------------|---------------|
| `/api/busqueda/semantica/historial/` | 09:31:54 | Connection Abort |
| `/api/envios/envios/` | 09:32:37 | Timeout |
| `/api/envios/productos/estadisticas/` | 09:33:00 | DNS Resolution Failure |
| `/api/envios/envios/` | 09:33:04 | DNS Resolution Failure |
| `/api/envios/envios/estadisticas/` | 09:33:06 | DNS Resolution Failure |
| `/api/usuarios/estadisticas/` | 09:33:05 | DNS Resolution Failure |
| `/api/busqueda/historial/` | 09:33:08 | DNS Resolution Failure |

### Funcionalidades Afectadas:
- ❌ Búsqueda semántica
- ❌ Gestión de envíos
- ❌ Estadísticas de productos
- ❌ Estadísticas de usuarios
- ❌ Historial de búsquedas

### Usuarios Afectados:
- Todos los usuarios activos en el momento del incidente
- Operaciones en curso fueron interrumpidas

---

## 🔧 Recomendaciones Técnicas

### 1. Implementar Pool de Conexiones con Reintentos

**Problema Actual**: Django intenta crear nuevas conexiones sin mecanismo de reintento robusto.

**Solución**:
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'
        },
        'CONN_MAX_AGE': 600,  # Reutilizar conexiones
    }
}
```

### 2. Implementar Circuit Breaker Pattern

**Propósito**: Prevenir que el sistema intente conectarse repetidamente cuando la base de datos está caída.

**Implementación Sugerida**:
- Usar `django-db-connection-pool` o similar
- Implementar circuit breaker para detectar fallos repetidos
- Retornar respuestas en caché o modo degradado cuando la BD esté caída

### 3. Monitoreo y Alertas

**Implementar**:
- Health checks periódicos a la base de datos
- Alertas cuando la conexión falle
- Dashboard de estado de conectividad
- Logging estructurado de errores de conexión

**Herramientas Sugeridas**:
- Sentry para monitoreo de errores
- Prometheus + Grafana para métricas
- Health check endpoint: `/api/health/`

### 4. Manejo de Errores Mejorado

**Actual**: Los errores de conexión resultan en error 500 genérico.

**Mejorado**: Retornar códigos de estado apropiados:
```python
# Ejemplo de manejo mejorado
try:
    # Operación de BD
except OperationalError as e:
    if 'timeout' in str(e).lower():
        return Response(
            {'error': 'Database timeout. Please try again.'},
            status=503  # Service Unavailable
        )
    elif 'could not translate host' in str(e).lower():
        return Response(
            {'error': 'Database service unavailable. Please contact support.'},
            status=503
        )
    else:
        return Response(
            {'error': 'Database connection error.'},
            status=503
        )
```

### 5. Configuración de Timeouts

**Ajustar timeouts** para evitar que las peticiones se cuelguen:
```python
# settings.py
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,  # 10 segundos para conectar
            'options': '-c statement_timeout=30000'  # 30 segundos para queries
        }
    }
}
```

### 6. Implementar Caché para Datos Críticos

**Propósito**: Servir datos desde caché cuando la BD esté temporalmente inaccesible.

**Implementación**:
- Redis o Memcached para caché
- Cachear estadísticas y datos frecuentemente consultados
- TTL apropiado según el tipo de dato

### 7. Verificar Estado de Supabase

**Acciones Inmediatas**:
1. Verificar el estado de Supabase en su dashboard
2. Revisar logs de Supabase para identificar problemas
3. Verificar límites de conexiones y rate limits
4. Considerar upgrade de plan si hay límites alcanzados

---

## 🛡️ Plan de Prevención

### Corto Plazo (1-2 semanas)
1. ✅ Implementar pool de conexiones con reintentos
2. ✅ Agregar health check endpoint
3. ✅ Configurar timeouts apropiados
4. ✅ Mejorar logging de errores de conexión
5. ✅ Implementar manejo de errores más robusto

### Mediano Plazo (1 mes)
1. ✅ Implementar circuit breaker
2. ✅ Configurar sistema de alertas (Sentry)
3. ✅ Implementar caché para datos críticos
4. ✅ Documentar procedimientos de recuperación
5. ✅ Crear dashboard de monitoreo

### Largo Plazo (2-3 meses)
1. ✅ Considerar base de datos de respaldo
2. ✅ Implementar replicación de base de datos
3. ✅ Plan de disaster recovery
4. ✅ Pruebas de carga y resistencia
5. ✅ Documentación completa de arquitectura

---

## 📝 Lecciones Aprendidas

1. **Falta de Resiliencia**: El sistema no tiene mecanismos para manejar fallos temporales de la base de datos.

2. **Falta de Visibilidad**: No hay alertas o monitoreo proactivo que detecte problemas de conectividad antes de que afecten a los usuarios.

3. **Manejo de Errores**: Los errores de conexión no están siendo manejados de manera user-friendly.

4. **Dependencia Única**: El sistema depende completamente de una sola instancia de base de datos sin redundancia.

---

## ✅ Acciones Inmediatas Requeridas

1. **Verificar Estado de Supabase**
   - Acceder al dashboard de Supabase
   - Revisar logs y métricas
   - Verificar si hubo mantenimiento programado

2. **Verificar Conectividad de Red**
   - Probar conexión a Supabase desde el servidor
   - Verificar DNS resolution
   - Probar desde diferentes ubicaciones

3. **Revisar Configuración de Base de Datos**
   - Verificar credenciales
   - Verificar límites de conexiones
   - Revisar configuración de timeouts

4. **Implementar Health Check Básico**
   - Crear endpoint `/api/health/` que verifique conectividad a BD
   - Usar para monitoreo básico

---

## 📞 Contactos y Recursos

- **Supabase Status**: https://status.supabase.com/
- **Supabase Dashboard**: https://app.supabase.com/
- **Documentación Django DB**: https://docs.djangoproject.com/en/stable/ref/databases/

---

## 📅 Seguimiento

- **Fecha del Reporte**: 6 de Enero de 2026
- **Próxima Revisión**: 13 de Enero de 2026
- **Responsable**: Equipo de Desarrollo

---

**Estado del Incidente**: ✅ RESUELTO (El servidor se recuperó automáticamente cuando se restableció la conectividad)

**Tiempo de Resolución**: ~1 minuto 14 segundos (recuperación automática)

---

*Este reporte fue generado automáticamente basado en el análisis de logs del sistema.*


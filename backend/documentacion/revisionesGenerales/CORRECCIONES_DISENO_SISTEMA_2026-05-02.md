# Correcciones de Diseño del Sistema — UBAppV2

**Fecha:** 2026-05-02
**Tipo:** Revisión de diseño (no funcional — no agrega features)
**Estado:** Aplicado

---

## Contexto

Revisión completa del proyecto para identificar y corregir problemas de diseño que afectaban la integridad de datos, correctitud de la lógica de negocio, mantenibilidad y seguridad de acceso. Se aplicaron 9 correcciones en total: 6 en el backend y 3 en el frontend.

---

## BACKEND

### B2 — `calcular_totales()` separado de su efecto de escritura

**Archivos modificados:**
- `backend/apps/archivos/models.py`
- `backend/apps/archivos/services.py`
- `backend/apps/archivos/serializers.py`
- `backend/apps/archivos/utils_importacion.py`

**Problema:** `Envio.calcular_totales()` llamaba a `self.save()` internamente. Un método de cálculo con efecto secundario de escritura en BD viola el principio de responsabilidad única y genera comportamiento inesperado en test y en código que solo quiere recalcular sin persistir.

**Solución:**
```python
def calcular_totales(self):
    """Solo recalcula en memoria. Sin escritura en BD."""
    ...  # sin self.save()

def actualizar_totales(self):
    """Calcula y persiste en BD."""
    self.calcular_totales()
    self.save(update_fields=['peso_total', 'cantidad_total', 'valor_total', 'costo_servicio'])
```
Todos los llamadores (services.py ×3, serializers.py ×1, utils_importacion.py ×2) actualizados a `actualizar_totales()`.

---

### B3 — `Usuario.nombre` y `Usuario.correo` no-nullable

**Archivos modificados:**
- `backend/apps/usuarios/models.py`
- `backend/apps/usuarios/migrations/0012_alter_usuario_nombre_correo_not_null.py` _(nuevo)_

**Problema:** `nombre` y `correo` tenían `null=True` a nivel de base de datos, permitiendo registros inválidos aunque `blank=False` bloqueara el formulario.

**Solución:**
```python
nombre = models.CharField(max_length=100, null=False, default='', ...)
correo = models.EmailField(unique=True, null=False, ...)
```
La migración rellena filas existentes con nulos antes de aplicar el constraint NOT NULL.

---

### B4 — Consolidar variables de entorno en `python-decouple`

**Archivos modificados:**
- `backend/settings.py`

**Problema:** Coexistían `from dotenv import load_dotenv` y `from decouple import config` — dos librerías distintas haciendo la misma función, con prioridad ambigua.

**Solución:** Eliminado `load_dotenv()` y su importación. `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` ahora usan `config()` con tipos correctos:
```python
from decouple import config, Csv
SECRET_KEY = config('SECRET_KEY', default='clave-por-defecto-solo-para-desarrollo')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
```

---

### B6 — Operaciones asíncronas: `threading` reemplazado por Celery

**Archivos modificados:**
- `backend/apps/archivos/services.py`

**Archivos creados:**
- `backend/apps/archivos/tasks.py` _(nuevo)_

**Problema:** `EnvioService` usaba `threading.Thread` para ejecutar tareas asíncronas (generación de embeddings, notificaciones, logging). Los threads Python en Django carecen de retry automático, no tienen visibilidad en administración, y pueden acceder al ORM sin contexto de conexión garantizado.

**Solución:** Cuatro tareas Celery con `max_retries=3` y `default_retry_delay=2`:

| Tarea antigua (thread) | Tarea Celery nueva |
|---|---|
| `_generar_embedding_async()` | `generar_embedding_envio.delay()` |
| `_notificar_envio_creado_async()` | `notificar_envio_creado.delay()` |
| `_notificar_cambio_estado_async()` | `notificar_cambio_estado.delay()` |
| `_log_creacion_envio_async()` | `log_creacion_envio.delay()` |

Los cuatro métodos privados `_*_async` eliminados de `services.py`.

---

### B7 — `BusquedaTradicional.resultados_ids` como campo normalizado

**Archivos modificados:**
- `backend/apps/busqueda/models.py`

**Archivos creados:**
- `backend/apps/busqueda/migrations/0013_busquedatradicional_resultados_ids.py` _(nuevo)_

**Problema:** `resultados_json` guardaba el JSON completo de resultados de búsqueda. Esto duplica datos ya existentes en la BD, puede ser muy voluminoso, y se desincroniza si los envíos son actualizados posteriormente.

**Solución:** Se agrega `resultados_ids = ArrayField(IntegerField(), default=list)` para almacenar solo los IDs de los envíos encontrados. `resultados_json` se mantiene marcado como deprecado para compatibilidad con código existente (PDF service, serializers, views). Migración para nueva columna incluida.

---

### B8 — `AuditLog` detecta soft-delete y restore

**Archivos modificados:**
- `backend/apps/core/signals.py`

**Problema:** Los signals `post_save` en `Envio` y `Usuario` registraban el soft-delete (que llama `save(update_fields=['deleted_at'])`) como `ACTUALIZAR` en lugar de `ELIMINAR`. El `restore()` tampoco se diferenciaba.

**Solución:** Nueva función `_resolver_accion()` que inspecciona `update_fields`:

```python
def _resolver_accion(created, update_fields, instance):
    from .models import AuditLog
    if created:
        return AuditLog.CREAR
    if update_fields and 'deleted_at' in update_fields:
        return AuditLog.ELIMINAR if instance.deleted_at is not None else AuditLog.RESTAURAR
    return AuditLog.ACTUALIZAR
```
Los handlers `audit_envio_save` y `audit_usuario_save` actualizados para recibir y usar `update_fields`.

---

## FRONTEND

### F1 — Lazy loading en todas las rutas

**Archivos modificados:**
- `frontend/src/app/app.routes.ts`

**Problema:** Todos los componentes eran importados estáticamente en `app.routes.ts`. Angular incluía el código de todos los componentes en el bundle principal, aumentando el tamaño de la carga inicial innecesariamente.

**Solución:** Eliminados los 20 imports estáticos de componentes. Todas las rutas usan `loadComponent`:
```typescript
{
  path: 'envios',
  loadComponent: () => import('./components/envios/envios-list/...').then(m => m.EnviosListComponent),
  canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR])]
}
```
Angular divide automáticamente el bundle por ruta (code splitting).

---

### F2 — Guards de rutas corregidos

**Archivos modificados:**
- `frontend/src/app/app.routes.ts`

**Problema:** Varias rutas tenían guards incorrectos o faltantes, permitiendo acceso a usuarios con rol incorrecto.

**Correcciones aplicadas:**

| Ruta | Antes | Después |
|---|---|---|
| `/mis-envios` | `authGuard` (cualquier rol) | `authGuard + roleGuard([COMPRADOR])` |
| `/actividades` | `authGuard` (cualquier rol) | `authGuard + roleGuard([ADMIN, GERENTE])` |
| `/envios` | `authGuard` (cualquier rol) | `authGuard + roleGuard([ADMIN, GERENTE, DIGITADOR])` |
| `/busqueda-envios` | `authGuard` (cualquier rol) | `authGuard + roleGuard([ADMIN, GERENTE, DIGITADOR])` |
| `/notificaciones` | `roleGuard([COMPRADOR])` únicamente | `authGuard` (todos los roles autenticados) |

---

### F3 — Tipado consistente del modelo `Envio`

**Archivos modificados:**
- `frontend/src/app/models/envio.ts`

**Problema:** La información del comprador estaba definida como un objeto literal inline anónimo en `comprador_info?`, sin nombre de tipo reutilizable. No había distinción tipada entre la respuesta GET (comprador como objeto) y el payload POST (comprador como ID).

**Solución:**
```typescript
// Nuevo tipo nombrado reutilizable
export interface CompradorInfo { id: number; username: string; nombre: string; ... }

// Envio existente sin breaking changes (compatibilidad total)
export interface Envio {
  comprador: number;           // ID para crear/actualizar
  comprador_info?: CompradorInfo;  // objeto expandido en GET
  ...
}

// Nuevo tipo para respuestas con profundidad
export interface EnvioDetalle extends Omit<Envio, 'comprador'> {
  comprador: CompradorInfo;   // siempre objeto completo
}
```

---

## Migraciones generadas

| Migración | App | Descripción |
|---|---|---|
| `0012_alter_usuario_nombre_correo_not_null.py` | `usuarios` | nombre y correo NOT NULL |
| `0013_busquedatradicional_resultados_ids.py` | `busqueda` | Nuevo campo resultados_ids |

**Comando para aplicar:**
```bash
cd backend
python manage.py migrate
```

---

## Archivos sin cambios requeridos

Las siguientes correcciones del plan original **no se aplicaron** en esta iteración:

- **B1** (`on_delete=CASCADE` → `PROTECT/SET_NULL`): Pendiente — requiere análisis de datos existentes en producción antes de migrar.
- **F1-rutas públicas** (informacion, ubicaciones, login, register): Aplicadas con lazy loading en el mismo commit que F1.

---

## Checklist de verificación

- [x] Sintaxis Python válida en todos los archivos modificados
- [x] Nombres de clases Angular correctos en `loadComponent`
- [x] Todos los componentes son `standalone: true`
- [x] Migraciones creadas para cambios de BD
- [x] Métodos privados `_*_async` eliminados de services.py
- [x] `import threading` eliminado de services.py
- [x] `load_dotenv` eliminado de settings.py
- [ ] `python manage.py migrate` ejecutado en entorno de staging
- [ ] Celery worker activo para recibir nuevas tareas
- [ ] Tests de regresión en rutas con guards modificados

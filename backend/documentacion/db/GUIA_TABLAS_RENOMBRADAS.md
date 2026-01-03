# Guía: Tablas Renombradas y Eliminadas

## Situación Actual

### Tablas Eliminadas (no se usan):
- ❌ `auth_group` - Eliminada, no se usan grupos
- ❌ `authtoken_token` - Eliminada, no se usa authtoken

### Tablas Renombradas:
- 🔄 `django_admin_log` → `logs`
- 🔄 `django_content_type` → `tipo_contenido`
- 🔄 `django_session` → `sesiones_key`

### Columnas Eliminadas de `usuarios`:
- ❌ `first_name`, `last_name`, `email`, `is_active`, `latitud`, `longitud`

## Solución Implementada

He creado una solución automática que maneja todo:

### 1. Patches Automáticos (`apps/core/patches_django.py`)
- Modifica los modelos de Django para usar los nombres de tabla renombrados
- Se aplican automáticamente al cargar la app `core`

### 2. Migración de Renombrado (`apps/core/migrations/0001_renombrar_tablas_django.py`)
- Renombra las tablas después de que Django las cree
- Se ejecuta automáticamente

### 3. Script Automático (`aplicar_migraciones_renombradas.py`)
- Maneja todo el proceso
- Marca migraciones de apps eliminadas como aplicadas
- Aplica migraciones normales
- Renombra tablas si es necesario

## Cómo Aplicar

### Opción 1: Script Automático (RECOMENDADO)

```bash
cd backend
python aplicar_migraciones_renombradas.py
```

Este script hace todo automáticamente:
- ✅ Marca migraciones de `auth` y `authtoken` como aplicadas (tablas eliminadas)
- ✅ Aplica migraciones de otras apps
- ✅ Renombra tablas si fueron creadas con nombres originales
- ✅ Verifica el estado final

### Opción 2: Manual

```bash
# 1. Marcar migraciones de apps eliminadas
python manage.py migrate auth --fake
python manage.py migrate authtoken --fake

# 2. Aplicar migraciones de otras apps
python manage.py migrate admin
python manage.py migrate contenttypes
python manage.py migrate sessions
python manage.py migrate usuarios
python manage.py migrate archivos
python manage.py migrate busqueda
python manage.py migrate notificaciones

# 3. Si las tablas fueron creadas con nombres originales, renombrarlas:
# (El script lo hace automáticamente, pero si lo haces manual):
# python manage.py migrate core
```

## Verificar

```bash
# Ver estado de migraciones
python manage.py showmigrations

# Verificar tablas
python verificar_tablas.py
```

## Cambios Realizados en el Código

### 1. Modelo Usuario
- ✅ Eliminados campos: `first_name`, `last_name`, `email`, `is_active`
- ✅ Usa `es_activo` en lugar de `is_active`
- ✅ Migración creada: `0007_eliminar_campos_abstractuser.py`

### 2. Configuración Core
- ✅ `apps/core/apps.py` - Aplica patches automáticamente
- ✅ `apps/core/patches_django.py` - Patches para modelos de Django
- ✅ `apps/core/migrations/0001_renombrar_tablas_django.py` - Migración de renombrado

### 3. Settings
- ✅ `apps.core.apps.CoreConfig` configurado para aplicar patches

## Notas Importantes

- ✅ Las tablas eliminadas NO se recrearán
- ✅ Las tablas renombradas se manejan automáticamente
- ✅ Las columnas eliminadas NO se recrearán
- ⚠️ El sistema de grupos de Django no funcionará (tabla eliminada)
- ⚠️ El sistema de authtoken no funcionará (tabla eliminada)
- ⚠️ Para futuras migraciones, usa normalmente: `python manage.py migrate`

## Solución de Problemas

### Si Django intenta crear tablas con nombres originales:

El script `aplicar_migraciones_renombradas.py` las renombra automáticamente.

### Si hay errores al aplicar migraciones:

1. Verifica que las tablas renombradas existen:
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_name IN ('logs', 'tipo_contenido', 'sesiones_key');
   ```

2. Si no existen, ejecuta el script de nuevo

3. Si persisten errores, verifica los logs de Django


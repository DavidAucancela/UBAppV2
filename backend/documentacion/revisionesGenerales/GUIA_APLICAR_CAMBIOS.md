# Guía: Aplicar Cambios Manuales en la Base de Datos

## Situación

Has hecho cambios manuales en la base de datos:
- ✅ Eliminaste tablas del sistema (`auth_group`, `authtoken_token`, etc.)
- ✅ Renombraste tablas (ej: `django_admin_log` → `logs`)
- ✅ Eliminaste columnas de `usuarios` (`first_name`, `last_name`, `email`, `is_active`, `latitud`, `longitud`)

## Cambios Realizados en el Código

### 1. Modelo Usuario Actualizado

He actualizado `backend/apps/usuarios/models.py` para:
- ✅ Eliminar campos heredados de `AbstractUser` que ya no existen (`first_name`, `last_name`, `email`, `is_active`)
- ✅ Usar `es_activo` en lugar de `is_active`
- ✅ El modelo ya usa `db_table = 'usuarios'` (coincide con tu renombrado)

### 2. Migración Creada

He creado `backend/apps/usuarios/migrations/0007_eliminar_campos_abstractuser.py` que:
- ✅ Refleja los cambios ya aplicados en la BD
- ✅ Usa `SeparateDatabaseAndState` para no modificar la BD (los cambios ya están hechos)

### 3. Referencias Actualizadas

- ✅ Cambiado `user.is_active` → `user.es_activo` en `views.py`

## Pasos para Aplicar los Cambios

### Opción 1: Usar el Script Automático (RECOMENDADO)

```bash
cd backend
python aplicar_cambios_manuales.py
```

Este script marcará todas las migraciones como aplicadas sin ejecutarlas.

### Opción 2: Aplicar Manualmente

1. **Aplicar la migración de usuarios (ya está lista):**
   ```bash
   python manage.py migrate usuarios --fake
   ```

2. **Marcar migraciones del sistema como aplicadas:**
   ```bash
   python manage.py migrate admin --fake
   python manage.py migrate auth --fake
   python manage.py migrate contenttypes --fake
   python manage.py migrate sessions --fake
   python manage.py migrate authtoken --fake
   ```

3. **Aplicar migraciones de tus apps:**
   ```bash
   python manage.py migrate archivos --fake
   python manage.py migrate busqueda --fake
   python manage.py migrate notificaciones --fake
   ```

### Opción 3: Aplicar Todas las Migraciones con --fake-initial

Si es la primera vez que aplicas migraciones:

```bash
python manage.py migrate --fake-initial
```

Luego aplica la migración de usuarios:

```bash
python manage.py migrate usuarios
```

## Verificar el Estado

Para verificar que todo está correcto:

```bash
# Ver estado de migraciones
python manage.py showmigrations

# Verificar tablas en la BD
python verificar_tablas.py
```

## Importante: Tablas Renombradas

Has renombrado tablas del sistema de Django:
- `django_admin_log` → `logs`
- `django_content_type` → `tipo_contenido`
- `django_migrations` → `migraciones`
- `django_session` → `sesiones_key`

**ADVERTENCIA**: Estas tablas son críticas para Django. Si Django intenta usarlas con sus nombres originales, puede haber problemas.

### Solución para Tablas Renombradas

Si Django necesita usar estas tablas, tienes dos opciones:

1. **Renombrarlas de vuelta a sus nombres originales** (recomendado)
2. **Crear modelos personalizados** que mapeen a los nuevos nombres (complejo)

Para renombrar de vuelta:

```sql
ALTER TABLE logs RENAME TO django_admin_log;
ALTER TABLE tipo_contenido RENAME TO django_content_type;
ALTER TABLE migraciones RENAME TO django_migrations;
ALTER TABLE sesiones_key RENAME TO django_session;
```

## Próximos Pasos

1. ✅ Ejecuta el script o aplica las migraciones con `--fake`
2. ✅ Verifica que no hay errores
3. ✅ Si Django intenta recrear tablas renombradas, considera renombrarlas de vuelta
4. ✅ Para futuras migraciones, usa normalmente: `python manage.py migrate`

## Notas

- Las tablas eliminadas (`auth_group`, `authtoken_token`, etc.) NO se recrearán porque las migraciones están marcadas como aplicadas
- Las columnas eliminadas de `usuarios` NO se recrearán porque el modelo ya no las incluye
- Si necesitas usar funcionalidades que requieren las tablas eliminadas, deberás recrearlas


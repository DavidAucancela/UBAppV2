# Solución: Tablas que se recrean después de borrarlas manualmente

## Problema
Borraste tablas manualmente de la base de datos, pero Django las recrea al ejecutar `python manage.py migrate`.

## Soluciones

### Opción 1: Eliminar los modelos del código (RECOMENDADA)

Si las tablas no se usan, elimina los modelos del código y crea una migración:

1. **Identifica qué modelos/tablas no necesitas**
   - Revisa los archivos `models.py` en cada app
   - Identifica los modelos que corresponden a las tablas que borraste

2. **Elimina los modelos del código**
   - Comenta o elimina los modelos en los archivos `models.py`
   - Asegúrate de eliminar también las referencias en:
     - `admin.py`
     - `serializers.py`
     - `views.py`
     - Cualquier otro archivo que use esos modelos

3. **Crea una migración que elimine esos modelos**
   ```bash
   python manage.py makemigrations
   ```

4. **Aplica la migración**
   ```bash
   python manage.py migrate
   ```

### Opción 2: Marcar migraciones como aplicadas (si quieres mantener los modelos)

Si quieres mantener los modelos pero evitar que se creen las tablas temporalmente:

1. **Marca las migraciones como aplicadas sin ejecutarlas**
   ```bash
   python manage.py migrate --fake nombre_app
   ```

   **ADVERTENCIA**: Esto puede causar inconsistencias si las tablas realmente no existen.

### Opción 3: Usar `--fake-initial` (si las tablas ya existen parcialmente)

Si algunas tablas existen pero otras no:

1. **Marca solo las migraciones iniciales como aplicadas**
   ```bash
   python manage.py migrate --fake-initial
   ```

2. **Luego aplica las migraciones restantes normalmente**
   ```bash
   python manage.py migrate
   ```

### Opción 4: Recrear la base de datos desde cero (si es posible)

Si es un entorno de desarrollo y puedes perder los datos:

1. **Elimina todas las tablas**
   ```sql
   -- En PostgreSQL
   DROP SCHEMA public CASCADE;
   CREATE SCHEMA public;
   ```

2. **Aplica todas las migraciones**
   ```bash
   python manage.py migrate
   ```

## Pasos Recomendados

1. **Identifica qué tablas borraste**
   - Revisa tu base de datos y compara con los modelos en el código

2. **Decide si necesitas esos modelos**
   - Si NO los necesitas: Usa Opción 1
   - Si SÍ los necesitas: Usa Opción 2 o 3

3. **Si usas Opción 1, verifica dependencias**
   - Asegúrate de que ningún otro modelo tenga ForeignKey hacia los modelos eliminados
   - Revisa las migraciones para ver si hay dependencias

## Ejemplo Práctico

Si borraste las tablas `archivo` y `categoria` pero ya no las usas:

1. En `backend/apps/archivos/models.py`, verifica si hay modelos que usen esas tablas
2. Si `ImportacionExcel` usa `db_table = 'archivo'`, considera renombrarlo o eliminarlo
3. Crea una migración:
   ```bash
   python manage.py makemigrations archivos
   ```
4. Aplica la migración:
   ```bash
   python manage.py migrate archivos
   ```

## Verificar el Estado

Para ver qué migraciones están aplicadas:
```bash
python manage.py showmigrations
```

Para ver el estado de la base de datos:
```bash
python manage.py dbshell
```

Luego en PostgreSQL:
```sql
\dt  -- Lista todas las tablas
```


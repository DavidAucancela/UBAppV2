# Solución para Error de Conexión a Supabase

## Error Común
```
django.db.utils.OperationalError: connection to server at "db.xxxxx.supabase.co", port 5432 failed: 
Connection timed out
```

## Pasos para Resolver

### 1. Ejecutar Diagnóstico
```bash
cd backend
python funciones/diagnostico_conexion.py
```

Este script verificará:
- Variables de entorno configuradas
- Resolución DNS
- Conectividad de red
- Conexión con Django

### 2. Verificar Archivo .env

Crea o verifica el archivo `.env` en el directorio `backend/`:

```env
DB_HOST=db.xxxxx.supabase.co
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=tu_contraseña_aqui
DB_PORT=5432
```

**⚠️ IMPORTANTE:** 
- Reemplaza `xxxxx` con tu ID de proyecto de Supabase
- Obtén la contraseña desde: Supabase Dashboard > Settings > Database > Database password

### 3. Verificar Supabase Dashboard

1. Ve a [Supabase Dashboard](https://app.supabase.com)
2. Selecciona tu proyecto
3. Ve a **Settings > Database**
4. Verifica que el proyecto esté **activo** (no pausado)
5. Copia las credenciales correctas

### 4. Verificar Restricciones de IP

En Supabase:
1. Ve a **Settings > Database**
2. Revisa **Connection Pooling** o **Network Restrictions**
3. Asegúrate de que tu IP no esté bloqueada
4. Si usas Connection Pooling, usa el puerto **6543** en lugar de **5432**

### 5. Usar Connection String (Alternativa)

Si las variables individuales no funcionan, puedes usar una connection string:

En Supabase Dashboard > Settings > Database, copia la **Connection String** (URI mode).

Luego en tu `.env`:
```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres?sslmode=require
```

Y modifica `settings.py` para usar esta URL:
```python
import dj_database_url

if os.getenv('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.parse(os.getenv('DATABASE_URL'))
```

### 6. Verificar Firewall/Red

- **Firewall local**: Asegúrate de que el puerto 5432 no esté bloqueado
- **Red corporativa**: Algunas redes bloquean conexiones externas
- **VPN**: Si usas VPN, intenta desconectarte temporalmente
- **Prueba desde otra red**: Usa tu móvil como hotspot para verificar

### 7. Usar Connection Pooling (Recomendado)

Supabase ofrece Connection Pooling que es más estable:

1. En Supabase Dashboard > Settings > Database
2. Busca **Connection Pooling**
3. Usa el puerto **6543** (pooling) en lugar de **5432** (directo)
4. Actualiza tu `.env`:
   ```env
   DB_PORT=6543
   ```

### 8. Verificar SSL

Supabase **requiere SSL**. Asegúrate de que en `settings.py` tengas:

```python
'OPTIONS': {
    'sslmode': 'require',
    'connect_timeout': 10,
},
```

### 9. Probar Conexión Manual

Puedes probar la conexión directamente con psql:

```bash
psql "postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres?sslmode=require"
```

O con Python:
```python
import psycopg2
conn = psycopg2.connect(
    host="db.xxxxx.supabase.co",
    port=5432,
    database="postgres",
    user="postgres",
    password="tu_contraseña",
    sslmode="require"
)
print("✅ Conexión exitosa!")
```

### 10. Contactar Soporte de Supabase

Si nada funciona:
1. Verifica el estado de Supabase: https://status.supabase.com
2. Revisa los logs en Supabase Dashboard > Logs
3. Contacta soporte de Supabase si el proyecto está inactivo

## Configuración Recomendada

Para desarrollo local, considera usar una base de datos local si Supabase da problemas:

```env
# Para desarrollo local
DB_HOST=localhost
DB_PORT=5432
DB_NAME=equityDB
DB_USER=postgres
DB_PASSWORD=admin
```

## Notas Importantes

- ⚠️ **Nunca subas el archivo `.env` a Git** - está en `.gitignore`
- ✅ **Usa Connection Pooling** para mejor rendimiento y estabilidad
- ✅ **Verifica el estado de Supabase** antes de reportar problemas
- ✅ **Usa SSL siempre** con Supabase


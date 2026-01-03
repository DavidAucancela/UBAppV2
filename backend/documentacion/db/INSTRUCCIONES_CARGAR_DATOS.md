# 📥 Instrucciones para Cargar Datos de Supabase a Docker

## ⚠️ Importante: Configuración del .env

Antes de ejecutar el script de exportación, debes configurar correctamente el `.env` para conectarte a Supabase.

### Problema Común

Si ves este error:
```
ValueError: 'admin' does not appear to be an IPv4 or IPv6 address
```

**Causa**: Tienes `[admin]` entre corchetes en tu `DATABASE_URL`, pero debes reemplazarlo con tu contraseña real de Supabase.

### Solución

En tu archivo `backend/.env`, busca la línea de `DATABASE_URL` de Supabase y reemplaza `[admin]` con tu contraseña real:

**❌ Incorrecto:**
```env
DATABASE_URL=postgresql://postgres:[admin]@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres
```

**✅ Correcto:**
```env
DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA_REAL@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres
```

## 📋 Pasos para Cargar Datos

### Paso 1: Configurar .env para Supabase

Edita `backend/.env` y asegúrate de tener:

```env
# Comenta la configuración de Docker (opción 1)
# DB_NAME=UBAppDB
# DB_USER=postgres
# DB_PASSWORD=admin
# DB_HOST=localhost
# DB_PORT=5435

# Activa la configuración de Supabase (opción 2)
DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA_REAL@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres
```

**⚠️ IMPORTANTE**: Reemplaza `TU_CONTRASEÑA_REAL` con tu contraseña real de Supabase (sin corchetes).

### Paso 2: Verificar Conexión a Supabase

Asegúrate de estar:
- ✅ Conectado a una red que soporte IPv6 (generalmente tu casa)
- ✅ Docker Desktop está corriendo (aunque usemos Supabase para exportar)
- ✅ Tienes la contraseña correcta en DATABASE_URL

### Paso 3: Exportar Datos desde Supabase

```powershell
cd backend
python exportar_datos_supabase.py
```

Esto creará archivos en `backend/backup/`:
- `usuarios.json`
- `envios.json`
- `productos.json`
- `embeddings.json`

### Paso 4: Cambiar Configuración a Docker

Edita `backend/.env` y cambia a Docker:

```env
# Activa la configuración de Docker (opción 1)
DB_NAME=UBAppDB
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5435

# Comenta la configuración de Supabase (opción 2)
# DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA_REAL@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres
```

### Paso 5: Verificar Docker está Corriendo

```powershell
docker ps | findstr postgres_local
```

Si no está corriendo:
```powershell
docker start postgres_local
```

### Paso 6: Importar Datos a Docker

```powershell
python importar_datos_local.py
```

El script te pedirá confirmación antes de limpiar la base de datos local.

## 🔄 Script Automatizado

También puedes usar el script guiado:

```powershell
python cargar_datos_supabase_a_docker.py
```

Este script te guiará paso a paso, pero **debes tener la contraseña correcta en DATABASE_URL antes de ejecutarlo**.

## ✅ Verificación Final

Después de importar, verifica que los datos estén en Docker:

```powershell
python manage.py shell
```

```python
from apps.usuarios.models import Usuario
from apps.archivos.models import Envio, Producto
from apps.busqueda.models import EnvioEmbedding

print(f"Usuarios: {Usuario.objects.count()}")
print(f"Envíos: {Envio.objects.count()}")
print(f"Productos: {Producto.objects.count()}")
print(f"Embeddings: {EnvioEmbedding.objects.count()}")
```

## 🆘 Solución de Problemas

### Error: "cannot import name 'EnvioProducto'"
✅ **Solucionado**: Los scripts ya han sido actualizados. Este modelo no existe, la relación es directa.

### Error: "'admin' does not appear to be an IPv4 or IPv6 address"
✅ **Causa**: Tienes `[admin]` en lugar de tu contraseña real
✅ **Solución**: Reemplaza `[admin]` con tu contraseña real de Supabase (sin corchetes)

### Error: "could not translate host name"
✅ **Causa**: No estás conectado a una red con IPv6
✅ **Solución**: Conéctate a tu red de casa o usa un hotspot móvil con IPv6

### Error: "connection refused" en Docker
✅ **Causa**: Docker no está corriendo
✅ **Solución**: `docker start postgres_local`


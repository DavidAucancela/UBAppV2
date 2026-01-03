# 🔄 Cómo Cambiar Entre Docker y Supabase

## 📋 Resumen

Puedes cambiar fácilmente entre la base de datos local (Docker) y Supabase simplemente comentando/descomentando líneas en tu archivo `.env`.

## 🔗 Cadenas de Conexión

### Docker Local (Puerto 5435)
```
postgresql://postgres:admin@localhost:5435/UBAppDB
```

### Supabase (Nube)
```
postgresql://postgres:[YOUR-PASSWORD]@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres
```

## 📝 Configuración del .env

### Opción 1: Usar DATABASE_URL (RECOMENDADO)

Abre `backend/.env` y configura así:

#### ✅ Para usar Docker Local:
```env
DATABASE_URL=postgresql://postgres:admin@localhost:5435/UBAppDB
# DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres
```

#### ✅ Para usar Supabase:
```env
# DATABASE_URL=postgresql://postgres:admin@localhost:5435/UBAppDB
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres
```

**⚠️ IMPORTANTE**: Reemplaza `[YOUR-PASSWORD]` con tu contraseña real de Supabase.

### Opción 2: Usar Variables Individuales

Si prefieres usar variables individuales, comenta `DATABASE_URL` y usa estas:

#### ✅ Para Docker Local:
```env
# DATABASE_URL=...
DB_HOST=localhost
DB_PORT=5435
DB_NAME=UBAppDB
DB_USER=postgres
DB_PASSWORD=admin
```

#### ✅ Para Supabase:
```env
# DATABASE_URL=...
DB_HOST=db.gybrifikqkibwqpzjuxm.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=[YOUR-PASSWORD]
```

## 🎯 Pasos para Cambiar

1. **Abre** `backend/.env`
2. **Comenta** la línea activa (agrega `#` al inicio)
3. **Descomenta** la línea que quieres usar (quita el `#`)
4. **Guarda** el archivo
5. **Reinicia** Django si está corriendo

### Ejemplo Visual:

**Antes (usando Docker):**
```env
DATABASE_URL=postgresql://postgres:admin@localhost:5435/UBAppDB
# DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres
```

**Después (cambiando a Supabase):**
```env
# DATABASE_URL=postgresql://postgres:admin@localhost:5435/UBAppDB
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres
```

## ⚙️ Cómo Funciona

El `settings.py` detecta automáticamente:
- ✅ Si es **localhost** → No requiere SSL (Docker local)
- ✅ Si es **Supabase** → Requiere SSL automáticamente

No necesitas cambiar nada más en el código.

## 🐳 Verificar Docker

Antes de usar Docker, asegúrate de que el contenedor esté corriendo:

```powershell
# Verificar estado
docker ps | findstr postgres_local

# Si no está corriendo, iniciarlo
docker start postgres_local
```

## 🔍 Verificar Conexión

Después de cambiar, verifica que funciona:

```powershell
cd backend
python manage.py migrate
```

Si no hay errores, ¡la conexión está funcionando! ✅

## 📊 Comparación Rápida

| Característica | Docker Local | Supabase |
|---------------|--------------|----------|
| **Puerto** | 5435 | 5432 |
| **Base de datos** | UBAppDB | postgres |
| **Usuario** | postgres | postgres |
| **Contraseña** | admin | [Tu password] |
| **Host** | localhost | db.xxxxx.supabase.co |
| **Requiere internet** | ❌ No | ✅ Sí (IPv6) |
| **SSL** | ❌ No | ✅ Sí |
| **Velocidad** | ⚡ Muy rápido | 🐌 Depende de red |

## 💡 Recomendaciones

- **En casa (con IPv6)**: Usa **Supabase** para tener los datos en la nube
- **En otras redes (sin IPv6)**: Usa **Docker local** para trabajar sin problemas
- **Para desarrollo rápido**: Usa **Docker local** (más rápido)
- **Para producción**: Usa **Supabase** o tu servidor de producción

## 🆘 Solución de Problemas

### Error: "could not translate host name"
- Estás intentando usar Supabase pero tu red no soporta IPv6
- **Solución**: Cambia a Docker local

### Error: "server does not support SSL"
- Estás intentando usar SSL con Docker local
- **Solución**: El código ya detecta esto automáticamente, pero verifica que tu `.env` use `localhost` para Docker

### Error: "connection refused" o "port 5435"
- Docker no está corriendo
- **Solución**: 
  ```powershell
  docker start postgres_local
  ```

## 📚 Archivos Relacionados

- `backend/.env` - Archivo de configuración (no está en git)
- `backend/.env.ejemplo` - Plantilla de ejemplo
- `backend/settings.py` - Configuración de Django (líneas 74-119)


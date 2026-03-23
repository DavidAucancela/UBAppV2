# Guía de Despliegue en Railway — UBApp

Migración completa desde Vercel + Render + Supabase → **Railway** (todo en un solo lugar).

---

## Resumen de servicios a crear

| Servicio       | Tipo              | Directorio raíz  |
|----------------|-------------------|------------------|
| `ubapp-db`     | PostgreSQL plugin | —                |
| `ubapp-redis`  | Redis plugin      | —                |
| `ubapp-backend`| Docker (Django)   | `/backend`       |
| `ubapp-frontend`| Docker (Angular) | `/frontend`      |

---

## PASO 1 — Crear el proyecto en Railway

1. Ir a [railway.app](https://railway.app) → **New Project**
2. Seleccionar **Deploy from GitHub repo** → conectar tu repositorio de GitHub
3. Railway detectará el repo. **No despliegues nada aún** — primero añade los plugins de DB.

---

## PASO 2 — Añadir PostgreSQL (con pgvector)

1. En el proyecto → **+ New** → **Database** → **PostgreSQL**
2. Railway creará el servicio `Postgres` y generará `DATABASE_URL` automáticamente.
3. **Habilitar pgvector** (requerido por la app):
   - En el servicio PostgreSQL → tab **Query** (o conéctate con cualquier cliente)
   - Ejecutar:
     ```sql
     CREATE EXTENSION IF NOT EXISTS vector;
     ```
4. Anota la variable `DATABASE_URL` que aparece en el tab **Variables** del servicio Postgres.
   Tiene el formato:
   ```
   postgresql://postgres:PASSWORD@HOST.railway.internal:5432/railway
   ```

---

## PASO 3 — Añadir Redis

1. En el proyecto → **+ New** → **Database** → **Redis**
2. Railway creará el servicio Redis y generará `REDIS_URL` automáticamente.
3. Anota la variable `REDIS_URL`. Tiene el formato:
   ```
   redis://default:PASSWORD@HOST.railway.internal:6379
   ```

---

## PASO 4 — Configurar el servicio Backend (Django)

### 4.1 Crear el servicio

1. En el proyecto → **+ New** → **GitHub Repo** → seleccionar tu repo
2. En el servicio creado → **Settings** → **Root Directory**: establecer `/backend`
3. Railway detectará el `Dockerfile` y el `railway.json` automáticamente.

### 4.2 Variables de entorno del Backend

En el servicio Backend → tab **Variables**, añadir las siguientes:

```
SECRET_KEY=<genera una clave larga y aleatoria, mínimo 50 caracteres>
DEBUG=False
ALLOWED_HOSTS=<tu-backend>.up.railway.app
DATABASE_URL=<pegar el valor del servicio PostgreSQL>
REDIS_URL=<pegar el valor del servicio Redis>
OPENAI_API_KEY=<tu clave de OpenAI>
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536
CORS_ALLOWED_ORIGINS=https://<tu-frontend>.up.railway.app
CSRF_TRUSTED_ORIGINS=https://<tu-backend>.up.railway.app,https://<tu-frontend>.up.railway.app
```

> **Nota sobre ALLOWED_HOSTS y CORS**: Las URLs de Railway tienen el formato
> `https://nombre-servicio-xxxx.up.railway.app`. Las conocerás después del primer deploy.
> Puedes actualizar las variables en cualquier momento sin re-buildear.

> **Generar SECRET_KEY**: ejecutar en cualquier terminal Python:
> ```python
> python -c "import secrets; print(secrets.token_urlsafe(60))"
> ```

### 4.3 Verificar que el startup script funcione

El backend usa `start_render.py` (CMD en Dockerfile) que:
1. Espera a que la DB esté lista (`wait_for_db.py`)
2. Ejecuta `rename_backup_tables.py` (migraciones de nombres de tablas)
3. Corre `python manage.py migrate`
4. Corre `python manage.py collectstatic`
5. Arranca Gunicorn en el `PORT` que Railway inyecta

✅ No necesitas cambiar nada — Railway inyecta `PORT` igual que Render.

---

## PASO 5 — Configurar el servicio Frontend (Angular)

### 5.1 Crear el servicio

1. En el proyecto → **+ New** → **GitHub Repo** → seleccionar el mismo repo
2. En el servicio creado → **Settings** → **Root Directory**: establecer `/frontend`
3. Railway detectará `Dockerfile.railway` y `railway.json` automáticamente.

### 5.2 Variables de entorno del Frontend

En el servicio Frontend → tab **Variables**, añadir:

```
API_URL=https://<tu-backend>.up.railway.app/api
```

> **Importante**: Esta variable se usa como **build arg** en el Dockerfile.
> Cada vez que cambies `API_URL` Railway re-buildeará el frontend.

> La URL del backend la obtienes en **Settings → Networking → Public Domain**
> del servicio Backend, después del primer deploy.

---

## PASO 6 — Primer deploy y verificación

### Orden de deploy recomendado:

1. ✅ PostgreSQL + Redis (ya están listos automáticamente)
2. ✅ Backend → esperar a que el health check en `/api/health/` responda 200
3. ✅ Frontend → esperar a que el health check en `/` responda 200

### Verificación del Backend:

```bash
curl https://<tu-backend>.up.railway.app/api/health/
# Esperado: {"status": "ok", ...}
```

### Verificación de pgvector (si las migraciones fallan):

Si las migraciones de Django relacionadas con búsqueda semántica fallan, ejecutar en
el **Query Console** de Railway PostgreSQL:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```
Luego re-deployar el backend o ejecutar desde **Railway Shell**:
```bash
python manage.py migrate
```

---

## PASO 7 — Dominio personalizado (opcional)

En cada servicio → **Settings → Networking → Custom Domain**:
- Backend: `api.tudominio.com`
- Frontend: `app.tudominio.com` o `tudominio.com`

Si usas dominio personalizado, actualizar las variables:
- `ALLOWED_HOSTS` → añadir `api.tudominio.com`
- `CORS_ALLOWED_ORIGINS` → cambiar a `https://app.tudominio.com`
- `CSRF_TRUSTED_ORIGINS` → actualizar con los nuevos dominios
- `API_URL` en el frontend → `https://api.tudominio.com/api`

---

## PASO 8 — Cancelar Vercel y Render

Solo cancelar **después** de verificar que Railway funciona correctamente:

1. **Render**: Dashboard → cada servicio → Settings → Delete Service
   - Eliminar: ubapp-backend, ubapp-frontend, ubapp-redis
   - Si tenías DB en Render, eliminar también (los datos ya no son necesarios si empiezas de 0)

2. **Vercel**: Dashboard → el proyecto → Settings → Delete Project

3. **Supabase** (si ya no la necesitas): Dashboard → Project Settings → Delete Project
   - ⚠️ Esto elimina todos los datos. Solo hacerlo si estás seguro.

---

## Variables de entorno — Referencia completa

### Backend (obligatorias)

| Variable | Ejemplo | Descripción |
|----------|---------|-------------|
| `SECRET_KEY` | `abc123...` (50+ chars) | Clave secreta Django |
| `DEBUG` | `False` | Siempre False en producción |
| `ALLOWED_HOSTS` | `ubapp-backend.up.railway.app` | Host del backend |
| `DATABASE_URL` | `postgresql://...railway.internal...` | Inyectada por Railway |
| `REDIS_URL` | `redis://...railway.internal...` | Inyectada por Railway |
| `CORS_ALLOWED_ORIGINS` | `https://ubapp-frontend.up.railway.app` | URL del frontend |
| `CSRF_TRUSTED_ORIGINS` | `https://ubapp-backend.up.railway.app,https://ubapp-frontend.up.railway.app` | Ambas URLs |
| `OPENAI_API_KEY` | `sk-...` | Clave de OpenAI |

### Backend (opcionales)

| Variable | Default | Descripción |
|----------|---------|-------------|
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Modelo de embeddings |
| `OPENAI_EMBEDDING_DIMENSIONS` | `1536` | Dimensiones |
| `SEMANTIC_CACHE_TIMEOUT` | `3600` | Timeout caché semántica (seg) |
| `EMBEDDING_CACHE_TIMEOUT` | `604800` | Timeout caché embeddings (seg) |

### Frontend (obligatorias)

| Variable | Ejemplo | Descripción |
|----------|---------|-------------|
| `API_URL` | `https://ubapp-backend.up.railway.app/api` | URL del backend |

---

## Troubleshooting

### Error: `SSL connection required` en DB
- Asegúrate de usar la URL interna de Railway (`*.railway.internal`), no la URL pública.
- La URL interna no requiere SSL y el código lo detecta automáticamente.

### Error: `extension "vector" does not exist`
- Ejecutar en Railway PostgreSQL Query Console:
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  ```

### CORS errors en el frontend
- Verificar que `CORS_ALLOWED_ORIGINS` incluye exactamente la URL del frontend (con https://, sin slash final).
- Si la URL cambió, actualizar la variable y re-deployar el backend.

### El frontend no puede conectar al backend
- Verificar que `API_URL` en el frontend termina en `/api` (sin slash final).
- Verificar que el backend está corriendo: `curl https://<backend>.up.railway.app/api/health/`

### Migraciones fallan al iniciar
- Revisar los logs del backend en Railway → el error específico de migración estará ahí.
- Acceder a Railway Shell del backend: `python manage.py showmigrations`

---

## Costos estimados en Railway

| Plan | Precio | Incluye |
|------|--------|---------|
| Hobby | $5/mes | $5 de crédito mensual, suficiente para desarrollo |
| Pro | $20/mes | Más recursos, sin sleep, mejor para producción |

Con el plan Hobby ($5 crédito), los 4 servicios (DB + Redis + Backend + Frontend) consumen aproximadamente:
- PostgreSQL: ~$0.000231/GB-hora
- Redis: ~$0.000231/GB-hora
- Backend + Frontend: ~$0.000463/vCPU-hora

Para un proyecto en desarrollo/staging, el crédito de $5 suele ser suficiente.

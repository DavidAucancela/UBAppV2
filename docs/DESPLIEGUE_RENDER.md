# Despliegue de UBApp en Render

Guía para desplegar el proyecto UBApp en [Render](https://render.com) usando Docker.

---

## Requisitos previos

- Cuenta en [Render](https://render.com)
- Repositorio conectado a GitHub/GitLab
- API Key de OpenAI (para búsqueda semántica)

---

## Opción 1: Blueprint (recomendado)

Render usa el archivo `render.yaml` como Blueprint para crear todos los servicios automáticamente.

### Paso 1: Conectar el repositorio

1. Entra a [dashboard.render.com](https://dashboard.render.com)
2. Clic en **New** → **Blueprint**
3. Conecta tu repositorio de GitHub
4. Render detectará el archivo `render.yaml`

### Paso 2: Configurar variables manuales

**Importante:** Render solo permite **1 base de datos PostgreSQL gratis**. Si ya tienes una, usa esa.

Antes del primer deploy, configura estas variables en el Dashboard:

| Servicio | Variable | Descripción |
|----------|----------|-------------|
| **ubapp-backend** | `DATABASE_URL` | **Internal Database URL** de tu PostgreSQL en Render (Dashboard → tu DB → Connect → Internal) |
| **ubapp-backend** | `OPENAI_API_KEY` | Tu API Key de [OpenAI](https://platform.openai.com/api-keys) |
| **ubapp-frontend** | `API_URL` | **URL del backend** (ej: `https://ubapp-backend-xxxx.onrender.com/api`). Ver Paso 4. |

### Paso 3: Crear el Blueprint

1. Clic en **Apply**
2. Render creará:
   - **ubapp-redis**: Redis para caché
   - **ubapp-backend**: API Django (Docker)
   - **ubapp-frontend**: SPA Angular (Docker)

> **Base de datos:** El Blueprint **no crea** una nueva PostgreSQL (Render solo permite 1 gratis). Usa tu base de datos existente y pega su `DATABASE_URL` en el backend.

### Paso 4: Configurar API_URL en el frontend

1. Espera a que el **backend** termine de desplegarse
2. Copia la URL del backend (ej: `https://ubapp-backend-xxxx.onrender.com`)
3. En el servicio **ubapp-frontend**, ve a **Environment**
4. Agrega o edita `API_URL` con el valor: `https://tu-backend-url.onrender.com/api`
5. Guarda y haz **Manual Deploy** en el frontend

### Paso 5: Habilitar pgvector en PostgreSQL

1. Ve a tu base de datos PostgreSQL en Render
2. En **Info** → **Extensions**, habilita **pgvector**
3. O ejecuta en la consola: `CREATE EXTENSION IF NOT EXISTS vector;`

### Paso 6: Crear superusuario

```bash
# Desde tu máquina, usando el Shell de Render o la conexión a la DB
# O ejecuta en el backend:
docker exec -it <backend-container> python manage.py createsuperuser
```

En Render: ve al servicio **ubapp-backend** → **Shell** → ejecuta:
```bash
python manage.py createsuperuser
```

---

## Opción 2: Creación manual

Si prefieres crear los servicios uno por uno:

### 1. Crear base de datos PostgreSQL

1. **New** → **PostgreSQL**
2. Nombre: `ubapp-db`
3. Plan: Free
4. Crear y anotar la **Internal Database URL**

### 2. Crear Redis (Key Value)

1. **New** → **Key Value**
2. Nombre: `ubapp-redis`
3. Plan: Free
4. Anotar **Internal Redis URL** (host y puerto)

### 3. Crear Web Service (Backend)

1. **New** → **Web Service**
2. Conecta tu repositorio
3. Configuración:
   - **Name**: ubapp-backend
   - **Region**: Oregon (o la más cercana)
   - **Branch**: main
   - **Root Directory**: (vacío)
   - **Runtime**: Docker
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Docker Context**: `backend`

4. **Environment Variables**:
   - `DATABASE_URL`: (desde el PostgreSQL creado)
   - `REDIS_HOST`: (desde Key Value)
   - `REDIS_PORT`: (desde Key Value)
   - `SECRET_KEY`: (generar una segura)
   - `DEBUG`: false
   - `OPENAI_API_KEY`: (tu clave)
   - `ALLOWED_HOSTS`: `.onrender.com,localhost`
   - `CORS_ALLOWED_ORIGINS`: `https://tu-frontend.onrender.com`

5. **Build Command**: (vacío, usa Dockerfile)
6. **Start Command**: (definido en Dockerfile o override)

### 4. Crear Web Service (Frontend)

1. **New** → **Web Service**
2. Mismo repositorio
3. Configuración:
   - **Name**: ubapp-frontend
   - **Runtime**: Docker
   - **Dockerfile Path**: `frontend/Dockerfile.render`
   - **Docker Context**: `frontend`

4. **Environment Variables**:
   - `API_URL`: `https://ubapp-backend-xxxx.onrender.com/api`

---

## Estructura de archivos para Render

```
App/
├── render.yaml              # Blueprint de Render
├── backend/
│   ├── Dockerfile           # Usado por Render
│   └── ...
├── frontend/
│   ├── Dockerfile.render    # Dockerfile específico para Render
│   ├── scripts/
│   │   └── set-api-url.js   # Inyecta API_URL en el build
│   └── ...
└── docs/
    └── DESPLIEGUE_RENDER.md # Esta guía
```

---

## Consideraciones importantes

### Plan Free

- **Backend**: Se "duerme" después de 15 min de inactividad. La primera petición puede tardar ~30-50 segundos.
- **Frontend**: Siempre activo.
- **PostgreSQL**: 1 GB de almacenamiento, datos persistentes.
- **Redis**: Sin persistencia en plan free (los datos se pierden al reiniciar).

### Puerto

Render usa el puerto **10000** por defecto. El `dockerCommand` en `render.yaml` usa la variable `PORT` que Render inyecta automáticamente.

### CORS

El backend permite orígenes `*.onrender.com` automáticamente cuando detecta un origen de Render en `CORS_ALLOWED_ORIGINS`.

### pgvector

La extensión pgvector debe habilitarse manualmente en la base de datos de Render para la búsqueda semántica.

---

## Solución de problemas

### El backend no arranca

- Revisa los logs en el Dashboard
- Verifica que `DATABASE_URL` esté correcta
- Verifica que `REDIS_HOST` y `REDIS_PORT` apunten al Key Value

### El frontend no conecta con el backend

- Verifica que `API_URL` en el frontend sea la URL correcta del backend (con `/api` al final)
- Haz un **Manual Deploy** del frontend después de cambiar `API_URL`

### Error de CORS

- Asegúrate de que la URL del frontend esté en `CORS_ALLOWED_ORIGINS` del backend
- El backend usa regex para permitir `*.onrender.com`

### Migraciones fallan

- Conecta al Shell del backend y ejecuta: `python manage.py migrate`
- Verifica que la extensión pgvector esté habilitada en PostgreSQL

---

## Enlaces útiles

- [Documentación de Render](https://render.com/docs)
- [Render Blueprint Spec](https://render.com/docs/blueprint-spec)
- [Render PostgreSQL](https://render.com/docs/postgresql)
- [Render Key Value (Redis)](https://render.com/docs/key-value)

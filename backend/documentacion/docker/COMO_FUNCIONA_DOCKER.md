# 🐳 Cómo Funciona Docker - Guía Completa

## 🎯 ¿Qué es Docker?

Docker es como una "mini-máquina virtual" muy ligera que contiene todo lo necesario para ejecutar una aplicación de forma aislada.

### Analogía Simple

Imagina que Docker es como **cajas de plástico apilables**:
- Cada caja contiene una aplicación completa (PostgreSQL, Redis, Django, Angular...)
- Las cajas están **aisladas** entre sí y de tu computadora
- Pero pueden **comunicarse** entre ellas por una red interna
- Se conectan al exterior por **puertas específicas** (puertos)
- Si rompes algo dentro de una caja, las demás siguen funcionando

---

## 🏗️ Arquitectura Actual del Sistema (docker-compose.yml)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TU COMPUTADORA (Windows)                             │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                        Docker Desktop                                   │ │
│  │                                                                         │ │
│  │  ┌─────────────────── Red: ubapp_network ───────────────────────────┐  │ │
│  │  │                                                                   │  │ │
│  │  │  ┌─────────────────┐    ┌─────────────────┐                      │  │ │
│  │  │  │ ubapp_postgres  │    │   ubapp_redis   │                      │  │ │
│  │  │  │ PostgreSQL +    │    │   Redis 7       │                      │  │ │
│  │  │  │ pgvector        │    │   Cache/Sesiones│                      │  │ │
│  │  │  │ Puerto: 5432    │    │   Puerto: 6379  │◄──────┐              │  │ │
│  │  │  └────────┬────────┘    └────────┬────────┘       │              │  │ │
│  │  │           │                      │                │              │  │ │
│  │  │           └──────────┬───────────┘                │              │  │ │
│  │  │                      ▼                            │              │  │ │
│  │  │           ┌─────────────────────┐                 │              │  │ │
│  │  │           │   ubapp_backend     │                 │              │  │ │
│  │  │           │   Django + Gunicorn │                 │              │  │ │
│  │  │           │   Puerto: 8000      │─────────────────┘              │  │ │
│  │  │           └──────────┬──────────┘                                │  │ │
│  │  │                      │                                           │  │ │
│  │  │                      ▼                                           │  │ │
│  │  │           ┌─────────────────────┐                                │  │ │
│  │  │           │   ubapp_frontend    │                                │  │ │
│  │  │           │   Angular + Nginx   │                                │  │ │
│  │  │           │   Puerto: 80        │                                │  │ │
│  │  │           └─────────────────────┘                                │  │ │
│  │  │                                                                   │  │ │
│  │  └───────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                         │ │
│  │  Puertos mapeados a tu PC:                                              │ │
│  │    • localhost:8000  → ubapp_backend:8000                               │ │
│  │    • localhost:4200  → ubapp_frontend:80                                │ │
│  │    • localhost:6379  → ubapp_redis:6379                                 │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  Tu navegador accede a:                                                      │
│    • http://localhost:4200 (Frontend Angular)                                │
│    • http://localhost:8000/api/ (Backend Django)                             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Los 5 Contenedores del Proyecto

### 1. ubapp_postgres (Base de Datos)

| Propiedad | Valor |
|-----------|-------|
| **Imagen** | `ankane/pgvector:latest` |
| **Puerto interno** | 5432 |
| **Puerto externo** | Ninguno (solo accesible desde otros contenedores) |
| **Volumen** | `postgres_data` (datos persistentes) |
| **Healthcheck** | `pg_isready` cada 10 segundos |

**Características:**
- PostgreSQL con extensión **pgvector** para embeddings/IA
- Los datos se guardan en el volumen `postgres_data` (no se pierden al reiniciar)
- Solo el backend puede conectarse (seguridad)

**Acceder desde Windows:**
```powershell
docker exec -it ubapp_postgres psql -U postgres -d UBAppDB
```

---

### 2. ubapp_redis (Cache y Sesiones)

| Propiedad | Valor |
|-----------|-------|
| **Imagen** | `redis:7-alpine` |
| **Puerto interno** | 6379 |
| **Puerto externo** | 6379 |
| **Volumen** | `redis_data` (datos persistentes) |
| **Contraseña** | Definida en `.env` como `REDIS_PASSWORD` |

**Características:**
- Cache para acelerar respuestas
- Almacena sesiones de usuarios
- Persistencia activada (`appendonly yes`)

---

### 3. ubapp_backend (API Django)

| Propiedad | Valor |
|-----------|-------|
| **Build desde** | `./backend/Dockerfile` |
| **Puerto interno** | 8000 |
| **Puerto externo** | 8000 |
| **Servidor** | Gunicorn (3 workers) |
| **Volúmenes** | Código, static, media, logs |

**Al iniciar ejecuta:**
1. Espera a que PostgreSQL esté listo
2. Renombra tablas de backup si es necesario
3. Ejecuta migraciones (`migrate`)
4. Recolecta archivos estáticos (`collectstatic`)
5. Inicia Gunicorn

**Variables de entorno importantes:**
- `DATABASE_URL`: Conexión a postgres (usa nombre del servicio, no localhost)
- `REDIS_URL`: Conexión a redis
- `SECRET_KEY`, `OPENAI_API_KEY`: Desde `.env`

---

### 4. ubapp_frontend (Angular + Nginx)

| Propiedad | Valor |
|-----------|-------|
| **Build desde** | `./frontend/Dockerfile` |
| **Puerto interno** | 80 (Nginx) |
| **Puerto externo** | 4200 |
| **Servidor** | Nginx sirviendo archivos estáticos |

**Proceso de build (Multi-stage):**
1. **Stage 1 (builder)**: Compila Angular con `npm run build:prod`
2. **Stage 2 (production)**: Copia archivos compilados a Nginx

---

### 5. ubapp_nginx (Solo Producción)

| Propiedad | Valor |
|-----------|-------|
| **Imagen** | `nginx:alpine` |
| **Puertos** | 80 (HTTP), 443 (HTTPS) |
| **Profile** | `production` (no se inicia por defecto) |

**Uso:**
```powershell
docker-compose --profile production up -d
```

---

## 🔄 ¿Cómo Aplicar Cambios? (MUY IMPORTANTE)

### Backend (Django) - Cambios se aplican al REINICIAR

El backend tiene un **bind mount** (tu carpeta está conectada al contenedor):

```yaml
volumes:
  - ./backend:/app  # Tu código está montado directamente
```

**Para aplicar cambios en el backend:**
```powershell
docker-compose restart backend
```

**¿Por qué funciona?** Gunicorn se reinicia y carga el código nuevo desde `/app`, que es tu carpeta `./backend`.

---

### Frontend (Angular) - Cambios requieren RECONSTRUIR

El frontend NO funciona igual porque:

1. El `Dockerfile` hace `npm run build:prod` durante el build
2. Los archivos compilados se copian a `/usr/share/nginx/html`
3. Nginx sirve esos archivos **ya compilados**, no tu código fuente

**El volumen `./frontend:/app` NO afecta** porque Nginx no mira `/app`.

**Para aplicar cambios en el frontend:**
```powershell
# Opción 1: Reconstruir solo el frontend
docker-compose build frontend
docker-compose up -d frontend

# Opción 2: En un solo comando
docker-compose up -d --build frontend

# Opción 3: Reconstruir todo (más lento)
docker-compose up -d --build
```

---

### Resumen de Comandos para Cambios

| Cambio en... | Comando |
|--------------|---------|
| **Backend (Python/Django)** | `docker-compose restart backend` |
| **Frontend (Angular)** | `docker-compose up -d --build frontend` |
| **docker-compose.yml** | `docker-compose up -d` |
| **.env** | `docker-compose up -d` (recrea contenedores) |
| **Dockerfile del backend** | `docker-compose up -d --build backend` |
| **Dockerfile del frontend** | `docker-compose up -d --build frontend` |
| **Base de datos (migraciones)** | `docker-compose exec backend python manage.py migrate` |

---

## 🔑 Conceptos Clave de Docker

### 1. Imagen vs Contenedor

| Concepto | Descripción | Analogía |
|----------|-------------|----------|
| **Imagen** | Plantilla/receta con todo lo necesario | Receta de cocina |
| **Contenedor** | Instancia en ejecución de una imagen | El plato servido |

Puedes crear múltiples contenedores desde la misma imagen.

### 2. Volúmenes (Persistencia de Datos)

Los volúmenes guardan datos que **sobreviven** cuando el contenedor se elimina.

**Tipos de volúmenes en tu proyecto:**

| Tipo | Ejemplo | Uso |
|------|---------|-----|
| **Volumen con nombre** | `postgres_data:/var/lib/postgresql/data` | Datos de la BD (Docker los gestiona) |
| **Bind mount** | `./backend:/app` | Tu código conectado al contenedor |
| **Volumen anónimo** | `/app/node_modules` | Evita que tu carpeta sobrescriba node_modules |

**Volúmenes del proyecto:**
```yaml
volumes:
  postgres_data:    # Datos de PostgreSQL
  redis_data:       # Datos de Redis
  backend_static:   # Archivos estáticos de Django
  backend_media:    # Archivos subidos por usuarios
  backend_logs:     # Logs de la aplicación
```

### 3. Redes (Comunicación entre Contenedores)

Todos los contenedores están en la red `ubapp_network`:

```yaml
networks:
  ubapp_network:
    driver: bridge
```

**Dentro de la red Docker**, los contenedores se llaman por nombre de servicio:
- El backend se conecta a `postgres:5432` (no `localhost`)
- El backend se conecta a `redis:6379` (no `localhost`)

**Desde tu PC (fuera de Docker)**:
- Usas `localhost:8000` para el backend
- Usas `localhost:4200` para el frontend

### 4. Healthchecks (Verificación de Salud)

Docker verifica periódicamente que los servicios estén funcionando:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s    # Cada 10 segundos
  timeout: 5s      # Espera máximo 5 segundos
  retries: 5       # Intenta 5 veces antes de marcar como unhealthy
```

**Estados posibles:**
- `healthy`: Todo funciona
- `unhealthy`: El servicio tiene problemas
- `starting`: Aún iniciando

### 5. depends_on (Orden de Inicio)

Define qué servicios deben iniciar primero:

```yaml
backend:
  depends_on:
    postgres:
      condition: service_healthy  # Espera a que postgres esté healthy
    redis:
      condition: service_healthy  # Espera a que redis esté healthy
```

**Orden de inicio:** postgres → redis → backend → frontend

---

## 🛠️ Comandos Esenciales de Docker Compose

### Gestión de Contenedores

```powershell
# Ver estado de todos los contenedores
docker-compose ps

# Levantar todo en segundo plano
docker-compose up -d

# Levantar y reconstruir imágenes
docker-compose up -d --build

# Detener todo (contenedores siguen existiendo)
docker-compose stop

# Detener y eliminar contenedores (datos en volúmenes persisten)
docker-compose down

# Detener, eliminar contenedores Y volúmenes (PIERDES DATOS)
docker-compose down -v
```

### Logs (Ver qué está pasando)

```powershell
# Ver logs de todos los servicios
docker-compose logs

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs backend
docker-compose logs -f frontend

# Ver últimas 100 líneas
docker-compose logs --tail=100 backend
```

### Ejecutar Comandos dentro de Contenedores

```powershell
# Ejecutar comando en el backend
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py shell

# Acceder a la terminal del backend
docker-compose exec backend bash

# Acceder a PostgreSQL
docker-compose exec postgres psql -U postgres -d UBAppDB

# Acceder a Redis
docker-compose exec redis redis-cli -a redis_password
```

### Reconstruir Imágenes

```powershell
# Reconstruir una imagen específica
docker-compose build frontend
docker-compose build backend

# Reconstruir sin usar cache (desde cero)
docker-compose build --no-cache frontend

# Reconstruir e iniciar
docker-compose up -d --build frontend
```

---

## ⚡ Flujo de Trabajo Diario

### Al Iniciar tu Día

```powershell
# 1. Verificar que Docker Desktop esté corriendo (ícono en bandeja)

# 2. Levantar todos los servicios
docker-compose up -d

# 3. Verificar que todo esté healthy
docker-compose ps

# 4. Ver logs si algo falla
docker-compose logs -f
```

### Cuando Haces Cambios en el Backend

```powershell
# 1. Guarda tus cambios en el código

# 2. Reinicia el backend
docker-compose restart backend

# 3. Verifica que reinició bien
docker-compose logs -f backend
```

### Cuando Haces Cambios en el Frontend

```powershell
# 1. Guarda tus cambios en el código

# 2. Reconstruye el frontend
docker-compose up -d --build frontend

# 3. Espera a que termine (puede tardar 1-2 minutos)
docker-compose logs -f frontend

# 4. Refresca el navegador (Ctrl+F5 para limpiar cache)
```

### Al Terminar tu Día

```powershell
# Opción 1: Dejar corriendo (recomendado, consume pocos recursos)
# No hacer nada

# Opción 2: Detener para liberar RAM
docker-compose stop

# Opción 3: Detener y eliminar contenedores (datos persisten)
docker-compose down
```

---

## 🔧 Solución de Problemas Comunes

### Problema: Cambios en el frontend no se ven

**Causa:** Nginx sirve archivos compilados, no tu código fuente.

**Solución:**
```powershell
docker-compose up -d --build frontend
# Luego Ctrl+F5 en el navegador para limpiar cache
```

### Problema: El backend no inicia

**Diagnóstico:**
```powershell
docker-compose logs backend
```

**Causas comunes:**
- PostgreSQL no está listo → Espera unos segundos más
- Error en migraciones → Revisa el código de las migraciones
- Falta variable de entorno → Revisa el archivo `.env`

### Problema: "Cannot connect to the Docker daemon"

**Causa:** Docker Desktop no está corriendo.

**Solución:** Inicia Docker Desktop desde el menú de Windows.

### Problema: Puerto ya en uso

```powershell
# Ver qué usa el puerto 8000
netstat -ano | findstr :8000

# Cambiar el puerto en .env
BACKEND_PORT=8001
```

### Problema: Contenedor se reinicia constantemente

```powershell
# Ver por qué falla
docker-compose logs backend

# Errores comunes:
# - Falta SECRET_KEY en .env
# - Error de conexión a la base de datos
# - Error de sintaxis en el código
```

### Problema: Base de datos no tiene datos

```powershell
# Ejecutar migraciones
docker-compose exec backend python manage.py migrate

# Cargar datos iniciales (si tienes fixtures)
docker-compose exec backend python manage.py loaddata datos_iniciales.json
```

---

## 📝 Resumen Final

| Concepto | Descripción |
|----------|-------------|
| **docker-compose.yml** | Define todos los servicios, redes y volúmenes |
| **Contenedor** | Instancia en ejecución (ubapp_backend, ubapp_frontend...) |
| **Imagen** | Plantilla para crear contenedores |
| **Volumen** | Almacenamiento persistente de datos |
| **Red** | Permite comunicación entre contenedores |
| **Healthcheck** | Verifica que un servicio esté funcionando |
| **Bind mount** | Conecta tu carpeta local al contenedor |
| **Build** | Proceso de crear una imagen desde un Dockerfile |

### Regla de Oro para Cambios

| Tipo de cambio | Comando |
|----------------|---------|
| Backend (Python) | `docker-compose restart backend` |
| Frontend (Angular) | `docker-compose up -d --build frontend` |
| Configuración (docker-compose.yml, .env) | `docker-compose up -d` |
| Dockerfile | `docker-compose up -d --build [servicio]` |

---

## 🚀 Tips Avanzados

### Ver uso de recursos

```powershell
docker stats
```

### Limpiar imágenes no usadas

```powershell
docker image prune
docker system prune  # Limpia todo lo no usado
```

### Ejecutar solo algunos servicios

```powershell
# Solo backend y sus dependencias
docker-compose up -d backend

# Esto levanta: postgres → redis → backend
```

### Escalar servicios (múltiples instancias)

```powershell
# 3 instancias del backend (requiere configuración adicional)
docker-compose up -d --scale backend=3
```

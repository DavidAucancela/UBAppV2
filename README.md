# UBApp — Sistema de Gestión de Envíos

> Sistema integral de gestión de envíos con **búsqueda semántica impulsada por IA**, visualización geográfica y generación de documentos. Construido con Django (backend) y Angular (frontend), orquestado con Docker Compose.

---

## Tabla de Contenidos

- [Inicio Rápido](#-inicio-rápido)
- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Tecnologías](#-tecnologías)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Variables de Entorno](#-variables-de-entorno)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [API](#-api)
- [Módulos](#-módulos)
- [Licencia](#-licencia)

---

## Inicio Rápido

```bash
# 1. Clonar el repositorio
git clone https://github.com/DavidAucancela/UBAppV2.git
cd UBAppV2

# 2. Configurar variables de entorno
.env.

# 3. Levantar la aplicación
docker-compose up -d

# 4. Acceder
# Frontend: http://localhost:4200
# API:      http://localhost:8000/api
# Swagger:  http://localhost:8000/api/docs
```

> **Importante:** El archivo `.env` contiene secretos y **no debe subirse a Git**. Usa `.env.example` como plantilla.

---

## Características

| Área | Funcionalidad |
|------|---------------|
| **Envíos** | CRUD completo de envíos, productos y tarifas |
| **Búsqueda** | Tradicional con filtros + semántica con embeddings (OpenAI + pgvector) |
| **Documentos** | Importación masiva desde Excel, generación de recibos en PDF |
| **Mapas** | Visualización geográfica de compradores con Leaflet |
| **Seguridad** | Autenticación JWT y control de acceso por roles |
| **Tiempo real** | Sistema de notificaciones para usuarios |
| **Métricas** | Panel de rendimiento y actividad del sistema |
| **Caché** | Redis para optimización de consultas |
| **API** | Documentación Swagger/OpenAPI integrada |

---

## Arquitectura

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│    Angular      │────▶│     Django       │────▶│   PostgreSQL     │
│   (Frontend)    │     │   (Backend)      │     │   + pgvector     │
│   Puerto 4200   │     │   Puerto 8000    │     │                  │
└─────────────────┘     └────────┬────────┘     └──────────────────┘
                                  │
                         ┌────────┴────────┐     ┌──────────────────┐
                         │      Redis      │     │   OpenAI API     │
                         │    (Caché)      │     │  (Embeddings)    │
                         │  Puerto 6379   │     └──────────────────┘
                         └─────────────────┘
```

**Capas del backend:**
- **Presentación** → Vistas y serializadores (DRF)
- **Lógica de negocio** → Servicios
- **Datos** → Repositorios y modelos
- **Semántica** → Motor de búsqueda con IA

---

## Tecnologías

### Backend
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.x | Lenguaje principal |
| Django | 5.2 | Framework web |
| Django REST Framework | 3.16 | API REST |
| PostgreSQL + pgvector | latest | Base de datos + búsqueda vectorial |
| Redis | 7 | Caché y sesiones |
| Gunicorn | - | Servidor WSGI (producción) |
| OpenAI API | - | Embeddings para búsqueda semántica |
| drf-spectacular | 0.27 | Documentación OpenAPI |

### Frontend
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Angular | 17.3 | Framework SPA |
| TypeScript | 5.2 | Lenguaje principal |
| Leaflet | 1.9 | Mapas interactivos |
| Chart.js | 4.5 | Gráficos |
| jsPDF | 3.0 | Generación de PDF |
| xlsx | 0.18 | Archivos Excel |

### Infraestructura
| Tecnología | Propósito |
|------------|-----------|
| Docker & Docker Compose | Contenedorización |
| Nginx | Servidor web (producción, opcional) |

---

## Requisitos

- **Docker** y **Docker Compose** (método recomendado)

O, para instalación manual:
- Python 3.10+
- Node.js 18+ y npm
- PostgreSQL 15+ con extensión pgvector
- Redis 7+

---

## Instalación

### Con Docker Compose (Recomendado)

**1. Clonar el repositorio**

```bash
git clone https://github.com/DavidAucancela/UBAppV2.git
cd UBAppV2
```

**2. Configurar variables de entorno**

Edita `.env` y configura al menos:
- `SECRET_KEY` — Genera una clave segura (ej: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `OPENAI_API_KEY` — Obtén una en [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- `DB_PASSWORD` y `REDIS_PASSWORD` — Contraseñas seguras

**3. Levantar los servicios**

```bash
# Modo desarrollo (sin Nginx)
docker-compose up -d

# Modo producción (con Nginx)
docker-compose --profile production up -d
```

**4. Acceder a la aplicación**

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:4200 |
| Backend API | http://localhost:8000/api |
| Swagger (API docs) | http://localhost:8000/api/docs |
| ReDoc (API docs) | http://localhost:8000/api/redoc |
| Admin Django | http://localhost:8000/admin |

### Instalación Manual

#### Backend

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

pip install -r requirements.txt
# Crear backend/.env con tus valores
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

#### Frontend

```bash
cd frontend
npm install
npm start
# o: ng serve --port 4200 --host 0.0.0.0
```

---

## Variables de Entorno

### Raíz (`.env` — Docker Compose)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DB_NAME` | Nombre de la base de datos | `UBAppDB` |
| `DB_USER` | Usuario PostgreSQL | `postgres` |
| `DB_PASSWORD` | Contraseña PostgreSQL | *(requerido)* |
| `DB_PORT` | Puerto PostgreSQL | `5434` |
| `REDIS_PASSWORD` | Contraseña Redis | *(requerido)* |
| `REDIS_PORT` | Puerto Redis | `6379` |
| `DEBUG` | Modo depuración | `False` |
| `SECRET_KEY` | Clave secreta Django | *(requerido)* |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1,backend` |
| `BACKEND_PORT` | Puerto del backend | `8000` |
| `FRONTEND_PORT` | Puerto del frontend | `4200` |
| `CORS_ALLOWED_ORIGINS` | Orígenes CORS | `http://localhost:4200,...` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes CSRF | `http://localhost:4200,...` |
| `OPENAI_API_KEY` | API Key de OpenAI | *(requerido para búsqueda semántica)* |
| `OPENAI_EMBEDDING_MODEL` | Modelo de embeddings | `text-embedding-3-small` |
| `OPENAI_EMBEDDING_DIMENSIONS` | Dimensiones | `1536` |
| `API_URL` | URL del backend (para frontend) | `http://backend:8000` |

### Backend (`backend/.env` — instalación manual)

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Clave secreta Django |
| `DEBUG` | Modo depuración |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Conexión PostgreSQL |
| `OPENAI_API_KEY` | API Key de OpenAI |

---

## Uso

### Comandos Docker útiles

```bash
# Ver logs
docker-compose logs -f
docker-compose logs -f backend

# Reiniciar un servicio
docker-compose restart backend

# Detener todo
docker-compose down

# Detener y eliminar volúmenes (¡borra datos!)
docker-compose down -v

# Acceder a PostgreSQL
docker exec -it ubapp_postgres psql -U postgres -d UBAppDB

# Comandos Django
docker exec -it ubapp_backend python manage.py migrate
docker exec -it ubapp_backend python manage.py createsuperuser
docker exec -it ubapp_backend python manage.py collectstatic
```

### Scripts del Frontend

```bash
npm start          # Servidor de desarrollo (puerto 4200)
npm run build      # Compilar aplicación
npm run build:prod # Compilar para producción
npm test           # Ejecutar tests
npm run lint       # Verificar estilo
npm run lint:fix   # Corregir estilo
```

---

## Estructura del Proyecto

```
UBAppV2/
├── docker-compose.yml      # Orquestación de servicios
├── .env 
├── README.md
│
├── backend/                 # API Django REST
│   ├── apps/
│   │   ├── core/           # Utilidades base, paginación, excepciones
│   │   ├── usuarios/       # Usuarios y autenticación
│   │   ├── archivos/       # Envíos y productos
│   │   ├── busqueda/       # Búsqueda tradicional y semántica
│   │   ├── notificaciones/
│   │   └── metricas/
│   ├── settings.py
│   ├── urls.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/               # SPA Angular
│   ├── src/app/
│   │   ├── components/
│   │   ├── services/
│   │   ├── models/
│   │   ├── guards/
│   │   └── interceptors/
│   ├── angular.json
│   ├── package.json
│   └── Dockerfile
│
├── media/                  # Archivos multimedia
├── logs/                   # Logs
└── docs/                   # Documentación adicional
```

---

## API

La API REST está documentada con OpenAPI/Swagger.

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

---

## Módulos

### Backend

| Módulo | Descripción |
|--------|-------------|
| **core** | Clases base, paginación, excepciones, throttling |
| **usuarios** | Usuario personalizado, JWT, perfiles, permisos por rol |
| **archivos** | CRUD envíos/productos, tarifas, PDF, importación Excel |
| **busqueda** | Búsqueda tradicional, semántica (OpenAI + pgvector), métricas |
| **notificaciones** | Sistema de notificaciones por usuario |
| **metricas** | Monitoreo, evaluación, actividad |

### Frontend

| Módulo | Descripción |
|--------|-------------|
| **Autenticación** | Login, JWT, guards |
| **Envíos** | CRUD de envíos y productos |
| **Búsqueda** | Tradicional y semántica |
| **Importación/Exportación** | Excel, PDF |
| **Mapas** | Visualización geográfica (Leaflet) |
| **Dashboard** | Métricas y gráficos |
| **Tarifas** | Gestión de tarifas |
| **Administración** | Gestión de usuarios |

---

## Licencia

Este proyecto es de uso privado.

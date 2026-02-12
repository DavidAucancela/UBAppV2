# UBApp - Sistema de Gestión de Envíos

Sistema integral de gestión de envíos con búsqueda semántica impulsada por IA, visualización geográfica y generación de documentos. Construido con **Django** (backend) y **Angular** (frontend), orquestado con **Docker Compose**.

---

## Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Tecnologías](#tecnologías)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
  - [Con Docker Compose (Recomendado)](#con-docker-compose-recomendado)
  - [Instalación Manual](#instalación-manual)
- [Variables de Entorno](#variables-de-entorno)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [API](#api)
- [Módulos](#módulos)

---

## Características

- **Gestión de envíos**: CRUD completo de envíos, productos y tarifas
- **Búsqueda avanzada**: Búsqueda tradicional y semántica con embeddings de OpenAI y pgvector
- **Importación/Exportación**: Carga masiva desde Excel y generación de recibos en PDF
- **Visualización geográfica**: Mapas interactivos con ubicaciones de compradores (Leaflet)
- **Autenticación JWT**: Control de acceso basado en roles
- **Notificaciones en tiempo real**: Sistema de notificaciones para usuarios
- **Métricas y monitoreo**: Panel de rendimiento y actividad del sistema
- **Caché con Redis**: Optimización de consultas y respuestas
- **Documentación API**: Swagger/OpenAPI integrada

---

## Arquitectura

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Angular    │────▶│   Django     │────▶│  PostgreSQL   │
│  (Frontend)  │     │  (Backend)   │     │  + pgvector   │
│  Puerto 4200 │     │  Puerto 8000 │     │               │
└─────────────┘     └──────┬──────┘     └──────────────┘
                           │
                    ┌──────┴──────┐     ┌──────────────┐
                    │    Redis     │     │   OpenAI API  │
                    │   (Caché)    │     │  (Embeddings) │
                    │  Puerto 6379 │     └──────────────┘
                    └─────────────┘
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
|---|---|---|
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
|---|---|---|
| Angular | 17.3 | Framework SPA |
| TypeScript | 5.2 | Lenguaje principal |
| Leaflet | 1.9 | Mapas interactivos |
| Chart.js | 4.5 | Gráficos y visualizaciones |
| jsPDF | 3.0 | Generación de PDF |
| xlsx | 0.18 | Manejo de archivos Excel |

### Infraestructura
| Tecnología | Propósito |
|---|---|
| Docker & Docker Compose | Contenedorización |
| Nginx | Servidor web (producción) |

---

## Requisitos Previos

- **Docker** y **Docker Compose** instalados (método recomendado)
- O bien, para instalación manual:
  - Python 3.10+
  - Node.js 18+ y npm
  - PostgreSQL 15+ con extensión pgvector
  - Redis 7+

---

## Instalación

### Con Docker Compose (Recomendado)

1. **Clonar el repositorio:**

```bash
git clone <url-del-repositorio>
cd App
```

2. **Configurar variables de entorno:**

```bash
# Copiar y editar el archivo .env en la raíz
cp .env.example .env
# Editar con tus valores (ver sección Variables de Entorno)
```

3. **Levantar los servicios:**

```bash
# Modo desarrollo (sin Nginx)
docker-compose up -d

# Modo producción (con Nginx)
docker-compose --profile production up -d
```

4. **Acceder a la aplicación:**

| Servicio | URL |
|---|---|
| Frontend | http://localhost:4200 |
| Backend API | http://localhost:8000/api |
| Documentación API (Swagger) | http://localhost:8000/api/docs |
| Documentación API (ReDoc) | http://localhost:8000/api/redoc |
| Admin Django | http://localhost:8000/admin |

### Instalación Manual

#### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Editar backend/.env con tus valores

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor de desarrollo
python manage.py runserver
```

#### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start
# o
ng serve --port 4200 --host 0.0.0.0

# Construir para producción
npm run build:prod
```

---

## Variables de Entorno

### Raíz (`.env` - Docker Compose)

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `DB_NAME` | Nombre de la base de datos | `UBAppDB` |
| `DB_USER` | Usuario de PostgreSQL | `postgres` |
| `DB_PASSWORD` | Contraseña de PostgreSQL | - |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |
| `REDIS_PASSWORD` | Contraseña de Redis | - |
| `REDIS_PORT` | Puerto de Redis | `6379` |
| `DEBUG` | Modo depuración | `False` |
| `SECRET_KEY` | Clave secreta de Django | - |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `BACKEND_PORT` | Puerto del backend | `8000` |
| `FRONTEND_PORT` | Puerto del frontend | `4200` |
| `CORS_ALLOWED_ORIGINS` | Orígenes CORS permitidos | - |
| `CSRF_TRUSTED_ORIGINS` | Orígenes CSRF confiables | - |
| `OPENAI_API_KEY` | Clave API de OpenAI | - |
| `OPENAI_EMBEDDING_MODEL` | Modelo de embeddings | `text-embedding-3-small` |
| `OPENAI_EMBEDDING_DIMENSIONS` | Dimensiones del embedding | `1536` |
| `API_URL` | URL del backend para el frontend | `http://backend:8000` |
| `NGINX_PORT` | Puerto HTTP de Nginx | `80` |
| `NGINX_HTTPS_PORT` | Puerto HTTPS de Nginx | `443` |

### Backend (`backend/.env`)

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `SECRET_KEY` | Clave secreta de Django | - |
| `DEBUG` | Modo depuración | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos | `*` |
| `DB_HOST` | Host de PostgreSQL | `localhost` |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |
| `DB_NAME` | Nombre de la base de datos | `UBAppDB` |
| `DB_USER` | Usuario de PostgreSQL | `postgres` |
| `DB_PASSWORD` | Contraseña de PostgreSQL | - |
| `OPENAI_API_KEY` | Clave API de OpenAI | - |
| `LOG_LEVEL` | Nivel de logging | `INFO` |

---

## Uso

### Comandos Docker útiles

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend

# Reiniciar un servicio
docker-compose restart backend

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (¡borra datos!)
docker-compose down -v

# Acceder a la base de datos
docker exec -it ubapp_postgres psql -U postgres -d UBAppDB

# Ejecutar comandos Django
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
npm run lint       # Verificar estilo de código
npm run lint:fix   # Corregir errores de estilo
```

---

## Estructura del Proyecto

```
App/
├── docker-compose.yml          # Orquestación de servicios
├── .env                        # Variables de entorno (Docker)
├── README.md                   # Este archivo
│
├── backend/                    # API Django REST
│   ├── apps/
│   │   ├── core/               # Utilidades base, paginación, excepciones
│   │   ├── usuarios/           # Gestión de usuarios y autenticación
│   │   ├── archivos/           # Gestión de envíos y productos
│   │   ├── busqueda/           # Búsqueda tradicional y semántica
│   │   ├── notificaciones/     # Sistema de notificaciones
│   │   └── metricas/           # Métricas y monitoreo
│   ├── settings.py             # Configuración de Django
│   ├── urls.py                 # Enrutamiento principal
│   ├── requirements.txt        # Dependencias Python
│   ├── Dockerfile              # Imagen Docker del backend
│   └── documentacion/          # Documentación técnica
│
├── frontend/                   # SPA Angular
│   ├── src/app/
│   │   ├── components/         # Componentes Angular
│   │   ├── services/           # Servicios (API, auth, búsqueda)
│   │   ├── models/             # Interfaces TypeScript
│   │   ├── guards/             # Guards de autenticación y roles
│   │   └── interceptors/       # Interceptores HTTP
│   ├── angular.json            # Configuración Angular CLI
│   ├── package.json            # Dependencias Node.js
│   ├── Dockerfile              # Imagen Docker del frontend
│   └── documentacion/          # Documentación del frontend
│
├── media/                      # Archivos multimedia (Excel, PDF)
└── logs/                       # Logs de la aplicación
```

---

## API

La API REST está documentada automáticamente con OpenAPI/Swagger.

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Endpoints principales

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/token/` | Obtener token JWT |
| `POST` | `/api/token/refresh/` | Refrescar token JWT |
| `GET/POST` | `/api/archivos/` | Listar/crear envíos |
| `GET/PUT/DELETE` | `/api/archivos/{id}/` | Detalle de envío |
| `GET/POST` | `/api/usuarios/` | Listar/crear usuarios |
| `GET` | `/api/busqueda/` | Búsqueda tradicional |
| `GET` | `/api/busqueda/semantica/` | Búsqueda semántica |
| `GET` | `/api/notificaciones/` | Listar notificaciones |
| `GET` | `/api/metricas/` | Métricas del sistema |
| `GET` | `/api/health/` | Estado del servicio |

---

## Módulos

### Backend

| Módulo | Descripción |
|---|---|
| **core** | Clases base (repositorios, servicios), paginación personalizada, manejo de excepciones y throttling |
| **usuarios** | Modelo de usuario personalizado, autenticación JWT, perfiles con datos de ubicación, permisos por rol |
| **archivos** | CRUD de envíos y productos, cálculo de tarifas por categoría/peso, generación de recibos PDF, importación desde Excel |
| **busqueda** | Búsqueda tradicional con filtros, búsqueda semántica con OpenAI embeddings y pgvector, expansión de consultas, métricas de relevancia (MRR, nDCG, Precision@5) |
| **notificaciones** | Sistema de notificaciones por usuario |
| **metricas** | Monitoreo de rendimiento, evaluación de módulos, seguimiento de actividad |

### Frontend

| Módulo | Descripción |
|---|---|
| **Autenticación** | Login/logout, gestión de tokens JWT, guards de autenticación y roles |
| **Envíos** | Crear, editar y visualizar envíos con sus productos |
| **Búsqueda** | Interfaz unificada para búsqueda tradicional y semántica |
| **Importación/Exportación** | Importación masiva desde Excel, exportación a PDF |
| **Mapas** | Visualización geográfica de compradores con Leaflet |
| **Dashboard** | Paneles por usuario, métricas y gráficos con Chart.js |
| **Tarifas** | Gestión y cálculo de tarifas de envío |
| **Administración** | Gestión de usuarios (rol administrador) |

---

## Licencia

Este proyecto es de uso privado.

# REPORTE DEL SISTEMA — UBAppV2
**Fecha de generación:** 2026-03-09
**Versión del proyecto:** V2 (producción)
**Estado general:** Estable — listo para producción

---

## ÍNDICE

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Arquitectura General](#2-arquitectura-general)
3. [Stack Tecnológico](#3-stack-tecnológico)
4. [Módulos del Sistema](#4-módulos-del-sistema)
5. [Esquema de Base de Datos](#5-esquema-de-base-de-datos)
6. [API REST — Endpoints](#6-api-rest--endpoints)
7. [Seguridad](#7-seguridad)
8. [Rendimiento y Optimizaciones](#8-rendimiento-y-optimizaciones)
9. [Despliegue e Infraestructura](#9-despliegue-e-infraestructura)
10. [Cobertura de Pruebas](#10-cobertura-de-pruebas)
11. [Métricas del Código Fuente](#11-métricas-del-código-fuente)
12. [Estado Actual del Proyecto](#12-estado-actual-del-proyecto)
13. [Historial de Cambios Recientes](#13-historial-de-cambios-recientes)
14. [Riesgos y Recomendaciones](#14-riesgos-y-recomendaciones)

---

## 1. RESUMEN EJECUTIVO

**UBAppV2** es una plataforma web de gestión de envíos y encomiendas diseñada para operadoras de logística. El sistema permite registrar, rastrear y buscar envíos de forma eficiente, integrando búsqueda semántica con inteligencia artificial (OpenAI Embeddings + pgvector) y búsqueda tradicional por filtros.

### Capacidades principales

| Funcionalidad | Estado |
|---|---|
| Gestión CRUD de envíos y productos | Activo |
| Importación masiva desde Excel | Activo |
| Búsqueda tradicional con filtros avanzados | Activo |
| Búsqueda semántica con IA (OpenAI + pgvector) | Activo |
| Notificaciones en tiempo real | Activo |
| Exportación de reportes (PDF y Excel) | Activo |
| Mapa geográfico de compradores (Leaflet) | Activo |
| Panel de métricas y rendimiento | Activo |
| Gestión de tarifas por categoría y peso | Activo |
| Control de acceso basado en roles (RBAC) | Activo |
| Documentación API automática (Swagger/ReDoc) | Activo |
| Despliegue en Render.com | Activo |

---

## 2. ARQUITECTURA GENERAL

El proyecto sigue una arquitectura **monorepo** con separación clara entre frontend y backend, desplegados como contenedores Docker independientes.

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE                              │
│               Angular 17 SPA (Nginx)                        │
│         Puerto: 4200 (dev) / 80 (producción)                │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST + JWT
┌─────────────────────────▼───────────────────────────────────┐
│                    BACKEND API                              │
│             Django 5.2 + DRF (Gunicorn)                     │
│                    Puerto: 8000                              │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ usuarios │ │ archivos │ │ busqueda │ │notificac.│      │
│  └──────────┘ └──────────┘ └────┬─────┘ └──────────┘      │
│                                 │                           │
│  ┌──────────┐ ┌──────────┐      │ OpenAI API               │
│  │ metricas │ │  core    │      │ (embeddings)              │
│  └──────────┘ └──────────┘      │                          │
└──────────┬──────────────────────┼──────────────────────────┘
           │                      │
┌──────────▼──────┐    ┌──────────▼──────────┐
│   PostgreSQL    │    │        Redis         │
│  + pgvector     │    │  (caché + sesiones)  │
│   Puerto: 5432  │    │    Puerto: 6379      │
└─────────────────┘    └─────────────────────┘
```

### Patrón de capas del backend

```
Presentación   →  Views (DRF ViewSets)
               →  Serializers (validación + serialización)
Negocio        →  Services (lógica de negocio)
Datos          →  Models (ORM Django)
Vectorial      →  OpenAI Embeddings + pgvector (búsqueda semántica)
```

---

## 3. STACK TECNOLÓGICO

### Backend

| Componente | Tecnología | Versión | Función |
|---|---|---|---|
| Lenguaje | Python | 3.11 | Lenguaje base |
| Framework web | Django | 5.2 | Framework MVC |
| API REST | Django REST Framework | 3.16 | Endpoints REST |
| Base de datos | PostgreSQL + pgvector | latest / 0.2.5 | Almacenamiento relacional + vectores |
| Caché | Redis | 7 (alpine) | Caché de consultas y sesiones |
| Autenticación | JWT (SimpleJWT) | 5.3.1 | Tokens de acceso |
| Servidor WSGI | Gunicorn | latest | Servidor de producción |
| IA / Embeddings | OpenAI API | 2.8.0+ | Búsqueda semántica |
| Documentación API | drf-spectacular | 0.27 | Swagger / ReDoc / OpenAPI 3.0 |
| Exportación PDF | ReportLab | latest | Generación de PDF |
| Importación Excel | openpyxl + pandas | latest | Lectura y procesamiento de Excel |
| Visualización | scikit-learn, plotly, umap-learn | latest | Análisis y visualización de métricas |

### Frontend

| Componente | Tecnología | Versión | Función |
|---|---|---|---|
| Framework | Angular | 17.3 | SPA framework |
| Lenguaje | TypeScript | 5.2 | JavaScript tipado |
| Mapas | Leaflet | 1.9 | Visualización geográfica |
| Gráficas | Chart.js | 4.5 | Visualización de datos |
| Exportación PDF | jsPDF | 3.0 | PDF del lado cliente |
| Excel | xlsx | 0.18 | Manejo de archivos Excel |
| Estilos | CSS3 | Nativo | Estilos por componente |
| Build | Angular CLI | 17 | Compilación y desarrollo |
| Servidor prod | Nginx | alpine | Proxy inverso + archivos estáticos |

### Infraestructura

| Componente | Tecnología |
|---|---|
| Contenedores | Docker + Docker Compose |
| Despliegue cloud | Render.com (blueprint automatizado) |
| Red interna | Bridge network `ubapp_network` |
| Health checks | Configurados en todos los servicios |
| Logs | JSON + rotación de archivos |

---

## 4. MÓDULOS DEL SISTEMA

### 4.1 `apps/core` — Núcleo del sistema

Proporciona la infraestructura base compartida por el resto de módulos.

- Paginación personalizada (`CustomPageNumberPagination`, 10 ítems/página)
- Manejo centralizado de excepciones y respuestas HTTP
- Throttling y rate limiting por tipo de operación
- Endpoint de health check (`GET /api/health/`)
- Clase base de servicio (`BaseService`)

### 4.2 `apps/usuarios` — Gestión de usuarios

Sistema completo de autenticación y gestión de usuarios con control de acceso por roles.

**Roles del sistema:**

| Rol | Valor | Permisos |
|---|---|---|
| Administrador | 1 | Acceso total al sistema |
| Gerente | 2 | Gestión de envíos, reportes y tarifas |
| Operador de datos | 3 | Registro y edición de envíos |
| Comprador | 4 | Visualización de propios envíos |

**Características:**
- Modelo de usuario personalizado (`AbstractUser`)
- Atributos adicionales: cédula (único), teléfono, rol, cupo anual de peso (kg)
- Localización geográfica: Provincia / Cantón / Ciudad
- Estadísticas de actividad por usuario
- JWT: tokens de acceso (60 min) y refresh (1 día)

### 4.3 `apps/archivos` — Gestión de envíos y productos

Módulo principal del sistema. Gestiona el ciclo de vida completo de los envíos.

**Modelo `Envio` (Envío):**
- Identificador único HAWB
- Comprador asignado (FK → Usuario rol=4)
- Peso total, cantidad, valor total
- Costo de servicio (calculado automáticamente por tarifas)
- Estados: `pendiente` → `en_transito` → `entregado` | `cancelado`
- Índices: HAWB, (comprador, fecha_emisión), (estado, fecha_emisión)

**Modelo `Producto`:**
- Descripción, peso, cantidad, valor
- Costo de envío calculado por producto
- Categorías: `electronica`, `ropa`, `hogar`, `deportes`, `otros`
- FK → Envío (con índices en categoría)

**Modelo `Tarifa`:**
- Precio por kg + cargo base
- Segmentado por categoría y rango de peso
- Restricción: única por (categoría, peso_mínimo, peso_máximo)

**Importación Excel:**
- Proceso en 2 etapas: validación previa → selección → procesamiento
- Rastreo de registros: totales, válidos, errores, duplicados
- Estado de importación: pendiente → validando → validado → procesando → completado | error
- Errores y columnas mapeadas almacenados como JSON

### 4.4 `apps/busqueda` — Motor de búsqueda

Doble motor de búsqueda: tradicional y semántico.

**Búsqueda tradicional:**
- Filtros por: HAWB, comprador, estado, rango de fechas, categoría
- Historial de búsquedas por usuario
- Exportación de resultados a PDF/Excel

**Búsqueda semántica (IA):**
- Embeddings de envíos generados con OpenAI (1536 dimensiones)
- Almacenados en PostgreSQL con extensión pgvector
- Comparación por similitud coseno
- Caché de embeddings para evitar regeneración innecesaria
- Historial de consultas con métricas de costo (USD) y tokens usados
- Sugerencias de búsquedas populares
- Métricas de calidad: MRR, nDCG@10, Precision@5

### 4.5 `apps/notificaciones` — Sistema de notificaciones

Notificaciones por usuario con estado de lectura.

**Tipos de notificación:**
- `nuevo_envio` — Nuevo envío registrado
- `envio_asignado` — Envío asignado al comprador
- `estado_cambiado` — Cambio de estado del envío
- `general` — Notificaciones generales del sistema

**Características:**
- Marca leída/no leída con timestamp
- Metadatos JSON (envío_id, estado anterior, etc.)
- Índices: (usuario, leída), fecha_creación
- Enlace opcional de acción rápida

### 4.6 `apps/metricas` — Métricas y rendimiento

Sistema completo de evaluación del rendimiento del sistema.

**Pruebas controladas semánticas:**
- Evaluación de calidad de búsqueda semántica
- Cálculo de MRR (Mean Reciprocal Rank)
- Cálculo de nDCG@10 (Normalized Discounted Cumulative Gain)
- Cálculo de Precision@5

**Pruebas de carga:**
- Cargas concurrentes: 1, 10, 30 operaciones simultáneas
- Métricas recogidas: tiempo de respuesta, CPU, RAM
- Desglose de procesos M1-M14 (métricas detalladas por etapa)

**Dashboard de rendimiento:**
- Visualizaciones de tiempo de respuesta
- Comparativa de rendimiento semántico vs tradicional
- Logs de generación de embeddings (modelo, tiempo, tokens)

---

## 5. ESQUEMA DE BASE DE DATOS

```
usuarios
├── id (PK)
├── username, password (Django)
├── nombre, correo, cedula (UNIQUE)
├── rol (1=Admin|2=Gerente|3=Operador|4=Comprador)
├── telefono, fecha_nacimiento, direccion
├── provincia, canton, ciudad
├── cupo_anual (kg)
└── is_active, fecha_creacion, fecha_actualizacion

envio
├── id (PK)
├── hawb (UNIQUE)
├── comprador_id (FK → usuarios)
├── peso_total, cantidad_total, valor_total
├── costo_servicio (calculado)
├── estado (pendiente|en_transito|entregado|cancelado)
├── observaciones
└── fecha_emision, fecha_creacion, fecha_actualizacion

producto
├── id (PK)
├── envio_id (FK → envio)
├── descripcion, peso, cantidad, valor
├── costo_envio (calculado)
└── categoria (electronica|ropa|hogar|deportes|otros)

tarifa
├── id (PK)
├── categoria, peso_minimo, peso_maximo
├── precio_por_kg, cargo_base
└── activa (bool)

embedding_envio          [pgvector]
├── envio_id (OneToOne → envio)
├── embedding_vector (1536 dims)
├── texto_indexado
├── cosine_similarity_avg
└── fecha_generacion, modelo_usado

embedding_busqueda       [pgvector]
├── id (PK)
├── usuario_id (FK → usuarios)
├── consulta
├── embedding_vector (1536 dims)
├── resultados_encontrados, tiempo_respuesta_ms
├── costo_consulta (USD), tokens_utilizados
├── filtros_aplicados, resultados_json
└── fecha_busqueda

archivo (importacion excel)
├── id (PK)
├── usuario_id (FK → usuarios)
├── archivo (FileField), nombre_original
├── estado (pendiente|validando|validado|procesando|completado|error)
├── total_registros, registros_validos, registros_errores, registros_duplicados
├── errores_validacion (JSON), columnas_mapeadas (JSON)
├── registros_seleccionados (JSON)
└── fecha_creacion, fecha_actualizacion, fecha_completado

notificaciones
├── id (PK)
├── usuario_id (FK → usuarios)
├── tipo (nuevo_envio|envio_asignado|estado_cambiado|general)
├── titulo, mensaje
├── leida (bool), fecha_lectura
├── enlace (opcional)
├── metadata (JSON)
└── fecha_creacion

busqueda_tradicional
├── id (PK)
├── usuario_id (FK → usuarios)
├── termino_busqueda, tipo_busqueda
├── resultados_encontrados
├── resultados_json
└── fecha_busqueda

-- Tablas de métricas --
prueba_controlada_semantica  →  definición de casos de prueba semántica
metrica_semantica            →  resultados MRR, nDCG@10, Precision@5
prueba_carga                 →  definición de pruebas de carga
metrica_rendimiento          →  mediciones individuales (tiempo, CPU, RAM)
registro_generacion_embedding →  log de generación de embeddings
prueba_rendimiento_completa  →  resultados consolidados por prueba
detalle_proceso_rendimiento  →  desglose por etapa M1-M14
```

**Total de modelos:** 15+
**Extensiones PostgreSQL:** pgvector (vectores de alta dimensión)
**Índices relevantes:** HAWB, (comprador, fecha), (estado, fecha), (usuario, leída)

---

## 6. API REST — ENDPOINTS

### Autenticación

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/token/` | Obtener tokens JWT (acceso + refresh) |
| POST | `/api/token/refresh/` | Renovar token expirado |

### Usuarios

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/usuarios/` | Listar usuarios (Admin/Gerente) |
| POST | `/api/usuarios/` | Crear usuario |
| GET | `/api/usuarios/{id}/` | Detalle de usuario |
| PUT/PATCH | `/api/usuarios/{id}/` | Actualizar usuario |
| DELETE | `/api/usuarios/{id}/` | Eliminar usuario |

### Envíos y Productos

| Método | Ruta | Descripción |
|---|---|---|
| GET/POST | `/api/envios/` | Listar / Crear envíos |
| GET/PUT/DELETE | `/api/envios/{id}/` | Detalle / Editar / Eliminar envío |
| GET/POST | `/api/productos/` | Listar / Crear productos |
| GET/PUT/DELETE | `/api/productos/{id}/` | Detalle / Editar / Eliminar producto |
| GET/POST | `/api/tarifas/` | Listar / Crear tarifas |
| POST | `/api/importacion/` | Importar Excel |

### Búsqueda

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/busqueda/tradicional/` | Búsqueda por filtros |
| POST | `/api/busqueda/semantica/` | Búsqueda semántica con IA |
| GET | `/api/busqueda/historial/` | Historial de búsquedas |
| GET | `/api/busqueda/sugerencias/` | Sugerencias populares |

### Notificaciones

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/notificaciones/` | Listar notificaciones del usuario |
| PATCH | `/api/notificaciones/{id}/leer/` | Marcar como leída |

### Métricas

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/metricas/` | Dashboard de métricas generales |
| GET | `/api/metricas/semantica/` | Métricas de búsqueda semántica |
| GET | `/api/metricas/rendimiento/` | Pruebas de carga y rendimiento |

### Sistema

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/health/` | Health check del sistema |
| GET | `/api/schema/` | Schema OpenAPI 3.0 |
| GET | `/api/docs/` | Swagger UI interactivo |
| GET | `/api/redoc/` | ReDoc documentación |

**Rate Limits configurados:**

| Operación | Límite |
|---|---|
| Búsqueda semántica | 30 req/min |
| Login | 5 req/min |
| Importación Excel | Límite propio |
| Operaciones generales | Configurado por rol |

---

## 7. SEGURIDAD

### Autenticación y Autorización

- **JWT (JSON Web Tokens)** con SimpleJWT
  - Token de acceso: duración 60 minutos
  - Token de refresh: duración 1 día
  - Transmisión solo por HTTPS en producción

- **RBAC (Role-Based Access Control)**
  - 4 roles con permisos diferenciados
  - Guards en el frontend (Angular route guards)
  - Verificación de permisos en cada endpoint backend

### Protecciones HTTP

| Protección | Estado |
|---|---|
| HTTPS / HSTS | Activo en producción |
| Protección XSS | Activo (`X-XSS-Protection`) |
| Bloqueo de sniffing de tipo de contenido | Activo |
| CSRF Protection | Activo (Django CSRF middleware) |
| CORS whitelist | Configurado (incluye *.onrender.com) |

### Protección de datos

- Prevención de inyección SQL mediante el ORM de Django
- Variables de entorno para credenciales (nunca hardcodeadas)
- `.gitignore` para excluir `.env` y archivos sensibles
- Incidente de secretos en Git documentado y mitigado (ver `docs/INCIDENTE_GIT_SECRETOS.md`)

---

## 8. RENDIMIENTO Y OPTIMIZACIONES

### Caché

| Capa de caché | Uso |
|---|---|
| Redis (producción) | Consultas frecuentes, sesiones |
| LocMemCache (desarrollo) | Caché en memoria local |
| Caché de embeddings | Evita regenerar vectores existentes |

### Base de datos

- Índices en campos de búsqueda frecuente: HAWB, (comprador, fecha), (estado, fecha), (usuario, leída)
- `pgvector` con búsqueda ANN (Approximate Nearest Neighbor) para similitud coseno
- Paginación: 10 ítems por página (configurable)
- Connection pooling con PostgreSQL

### Servidor

- Gunicorn: 3 workers (local) / 1 worker (Render free tier — 512MB RAM)
- Nginx como proxy inverso en producción
- Multi-stage Docker build en frontend (reduce tamaño de imagen)

### Métricas del sistema

El módulo `metricas` mide activamente:
- **Tiempo de respuesta** por operación
- **Uso de CPU y RAM** durante pruebas de carga
- **Calidad de búsqueda semántica:** MRR, nDCG@10, Precision@5
- **Desglose por etapas M1-M14** en operaciones complejas
- **Costo de embeddings** en USD y tokens consumidos

---

## 9. DESPLIEGUE E INFRAESTRUCTURA

### Despliegue local (Docker Compose)

```bash
# Clonar repositorio y configurar .env
cp .env.example .env
# Editar .env con tus credenciales

# Iniciar todos los servicios
docker-compose up -d

# Frontend: http://localhost:4200
# Backend API: http://localhost:8000
# Swagger: http://localhost:8000/api/docs/
```

**Servicios Docker:**

| Servicio | Imagen | Puerto | Función |
|---|---|---|---|
| `db` | ankane/pgvector | 5432 (interno) | PostgreSQL + pgvector |
| `redis` | redis:7-alpine | 6379 | Caché y sesiones |
| `backend` | Dockerfile local | 8000 | API Django |
| `frontend` | Dockerfile multi-stage | 4200 | Angular + Nginx |
| `nginx` | nginx:alpine | 80/443 | Proxy (perfil producción) |

### Despliegue en Render.com

El proyecto incluye un `render.yaml` (Blueprint) que provisiona automáticamente:

- Backend service (Docker runtime, free plan)
- Frontend service (Docker runtime, free plan)
- Redis (Key-Value store, free plan)
- PostgreSQL externo recomendado (Supabase o Render)

**Variables de entorno requeridas en Render:**

```
SECRET_KEY=<generado>
DEBUG=False
ALLOWED_HOSTS=<dominio>.onrender.com
DATABASE_URL=<conexión PostgreSQL externa>
REDIS_URL=<conexión Redis Render>
OPENAI_API_KEY=<clave API OpenAI>
CORS_ALLOWED_ORIGINS=https://<frontend>.onrender.com
```

### Scripts de inicio

| Script | Función |
|---|---|
| `start_render.py` | Ejecuta migraciones y arranca Gunicorn en Render |
| `wait_for_db.py` | Espera disponibilidad de PostgreSQL |
| `rename_backup_tables.py` | Manejo de migraciones de nombre de tablas |

---

## 10. COBERTURA DE PRUEBAS

### Frontend

- **Framework:** Jasmine + Karma
- **Archivos spec:** 19 (`*.spec.ts`)
- **Componentes con tests:** Auth, Dashboard, Envíos, Búsqueda, Usuarios, Notificaciones, Perfil, Importación, Tarifas y más

### Backend

- **Framework:** Django test suite
- **Ejecución:** `python manage.py test`
- **Módulo de métricas:** Pruebas de carga y evaluación semántica integradas en el sistema

### Ejecutar pruebas

```bash
# Backend
docker-compose exec backend python manage.py test

# Frontend
cd frontend && npm test

# Frontend con cobertura
cd frontend && npm run test:coverage
```

---

## 11. MÉTRICAS DEL CÓDIGO FUENTE

| Métrica | Valor |
|---|---|
| Total de archivos fuente (sin dependencias) | 293 |
| Archivos Python (backend) | ~150 |
| Archivos TypeScript (frontend) | ~143 |
| Líneas en capa de servicios (backend) | 2,632 |
| Líneas en Views + Serializers | 3,808 |
| Líneas en Admin | 361 |
| Componentes Angular | 17 |
| Servicios Angular | 9 |
| Modelos de base de datos | 15+ |
| Grupos de endpoints API | 6 |
| Archivos spec (tests frontend) | 19 |
| Roles de usuario | 4 |
| Estados de envío | 4 |
| Categorías de producto | 5 |
| Servicios Docker | 5 (4 core + 1 Nginx opcional) |
| Variables de entorno | 20+ |
| Tiers de rate limiting | 9+ |

---

## 12. ESTADO ACTUAL DEL PROYECTO

### Estado general: ESTABLE

| Área | Estado | Notas |
|---|---|---|
| Backend API | Estable | Todos los endpoints funcionales |
| Frontend SPA | Estable | 17 componentes activos |
| Base de datos | Estable | Migraciones al día |
| Búsqueda semántica | Estable | Requiere OPENAI_API_KEY válida |
| Importación Excel | Estable | Validación en 2 etapas |
| Notificaciones | Estable | Sin websockets (polling) |
| Métricas | Estable | Dashboard completo |
| Docker local | Estable | `docker-compose up -d` funcional |
| Despliegue Render | Estable | Blueprint probado |
| Documentación API | Completa | Swagger + ReDoc disponibles |
| Tests frontend | Parcial | 19 spec files |
| Tests backend | Parcial | Sin suite de tests unitarios explícita |

### Limitaciones conocidas

1. **Tier gratuito de Render:** Solo 1 worker de Gunicorn (512MB RAM). No apto para carga alta.
2. **Notificaciones:** Implementadas por polling (no WebSocket en tiempo real).
3. **Búsqueda semántica:** Depende de disponibilidad y costo de la API de OpenAI.
4. **Tests backend:** No hay una suite de pruebas unitarias explícita para cada módulo.

---

## 13. HISTORIAL DE CAMBIOS RECIENTES

| Commit | Descripción |
|---|---|
| `3c82291` | Reducir workers de Gunicorn a 1 (límite de RAM en Render free tier) |
| `9442d3a` | Corregir URL de health check que retornaba 404 en Render |
| `0ea663b` | Correcciones de despliegue en Render: `start_render.py`, `.gitattributes`, valor por defecto `OPENAI_API_KEY` |
| `a54b63e` | Cambios en `Dockerfile`, `render.yaml` y `start-render.sh` |
| `d0eb0ef` | Ajustes de despliegue en Render |
| `94e404a` | Actualizaciones de `README.md` y `settings.py` |
| `329126b` | Configuración de `.gitignore` |
| `67920c7` | Cambios finales de diseño, proceso semántico, eficiencia y Docker |
| `40af97e` | Panel de métricas y evaluación semántica |
| `329ede8` | Correcciones para pruebas |
| `078424c` | Correcciones de diseño y desarrollo del panel semántico |

**Tendencia reciente:** El foco ha sido en estabilizar el despliegue en Render.com (últimos 5 commits).

---

## 14. RIESGOS Y RECOMENDACIONES

### Riesgos

| Riesgo | Impacto | Probabilidad | Mitigación |
|---|---|---|---|
| Agotamiento de créditos OpenAI | Alto | Media | Monitorear uso; caché de embeddings activo |
| Límite de RAM en Render free tier | Alto | Alta | Migrar a plan pago o servidor propio |
| Sin WebSockets para notificaciones | Bajo | Alta | Polling implementado como alternativa |
| Secretos expuestos en Git (pasado) | Crítico | Bajo | Documentado y mitigado (ver `INCIDENTE_GIT_SECRETOS.md`) |
| Ausencia de suite de tests backend | Medio | N/A | Implementar pruebas unitarias/integración |

### Recomendaciones técnicas

1. **Tests backend:** Implementar pruebas unitarias con `pytest-django` para cubrir vistas, servicios y modelos críticos.
2. **WebSockets:** Evaluar `Django Channels` + Redis para notificaciones en tiempo real verdaderas.
3. **CI/CD:** Configurar GitHub Actions para ejecutar tests y build automáticamente en cada PR.
4. **Monitoreo:** Integrar Sentry para captura de errores en producción.
5. **Rate limiting:** Revisar y ajustar límites según uso real en producción.
6. **Backups:** Configurar backups automáticos de PostgreSQL en producción.

---

*Este reporte fue generado automáticamente el 2026-03-09 analizando el estado del repositorio `UBAppV2`.*

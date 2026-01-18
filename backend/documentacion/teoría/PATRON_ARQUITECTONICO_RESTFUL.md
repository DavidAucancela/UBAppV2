# 🌐 PATRÓN ARQUITECTÓNICO RESTFUL - SISTEMA UBAPP

**Fecha:** Enero 2025  
**Versión:** 1.0  
**Autor:** Documentación Técnica

---

## 📋 TABLA DE CONTENIDOS

1. [Introducción](#1-introducción)
2. [Arquitectura RESTful General](#2-arquitectura-restful-general)
3. [Comunicación Frontend-Backend](#3-comunicación-frontend-backend)
4. [Recursos y Operaciones HTTP](#4-recursos-y-operaciones-http)
5. [Endpoints del Sistema](#5-endpoints-del-sistema)
6. [Integración con Arquitectura en Capas](#6-integración-con-arquitectura-en-capas)
7. [Diagramas de Flujo REST](#7-diagramas-de-flujo-rest)
8. [Principios REST](#8-principios-rest)

---

## 1. INTRODUCCIÓN

### 1.1 Definición del Patrón

Para el desarrollo del sistema de almacenamiento web UBApp, se define el **patrón arquitectónico RESTful** que permite la estructura global del sistema y la organización de los componentes.

La implementación de este patrón arquitectónico permite la comunicación entre los procesos (Backend) y las interfaces (Frontend), estableciendo una interacción uniforme y desacoplada entre los componentes del sistema.

### 1.2 Tecnologías Utilizadas

- **Framework Backend:** Django 5.2.4
- **Framework API:** Django REST Framework (DRF) 3.16.0
- **Framework Frontend:** Angular 17
- **Autenticación:** JWT (JSON Web Tokens)
- **Documentación API:** drf-spectacular (OpenAPI/Swagger)

### 1.3 Objetivos del Patrón RESTful

1. ✅ **Interoperabilidad:** Comunicación estándar entre Frontend y Backend
2. ✅ **Desacoplamiento:** Separación entre capa de presentación y lógica
3. ✅ **Simplicidad:** Operaciones HTTP estándar (GET, POST, PUT, DELETE)
4. ✅ **Escalabilidad:** Fácil agregar nuevos recursos y endpoints
5. ✅ **Uniformidad:** Estructura consistente en todos los recursos

---

## 2. ARQUITECTURA RESTFUL GENERAL

### 2.1 Diagrama de Alto Nivel

```mermaid
graph TB
    subgraph "Cliente (Frontend)"
        A[Angular Application]
        A1[Componentes]
        A2[Services HTTP]
        A3[Interceptors]
    end
    
    subgraph "Comunicación"
        B[HTTP/REST Protocol]
        B1[JSON Format]
        B2[JWT Authentication]
    end
    
    subgraph "Servidor (Backend)"
        C[Django REST Framework]
        C1[URL Router]
        C2[ViewSets]
        C3[Serializers]
        C4[Permissions]
    end
    
    subgraph "Recursos del Sistema"
        D1[Usuarios]
        D2[Envíos]
        D3[Productos]
        D4[Búsqueda]
        D5[Notificaciones]
        D6[Métricas]
    end
    
    A --> A1
    A1 --> A2
    A2 --> A3
    A3 --> B
    B --> B1
    B --> B2
    B --> C
    C --> C1
    C1 --> C2
    C2 --> C3
    C2 --> C4
    C2 --> D1
    C2 --> D2
    C2 --> D3
    C2 --> D4
    C2 --> D5
    C2 --> D6
```

### 2.2 Diagrama ASCII Alternativo

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENTE (Frontend - Angular)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Componentes  │  │ HTTP Services│  │ Interceptors │         │
│  │   Angular    │  │   (RxJS)     │  │   (JWT)      │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         └──────────────────┴──────────────────┘                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ HTTP/REST
                               │ JSON
                               │ JWT Token
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              SERVIDOR (Backend - Django REST Framework)          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ URL Router   │  │  ViewSets    │  │ Serializers  │         │
│  │ (DefaultRouter)│  │  (DRF)      │  │  (DRF)       │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         └──────────────────┴──────────────────┘                 │
│                               │                                 │
│                               ▼                                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              RECURSOS DEL SISTEMA                    │      │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐   │      │
│  │  │Usuarios│  │ Envíos │  │Productos│  │Búsqueda│   │      │
│  │  └────────┘  └────────┘  └────────┘  └────────┘   │      │
│  │  ┌────────┐  ┌────────┐                            │      │
│  │  │Notific.│  │Métricas│                            │      │
│  │  └────────┘  └────────┘                            │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Principios de Comunicación

```
┌─────────────────────────────────────────────────────────────┐
│              PRINCIPIOS DE COMUNICACIÓN RESTFUL              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. STATELESS (Sin Estado)                                   │
│     - Cada petición contiene toda la información necesaria   │
│     - No se almacena estado en el servidor                   │
│     - Autenticación mediante JWT en cada petición            │
│                                                               │
│  2. UNIFORM INTERFACE (Interfaz Uniforme)                   │
│     - URLs consistentes para recursos                        │
│     - Métodos HTTP estándar (GET, POST, PUT, DELETE)       │
│     - Formatos de datos estándar (JSON)                     │
│                                                               │
│  3. RESOURCE-BASED (Basado en Recursos)                      │
│     - Cada recurso tiene una URL única                       │
│     - Recursos representan entidades del dominio            │
│     - Operaciones sobre recursos, no acciones                │
│                                                               │
│  4. REPRESENTATION (Representación)                           │
│     - Recursos se representan en JSON                        │
│     - Múltiples representaciones posibles                   │
│     - Separación entre recurso y representación             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. COMUNICACIÓN FRONTEND-BACKEND

### 3.1 Flujo de Comunicación General

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend (Angular)
    participant I as HTTP Interceptor
    participant B as Backend (Django)
    participant A as Autenticación
    participant DB as Base de Datos

    U->>F: Interacción (click, submit, etc.)
    F->>I: Petición HTTP
    I->>I: Agregar JWT Token
    I->>I: Agregar Headers
    I->>B: HTTP Request (GET/POST/PUT/DELETE)
    
    B->>A: Validar Token JWT
    A-->>B: Token válido
    
    B->>B: Procesar Request
    B->>DB: Consulta/Operación
    DB-->>B: Resultado
    
    B->>B: Serializar Datos
    B-->>I: HTTP Response (JSON)
    I-->>F: Response procesado
    F->>F: Actualizar UI
    F-->>U: Mostrar resultado
```

### 3.2 Estructura de Petición HTTP

```
┌─────────────────────────────────────────────────────────────┐
│                    ESTRUCTURA DE PETICIÓN HTTP                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Método HTTP:  GET | POST | PUT | DELETE                     │
│  URL:          /api/{recurso}/{id?}/{accion?}                 │
│  Headers:      Authorization: Bearer {JWT_TOKEN}             │
│                Content-Type: application/json                │
│  Body:         { "campo1": "valor1", ... } (solo POST/PUT)  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Estructura de Respuesta HTTP

```
┌─────────────────────────────────────────────────────────────┐
│                   ESTRUCTURA DE RESPUESTA HTTP               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Status Code:  200 OK | 201 Created | 400 Bad Request       │
│                401 Unauthorized | 403 Forbidden              │
│                404 Not Found | 500 Internal Server Error     │
│                                                               │
│  Headers:      Content-Type: application/json                │
│                                                               │
│  Body:         {                                              │
│                  "id": 1,                                    │
│                  "campo1": "valor1",                          │
│                  "campo2": "valor2",                          │
│                  ...                                          │
│                }                                              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. RECURSOS Y OPERACIONES HTTP

### 4.1 Operaciones HTTP Estándar

El sistema implementa las **4 operaciones HTTP estándar** del patrón RESTful:

#### 1. GET - Obtener Información

```mermaid
graph LR
    A[Cliente] -->|GET /api/recurso/| B[Servidor]
    B -->|200 OK + JSON| A
    
    A1[Cliente] -->|GET /api/recurso/id/| B1[Servidor]
    B1 -->|200 OK + JSON| A1
```

**Uso:**
- Obtener lista de recursos: `GET /api/envios/`
- Obtener recurso específico: `GET /api/envios/123/`
- Consultas y búsquedas: `GET /api/busqueda/semantica/`

#### 2. POST - Insertar Nuevos Recursos

```mermaid
graph LR
    A[Cliente] -->|POST /api/recurso/<br/>+ JSON Body| B[Servidor]
    B -->|201 Created + JSON| A
```

**Uso:**
- Crear nuevo recurso: `POST /api/envios/`
- Crear usuario: `POST /api/usuarios/`
- Búsqueda semántica: `POST /api/busqueda/semantica/`

#### 3. PUT - Actualizar Recurso

```mermaid
graph LR
    A[Cliente] -->|PUT /api/recurso/id/<br/>+ JSON Body| B[Servidor]
    B -->|200 OK + JSON| A
```

**Uso:**
- Actualizar recurso completo: `PUT /api/envios/123/`
- Actualizar estado: `PUT /api/envios/123/cambiar_estado/`

#### 4. DELETE - Borrar Recurso

```mermaid
graph LR
    A[Cliente] -->|DELETE /api/recurso/id/| B[Servidor]
    B -->|204 No Content| A
```

**Uso:**
- Eliminar recurso: `DELETE /api/envios/123/`
- Limpiar historial: `DELETE /api/busqueda/limpiar_historial/`

### 4.2 Tabla de Operaciones por Recurso

| Recurso | GET | POST | PUT | DELETE | Acciones Personalizadas |
|---------|-----|------|-----|--------|------------------------|
| **Usuarios** | ✅ Lista/Detalle | ✅ Crear | ✅ Actualizar | ✅ Eliminar | `login`, `logout`, `reset-password` |
| **Envíos** | ✅ Lista/Detalle | ✅ Crear | ✅ Actualizar | ✅ Eliminar | `cambiar_estado`, `exportar` |
| **Productos** | ✅ Lista/Detalle | ✅ Crear | ✅ Actualizar | ✅ Eliminar | - |
| **Búsqueda** | ✅ Historial | ✅ Búsqueda | - | ✅ Limpiar | `semantica`, `sugerencias`, `feedback` |
| **Notificaciones** | ✅ Lista/Detalle | ✅ Crear | ✅ Marcar leída | ✅ Eliminar | - |
| **Métricas** | ✅ Lista/Detalle | ✅ Crear | - | - | `exportar` |

---

## 5. ENDPOINTS DEL SISTEMA

### 5.1 Estructura Base de URLs

```
Base URL: http://localhost:8000/api/

┌─────────────────────────────────────────────────────────────┐
│                    ESTRUCTURA DE ENDPOINTS                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  /api/usuarios/                    - Gestión de usuarios    │
│  /api/envios/                      - Gestión de envíos      │
│  /api/busqueda/                    - Búsqueda y consultas   │
│  /api/notificaciones/              - Sistema de notificaciones│
│  /api/metricas/                    - Métricas del sistema   │
│  /api/token/                       - Autenticación JWT      │
│  /api/docs/                        - Documentación Swagger   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Endpoints: Usuarios

```mermaid
graph TB
    subgraph "Recurso: Usuarios"
        U1[GET /api/usuarios/]
        U2[GET /api/usuarios/{id}/]
        U3[POST /api/usuarios/]
        U4[PUT /api/usuarios/{id}/]
        U5[DELETE /api/usuarios/{id}/]
        U6[POST /api/usuarios/auth/login/]
        U7[POST /api/usuarios/auth/logout/]
        U8[POST /api/usuarios/auth/register/]
        U9[POST /api/usuarios/auth/reset-password/]
    end
```

**Endpoints Completos:**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/usuarios/` | Lista todos los usuarios |
| GET | `/api/usuarios/{id}/` | Obtiene un usuario específico |
| POST | `/api/usuarios/` | Crea un nuevo usuario |
| PUT | `/api/usuarios/{id}/` | Actualiza un usuario |
| DELETE | `/api/usuarios/{id}/` | Elimina un usuario |
| POST | `/api/usuarios/auth/login/` | Inicio de sesión |
| POST | `/api/usuarios/auth/logout/` | Cierre de sesión |
| POST | `/api/usuarios/auth/register/` | Registro de comprador |
| POST | `/api/usuarios/auth/reset-password/` | Restablecer contraseña |
| GET | `/api/usuarios/ubicaciones/provincias/` | Obtener provincias |
| GET | `/api/usuarios/ubicaciones/cantones/` | Obtener cantones |
| GET | `/api/usuarios/ubicaciones/ciudades/` | Obtener ciudades |

### 5.3 Endpoints: Envíos

```mermaid
graph TB
    subgraph "Recurso: Envíos"
        E1[GET /api/envios/envios/]
        E2[GET /api/envios/envios/{id}/]
        E3[POST /api/envios/envios/]
        E4[PUT /api/envios/envios/{id}/]
        E5[DELETE /api/envios/envios/{id}/]
    end
    
    subgraph "Recurso: Productos"
        P1[GET /api/envios/productos/]
        P2[POST /api/envios/productos/]
        P3[PUT /api/envios/productos/{id}/]
        P4[DELETE /api/envios/productos/{id}/]
    end
    
    subgraph "Recurso: Importación"
        I1[POST /api/envios/importaciones-excel/]
        I2[GET /api/envios/importaciones-excel/{id}/]
    end
```

**Endpoints Completos:**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/envios/envios/` | Lista todos los envíos |
| GET | `/api/envios/envios/{id}/` | Obtiene un envío específico |
| POST | `/api/envios/envios/` | Crea un nuevo envío |
| PUT | `/api/envios/envios/{id}/` | Actualiza un envío |
| DELETE | `/api/envios/envios/{id}/` | Elimina un envío |
| GET | `/api/envios/productos/` | Lista todos los productos |
| POST | `/api/envios/productos/` | Crea un nuevo producto |
| PUT | `/api/envios/productos/{id}/` | Actualiza un producto |
| DELETE | `/api/envios/productos/{id}/` | Elimina un producto |
| POST | `/api/envios/importaciones-excel/` | Importa envíos desde Excel |
| GET | `/api/envios/tarifas/` | Lista tarifas |

### 5.4 Endpoints: Búsqueda

```mermaid
graph TB
    subgraph "Búsqueda Tradicional"
        B1[GET /api/busqueda/]
        B2[GET /api/busqueda/historial/]
        B3[DELETE /api/busqueda/limpiar_historial/]
    end
    
    subgraph "Búsqueda Semántica"
        S1[POST /api/busqueda/semantica/]
        S2[GET /api/busqueda/semantica/sugerencias/]
        S3[GET /api/busqueda/semantica/historial/]
        S4[POST /api/busqueda/semantica/feedback/]
        S5[GET /api/busqueda/semantica/metricas/]
    end
```

**Endpoints Completos:**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/busqueda/` | Lista búsquedas |
| POST | `/api/busqueda/` | Crea una búsqueda |
| GET | `/api/busqueda/historial/` | Obtiene historial de búsquedas |
| DELETE | `/api/busqueda/limpiar_historial/` | Limpia el historial |
| GET | `/api/busqueda/estadisticas/` | Obtiene estadísticas |
| **POST** | **`/api/busqueda/semantica/`** | **Búsqueda semántica (principal)** |
| GET | `/api/busqueda/semantica/sugerencias/` | Obtiene sugerencias |
| GET | `/api/busqueda/semantica/historial/` | Historial semántico |
| POST | `/api/busqueda/semantica/historial/` | Guarda en historial |
| DELETE | `/api/busqueda/semantica/historial/` | Limpia historial semántico |
| POST | `/api/busqueda/semantica/feedback/` | Envía feedback |
| GET | `/api/busqueda/semantica/metricas/` | Métricas semánticas |

### 5.5 Endpoints: Notificaciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/notificaciones/` | Lista todas las notificaciones |
| GET | `/api/notificaciones/{id}/` | Obtiene una notificación |
| POST | `/api/notificaciones/` | Crea una notificación |
| PUT | `/api/notificaciones/{id}/` | Actualiza notificación (marcar leída) |
| DELETE | `/api/notificaciones/{id}/` | Elimina una notificación |

### 5.6 Endpoints: Métricas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/metricas/pruebas-controladas/` | Lista pruebas controladas |
| GET | `/api/metricas/metricas-semanticas/` | Lista métricas semánticas |
| GET | `/api/metricas/registros-embedding/` | Lista registros de embeddings |
| GET | `/api/metricas/metricas-rendimiento/` | Lista métricas de rendimiento |
| POST | `/api/metricas/exportacion/` | Exporta métricas |

### 5.7 Endpoints: Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/token/` | Obtiene token JWT (login) |
| POST | `/api/token/refresh/` | Refresca token JWT |

### 5.8 Diagrama de Endpoints Completo

```mermaid
graph TB
    subgraph "Base URL: /api/"
        A[Autenticación<br/>/token/]
        
        B[Usuarios<br/>/usuarios/]
        B1[Auth<br/>/usuarios/auth/]
        B2[Ubicaciones<br/>/usuarios/ubicaciones/]
        
        C[Envíos<br/>/envios/]
        C1[Envíos<br/>/envios/envios/]
        C2[Productos<br/>/envios/productos/]
        C3[Tarifas<br/>/envios/tarifas/]
        C4[Importación<br/>/envios/importaciones-excel/]
        
        D[Búsqueda<br/>/busqueda/]
        D1[Tradicional<br/>/busqueda/]
        D2[Semántica<br/>/busqueda/semantica/]
        
        E[Notificaciones<br/>/notificaciones/]
        F[Métricas<br/>/metricas/]
        G[Documentación<br/>/docs/]
    end
    
    A --> B
    B --> B1
    B --> B2
    C --> C1
    C --> C2
    C --> C3
    C --> C4
    D --> D1
    D --> D2
```

### 5.9 Servicios HTTP del Frontend (Angular)

El frontend Angular implementa servicios HTTP organizados por funcionalidad que consumen los endpoints REST del backend. Estos servicios utilizan `HttpClient` de Angular y `Observables` de RxJS para manejar las peticiones asíncronas.

#### 5.9.1 Estructura Base de Servicios

```
Base URL: environment.apiUrl (configuración por entorno)

┌─────────────────────────────────────────────────────────────┐
│           SERVICIOS HTTP DEL FRONTEND (Angular)              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ApiService                   - Servicio principal API       │
│  AuthService                  - Autenticación y sesión       │
│  BusquedaService              - Búsquedas tradicional/semántica│
│  NotificacionService          - Sistema de notificaciones   │
│  UsuarioService               - Dashboard y perfil usuario   │
│  ImportacionExcelService      - Importación de archivos Excel│
│  MetricasService              - Métricas y pruebas           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

#### 5.9.2 Servicio: AuthService

**Ubicación:** `frontend/src/app/services/auth.service.ts`

**Métodos:**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `login()` | POST | `/api/usuarios/auth/login/` | Inicio de sesión |
| `logout()` | POST | `/api/usuarios/auth/logout/` | Cierre de sesión |
| `resetPassword()` | POST | `/api/usuarios/auth/reset-password/` | Restablecer contraseña |
| `verifyEmailExists()` | POST | `/api/usuarios/auth/verify-email/` | Verificar email |
| `getToken()` | - | - | Obtener token JWT (localStorage) |
| `getRefreshToken()` | - | - | Obtener refresh token (localStorage) |
| `isAuthenticated()` | - | - | Verificar autenticación |
| `hasRole()` | - | - | Verificar rol de usuario |

#### 5.9.3 Servicio: ApiService

**Ubicación:** `frontend/src/app/services/api.service.ts`

**Recurso: Usuarios**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `getUsuarios()` | GET | `/api/usuarios/` | Lista todos los usuarios |
| `getUsuario(id)` | GET | `/api/usuarios/{id}/` | Obtiene un usuario específico |
| `createUsuario()` | POST | `/api/usuarios/` | Crea un nuevo usuario |
| `updateUsuario()` | PUT | `/api/usuarios/{id}/` | Actualiza un usuario |
| `actualizarUsuarioParcial()` | PATCH | `/api/usuarios/{id}/` | Actualiza parcialmente |
| `deleteUsuario()` | DELETE | `/api/usuarios/{id}/` | Elimina un usuario |
| `registerComprador()` | POST | `/api/usuarios/auth/register/` | Registro de comprador |
| `getCompradores()` | GET | `/api/usuarios/compradores/` | Lista compradores |
| `getUsuariosPorRol()` | GET | `/api/usuarios/por_rol/` | Lista usuarios por rol |
| `getEstadisticasUsuarios()` | GET | `/api/usuarios/estadisticas/` | Estadísticas de usuarios |
| `changePassword()` | POST | `/api/usuarios/{id}/change_password/` | Cambiar contraseña |
| `actualizarPerfil()` | PUT | `/api/usuarios/actualizar_perfil/` | Actualizar perfil |
| `cambiarPasswordPerfil()` | POST | `/api/usuarios/cambiar_password/` | Cambiar contraseña perfil |
| `getUbicacionesProvincias()` | GET | `/api/usuarios/ubicaciones/provincias/` | Obtener provincias |
| `getUbicacionesCantones()` | GET | `/api/usuarios/ubicaciones/cantones/` | Obtener cantones |
| `getUbicacionesCiudades()` | GET | `/api/usuarios/ubicaciones/ciudades/` | Obtener ciudades |
| `getUbicacionesCoordenadas()` | GET | `/api/usuarios/ubicaciones/coordenadas/` | Obtener coordenadas |
| `getMapaCompradores()` | GET | `/api/usuarios/mapa_compradores/` | Mapa de compradores |
| `getEnviosComprador()` | GET | `/api/usuarios/{id}/envios_comprador/` | Envíos de comprador |

**Recurso: Envíos**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `getEnvios()` | GET | `/api/envios/envios/` | Lista todos los envíos |
| `getEnvio(id)` | GET | `/api/envios/envios/{id}/` | Obtiene un envío específico |
| `createEnvio()` | POST | `/api/envios/envios/` | Crea un nuevo envío |
| `updateEnvio()` | PUT | `/api/envios/envios/{id}/` | Actualiza un envío |
| `deleteEnvio()` | DELETE | `/api/envios/envios/{id}/` | Elimina un envío |
| `getMisEnvios()` | GET | `/api/envios/envios/mis_envios/` | Mis envíos |
| `getEnviosPorEstado()` | GET | `/api/envios/envios/por_estado/` | Envíos por estado |
| `cambiarEstadoEnvio()` | POST | `/api/envios/envios/{id}/cambiar_estado/` | Cambiar estado |
| `getEstadisticasEnvios()` | GET | `/api/envios/envios/estadisticas/` | Estadísticas de envíos |
| `calcularCostoEnvio()` | POST | `/api/envios/envios/calcular_costo/` | Calcular costo |
| `buscarEnviosAvanzado()` | GET | `/api/envios/envios/` | Búsqueda avanzada con filtros |
| `obtenerEstadisticasBusquedaEnvios()` | GET | `/api/envios/envios/estadisticas/` | Estadísticas de búsqueda |
| `exportarResultadosBusqueda()` | GET | `/api/envios/envios/exportar/` | Exportar resultados |
| `obtenerComprobanteEnvio()` | GET | `/api/envios/envios/{id}/comprobante/` | Comprobante PDF |

**Recurso: Productos**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `getProductos()` | GET | `/api/envios/productos/` | Lista todos los productos |
| `getProducto(id)` | GET | `/api/envios/productos/{id}/` | Obtiene un producto específico |
| `createProducto()` | POST | `/api/envios/productos/` | Crea un nuevo producto |
| `updateProducto()` | PUT | `/api/envios/productos/{id}/` | Actualiza un producto |
| `deleteProducto()` | DELETE | `/api/envios/productos/{id}/` | Elimina un producto |
| `getProductosPorCategoria()` | GET | `/api/envios/productos/por_categoria/` | Productos por categoría |
| `getEstadisticasProductos()` | GET | `/api/envios/productos/estadisticas/` | Estadísticas de productos |

**Recurso: Tarifas**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `getTarifas()` | GET | `/api/envios/tarifas/` | Lista todas las tarifas |
| `getTarifa(id)` | GET | `/api/envios/tarifas/{id}/` | Obtiene una tarifa específica |
| `createTarifa()` | POST | `/api/envios/tarifas/` | Crea una nueva tarifa |
| `updateTarifa()` | PUT | `/api/envios/tarifas/{id}/` | Actualiza una tarifa |
| `deleteTarifa()` | DELETE | `/api/envios/tarifas/{id}/` | Elimina una tarifa |
| `getTarifasPorCategoria()` | GET | `/api/envios/tarifas/por_categoria/` | Tarifas por categoría |
| `buscarTarifa()` | POST | `/api/envios/tarifas/buscar_tarifa/` | Buscar tarifa |

**Recurso: Búsqueda**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `buscar()` | GET | `/api/busqueda/buscar/` | Búsqueda tradicional |
| `getHistorialBusqueda()` | GET | `/api/busqueda/historial/` | Historial de búsquedas |
| `limpiarHistorialBusqueda()` | DELETE | `/api/busqueda/limpiar_historial/` | Limpiar historial |
| `getEstadisticasBusqueda()` | GET | `/api/busqueda/estadisticas/` | Estadísticas de búsqueda |

**Recurso: Búsqueda Semántica**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `buscarEnviosSemantica()` | POST | `/api/busqueda/semantica/` | Búsqueda semántica |
| `obtenerSugerenciasSemanticas()` | GET | `/api/busqueda/semantica/sugerencias/` | Obtener sugerencias |
| `guardarHistorialSemantico()` | POST | `/api/busqueda/semantica/historial/` | Guardar en historial |
| `obtenerHistorialSemantico()` | GET | `/api/busqueda/semantica/historial/` | Obtener historial |
| `limpiarHistorialSemantico()` | DELETE | `/api/busqueda/semantica/historial/` | Limpiar historial |
| `obtenerMetricasSemanticas()` | GET | `/api/busqueda/semantica/metricas/` | Métricas semánticas |
| `enviarFeedbackSemantico()` | POST | `/api/busqueda/semantica/feedback/` | Enviar feedback |

**Recurso: Notificaciones**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `getNotificaciones()` | GET | `/api/notificaciones/` | Lista notificaciones |
| `getContadorNotificaciones()` | GET | `/api/notificaciones/contador/` | Contador de notificaciones |

#### 5.9.4 Servicio: BusquedaService

**Ubicación:** `frontend/src/app/services/busqueda.service.ts`

**Métodos:**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `buscar()` | GET | `/api/busqueda/buscar/` | Búsqueda tradicional |
| `getHistorialTradicional()` | GET | `/api/busqueda/` | Historial tradicional |
| `limpiarHistorialTradicional()` | DELETE | `/api/busqueda/limpiar_historial/` | Limpiar historial |
| `descargarPdfBusquedaTradicional()` | GET | `/api/busqueda/{id}/descargar-pdf/` | Descargar PDF búsqueda |
| `buscarSemantica()` | POST | `/api/busqueda/semantica/` | Búsqueda semántica |
| `obtenerSugerencias()` | GET | `/api/busqueda/semantica/sugerencias/` | Obtener sugerencias |
| `getHistorialSemantico()` | GET | `/api/busqueda/semantica/historial/` | Historial semántico |
| `guardarHistorialSemantico()` | POST | `/api/busqueda/semantica/historial/` | Guardar historial |
| `limpiarHistorialSemantico()` | DELETE | `/api/busqueda/semantica/historial/` | Limpiar historial |
| `obtenerMetricasSemanticas()` | GET | `/api/busqueda/semantica/metricas/` | Métricas semánticas |
| `descargarPdfBusquedaSemantica()` | GET | `/api/busqueda/semantica/{id}/descargar-pdf/` | Descargar PDF semántico |

#### 5.9.5 Servicio: NotificacionService

**Ubicación:** `frontend/src/app/services/notificacion.service.ts`

**Métodos:**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `obtenerNotificaciones()` | GET | `/api/notificaciones/` | Obtener notificaciones |
| `obtenerContador()` | GET | `/api/notificaciones/contador/` | Contador de notificaciones |
| `marcarComoLeida()` | PATCH | `/api/notificaciones/{id}/marcar-leida/` | Marcar como leída |
| `marcarTodasComoLeidas()` | POST | `/api/notificaciones/marcar-todas-leidas/` | Marcar todas como leídas |
| `eliminarNotificacion()` | DELETE | `/api/notificaciones/{id}/` | Eliminar notificación |

**Características adicionales:**
- Polling automático cada 30 segundos para compradores
- BehaviorSubject para estado reactivo
- Manejo de contadores en tiempo real

#### 5.9.6 Servicio: UsuarioService

**Ubicación:** `frontend/src/app/services/usuario.service.ts`

**Métodos:**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `getDashboardUsuario()` | GET | `/api/usuarios/dashboard_usuario/` | Dashboard del usuario |
| `getEstadisticasCupo()` | GET | `/api/usuarios/estadisticas_cupo/` | Estadísticas de cupo |
| `getMisEnvios()` | GET | `/api/usuarios/mis_envios/` | Mis envíos con filtros |

#### 5.9.7 Servicio: ImportacionExcelService

**Ubicación:** `frontend/src/app/services/importacion-excel.service.ts`

**Métodos:**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `leerArchivoLocal()` | - | - | Lee archivo Excel localmente (sin backend) |
| `subirArchivo()` | POST | `/api/envios/importaciones-excel/` | Sube archivo Excel |
| `obtenerPreview()` | GET | `/api/envios/importaciones-excel/{id}/preview/` | Vista previa |
| `validarDatos()` | POST | `/api/envios/importaciones-excel/{id}/validar/` | Validar datos |
| `procesarDatos()` | POST | `/api/envios/importaciones-excel/{id}/procesar/` | Procesar importación |
| `obtenerImportacion()` | GET | `/api/envios/importaciones-excel/{id}/` | Obtener importación |
| `listarImportaciones()` | GET | `/api/envios/importaciones-excel/` | Listar importaciones |
| `obtenerReporteErrores()` | GET | `/api/envios/importaciones-excel/{id}/reporte_errores/` | Reporte de errores |
| `obtenerEstadisticas()` | GET | `/api/envios/importaciones-excel/estadisticas/` | Estadísticas |
| `descargarPlantillaEjemplo()` | - | - | Descarga plantilla ejemplo (local) |

**Características adicionales:**
- BehaviorSubject para estado de importación
- Validación local antes de enviar al backend
- Manejo de archivos Excel con XLSX library

#### 5.9.8 Servicio: MetricasService

**Ubicación:** `frontend/src/app/services/metricas.service.ts`

**Métodos:**

**Pruebas Controladas**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `getPruebasControladas()` | GET | `/api/metricas/pruebas-controladas/` | Lista pruebas controladas |
| `crearPruebaControlada()` | POST | `/api/metricas/pruebas-controladas/` | Crear prueba controlada |
| `ejecutarPruebaControlada()` | POST | `/api/metricas/pruebas-controladas/{id}/ejecutar/` | Ejecutar prueba |

**Métricas Semánticas**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `getMetricasSemanticas()` | GET | `/api/metricas/metricas-semanticas/` | Lista métricas semánticas |
| `getEstadisticasSemanticas()` | GET | `/api/metricas/metricas-semanticas/estadisticas/` | Estadísticas semánticas |

**Registros de Embedding**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `getRegistrosEmbedding()` | GET | `/api/metricas/registros-embedding/` | Lista registros |
| `getEstadisticasEmbedding()` | GET | `/api/metricas/registros-embedding/estadisticas/` | Estadísticas |

**Pruebas de Carga**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `getPruebasCarga()` | GET | `/api/metricas/pruebas-carga/` | Lista pruebas de carga |
| `ejecutarPruebaCargaBusqueda()` | POST | `/api/metricas/pruebas-carga/ejecutar_busqueda/` | Ejecutar prueba de carga |

**Métricas de Rendimiento**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `getMetricasRendimiento()` | GET | `/api/metricas/metricas-rendimiento/` | Lista métricas de rendimiento |
| `getEstadisticasRendimiento()` | GET | `/api/metricas/metricas-rendimiento/estadisticas/` | Estadísticas de rendimiento |

**Registros Manuales**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `getRegistrosManuales()` | GET | `/api/metricas/registros-manuales/` | Lista registros manuales |
| `registrarEnvioManual()` | POST | `/api/metricas/registros-manuales/registrar/` | Registrar envío manual |
| `getEstadisticasRegistrosManuales()` | GET | `/api/metricas/registros-manuales/estadisticas/` | Estadísticas |

**Pruebas del Sistema**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `listarTests()` | GET | `/api/metricas/pruebas-sistema/listar_tests/` | Lista tests disponibles |
| `ejecutarTests()` | POST | `/api/metricas/pruebas-sistema/ejecutar_tests/` | Ejecutar tests unitarios |
| `ejecutarPruebasRendimiento()` | POST | `/api/metricas/pruebas-sistema/ejecutar_rendimiento/` | Ejecutar pruebas rendimiento |
| `getEstadisticasPruebas()` | GET | `/api/metricas/pruebas-sistema/estadisticas_pruebas/` | Estadísticas de pruebas |
| `getPruebasRendimientoGuardadas()` | GET | `/api/metricas/pruebas-sistema/pruebas_rendimiento_guardadas/` | Pruebas guardadas |
| `getDetallePruebaRendimiento()` | GET | `/api/metricas/pruebas-sistema/{id}/detalle_prueba_rendimiento/` | Detalle de prueba |

**Exportación**

| Método | Tipo | Endpoint Backend | Descripción |
|--------|------|------------------|-------------|
| `exportarMetricasSemanticasCSV()` | GET | `/api/metricas/exportacion/metricas_semanticas/` | Exportar CSV métricas semánticas |
| `exportarMetricasRendimientoCSV()` | GET | `/api/metricas/exportacion/metricas_rendimiento/` | Exportar CSV métricas rendimiento |

#### 5.9.9 Diagrama de Servicios Frontend

```mermaid
graph TB
    subgraph "Frontend Angular Services"
        A[ApiService<br/>Servicio Principal]
        B[AuthService<br/>Autenticación]
        C[BusquedaService<br/>Búsquedas]
        D[NotificacionService<br/>Notificaciones]
        E[UsuarioService<br/>Dashboard Usuario]
        F[ImportacionExcelService<br/>Importación Excel]
        G[MetricasService<br/>Métricas]
    end
    
    subgraph "Backend REST API"
        H[/api/usuarios/]
        I[/api/envios/]
        J[/api/busqueda/]
        K[/api/notificaciones/]
        L[/api/metricas/]
    end
    
    A --> H
    A --> I
    A --> J
    A --> K
    B --> H
    C --> J
    D --> K
    E --> H
    F --> I
    G --> L
```

---

## 6. INTEGRACIÓN CON ARQUITECTURA EN CAPAS

### 6.1 RESTful en la Arquitectura en Capas

El patrón RESTful se integra perfectamente con la arquitectura en capas:

```mermaid
graph TB
    subgraph "Cliente"
        A[Angular Frontend]
    end
    
    subgraph "Capa de Presentación (REST)"
        B[ViewSets<br/>Endpoints REST]
        C[Serializers<br/>JSON]
        D[Permissions<br/>JWT]
        E[Validators]
    end
    
    subgraph "Capa de Lógica de Negocio"
        F[Services]
        G[Business Logic]
    end
    
    subgraph "Capa de Datos"
        H[Repositories]
        I[Models]
    end
    
    subgraph "Capa Semántica"
        J[Embedding Service]
        K[Vector Search]
    end
    
    A -->|HTTP REST| B
    B --> C
    B --> D
    B --> E
    B --> F
    F --> G
    F --> H
    F --> J
    H --> I
    J --> K
```

### 6.2 Flujo Completo: Petición REST → Capas

```
┌─────────────────────────────────────────────────────────────┐
│              FLUJO REST EN ARQUITECTURA EN CAPAS             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. CLIENTE (Angular)                                         │
│     POST /api/envios/                                         │
│     Headers: Authorization: Bearer {token}                     │
│     Body: { "hawb": "HAW123", ... }                          │
│                                                               │
│  2. CAPA DE PRESENTACIÓN (REST)                               │
│     ├─ URL Router: Enruta a EnvioViewSet                     │
│     ├─ Permission: Valida JWT token                          │
│     ├─ Serializer: Valida formato JSON                       │
│     └─ ViewSet: Recibe petición HTTP                         │
│                                                               │
│  3. CAPA DE LÓGICA DE NEGOCIO                                 │
│     ├─ EnvioService.crear_envio()                            │
│     ├─ Validar permisos                                      │
│     ├─ Validar reglas de negocio                             │
│     └─ Orquestar operaciones                                 │
│                                                               │
│  4. CAPA DE DATOS                                             │
│     ├─ EnvioRepository.crear()                               │
│     └─ Model.objects.create()                                │
│                                                               │
│  5. CAPA SEMÁNTICA (si aplica)                               │
│     ├─ EmbeddingService.generar_embedding()                  │
│     └─ SemanticRepository.guardar()                          │
│                                                               │
│  6. RESPUESTA                                                 │
│     ├─ Serializer: Serializa datos                           │
│     ├─ ViewSet: Retorna Response                             │
│     └─ HTTP 201 Created + JSON                                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Separación de Responsabilidades

```
┌─────────────────────────────────────────────────────────────┐
│         SEPARACIÓN RESTFUL Y ARQUITECTURA EN CAPAS          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  CAPA DE PRESENTACIÓN (REST)                                 │
│  ✅ Maneja HTTP (request/response)                           │
│  ✅ Valida formato de datos                                  │
│  ✅ Controla acceso (permissions)                            │
│  ❌ NO contiene lógica de negocio                            │
│  ❌ NO accede directamente a modelos                          │
│                                                               │
│  CAPA DE LÓGICA DE NEGOCIO                                   │
│  ✅ Implementa reglas de negocio                            │
│  ✅ Orquesta operaciones                                     │
│  ✅ Valida reglas de dominio                                 │
│  ❌ NO conoce detalles de HTTP                                │
│  ❌ NO accede directamente a modelos                          │
│                                                               │
│  CAPA DE DATOS                                               │
│  ✅ Accede a base de datos                                   │
│  ✅ Optimiza consultas                                       │
│  ❌ NO contiene lógica de negocio                            │
│                                                               │
│  CAPA SEMÁNTICA                                              │
│  ✅ Procesa embeddings                                       │
│  ✅ Búsqueda vectorial                                       │
│  ❌ NO contiene lógica de negocio                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. DIAGRAMAS DE FLUJO REST

### 7.1 Flujo: Crear Envío (POST)

```mermaid
sequenceDiagram
    participant C as Cliente Angular
    participant V as EnvioViewSet
    participant S as EnvioSerializer
    participant P as Permission
    participant SV as EnvioService
    participant R as EnvioRepository
    participant M as Envio Model
    participant DB as PostgreSQL

    C->>V: POST /api/envios/envios/
    Note over C,V: Headers: Authorization: Bearer {token}
    Note over C,V: Body: {"hawb": "HAW123", ...}
    
    V->>P: Verificar token JWT
    P-->>V: Token válido
    
    V->>S: Validar datos (is_valid)
    S->>S: Validar formato JSON
    S-->>V: Datos válidos
    
    V->>SV: crear_envio(data, usuario)
    
    SV->>SV: Validar permisos
    SV->>SV: Validar reglas negocio
    SV->>R: crear(datos)
    
    R->>M: objects.create(**datos)
    M->>DB: INSERT INTO envios
    DB-->>M: Envío creado (id=123)
    M-->>R: Envio instance
    R-->>SV: Envio instance
    
    SV->>SV: Operaciones post-creación
    SV-->>V: Envio instance
    
    V->>S: Serializar (envio)
    S-->>V: JSON data
    V-->>C: HTTP 201 Created
    Note over C,V: {"id": 123, "hawb": "HAW123", ...}
```

### 7.2 Flujo: Obtener Envíos (GET)

```mermaid
sequenceDiagram
    participant C as Cliente Angular
    participant V as EnvioViewSet
    participant P as Permission
    participant R as EnvioRepository
    participant M as Envio Model
    participant DB as PostgreSQL
    participant S as EnvioSerializer

    C->>V: GET /api/envios/envios/
    Note over C,V: Headers: Authorization: Bearer {token}
    
    V->>P: Verificar token JWT
    P-->>V: Token válido
    
    V->>R: filtrar_por_usuario(usuario)
    
    R->>M: objects.select_related().filter(...)
    M->>DB: SELECT * FROM envios WHERE ...
    DB-->>M: Resultados
    M-->>R: QuerySet
    
    R-->>V: QuerySet de envíos
    
    V->>S: Serializar (queryset)
    S->>S: Serializar cada envío
    S-->>V: JSON array
    
    V-->>C: HTTP 200 OK
    Note over C,V: [{"id": 1, ...}, {"id": 2, ...}]
```

### 7.3 Flujo: Búsqueda Semántica (POST)

```mermaid
sequenceDiagram
    participant C as Cliente Angular
    participant V as BusquedaViewSet
    participant S as BusquedaSerializer
    participant BS as BusquedaSemanticaService
    participant ES as EmbeddingService
    participant VS as VectorSearchService
    participant OAI as OpenAI API
    participant DB as PostgreSQL

    C->>V: POST /api/busqueda/semantica/
    Note over C,V: Body: {"texto": "envíos a Quito"}
    
    V->>S: Validar datos
    S-->>V: Datos válidos
    
    V->>BS: buscar(consulta, usuario, filtros)
    
    BS->>ES: generar_embedding("envíos a Quito")
    ES->>OAI: API Call
    OAI-->>ES: Embedding vector
    ES-->>BS: Embedding consulta
    
    BS->>BS: Filtrar por usuario
    BS->>VS: buscar_similares(embedding, queryset)
    
    VS->>DB: Búsqueda pgvector
    Note over VS,DB: SELECT * FROM envio_embeddings<br/>ORDER BY embedding <-> query_embedding
    DB-->>VS: Resultados ordenados
    
    VS-->>BS: Envíos similares con scores
    BS->>BS: Procesar resultados
    BS-->>V: Resultados búsqueda
    
    V->>S: Serializar resultados
    S-->>V: JSON response
    V-->>C: HTTP 200 OK
    Note over C,V: {"resultados": [...], "total": 10}
```

### 7.4 Flujo: Autenticación (POST /api/token/)

```mermaid
sequenceDiagram
    participant C as Cliente Angular
    participant A as TokenObtainPairView
    participant U as Usuario Model
    participant DB as PostgreSQL
    participant JWT as JWT Service

    C->>A: POST /api/token/
    Note over C,A: Body: {"email": "user@example.com", "password": "***"}
    
    A->>U: authenticate(email, password)
    U->>DB: SELECT * FROM usuarios WHERE email=...
    DB-->>U: Usuario encontrado
    U->>U: Verificar password
    U-->>A: Usuario autenticado
    
    A->>JWT: Generar token pair
    JWT->>JWT: Crear access token
    JWT->>JWT: Crear refresh token
    JWT-->>A: Token pair
    
    A-->>C: HTTP 200 OK
    Note over C,A: {"access": "eyJ...", "refresh": "eyJ..."}
    
    Note over C: Guardar tokens en localStorage
```

---

## 8. PRINCIPIOS REST

### 8.1 Principios Aplicados en el Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                  PRINCIPIOS REST APLICADOS                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. ✅ STATELESS (Sin Estado)                                │
│     - Cada petición es independiente                        │
│     - Autenticación mediante JWT en cada petición           │
│     - No se almacena sesión en servidor                      │
│                                                               │
│  2. ✅ UNIFORM INTERFACE (Interfaz Uniforme)                │
│     - URLs consistentes: /api/{recurso}/                     │
│     - Métodos HTTP estándar: GET, POST, PUT, DELETE          │
│     - Formato JSON para todas las respuestas                 │
│     - Códigos de estado HTTP estándar                       │
│                                                               │
│  3. ✅ RESOURCE-BASED (Basado en Recursos)                   │
│     - Recursos: usuarios, envíos, productos, búsqueda       │
│     - Cada recurso tiene URL única                          │
│     - Operaciones sobre recursos, no acciones               │
│                                                               │
│  4. ✅ REPRESENTATION (Representación)                       │
│     - Recursos representados en JSON                        │
│     - Serializers definen representación                     │
│     - Separación recurso/representación                      │
│                                                               │
│  5. ✅ CLIENT-SERVER (Cliente-Servidor)                      │
│     - Separación clara Frontend/Backend                     │
│     - Comunicación mediante HTTP                            │
│     - Desacoplamiento entre componentes                      │
│                                                               │
│  6. ✅ CACHEABLE (Cacheable)                                 │
│     - Respuestas GET pueden ser cacheadas                   │
│     - Headers Cache-Control donde aplica                    │
│                                                               │
│  7. ✅ LAYERED SYSTEM (Sistema en Capas)                    │
│     - Arquitectura en capas implementada                    │
│     - Separación Presentación/Negocio/Datos                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Convenciones de Nomenclatura

```
┌─────────────────────────────────────────────────────────────┐
│              CONVENCIONES DE NOMENCLATURA REST               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  URLs:                                                        │
│  ✅ /api/recurso/              (plural, minúsculas)          │
│  ✅ /api/recurso/{id}/         (singular para detalle)       │
│  ✅ /api/recurso/{id}/accion/  (acciones personalizadas)     │
│                                                               │
│  Métodos HTTP:                                                │
│  ✅ GET    - Obtener recursos                                │
│  ✅ POST   - Crear recursos                                  │
│  ✅ PUT    - Actualizar recursos completos                   │
│  ✅ DELETE - Eliminar recursos                               │
│                                                               │
│  Códigos de Estado:                                           │
│  ✅ 200 OK           - Operación exitosa                     │
│  ✅ 201 Created      - Recurso creado                        │
│  ✅ 204 No Content   - Eliminación exitosa                   │
│  ✅ 400 Bad Request  - Error en datos                        │
│  ✅ 401 Unauthorized - No autenticado                        │
│  ✅ 403 Forbidden    - Sin permisos                           │
│  ✅ 404 Not Found    - Recurso no existe                      │
│  ✅ 500 Server Error - Error interno                         │
│                                                               │
│  Formato JSON:                                                │
│  ✅ Campos en snake_case                                     │
│  ✅ IDs numéricos                                            │
│  ✅ Fechas en ISO 8601                                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. EJEMPLOS PRÁCTICOS

### 9.1 Ejemplo: Crear Envío

**Request:**
```http
POST /api/envios/envios/ HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "hawb": "HAW12345",
  "comprador_id": 1,
  "fecha_emision": "2025-01-15",
  "estado": "Pendiente"
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 123,
  "hawb": "HAW12345",
  "comprador": 1,
  "comprador_nombre": "Juan Pérez",
  "fecha_emision": "2025-01-15T10:30:00Z",
  "estado": "Pendiente",
  "created_at": "2025-01-15T10:30:00Z"
}
```

### 9.2 Ejemplo: Búsqueda Semántica

**Request:**
```http
POST /api/busqueda/semantica/ HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "texto": "envíos a Quito pendientes",
  "limite": 20,
  "filtrosAdicionales": {
    "estado": "Pendiente",
    "fecha_desde": "2025-01-01"
  }
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "resultados": [
    {
      "envio": {
        "id": 123,
        "hawb": "HAW12345",
        "comprador_nombre": "Juan Pérez",
        "estado": "Pendiente"
      },
      "similitud": 0.85,
      "texto_indexado": "HAW12345 Juan Pérez Quito Pendiente..."
    }
  ],
  "total": 15,
  "tiempo_respuesta_ms": 245
}
```

---

## 10. VENTAJAS DEL PATRÓN RESTFUL

### 10.1 Beneficios Implementados

```
┌─────────────────────────────────────────────────────────────┐
│              VENTAJAS DEL PATRÓN RESTFUL                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ✅ INTEROPERABILIDAD                                         │
│     - Comunicación estándar entre Frontend y Backend        │
│     - Fácil integración con otros sistemas                   │
│     - APIs consumibles por cualquier cliente HTTP            │
│                                                               │
│  ✅ SIMPLICIDAD                                               │
│     - Operaciones HTTP estándar y conocidas                 │
│     - Fácil de entender y documentar                         │
│     - Curva de aprendizaje baja                              │
│                                                               │
│  ✅ DESACOPLAMIENTO                                           │
│     - Separación Frontend/Backend                           │
│     - Cambios en una capa no afectan la otra                │
│     - Desarrollo paralelo posible                           │
│                                                               │
│  ✅ ESCALABILIDAD                                             │
│     - Fácil agregar nuevos recursos                         │
│     - Estructura consistente                                │
│     - Soporte para caché y balanceo de carga                │
│                                                               │
│  ✅ MANTENIBILIDAD                                            │
│     - Código organizado y estructurado                      │
│     - Fácil de testear                                       │
│     - Documentación automática (Swagger)                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. CONCLUSIÓN

El patrón arquitectónico RESTful implementado en el sistema UBApp proporciona:

1. ✅ **Comunicación uniforme** entre Frontend y Backend
2. ✅ **Separación de responsabilidades** mediante arquitectura en capas
3. ✅ **Simplicidad** en las operaciones mediante métodos HTTP estándar
4. ✅ **Interoperabilidad** mediante formatos estándar (JSON, HTTP)
5. ✅ **Escalabilidad** para agregar nuevos recursos y funcionalidades

La integración del patrón RESTful con la arquitectura en capas permite una estructura robusta, mantenible y escalable del sistema.

---

**Documento creado:** Enero 2025  
**Última actualización:** Enero 2025  
**Versión:** 1.0


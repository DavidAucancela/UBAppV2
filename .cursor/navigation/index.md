# 🧭 Navegación Rápida - Sistema UBApp

> **Guía completa de todos los módulos del sistema para navegación rápida con Cursor AI**

---

## 📑 Tabla de Contenidos

1. [Módulos Principales](#módulos-principales)
   - [🔍 Búsqueda Semántica](#-búsqueda-semántica)
   - [📦 Gestión de Envíos](#-gestión-de-envíos)
   - [👥 Gestión de Usuarios](#-gestión-de-usuarios)
   - [📦 Gestión de Productos](#-gestión-de-productos)
   - [📊 Importación desde Excel](#-importación-desde-excel)
   - [💰 Gestión de Tarifas](#-gestión-de-tarifas)
   - [🗺️ Mapa de Compradores](#️-mapa-de-compradores)
   - [📈 Dashboard y Actividades](#-dashboard-y-actividades-del-sistema)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Autenticación y Seguridad](#autenticación-y-seguridad)
4. [Componentes Compartidos](#componentes-compartidos)
5. [Comandos Útiles](#comandos-útiles)
6. [Troubleshooting](#troubleshooting)

---

## 📋 Módulos Principales

### 🔍 Búsqueda Semántica

**📍 Ubicación:**
- **Frontend:** `frontend/src/app/components/busqueda-semantica/`
- **Backend:** `backend/apps/busqueda/`
- **Ruta:** `/busqueda-semantica`

**🎯 Funcionalidad:** Búsqueda avanzada usando embeddings y vector search para encontrar envíos por similitud semántica, no solo palabras clave exactas.

**📁 Estructura:**
```
Frontend: busqueda-semantica/
  ├── busqueda-semantica.component.ts
  ├── busqueda-semantica.component.html
  └── busqueda-semantica.component.css

Backend: busqueda/
  ├── semantic/
  │   ├── views.py          # ViewSets de búsqueda
  │   ├── serializers.py    # Serializers de búsqueda
  │   ├── text_processor.py # Procesamiento de texto
  │   └── embeddings.py     # Generación de embeddings
  ├── models.py             # Modelos relacionados
  └── services.py           # Lógica de negocio
```

**🔑 Componentes Clave:**
- **Procesamiento de Texto:** `backend/apps/busqueda/semantic/text_processor.py` - Limpieza, normalización, tokenización
- **Generación de Embeddings:** `backend/apps/busqueda/semantic/embeddings.py` - Modelos de IA, almacenamiento
- **Búsqueda Vectorial:** `backend/apps/busqueda/semantic/views.py` - Similitud coseno, ranking

**📊 Métricas:** MRR, nDCG@10, Precision@5

**🚀 Prompts Útiles:**
- "Muéstrame cómo se generan los embeddings para un envío"
- "Cómo funciona la búsqueda vectorial en el backend"
- "Dónde se procesa el texto antes de generar embeddings"
- "Cómo se calculan las métricas de búsqueda semántica"

**🔗 Relaciones:** Envios (embeddings por envío), Dashboard (métricas), API `/api/busqueda/semantica/`

---

### 📦 Gestión de Envíos

**📍 Ubicación:**
- **Frontend:** `frontend/src/app/components/envios/envios-list/`
- **Backend:** `backend/apps/archivos/`
- **Ruta:** `/envios`

**🎯 Funcionalidad:** Módulo core del sistema para crear, editar, listar, filtrar y gestionar envíos con productos, cálculo de costos y generación de comprobantes.

**📁 Estructura:**
```
Frontend: envios/
  ├── envios-list/
  │   ├── envios-list.component.ts
  │   ├── envios-list.component.html
  │   └── envios-list.component.css
  └── mis-envios/

Backend: archivos/
  ├── models.py              # Modelo Envio, Producto
  ├── views.py               # EnvioViewSet
  ├── serializers.py         # EnvioSerializer, EnvioCreateSerializer
  ├── utils_exportacion.py   # Generación de PDFs
  └── services.py            # Lógica de negocio
```

**🔑 Componentes Clave:**
- **Modelo Envio:** HAWB único, Comprador (FK), Productos (M2M), Estados, Campos calculados
- **Generación HAWB:** Secuencial automática (HAW + número)
- **Cálculo de Costos:** `backend/apps/archivos/views.py` - Usa tarifas por categoría
- **Generación PDF:** `backend/apps/archivos/utils_exportacion.py` - `generar_comprobante_envio()`, ReportLab

**📊 Estados:** PENDIENTE, EN_TRANSITO, ENTREGADO, CANCELADO

**🚀 Prompts Útiles:**
- "Muéstrame el flujo completo de creación de un envío"
- "Cómo se genera el HAWB automáticamente"
- "Dónde se calculan los costos de envío usando tarifas"
- "Cómo se genera el PDF del comprobante"
- "Cómo se relacionan productos con envíos"

**🔗 Relaciones:** Usuarios (comprador), Productos (M2M), Tarifas (cálculo costos), Búsqueda Semántica (embeddings)

**⚠️ Validaciones:** HAWB único, al menos un producto, comprador requerido, peso/valor positivos

---

### 👥 Gestión de Usuarios

**📍 Ubicación:**
- **Frontend:** `frontend/src/app/components/usuarios/usuarios-list/`
- **Backend:** `backend/apps/usuarios/`
- **Ruta:** `/usuarios`

**🎯 Funcionalidad:** Administración completa de usuarios con roles, permisos, ubicaciones geográficas y control de acceso.

**📁 Estructura:**
```
Frontend: usuarios/usuarios-list/
Backend: usuarios/
  ├── models.py          # Modelo Usuario
  ├── views.py           # UsuarioViewSet
  ├── serializers.py     # UsuarioSerializer
  ├── services.py        # UsuarioService (cambiar_password)
  ├── validators.py      # validar_password_fuerte
  └── permissions.py     # Permisos por rol
```

**🔑 Componentes Clave:**
- **Modelo Usuario:** username, nombre, correo, cedula, rol, ubicación, cupo_anual, es_activo
- **Roles:** Admin(1), Gerente(2), Digitador(3), Comprador(4)
- **Validación Contraseñas:** `backend/apps/usuarios/validators.py` - 8+ chars, mayúscula, minúscula, número, especial
- **Ubicaciones:** Selectores en cascada (Provincia → Cantón → Ciudad)

**🚀 Prompts Útiles:**
- "Cómo se implementan los roles y permisos"
- "Dónde se validan las contraseñas"
- "Cómo funcionan los selectores de ubicación en cascada"
- "Dónde se controla el acceso basado en roles"
- "Cómo se restablece una contraseña de usuario"

**🔗 Relaciones:** Envios (comprador), Autenticación (JWT), Permisos (guards/permissions)

**⚠️ Validaciones:** Username único, correo único, cédula única, contraseña fuerte, rol requerido

---

### 📦 Gestión de Productos

**📍 Ubicación:**
- **Frontend:** `frontend/src/app/components/productos/productos-list/`
- **Backend:** `backend/apps/archivos/models.py` (Modelo Producto)
- **Ruta:** `/productos`

**🎯 Funcionalidad:** Catálogo de productos con categorías, características y reutilización en múltiples envíos.

**📁 Estructura:**
```
Frontend: productos/productos-list/
Backend: archivos/
  ├── models.py          # Modelo Producto
  ├── views.py           # ProductoViewSet
  └── serializers.py     # ProductoSerializer
```

**🔑 Componentes Clave:**
- **Modelo Producto:** Descripción, Categoría, Peso (kg), Valor unitario
- **Categorías:** ELECTRONICA, ROPA, HOGAR, DEPORTES, OTROS
- **Relación con Envíos:** M2M, cantidad por envío, cálculo de totales

**🚀 Prompts Útiles:**
- "Cómo se crean y gestionan los productos"
- "Cómo se relacionan productos con envíos"
- "Dónde se calculan los totales de peso y valor por producto"
- "Cómo se reutilizan productos en múltiples envíos"

**🔗 Relaciones:** Envios (asociación M2M), Tarifas (por categoría), Cálculos (totales)

**⚠️ Validaciones:** Descripción requerida, categoría requerida, peso/valor positivos

---

### 📊 Importación desde Excel

**📍 Ubicación:**
- **Frontend:** `frontend/src/app/components/importacion-excel/`
- **Backend:** `backend/apps/archivos/views.py` (ImportacionExcelViewSet)
- **Ruta:** `/importacion-excel`

**🎯 Funcionalidad:** Carga masiva de envíos desde archivos Excel con validación previa, preview de datos y procesamiento controlado.

**📁 Estructura:**
```
Frontend: importacion-excel/
Backend: archivos/
  ├── views.py               # ImportacionExcelViewSet
  └── serializers.py         # ImportacionExcelSerializer, PreviewExcelSerializer
```

**🔑 Componentes Clave:**
- **Carga de Archivo:** Validación formato (.xlsx, .xls), lectura de datos
- **Preview de Datos:** Muestra antes de importar, validación estructura
- **Procesamiento:** Validación por fila, creación de envíos, manejo de errores

**📋 Formato Excel:** HAWB (opcional), Comprador, Productos, Estado, Observaciones

**🚀 Prompts Útiles:**
- "Cómo se valida el formato del archivo Excel"
- "Dónde se procesan los datos del Excel antes de crear envíos"
- "Cómo se manejan los errores en la importación"
- "Qué validaciones se aplican a los datos importados"

**🔗 Relaciones:** Envios (crea múltiples), Productos (puede crear nuevos), Usuarios (asocia compradores)

**⚠️ Validaciones:** Formato correcto, estructura columnas válida, datos requeridos, tipos de datos, unicidad HAWB

---

### 💰 Gestión de Tarifas

**📍 Ubicación:**
- **Frontend:** `frontend/src/app/components/tarifas/`
- **Backend:** `backend/apps/archivos/models.py` (Modelo Tarifa)
- **Ruta:** `/tarifas`

**🎯 Funcionalidad:** Configuración de tarifas de envío por categoría de producto. Se usan para calcular automáticamente los costos de envío.

**📁 Estructura:**
```
Frontend: tarifas/
Backend: archivos/
  ├── models.py          # Modelo Tarifa
  ├── views.py           # TarifaViewSet
  └── serializers.py     # TarifaSerializer
```

**🔑 Componentes Clave:**
- **Modelo Tarifa:** Categoría producto, Precio por kg, Precio base, Fecha vigencia
- **Cálculo de Costos:** `backend/apps/archivos/views.py` - Busca tarifa por categoría, calcula: cantidad × peso × precio_kg

**📊 Flujo:** Usuario crea envío → Identifica categoría producto → Busca tarifa → Calcula costo → Suma totales

**🚀 Prompts Útiles:**
- "Cómo se buscan las tarifas por categoría de producto"
- "Dónde se calculan los costos de envío usando tarifas"
- "Cómo se muestra el desglose de costos en el frontend"
- "Qué pasa si no hay tarifa para una categoría"

**🔗 Relaciones:** Productos (tarifas por categoría), Envios (cálculo costos)

**⚠️ Validaciones:** Categoría requerida, precio kg positivo, no duplicados por categoría

---

### 🗺️ Mapa de Compradores

**📍 Ubicación:**
- **Frontend:** `frontend/src/app/components/mapa-compradores/`
- **Ruta:** `/mapa-compradores`

**🎯 Funcionalidad:** Visualización geográfica interactiva de compradores en un mapa, mostrando distribución geográfica de usuarios.

**📁 Estructura:**
```
Frontend: mapa-compradores/
  ├── mapa-compradores.component.ts
  ├── mapa-compradores.component.html
  └── mapa-compradores.component.css
```

**🔑 Componentes Clave:**
- **Mapa Interactivo:** Librería de mapas (Leaflet/Google Maps), marcadores, zoom
- **Datos Compradores:** Usuarios rol Comprador, ubicación (Provincia, Cantón, Ciudad)
- **Filtros:** Por provincia, cantón, ciudad, búsqueda por nombre

**🚀 Prompts Útiles:**
- "Qué librería de mapas se usa y cómo se configura"
- "Cómo se obtienen las coordenadas de las ubicaciones"
- "Dónde se filtran los compradores por ubicación"
- "Cómo se muestran los detalles al hacer clic en un marcador"

**🔗 Relaciones:** Usuarios (rol Comprador), Ubicaciones (provincia/cantón/ciudad), API (endpoints filtrados)

---

### 📈 Dashboard y Actividades del Sistema

**📍 Ubicación:**
- **Frontend:** `frontend/src/app/components/dashboard/actividades-sistema/`
- **Backend:** `backend/apps/busqueda/` (Métricas)
- **Ruta:** `/actividades`

**🎯 Funcionalidad:** Panel de control con métricas, reportes, pruebas de rendimiento y visualizaciones del sistema.

**📁 Estructura:**
```
Frontend: dashboard/actividades-sistema/
Backend: busqueda/
  ├── views.py           # MetricasSemanticaViewSet, MetricaRendimientoViewSet
  └── models.py         # MetricaRendimiento, MetricaSemantica
```

**🔑 Componentes Clave:**
- **Métricas Semánticas:** MRR, nDCG@10, Precision@5, gráficos evolución temporal
- **Métricas Rendimiento:** Tiempo respuesta, nivel carga (1/10/30), estadísticas por fecha
- **Pruebas de Carga:** Ejecución controlada, múltiples consultas simultáneas, análisis
- **Registros Embeddings:** Estadísticas generación, procesamiento, calidad
- **Registros Manuales:** Tiempos manuales, análisis procesos

**📊 Visualizaciones:** Gráficos líneas tiempo, rendimiento, comparativas recursos

**🚀 Prompts Útiles:**
- "Cómo se calculan las métricas semánticas (MRR, nDCG, Precision)"
- "Dónde se ejecutan las pruebas de carga y cómo funcionan"
- "Cómo se muestran los gráficos en el dashboard"
- "Dónde se almacenan los registros de embeddings"
- "Cómo se filtran las métricas por fecha y nivel de carga"

**🔗 Relaciones:** Búsqueda Semántica (métricas), Envios (embeddings), API (endpoints métricas)

**⚠️ Notas:** Métricas se cargan al iniciar, gráficos después de cargar datos, pruebas requieren consultas válidas

---

## 🏗️ Arquitectura del Sistema

### Frontend (Angular 17)
- **Estructura:** Componentes standalone
- **Rutas:** `frontend/src/app/app.routes.ts`
- **Servicios:** `frontend/src/app/services/`
- **Modelos:** `frontend/src/app/models/`
- **Guards:** `frontend/src/app/guards/`

### Backend (Django REST Framework)
- **Apps principales:**
  - `backend/apps/usuarios/` - Gestión de usuarios
  - `backend/apps/archivos/` - Envíos, productos, tarifas
  - `backend/apps/busqueda/` - Búsqueda semántica y embeddings
  - `backend/apps/core/` - Configuración base

**🚀 Prompt útil:** "Muéstrame la estructura completa de la arquitectura del sistema, frontend y backend"

---

## 🔐 Autenticación y Seguridad

**Servicio:** `frontend/src/app/services/auth.service.ts`  
**Guards:** `frontend/src/app/guards/`  
**Backend:** `backend/apps/usuarios/views.py` (Autenticación JWT)

**Roles del Sistema:**
1. **Admin (1):** Acceso completo
2. **Gerente (2):** Gestión de usuarios y envíos
3. **Digitador (3):** Registro de envíos
4. **Comprador (4):** Solo sus envíos

**🚀 Prompt útil:** "Cómo funciona el sistema de autenticación y autorización con JWT y roles"

---

## 📝 Componentes Compartidos

### Cambio de Contraseña
**Componente:** `frontend/src/app/components/shared/cambio-password/`  
**Uso:** Reutilizable en perfil, registro y gestión de usuarios

**🚀 Prompt útil:** "Cómo usar el componente de cambio de contraseña en otros módulos"

---

## 🚀 Comandos Útiles

### Desarrollo Frontend
```bash
cd frontend
npm install
ng serve
```

### Desarrollo Backend
```bash
cd backend
python manage.py runserver
python manage.py migrate
```

### Scripts Útiles
- `backend/Otros scripts/restablecer_password.py` - Restablecer contraseñas
- `backend/Otros scripts/exportar_datos_supabase.py` - Exportar datos

**🚀 Prompt útil:** "Qué scripts de utilidad hay disponibles y cómo usarlos"

---

## 📚 Documentación Adicional

- **Arquitectura:** `backend/documentacion/ARQUITECTURA_EN_CAPAS.md`
- **Frontend:** `frontend/documentacion/`
- **Resumen:** `backend/documentacion/README.md`

**🚀 Prompt útil:** "Dónde encontrar documentación sobre la arquitectura y diseño del sistema"

---

## 🔧 Troubleshooting

**Problemas comunes:**
- **Error 400 al crear envío** → Verificar HAWB y validaciones en `envios-list.component.ts`
- **Métricas no se muestran** → Verificar carga de datos en `actividades-sistema.component.ts`
- **PDF con nombres largos** → Verificar `utils_exportacion.py`, uso de Paragraph
- **Errores de validación** → Revisar serializers y validators en backend

**🚀 Prompt útil:** "Cómo solucionar errores comunes en [módulo específico]"

---

## 🎯 Prompts de Navegación Rápida

1. "Muéstrame el módulo de búsqueda semántica completo"
2. "Explícame cómo crear un envío paso a paso"
3. "Cómo funcionan los roles y permisos en usuarios"
4. "Dónde se calculan los costos de envío"
5. "Cómo se importan envíos desde Excel"
6. "Dónde están las tarifas y cómo se aplican"
7. "Cómo funciona el mapa de compradores"
8. "Dónde se muestran las métricas del sistema"

---

**Última actualización:** Enero 2025 | **Versión:** 1.0

# 🗺️ Módulo de Mapa de Compradores

## 📍 Ubicación
- **Frontend:** `frontend/src/app/components/mapa-compradores/`
- **Ruta:** `/mapa-compradores`

## 🎯 Funcionalidad
Visualización geográfica interactiva de compradores en un mapa, permitiendo ver la distribución geográfica de los usuarios del sistema.

## 📁 Estructura de Archivos

### Frontend
```
mapa-compradores/
├── mapa-compradores.component.ts
├── mapa-compradores.component.html
└── mapa-compradores.component.css
```

## 🔑 Componentes Clave

### 1. Mapa Interactivo
- Librería de mapas (probablemente Leaflet, Google Maps, o similar)
- Marcadores por ubicación
- Zoom y navegación

### 2. Datos de Compradores
- Información de usuarios con rol Comprador
- Ubicación (Provincia, Cantón, Ciudad)
- Datos adicionales (nombre, cédula, etc.)

### 3. Filtros
- Por provincia
- Por cantón
- Por ciudad
- Búsqueda por nombre

## 📊 Funcionalidades

### Visualización
- Marcadores en el mapa
- Información al hacer clic
- Agrupación de marcadores cercanos
- Leyenda y controles

### Interacción
- Click en marcador muestra detalles
- Filtros dinámicos
- Búsqueda de ubicaciones

## 🚀 Prompts Útiles

1. **"Qué librería de mapas se usa y cómo se configura"**
2. **"Cómo se obtienen las coordenadas de las ubicaciones"**
3. **"Dónde se filtran los compradores por ubicación"**
4. **"Cómo se muestran los detalles al hacer clic en un marcador"**
5. **"Cómo se agrupan los marcadores cuando hay muchos compradores"**

## 🔗 Relaciones
- **Usuarios:** Obtiene datos de usuarios con rol Comprador
- **Ubicaciones:** Usa datos de provincia, cantón, ciudad
- **API:** Endpoints para obtener compradores filtrados

## 📍 Datos de Ubicación
- Provincia
- Cantón
- Ciudad
- Coordenadas (si están disponibles)


# 🗺️ Sistema de Mapa de Compradores - Ecuador

## Descripción General

Se ha implementado un sistema completo e interactivo de visualización geográfica de compradores en Ecuador, con las siguientes características:

## ✨ Características Principales

### 1. **Mapa Interactivo de Ecuador**
- Visualización de todas las ciudades principales de Ecuador
- Marcadores personalizados con emojis para ciudades (📍) y compradores (👤)
- Mapa basado en Leaflet con tiles de OpenStreetMap
- Zoom y navegación fluidos

### 2. **Ciudades Incluidas**
- Quito
- Guayaquil
- Cuenca
- Ambato
- Manta
- Loja
- Esmeraldas
- Riobamba
- Machala
- Santo Domingo
- Ibarra
- Portoviejo
- Durán
- Quevedo
- Milagro

### 3. **Funcionalidades del Mapa**

#### **Vista de Ciudades (Zoom < 10)**
- Marcadores azules (📍) representan ciudades
- Al hacer clic en una ciudad:
  - Se muestra un popup con información de la ciudad
  - Número total de compradores en esa ciudad
  - Botón para hacer zoom y ver compradores individuales

#### **Vista de Compradores Individuales (Zoom >= 10)**
- Marcadores verdes (👤) representan compradores
- Distribución automática para evitar superposición
- Al hacer clic en un comprador:
  - Información personal (nombre, email, teléfono)
  - Total de envíos realizados
  - **Últimos 5 envíos** con detalles:
    - HAWB
    - Estado (con colores: ⏳ Pendiente, 🚚 En Tránsito, ✅ Entregado, ❌ Cancelado)
    - Peso total
    - Valor total
    - Costo del servicio

### 4. **Panel de Estadísticas**
- **Compradores Totales**: Cuenta global de compradores registrados
- **Ciudades con Compradores**: Número de ciudades con al menos un comprador
- **Ciudad Seleccionada**: Indica la ciudad actualmente en foco

### 5. **Controles del Mapa**
- 🏠 **Vista General**: Vuelve a la vista completa de Ecuador
- 🔄 **Recargar**: Actualiza los datos del mapa desde el servidor

### 6. **Leyenda Interactiva**
- Explicación de marcadores y símbolos
- Estados de envío con colores correspondientes
- Siempre visible en la esquina superior derecha

### 7. **Panel de Instrucciones**
- Guía paso a paso sobre cómo usar el mapa
- Ubicado en la esquina inferior izquierda

### 8. **Lista de Resumen por Ciudad**
- Tabla debajo del mapa con:
  - Nombre de cada ciudad
  - Número total de compradores
  - Vista previa de los primeros 3 compradores
  - Indicador de compradores adicionales

## 🔧 Implementación Técnica

### Backend (Django)

#### **Modelo Usuario Actualizado**
```python
# Nuevos campos agregados
ciudad = CharField(max_length=100, choices=[...])
latitud = DecimalField(max_digits=9, decimal_places=6)
longitud = DecimalField(max_digits=9, decimal_places=6)
```

#### **Nuevos Endpoints**

1. **`GET /api/usuarios/mapa_compradores/`**
   - Retorna todos los compradores con ubicación
   - Agrupa por ciudad
   - Incluye estadísticas de envíos
   - Parámetros opcionales:
     - `ciudad`: Filtrar por ciudad específica

2. **`GET /api/usuarios/{id}/envios_comprador/`**
   - Retorna todos los envíos de un comprador
   - Incluye información detallada del comprador
   - Parámetros opcionales:
     - `estado`: Filtrar por estado de envío

#### **Serializers**
- `CompradorMapaSerializer`: Incluye datos de ubicación y envíos recientes
- Optimizado para reducir consultas a la base de datos

#### **Comando de Management**
```bash
python manage.py actualizar_ubicaciones --random
```
- Asigna ubicaciones aleatorias a compradores existentes
- Agrega variación para evitar superposición exacta
- Muestra estadísticas de distribución por ciudad

### Frontend (Angular)

#### **Componente: `MapaCompradoresComponent`**
- **Ubicación**: `src/app/components/mapa-compradores/`
- **Características**:
  - Standalone component con CommonModule
  - Integración completa con Leaflet
  - Manejo de estado y eventos de zoom
  - Iconos personalizados en SVG

#### **Modelos TypeScript**
- `CiudadEcuador`: Coordenadas de ciudades
- `CompradorMapa`: Datos de compradores con ubicación
- `EnvioSimple`: Información resumida de envíos
- `MapaResponse`: Respuesta del endpoint de mapa

#### **Estilos**
- Diseño moderno con gradientes
- Paleta de colores suaves (azul, verde, naranja, rojo)
- Responsive para móviles y tablets
- Animaciones suaves en hover y transiciones

## 📱 Acceso al Mapa

### Desde el Dashboard
- Los usuarios con rol **Admin**, **Gerente** o **Digitador** verán una tarjeta verde especial:
  - **Título**: "Mapa de Compradores"
  - **Icono**: 🗺️ (mapa)
  - **Acción**: Click para navegar al mapa

### Ruta Directa
- URL: `/mapa-compradores`
- Requiere autenticación
- Permisos: Admin, Gerente, Digitador

## 🎨 Paleta de Colores

### Estados de Envío
- 🟡 **Pendiente**: `#f59e0b` (naranja/amarillo)
- 🔵 **En Tránsito**: `#3b82f6` (azul)
- 🟢 **Entregado**: `#10b981` (verde)
- 🔴 **Cancelado**: `#ef4444` (rojo)

### Marcadores
- 🔵 **Ciudad**: `#3b82f6` (azul)
- 🟢 **Comprador**: `#10b981` (verde)

### Gradientes
- **Header**: Púrpura (`#667eea` → `#764ba2`)
- **Tarjeta Mapa**: Verde (`#10b981` → `#059669`)

## 📊 Datos de Ejemplo

Para poblar el mapa con datos de prueba:

```bash
cd backend
python manage.py actualizar_ubicaciones --random
```

Esto asignará ubicaciones aleatorias a todos los compradores existentes.

## 🔄 Flujo de Uso

1. **Inicio**: Usuario accede desde el dashboard
2. **Vista General**: Ve todas las ciudades con compradores
3. **Selección de Ciudad**: Hace clic en un marcador de ciudad
4. **Zoom Automático**: El mapa se acerca a la ciudad seleccionada
5. **Vista de Compradores**: Se muestran marcadores individuales
6. **Detalles**: Click en comprador para ver envíos
7. **Navegación**: Puede volver a la vista general en cualquier momento

## 🛠️ Configuración

### Instalación de Dependencias

```bash
cd frontend
npm install leaflet @types/leaflet
```

### Configuración de Angular

El archivo `angular.json` ya incluye los estilos de Leaflet:
```json
"styles": [
  "src/styles.css",
  "node_modules/leaflet/dist/leaflet.css"
]
```

### Migración de Base de Datos

```bash
cd backend
python manage.py makemigrations usuarios
python manage.py migrate usuarios
```

## 🚀 Tecnologías Utilizadas

- **Backend**: Django 5.2, Django REST Framework
- **Frontend**: Angular 18, TypeScript
- **Mapa**: Leaflet.js
- **Tiles**: OpenStreetMap
- **Base de Datos**: PostgreSQL (con campos Decimal para coordenadas)

## 📈 Futuras Mejoras Sugeridas

1. **Clustering**: Agrupar compradores cercanos en clusters
2. **Heatmap**: Mapa de calor basado en densidad de envíos
3. **Filtros**: Por fecha, estado, rango de valores
4. **Rutas**: Visualizar rutas de envío
5. **Geocodificación**: Convertir direcciones a coordenadas automáticamente
6. **Exportación**: Descargar datos del mapa en CSV/PDF
7. **Tiempo Real**: WebSockets para actualizaciones en vivo

## 📝 Notas Importantes

- Las coordenadas se almacenan con 6 decimales de precisión (~11cm de precisión)
- El offset automático evita que compradores en la misma ciudad se superpongan
- Los popups están optimizados para mostrar información concisa pero completa
- El mapa es completamente responsive y funciona en dispositivos móviles

## 🐛 Solución de Problemas

### El mapa no se muestra
- Verificar que Leaflet está instalado: `npm list leaflet`
- Revisar la consola del navegador para errores
- Asegurarse de que los estilos de Leaflet están cargados

### No aparecen compradores
- Ejecutar: `python manage.py actualizar_ubicaciones --random`
- Verificar que los compradores tienen `ciudad`, `latitud` y `longitud` en la BD

### Errores de permisos
- Verificar que el usuario tiene rol Admin, Gerente o Digitador
- Revisar la configuración de `roleGuard` en las rutas

## 📄 Licencia

Este módulo es parte del sistema Universal Box y sigue la misma licencia del proyecto principal.

---

**Desarrollado con 💚 para Universal Box**


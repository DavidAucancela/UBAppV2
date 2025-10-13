# Dashboard de Analytics - Universal Box

## 📊 Descripción General

El nuevo módulo de **Analytics** es una herramienta avanzada de visualización y análisis de datos que proporciona insights profundos sobre el rendimiento del sistema de gestión de envíos. Implementado con **Chart.js** y Angular 17, ofrece gráficos interactivos y filtros dinámicos para un análisis exhaustivo.

## 🎯 Características Principales

### 1. **Panel de Control Interactivo**
- Filtros por período (día, semana, mes, año, todo)
- Múltiples tipos de gráficos (línea, barras, dona, radar, área)
- Selección de métricas (envíos, productos, usuarios, ingresos)
- Exportación de datos (PDF, Excel)

### 2. **KPIs en Tiempo Real**
El dashboard muestra 6 indicadores clave:
- **Total Envíos**: Cantidad total con tasa de crecimiento
- **Envíos Pendientes**: Alertas de envíos que requieren atención
- **Total Productos**: Inventario actual
- **Valor Promedio**: Valor económico promedio por envío
- **Satisfacción Cliente**: Métrica de calidad del servicio
- **Eficiencia**: Porcentaje de envíos completados exitosamente

### 3. **Visualizaciones Avanzadas**

#### Gráfico de Evolución de Envíos
- Visualización temporal de envíos
- Adaptable a diferentes períodos
- Soporta múltiples tipos de gráficos

#### Distribución por Estados
- Gráfico tipo dona interactivo
- Muestra envíos: Entregados, En tránsito, Pendientes, Cancelados
- Códigos de color intuitivos

#### Productos por Categoría
- Gráfico de barras horizontales
- Distribución por categorías
- Colores distintivos por categoría

#### Análisis de Tendencias y Proyección
- Proyección basada en regresión lineal
- Muestra datos históricos vs proyectados
- Predicción de hasta 3 períodos futuros

#### Rendimiento Multidimensional
- Gráfico radar con 6 dimensiones:
  - Puntualidad
  - Calidad
  - Eficiencia
  - Volumen
  - Satisfacción
  - Rentabilidad

#### Indicadores Clave (KPIs)
- Gráfico de barras horizontales
- Visualización de 4 KPIs principales
- Escala normalizada al 100%

### 4. **Insights y Recomendaciones**

El sistema genera automáticamente insights inteligentes basados en los datos:
- **Crecimiento Positivo**: Alertas cuando hay aumento en envíos
- **Atención Requerida**: Notificaciones de envíos pendientes excesivos
- **Alta Satisfacción**: Reconocimiento de buen servicio
- **Análisis Predictivo**: Proyecciones de volumen futuro
- **Mejor Rendimiento**: Patrones de días óptimos
- **Objetivos del Mes**: Seguimiento de metas

## 🛠️ Tecnologías Utilizadas

- **Angular 17**: Framework principal
- **Chart.js**: Librería de gráficos
- **TypeScript**: Lenguaje de programación
- **RxJS**: Manejo de datos reactivos
- **CSS3**: Estilos y animaciones

## 📁 Estructura de Archivos

```
frontend/src/app/components/dashboard/analytics/
├── analytics.component.ts       # Lógica del componente
├── analytics.component.html     # Template HTML
├── analytics.component.css      # Estilos
└── analytics.component.spec.ts  # Tests unitarios
```

## 🚀 Cómo Usar

### Acceso al Dashboard

1. **Desde el menú principal**: Clic en "Analytics" en la barra de navegación
2. **Desde el dashboard**: Botón "Ver Analytics Avanzado" en la sección de bienvenida

### Filtros y Controles

#### Selector de Período
- **Último día**: Datos de las últimas 24 horas
- **Última semana**: Datos de los últimos 7 días
- **Último mes**: Datos de los últimos 30 días
- **Último año**: Datos de los últimos 12 meses
- **Todo el tiempo**: Todos los datos disponibles

#### Tipos de Gráfico
- **Línea**: Ideal para tendencias temporales
- **Barras**: Comparaciones categóricas
- **Dona**: Distribuciones porcentuales
- **Radar**: Análisis multidimensional
- **Área**: Tendencias con relleno

#### Métricas
- **Envíos**: Análisis de entregas
- **Productos**: Gestión de inventario
- **Usuarios**: Actividad de usuarios
- **Ingresos**: Análisis financiero

### Exportación de Datos

Los datos pueden exportarse en dos formatos:
- **PDF**: Documento visual con gráficos
- **Excel**: Datos tabulares para análisis adicional

*Nota: La funcionalidad de exportación está en desarrollo.*

## 📊 Algoritmos y Cálculos

### Tasa de Crecimiento
```typescript
tasaCrecimiento = ((enviosRecientes - enviosAnteriores) / enviosAnteriores) * 100
```

### Eficiencia
```typescript
eficiencia = (totalEnvios / (totalEnvios + enviosPendientes)) * 100
```

### Proyección Lineal
Se utiliza regresión lineal simple:
```typescript
y = mx + b
donde:
  m = pendiente (slope)
  b = intercepto (intercept)
```

### Agrupación por Período
Los datos se agrupan automáticamente según el período seleccionado:
- **Día**: Por horas
- **Semana**: Por días de la semana
- **Mes/Año**: Por fecha
- **Todo**: Por meses

## 🎨 Paleta de Colores

El dashboard utiliza una paleta coherente:
- **Primario**: `#667eea` (Azul-Púrpura)
- **Secundario**: `#764ba2` (Púrpura)
- **Éxito**: `#10b981` (Verde)
- **Advertencia**: `#f59e0b` (Naranja)
- **Peligro**: `#ef4444` (Rojo)
- **Info**: `#3b82f6` (Azul)

## 📱 Responsive Design

El dashboard es completamente responsive:
- **Desktop** (>1200px): Grid completo de 12 columnas
- **Tablet** (768-1200px): Grid adaptativo de 6 columnas
- **Mobile** (<768px): Columna única vertical

## 🔄 Actualización de Datos

Los datos se cargan al inicializar el componente y pueden refrescarse:
- Cambiando filtros de período
- Cambiando tipo de gráfico
- Cambiando métrica
- Usando el botón "Resetear"

## 🐛 Solución de Problemas

### Los gráficos no se muestran
- Verifica que Chart.js esté instalado: `npm list chart.js`
- Asegúrate de que el backend esté respondiendo correctamente

### Datos no actualizados
- Verifica la conexión con el API
- Revisa la consola del navegador para errores
- Confirma que el usuario tenga permisos adecuados

### Errores de rendimiento
- Limita el período de búsqueda
- Reduce la cantidad de datos mostrados
- Usa el filtro de período más específico

## 🔐 Permisos y Roles

El dashboard de analytics respeta los permisos del sistema:
- **Admin/Gerente**: Acceso completo a todas las visualizaciones
- **Digitador**: Vista limitada a envíos y productos
- **Comprador**: Solo visualiza sus propios envíos

## 🚧 Funcionalidades Futuras

- [ ] Exportación real a PDF y Excel
- [ ] Gráficos de comparación entre períodos
- [ ] Alertas personalizables
- [ ] Dashboard personalizable (drag & drop)
- [ ] Filtros avanzados múltiples
- [ ] Integración con BI externo
- [ ] Reportes programados
- [ ] Análisis predictivo con Machine Learning

## 📞 Soporte

Para problemas o sugerencias sobre el dashboard de analytics:
- Revisa la documentación técnica
- Contacta al equipo de desarrollo
- Abre un issue en el repositorio

---

**Versión**: 1.0.0  
**Última actualización**: Octubre 2025  
**Autor**: Equipo UBApp


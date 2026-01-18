# 📈 Módulo de Dashboard y Actividades del Sistema

## 📍 Ubicación
- **Frontend:** `frontend/src/app/components/dashboard/actividades-sistema/`
- **Backend:** `backend/apps/busqueda/` (Métricas)
- **Ruta:** `/actividades`

## 🎯 Funcionalidad
Panel de control con métricas, reportes, pruebas de rendimiento y visualizaciones del sistema. Incluye métricas de búsqueda semántica y rendimiento.

## 📁 Estructura de Archivos

### Frontend
```
dashboard/
└── actividades-sistema/
    ├── actividades-sistema.component.ts
    ├── actividades-sistema.component.html
    └── actividades-sistema.component.css
```

### Backend
```
busqueda/
├── views.py           # MetricasSemanticaViewSet, MetricaRendimientoViewSet
└── models.py         # MetricaRendimiento, MetricaSemantica
```

## 🔑 Componentes Clave

### 1. Métricas Semánticas
- **MRR (Mean Reciprocal Rank)**
- **nDCG@10** - Normalized Discounted Cumulative Gain
- **Precision@5** - Precisión en los primeros 5 resultados
- Gráficos de evolución temporal

### 2. Métricas de Rendimiento
- Tiempo de respuesta
- Nivel de carga (1, 10, 30 búsquedas)
- Estadísticas por fecha
- Comparativas de rendimiento

### 3. Pruebas de Carga
- Ejecución de pruebas controladas
- Múltiples consultas simultáneas
- Registro de resultados
- Análisis de rendimiento

### 4. Registros de Embeddings
- Estadísticas de embeddings generados
- Registros de procesamiento
- Métricas de calidad

### 5. Registros Manuales
- Registro manual de tiempos
- Análisis de procesos
- Comparativas

## 📊 Visualizaciones

### Gráficos
- Líneas de tiempo para métricas semánticas
- Gráficos de rendimiento
- Comparativas de recursos

### Filtros
- Por fecha (desde/hasta)
- Por nivel de carga
- Por tipo de métrica

## 🚀 Prompts Útiles

1. **"Cómo se calculan las métricas semánticas (MRR, nDCG, Precision)"**
2. **"Dónde se ejecutan las pruebas de carga y cómo funcionan"**
3. **"Cómo se muestran los gráficos en el dashboard"**
4. **"Dónde se almacenan los registros de embeddings"**
5. **"Cómo se filtran las métricas por fecha y nivel de carga"**
6. **"Qué datos se muestran en las estadísticas de rendimiento"**

## 🔗 Relaciones
- **Búsqueda Semántica:** Las métricas provienen de las búsquedas
- **Envios:** Los embeddings se generan para envíos
- **API:** Endpoints de métricas y estadísticas

## 📈 Métricas Disponibles

### Semánticas
- MRR promedio
- nDCG@10 promedio
- Precision@5 promedio
- Evolución temporal

### Rendimiento
- Tiempo promedio de respuesta
- Tiempo mínimo/máximo
- Desviación estándar
- Por nivel de carga

## ⚠️ Notas Importantes
- Las métricas se cargan al iniciar el componente
- Los gráficos se crean después de cargar datos
- Las pruebas de carga requieren consultas válidas
- Los filtros afectan todas las métricas


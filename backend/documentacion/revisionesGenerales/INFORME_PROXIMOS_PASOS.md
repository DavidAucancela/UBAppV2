# 📋 Informe de Próximos Pasos - Dashboard de Pruebas y Métricas

## 🎯 Estado Actual del Proyecto

### ✅ Completado

#### Backend (100%)
- ✅ App `metricas` creada e integrada
- ✅ 6 modelos de base de datos implementados
- ✅ Repositorios con métodos especializados
- ✅ Servicios de negocio completos
- ✅ Endpoints REST documentados
- ✅ Signals para registro automático
- ✅ Comando de exportación CSV
- ✅ Utilidades para cálculo de métricas (MRR, nDCG@10, Precision@5)
- ✅ Migraciones creadas
- ✅ Integración con sistema de embeddings

#### Frontend (100%)
- ✅ Servicio de métricas implementado
- ✅ Componente dashboard completo
- ✅ Gráficos con Chart.js
- ✅ Navegación por pestañas
- ✅ Filtros y exportación CSV
- ✅ Diseño responsive
- ✅ Modo oscuro soportado

---

## 🚀 Próximos Pasos Inmediatos

### 1. Aplicar Migraciones (URGENTE)

**Objetivo**: Crear las tablas en la base de datos

**Comando**:
```bash
cd backend
python manage.py migrate metricas
```

**Verificación**:
```bash
python manage.py showmigrations metricas
```

**Tiempo estimado**: 2-3 minutos

---

### 2. Poblar Datos de Prueba

**Objetivo**: Tener datos iniciales para probar el dashboard

**Comando**:
```bash
cd backend
python manage.py poblar_datos_prueba
```

**Opciones disponibles**:
```bash
# Poblar con datos limpios (elimina existentes)
python manage.py poblar_datos_prueba --limpiar

# Personalizar cantidad de métricas
python manage.py poblar_datos_prueba --cantidad-metricas 100

# Personalizar cantidad de pruebas de carga
python manage.py poblar_datos_prueba --cantidad-pruebas-carga 20
```

**Tiempo estimado**: 5-10 minutos

**Resultado esperado**:
- 5 pruebas controladas semánticas
- 50 métricas semánticas (configurable)
- 100 registros de generación de embeddings
- 10 pruebas de carga (configurable)
- 200 métricas de rendimiento
- 30 registros manuales de envíos

---

### 3. Verificar Endpoints del Backend

**Objetivo**: Confirmar que todos los endpoints funcionan correctamente

**Herramientas**:
- Swagger UI: `http://localhost:8000/api/docs/`
- Postman
- curl

**Endpoints a verificar**:

```bash
# Métricas Semánticas
GET /api/metricas/metricas-semanticas/
GET /api/metricas/metricas-semanticas/estadisticas/

# Registros de Embeddings
GET /api/metricas/registros-embedding/
GET /api/metricas/registros-embedding/estadisticas/

# Pruebas de Carga
GET /api/metricas/pruebas-carga/
POST /api/metricas/pruebas-carga/ejecutar_busqueda/

# Métricas de Rendimiento
GET /api/metricas/metricas-rendimiento/
GET /api/metricas/metricas-rendimiento/estadisticas/

# Exportación
GET /api/metricas/exportacion/metricas_semanticas/
GET /api/metricas/exportacion/metricas_rendimiento/
```

**Tiempo estimado**: 15-20 minutos

---

### 4. Probar el Frontend

**Objetivo**: Verificar que el dashboard funciona correctamente

**Pasos**:
1. Iniciar servidor de desarrollo:
   ```bash
   cd frontend
   npm start
   ```

2. Acceder al dashboard:
   - URL: `http://localhost:4200/actividades`
   - Requiere autenticación (login)

3. Verificar funcionalidades:
   - [ ] Carga de datos
   - [ ] Navegación entre pestañas
   - [ ] Visualización de gráficos
   - [ ] Filtros funcionando
   - [ ] Exportación CSV
   - [ ] Ejecución de pruebas de carga
   - [ ] Registro manual de envíos

**Tiempo estimado**: 20-30 minutos

---

## 📝 Proceso de Registro Manual

### Documentación Creada

Se ha creado el documento: `PROCESO_REGISTRO_MANUAL_ENVIOS.md`

**Ubicación**: `backend/documentacion/PROCESO_REGISTRO_MANUAL_ENVIOS.md`

**Contenido**:
- Proceso paso a paso detallado
- Ejemplo práctico completo
- Checklist de verificación
- Solución de problemas

### Pasos para Registrar Manualmente

1. **Preparar materiales**:
   - Cronómetro
   - Datos del envío
   - Acceso al dashboard

2. **Simular proceso manual**:
   - Abrir Excel
   - Buscar fila
   - Ingresar datos
   - Calcular tarifas
   - Validar y guardar
   - Medir tiempo total

3. **Registrar en dashboard**:
   - Ir a `/actividades`
   - Pestaña "Métricas de Eficiencia"
   - Sección "Registro Manual de Envíos"
   - Completar formulario
   - Guardar

**Tiempo por registro**: 4-7 minutos (proceso manual) + 1 minuto (registro en sistema)

**Recomendación**: Registrar al menos 10-20 envíos para datos estadísticamente significativos

---

## 🔧 Tareas de Configuración

### 5. Configurar Permisos (Si es necesario)

**Verificar**: Que solo administradores puedan acceder al dashboard

**Archivo**: `backend/apps/metricas/views.py`

**Líneas relevantes**:
```python
BaseService.validar_es_admin(request.user)
```

**Si necesitas cambiar permisos**:
- Modificar en `views.py` las validaciones de permisos
- Actualizar guards en `frontend/src/app/app.routes.ts`

---

### 6. Configurar Variables de Entorno

**Verificar**:
- `OPENAI_API_KEY`: Para generación de embeddings
- `DATABASE_URL`: Conexión a Supabase
- `SECRET_KEY`: Clave secreta de Django

**Archivo**: `.env` en el directorio `backend/`

---

## 📊 Tareas de Pruebas y Validación

### 7. Ejecutar Pruebas de Carga desde el Dashboard

**Objetivo**: Generar datos reales de pruebas de carga

**Pasos**:
1. Acceder a `/actividades`
2. Pestaña "Métricas de Eficiencia"
3. Sección "Ejecutar Prueba de Carga"
4. Configurar:
   - Nivel de carga: 1, 10 o 30
   - Consultas: Mínimo 1 consulta
   - Nombre de prueba (opcional)
5. Ejecutar prueba
6. Esperar resultados (puede tardar varios minutos)

**Recomendación**: Empezar con nivel 1, luego 10, finalmente 30

**Tiempo estimado por prueba**:
- Nivel 1: 1-2 minutos
- Nivel 10: 5-10 minutos
- Nivel 30: 15-30 minutos

---

### 8. Crear Pruebas Controladas Semánticas

**Objetivo**: Tener pruebas controladas para evaluación offline

**Pasos**:
1. Identificar consultas de prueba relevantes
2. Ejecutar búsquedas semánticas reales
3. Evaluar manualmente qué resultados son relevantes
4. Crear prueba controlada con:
   - Nombre descriptivo
   - Consulta
   - Lista de IDs de envíos relevantes

**Ejemplo**:
```json
{
  "nombre": "Prueba: Envíos a Quito",
  "consulta": "envíos entregados en Quito",
  "resultados_relevantes": [1, 5, 12, 23, 45]
}
```

**Tiempo estimado**: 30-60 minutos por prueba controlada

---

### 9. Ejecutar Pruebas Controladas

**Objetivo**: Calcular métricas semánticas sobre pruebas controladas

**Pasos**:
1. Acceder a `/actividades`
2. Pestaña "Métricas Semánticas"
3. Seleccionar prueba controlada
4. Ejecutar prueba
5. Revisar métricas calculadas (MRR, nDCG@10, Precision@5)

**Tiempo estimado**: 2-5 minutos por prueba

---

## 📈 Tareas de Análisis y Documentación

### 10. Exportar Datos para Análisis

**Objetivo**: Obtener datos en CSV para análisis estadístico

**Método 1: Desde el Dashboard**
1. Aplicar filtros si es necesario
2. Clic en "Exportar CSV"
3. Descargar archivo

**Método 2: Comando de Gestión**
```bash
cd backend
python manage.py exportar_metricas_csv --tipo semanticas
python manage.py exportar_metricas_csv --tipo rendimiento
python manage.py exportar_metricas_csv --tipo ambos
```

**Opciones**:
```bash
# Con filtros de fecha
python manage.py exportar_metricas_csv --tipo semanticas --fecha-desde 2025-01-01 --fecha-hasta 2025-01-31

# Directorio de salida personalizado
python manage.py exportar_metricas_csv --tipo ambos --output-dir exports
```

---

### 11. Generar Reportes para Tesis

**Objetivo**: Documentar resultados experimentales

**Datos a incluir**:
1. **Métricas Semánticas**:
   - Tabla de MRR, nDCG@10, Precision@5
   - Gráficos de evolución
   - Estadísticas descriptivas

2. **Métricas de Rendimiento**:
   - Tiempos de respuesta (promedio, mínimo, máximo)
   - Utilización de recursos (CPU, RAM)
   - Comparación manual vs automatizado

3. **Análisis Comparativo**:
   - Factor de mejora
   - Eficiencia del sistema
   - Justificación técnica

**Formato recomendado**:
- CSV para datos numéricos
- Gráficos exportados desde el dashboard
- Tablas formateadas en LaTeX/Word

---

## 🔍 Tareas de Optimización

### 12. Optimizar Consultas de Base de Datos

**Verificar**:
- Índices en campos frecuentemente consultados
- Uso de `select_related` y `prefetch_related`
- Paginación en listados grandes

**Archivos a revisar**:
- `backend/apps/metricas/repositories.py`
- `backend/apps/metricas/views.py`

---

### 13. Mejorar Rendimiento del Frontend

**Optimizaciones posibles**:
- Lazy loading de gráficos
- Paginación en tablas
- Caché de datos estadísticos
- Virtual scrolling para listas grandes

---

## 🐛 Tareas de Depuración

### 14. Monitorear Logs

**Archivos de log**:
- `logs/app.log`: Logs generales
- `logs/errors.log`: Errores
- `logs/services.log`: Logs de servicios

**Verificar**:
- Errores en generación de embeddings
- Errores en cálculo de métricas
- Errores en pruebas de carga

---

### 15. Validar Integridad de Datos

**Verificar**:
- Relaciones entre modelos
- Consistencia de datos
- Validez de métricas calculadas

**Comandos útiles**:
```bash
# Verificar registros de embeddings
python manage.py shell
>>> from apps.metricas.models import RegistroGeneracionEmbedding
>>> RegistroGeneracionEmbedding.objects.filter(estado='error').count()

# Verificar métricas sin valores
>>> from apps.metricas.models import MetricaSemantica
>>> MetricaSemantica.objects.filter(mrr__isnull=True).count()
```

---

## 📚 Tareas de Documentación

### 16. Documentar Endpoints API

**Herramienta**: Swagger UI ya configurado

**Acceso**: `http://localhost:8000/api/docs/`

**Verificar**:
- Todos los endpoints documentados
- Ejemplos de request/response
- Códigos de error documentados

---

### 17. Crear Guía de Usuario

**Contenido sugerido**:
- Cómo acceder al dashboard
- Cómo ejecutar pruebas
- Cómo interpretar métricas
- Cómo exportar datos
- Solución de problemas comunes

---

## 🎓 Tareas para Tesis

### 18. Recopilar Datos Experimentales

**Datos necesarios**:
- [ ] Mínimo 50 métricas semánticas
- [ ] Mínimo 10 pruebas de carga (diferentes niveles)
- [ ] Mínimo 20 registros manuales
- [ ] Mínimo 5 pruebas controladas ejecutadas

**Tiempo estimado**: 2-3 semanas de recolección

---

### 19. Análisis Estadístico

**Herramientas recomendadas**:
- Python (pandas, numpy, scipy)
- R
- Excel/Google Sheets

**Análisis a realizar**:
- Estadísticas descriptivas
- Intervalos de confianza
- Pruebas de hipótesis
- Análisis de varianza (ANOVA)
- Correlaciones

---

### 20. Redacción de Capítulo de Resultados

**Estructura sugerida**:
1. Introducción
2. Metodología Experimental
3. Resultados de Métricas Semánticas
4. Resultados de Rendimiento
5. Análisis Comparativo
6. Discusión
7. Conclusiones

---

## ⚠️ Consideraciones Importantes

### Seguridad
- ✅ El dashboard solo es accesible para administradores
- ✅ Validación de permisos en backend y frontend
- ⚠️ Revisar que no se expongan datos sensibles en logs

### Rendimiento
- ⚠️ Las pruebas de carga pueden tardar varios minutos
- ⚠️ Los gráficos con muchos datos pueden ser lentos
- 💡 Considerar paginación si hay más de 1000 registros

### Datos
- ⚠️ Los datos de prueba son simulados
- ⚠️ Para tesis, usar datos reales
- 💡 Validar que las métricas calculadas sean correctas

---

## 📅 Cronograma Sugerido

### Semana 1: Configuración y Pruebas Iniciales
- Día 1-2: Aplicar migraciones, poblar datos
- Día 3-4: Verificar endpoints, probar frontend
- Día 5: Ejecutar primeras pruebas de carga

### Semana 2: Recolección de Datos
- Día 1-3: Ejecutar pruebas de carga (niveles 1, 10, 30)
- Día 4-5: Registrar envíos manuales (mínimo 10)

### Semana 3: Pruebas Controladas
- Día 1-2: Crear pruebas controladas
- Día 3-4: Ejecutar pruebas controladas
- Día 5: Revisar y validar métricas

### Semana 4: Análisis y Documentación
- Día 1-2: Exportar datos, análisis estadístico
- Día 3-4: Generar gráficos y tablas
- Día 5: Redacción de resultados

---

## ✅ Checklist Final

Antes de considerar el proyecto completo:

- [ ] Migraciones aplicadas
- [ ] Datos de prueba poblados
- [ ] Endpoints verificados
- [ ] Frontend funcionando
- [ ] Pruebas de carga ejecutadas
- [ ] Registros manuales completados
- [ ] Pruebas controladas ejecutadas
- [ ] Datos exportados
- [ ] Análisis estadístico realizado
- [ ] Documentación actualizada
- [ ] Resultados listos para tesis

---

## 📞 Soporte y Recursos

### Documentación
- `PROCESO_REGISTRO_MANUAL_ENVIOS.md`: Guía de registro manual
- `nuevoDahsboardPruebas.md`: Especificaciones originales
- Swagger UI: Documentación de API

### Comandos Útiles
```bash
# Poblar datos
python manage.py poblar_datos_prueba

# Exportar CSV
python manage.py exportar_metricas_csv --tipo ambos

# Verificar migraciones
python manage.py showmigrations metricas

# Shell de Django
python manage.py shell
```

---

**Fecha del informe**: Enero 2025  
**Versión**: 1.0  
**Estado**: Listo para implementación


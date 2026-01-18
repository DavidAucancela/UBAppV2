# 📊 Guía Completa del Dashboard de Pruebas y Métricas

## 🎯 Objetivo del Dashboard

El Dashboard de Pruebas y Métricas es un sistema experimental diseñado para:
- **Evaluar el desempeño** del sistema de búsqueda semántica
- **Medir la eficiencia** del sistema automatizado vs procesos manuales
- **Recopilar datos experimentales** para análisis estadístico y documentación de tesis
- **Monitorear recursos** del sistema (CPU, RAM) durante operaciones

---

## 📋 Estructura del Dashboard

El dashboard está dividido en **3 secciones principales** accesibles mediante pestañas de navegación:

### 1️⃣ Métricas Semánticas del Sistema
### 2️⃣ Métricas de Eficiencia y Rendimiento del Sistema  
### 3️⃣ Pruebas del Sistema (Futuro - No implementado aún)

---

## 🧠 1. MÉTRICAS SEMÁNTICAS DEL SISTEMA

### 📍 Ubicación
Pestaña: **"Métricas Semánticas"** (primera pestaña)

### 🎯 Propósito
Evaluar la **calidad y precisión** del sistema de búsqueda semántica mediante métricas estándar de Information Retrieval.

### 📊 Componentes

#### A. Tarjetas de Estadísticas Resumen
Muestran promedios agregados de todas las métricas:

1. **MRR Promedio** (Mean Reciprocal Rank)
   - **Qué mide**: Posición del primer resultado relevante
   - **Rango**: 0.0 a 1.0 (1.0 = perfecto)
   - **Interpretación**: 
     - `> 0.7`: Excelente
     - `0.5 - 0.7`: Bueno
     - `< 0.5`: Necesita mejora

2. **nDCG@10 Promedio** (Normalized Discounted Cumulative Gain)
   - **Qué mide**: Calidad del ranking completo (primeros 10 resultados)
   - **Rango**: 0.0 a 1.0
   - **Interpretación**: Evalúa si los resultados más relevantes están en las primeras posiciones

3. **Precision@5 Promedio**
   - **Qué mide**: Proporción de resultados relevantes en los primeros 5
   - **Rango**: 0.0 a 1.0
   - **Interpretación**: 
     - `> 0.6`: Alta precisión
     - `0.4 - 0.6`: Precisión aceptable
     - `< 0.4`: Baja precisión

4. **Total Métricas**
   - Cantidad total de evaluaciones realizadas

#### B. Gráfico de Evolución de Métricas Semánticas
- **Tipo**: Gráfico de líneas
- **Datos**: Últimas 20 métricas registradas
- **Líneas**:
  - 🔵 Azul: MRR
  - 🔴 Rosa: nDCG@10
  - 🟢 Verde: Precision@5
- **Uso**: Visualizar tendencias y mejoras en el tiempo

#### C. Tabla de Métricas Semánticas Registradas
Muestra todas las métricas calculadas con:
- ID de la métrica
- Consulta evaluada
- Valores de MRR, nDCG@10, Precision@5
- Cantidad de resultados encontrados
- Fecha de cálculo

#### D. Registros de Generación de Embeddings
**Propósito**: Verificar que cada envío genera correctamente su embedding.

**Estadísticas**:
- **Total**: Cantidad total de registros
- **Exitosos**: Embeddings generados correctamente
- **Errores**: Fallos en la generación
- **Tiempo Promedio**: Tiempo promedio de generación

**Tabla de Registros**:
- HAWB del envío
- Estado (generado/error/omitido)
- Tiempo de generación
- Modelo utilizado
- Tipo de proceso (automático/manual/masivo)
- Fecha de generación

**Estados**:
- ✅ **Generado**: Embedding creado exitosamente
- ❌ **Error**: Fallo en la generación (ver mensaje de error)
- ⚠️ **Omitido**: Embedding ya existía, no se regeneró

#### E. Botón de Exportación CSV
- **Ubicación**: Encima del gráfico de métricas semánticas
- **Función**: Descarga un archivo CSV con todas las métricas semánticas
- **Formato**: Incluye todas las columnas de la tabla
- **Uso**: Análisis estadístico externo, importar a Excel/Python/R

---

## ⚡ 2. MÉTRICAS DE EFICIENCIA Y RENDIMIENTO DEL SISTEMA

### 📍 Ubicación
Pestaña: **"Métricas de Eficiencia y Rendimiento"** (segunda pestaña)

### 🎯 Propósito
Medir el **rendimiento y eficiencia** del sistema bajo diferentes condiciones de carga, comparando tiempos y recursos utilizados.

### 📊 Componentes

#### A. Tarjetas de Estadísticas Resumen
1. **Tiempo Promedio**
   - Tiempo promedio de respuesta del sistema
   - Formato: milisegundos o segundos
   - **Interpretación**: 
     - `< 500ms`: Excelente
     - `500ms - 2s`: Bueno
     - `> 2s`: Puede optimizarse

2. **CPU Promedio**
   - Uso promedio de procesador durante operaciones
   - Formato: Porcentaje (0-100%)
   - **Interpretación**:
     - `< 30%`: Uso normal
     - `30-50%`: Moderado
     - `> 50%`: Alto uso

3. **RAM Promedio**
   - Uso promedio de memoria
   - Formato: Megabytes (MB)
   - **Interpretación**: Depende del servidor, monitorear tendencias

4. **Operaciones Exitosas**
   - Cantidad de operaciones completadas sin errores

#### B. Gráficos de Rendimiento

**1. Gráfico de Tiempos de Respuesta**
- **Tipo**: Línea temporal
- **Datos**: Últimas 30 mediciones
- **Eje X**: Fecha y hora de medición
- **Eje Y**: Tiempo en milisegundos
- **Uso**: Identificar picos de latencia, tendencias de rendimiento

**2. Gráfico de Utilización de Recursos**
- **Tipo**: Línea temporal con doble eje Y
- **Datos**: Últimas 30 mediciones
- **Líneas**:
  - 🔴 Rojo: CPU (%)
  - 🟢 Verde: RAM (MB)
- **Uso**: Monitorear consumo de recursos, detectar cuellos de botella

#### C. Ejecutar Prueba de Carga
**Propósito**: Simular diferentes niveles de carga para medir rendimiento.

**Formulario**:
1. **Nivel de Carga**: 
   - `1`: Una sola búsqueda (baseline)
   - `10`: Diez búsquedas secuenciales (carga media)
   - `30`: Treinta búsquedas secuenciales (carga alta)

2. **Nombre de la Prueba** (opcional):
   - Identificador descriptivo
   - Ejemplo: "Prueba carga 10 búsquedas - Enero 2025"

3. **Consultas a Ejecutar**:
   - Mínimo 1 consulta
   - Puede agregar múltiples consultas
   - El sistema ejecutará cada consulta secuencialmente

**Proceso**:
1. Configurar nivel de carga y consultas
2. Clic en "Ejecutar Prueba"
3. Esperar resultados (puede tardar varios minutos)
4. Ver resultados en la tabla de historial

**Resultados Generados**:
- Tiempo promedio, mínimo y máximo
- CPU promedio y máximo
- RAM promedio y máximo
- Cantidad de operaciones exitosas vs errores

#### D. Historial de Pruebas de Carga
**Tabla con**:
- ID de la prueba
- Nombre de la prueba
- Tipo (búsqueda semántica / registro de envío)
- Nivel de carga ejecutado
- Métricas agregadas (tiempos, recursos)
- Fecha de ejecución

**Uso**: Comparar diferentes pruebas, analizar tendencias

#### E. Registro Manual de Envíos
**Propósito**: Simular y registrar tiempos del proceso manual tradicional (Excel) para comparación.

**Formulario**:
1. **HAWB**: Número de envío simulado
2. **Tiempo de Registro (segundos)**: Tiempo medido con cronómetro
3. **Notas** (opcional): Observaciones sobre el registro

**Proceso de Registro Manual**:
1. Preparar cronómetro y datos del envío
2. Simular proceso manual completo:
   - Abrir Excel
   - Buscar fila
   - Ingresar datos
   - Calcular tarifas
   - Validar y guardar
3. Detener cronómetro y anotar tiempo
4. Registrar en el dashboard

**Estadísticas Generadas**:
- Total de registros manuales
- Tiempo promedio, mínimo, máximo
- Comparación con tiempos automatizados

**Uso**: Demostrar mejoras de eficiencia (típicamente 300-500x más rápido)

#### F. Tabla de Métricas de Rendimiento Individuales
Muestra cada medición individual con:
- Proceso ejecutado
- Tiempo de respuesta
- Uso de CPU y RAM en ese momento
- Nivel de carga asociado
- Estado (éxito/error)
- Fecha de medición

**Uso**: Análisis detallado, identificar outliers, patrones de comportamiento

#### G. Botón de Exportación CSV
- **Ubicación**: Encima de la tabla de pruebas de carga
- **Función**: Descarga CSV con métricas de rendimiento
- **Uso**: Análisis estadístico, generación de reportes

---

## 🧪 3. PRUEBAS DEL SISTEMA (Futuro)

### 📍 Estado Actual
**⚠️ Esta sección NO está implementada aún**

### 🎯 Propósito Planificado
Ejecutar y gestionar pruebas unitarias e integración del sistema.

### 📊 Funcionalidades Planificadas (No implementadas)
- Listado de tests disponibles
- Ejecución de tests unitarios
- Ejecución de pruebas de integración
- Visualización de resultados de tests
- Estadísticas de cobertura de código

**Nota**: El servicio `MetricasService` ya tiene métodos preparados para esta funcionalidad, pero el frontend aún no está implementado.

---

## 🔘 Botones de Navegación

### Pestañas Principales

#### 1. Pestaña "Métricas Semánticas"
**Icono**: 🧠 (cerebro)
**Función**: Cambiar a la vista de métricas semánticas
**Contenido**: 
- Estadísticas de MRR, nDCG@10, Precision@5
- Gráfico de evolución
- Registros de embeddings

#### 2. Pestaña "Métricas de Eficiencia y Rendimiento"
**Icono**: ⚡ (tacómetro)
**Función**: Cambiar a la vista de rendimiento
**Contenido**:
- Estadísticas de tiempos y recursos
- Gráficos de rendimiento
- Pruebas de carga
- Registros manuales

**Comportamiento**:
- Solo una pestaña activa a la vez
- Al cambiar de pestaña, se recargan los gráficos
- Los filtros se mantienen entre pestañas

---

## 🎛️ Filtros Globales

### Ubicación
Arriba de las pestañas, en todas las secciones

### Filtros Disponibles

#### 1. Fecha Desde
- **Tipo**: Selector de fecha
- **Función**: Filtrar métricas desde una fecha específica
- **Formato**: YYYY-MM-DD
- **Uso**: Analizar períodos específicos

#### 2. Fecha Hasta
- **Tipo**: Selector de fecha
- **Función**: Filtrar métricas hasta una fecha específica
- **Formato**: YYYY-MM-DD
- **Uso**: Definir rango de análisis

#### 3. Nivel de Carga (solo en Rendimiento)
- **Tipo**: Selector dropdown
- **Opciones**: Todos, 1, 10, 30
- **Función**: Filtrar métricas por nivel de carga
- **Uso**: Comparar rendimiento por nivel de carga

#### 4. Botón "Aplicar Filtros"
- **Función**: Aplicar los filtros seleccionados
- **Efecto**: 
  - Recarga datos del backend
  - Actualiza gráficos
  - Actualiza tablas
  - Actualiza estadísticas

**Nota**: Los filtros NO se aplican automáticamente, debe hacer clic en "Aplicar Filtros"

---

## 📥 Botones de Exportación

### Exportar Métricas Semánticas CSV
- **Ubicación**: Encima del gráfico de métricas semánticas
- **Icono**: ⬇️ (descarga)
- **Función**: Descarga archivo CSV con métricas semánticas
- **Contenido del CSV**:
  - ID, Fecha, Consulta
  - MRR, nDCG@10, Precision@5
  - Total resultados, Relevantes encontrados
  - Tiempo procesamiento, Modelo, Métrica ordenamiento
- **Respeto de filtros**: Sí, exporta solo datos filtrados

### Exportar Métricas de Rendimiento CSV
- **Ubicación**: Encima de la tabla de pruebas de carga
- **Icono**: ⬇️ (descarga)
- **Función**: Descarga archivo CSV con métricas de rendimiento
- **Contenido del CSV**:
  - ID, Fecha, Proceso
  - Tiempo respuesta, CPU, RAM
  - Nivel carga, Estado (éxito/error)
- **Respeto de filtros**: Sí, exporta solo datos filtrados

---

## 📈 Qué se Obtiene al Final del Proceso

### Al Poblar Datos de Prueba

Al ejecutar `python manage.py poblar_datos_prueba`, obtienes:

#### 1. Datos de Prueba Iniciales
- ✅ **5 Pruebas Controladas Semánticas**
  - Consultas predefinidas
  - Resultados relevantes asignados
  - Listas para ejecutar

- ✅ **50 Métricas Semánticas** (configurable)
  - Con valores de MRR, nDCG@10, Precision@5
  - Consultas variadas
  - Fechas distribuidas en los últimos 30 días

- ✅ **100 Registros de Generación de Embeddings**
  - Estados variados (generado/error/omitido)
  - Diferentes tipos de proceso
  - Tiempos de generación simulados

- ✅ **10 Pruebas de Carga** (configurable)
  - Diferentes niveles (1, 10, 30)
  - Métricas agregadas calculadas
  - Fechas de ejecución variadas

- ✅ **200 Métricas de Rendimiento Individuales**
  - Diferentes procesos
  - Varios niveles de carga
  - Uso de CPU y RAM variado

- ✅ **30 Registros Manuales de Envíos**
  - Tiempos de registro manual simulados (2-5 minutos)
  - Datos de envíos simulados
  - Notas descriptivas

#### 2. Dashboard Funcional
- Gráficos con datos para visualizar
- Tablas pobladas con información
- Estadísticas calculadas y visibles
- Capacidad de probar todas las funcionalidades

#### 3. Base para Experimentación
- Datos iniciales para entender el sistema
- Ejemplos de cómo se ven los datos
- Punto de partida para agregar datos reales

---

### Al Completar el Proceso Completo (Para Tesis)

#### 1. Datos Experimentales Completos
- **Métricas Semánticas Reales**:
  - Mínimo 50-100 evaluaciones
  - Sobre búsquedas reales del sistema
  - Con resultados relevantes evaluados manualmente

- **Pruebas de Carga Ejecutadas**:
  - Múltiples pruebas en cada nivel (1, 10, 30)
  - Bajo diferentes condiciones
  - Con datos reales del sistema

- **Registros Manuales**:
  - Mínimo 20-30 envíos registrados manualmente
  - Tiempos reales medidos
  - Variedad de tipos de envíos

#### 2. Análisis Estadístico
- **Estadísticas Descriptivas**:
  - Promedios, medianas, desviaciones estándar
  - Valores mínimos y máximos
  - Intervalos de confianza

- **Comparaciones**:
  - Manual vs Automatizado
  - Diferentes niveles de carga
  - Evolución en el tiempo

#### 3. Visualizaciones
- **Gráficos Exportados**:
  - Gráficos de evolución de métricas
  - Gráficos de rendimiento
  - Comparativas visuales

- **Tablas Formateadas**:
  - Para inclusión en tesis
  - Con formato académico
  - Con análisis incluido

#### 4. Documentación
- **Reportes Generados**:
  - Análisis de resultados
  - Conclusiones
  - Recomendaciones

- **Datos Exportados**:
  - Archivos CSV para análisis externo
  - Datos estructurados para procesamiento

---

## 🔄 Flujo de Trabajo Recomendado

### Fase 1: Configuración Inicial
1. Aplicar migraciones
2. Poblar datos de prueba
3. Explorar el dashboard
4. Familiarizarse con las funcionalidades

### Fase 2: Recolección de Datos Reales
1. Ejecutar pruebas de carga (niveles 1, 10, 30)
2. Registrar envíos manuales (mínimo 20)
3. Crear y ejecutar pruebas controladas
4. Evaluar resultados relevantes

### Fase 3: Análisis
1. Exportar datos a CSV
2. Realizar análisis estadístico
3. Generar visualizaciones
4. Comparar resultados

### Fase 4: Documentación
1. Redactar resultados
2. Incluir gráficos y tablas
3. Analizar y concluir
4. Preparar para tesis

---

## 📊 Interpretación de Resultados

### Métricas Semánticas

**MRR > 0.7**: El sistema encuentra resultados relevantes rápidamente
**nDCG@10 > 0.6**: El ranking completo es de buena calidad
**Precision@5 > 0.5**: Los primeros resultados son mayormente relevantes

### Métricas de Rendimiento

**Tiempo < 500ms**: Respuesta muy rápida
**CPU < 30%**: Uso normal de recursos
**Mejora 300x+**: Sistema significativamente más eficiente que manual

---

**Última actualización**: Enero 2025  
**Versión**: 1.0


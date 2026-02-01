# Métricas de Evaluación para Búsqueda Semántica

## 🎯 Resumen Ejecutivo

Este documento explica las métricas de evaluación adecuadas para medir la calidad del sistema de búsqueda semántica, sus ventajas, limitaciones y cómo implementarlas.

---

## ⚠️ Análisis de Métricas Propuestas

### Métricas Consideradas
1. **Precision (Precisión)** ⚠️ **LIMITADA** - Requiere ground truth
2. **Recall (Exhaustividad)** ⚠️ **LIMITADA** - Requiere ground truth completo
3. **MRR (Mean Reciprocal Rank)** ✅ **ADECUADA** - Ideal para búsqueda

---

## 📊 1. Precision (Precisión)

### Definición
**Proporción de resultados recuperados que son relevantes.**

**Fórmula:**
```
Precision = (Resultados Relevantes Recuperados) / (Total Resultados Recuperados)
Precision = TP / (TP + FP)

Donde:
- TP (True Positives): Resultados recuperados que son relevantes
- FP (False Positives): Resultados recuperados que NO son relevantes
```

**Rango:** `[0, 1]`
- `1.0` = Todos los resultados son relevantes (perfecto)
- `0.0` = Ningún resultado es relevante (muy malo)

### Ejemplo Práctico

```
Consulta: "envíos de celulares del mes anterior"
Resultados recuperados: 10 envíos

Evaluación manual:
- 7 envíos son relevantes (tienen celulares del mes anterior)
- 3 envíos NO son relevantes (otros productos o fechas diferentes)

Precision = 7 / 10 = 0.70 (70%)
```

### ✅ Ventajas

1. **Fácil de entender:** "De lo que mostré, ¿qué porcentaje es útil?"
2. **No requiere conocer todos los resultados relevantes:** Solo evalúa lo que se recuperó
3. **Útil para evaluar calidad del ranking:** Especialmente Precision@K

### ⚠️ Limitaciones

1. **Requiere ground truth o feedback:** Necesitas saber qué resultados son relevantes
2. **No mide cobertura:** Puedes tener alta precision con pocos resultados
3. **Depende del tamaño del conjunto recuperado:** Más resultados → generalmente menor precision

### 🎯 Precision@K (Variante Recomendada)

**Precisión considerando solo los primeros K resultados.**

**Fórmula:**
```
Precision@K = (Relevantes en top K) / K
```

**Ejemplo:**
```
Consulta: "envíos a Quito"
Resultados: [HAW001, HAW002, HAW003, HAW004, HAW005]
Relevantes: HAW001, HAW003, HAW005

Precision@1 = 1/1 = 1.00 (100%)
Precision@3 = 2/3 = 0.67 (67%)
Precision@5 = 3/5 = 0.60 (60%)
```

**✅ Ventaja:** Evalúa qué tan bien están ordenados los resultados más importantes (top K).

---

## 📊 2. Recall (Exhaustividad)

### Definición
**Proporción de resultados relevantes que fueron recuperados del total de relevantes existentes.**

**Fórmula:**
```
Recall = (Resultados Relevantes Recuperados) / (Total Resultados Relevantes Existentes)
Recall = TP / (TP + FN)

Donde:
- TP (True Positives): Resultados recuperados que son relevantes
- FN (False Negatives): Resultados relevantes que NO fueron recuperados
```

**Rango:** `[0, 1]`
- `1.0` = Se recuperaron todos los resultados relevantes (perfecto)
- `0.0` = No se recuperó ningún resultado relevante (muy malo)

### Ejemplo Práctico

```
Consulta: "envíos de celulares del mes anterior"
Total de envíos relevantes en el sistema: 25
Resultados recuperados: 10
De los 10 recuperados, 7 son relevantes

Recall = 7 / 25 = 0.28 (28%)
```

### ✅ Ventajas

1. **Mide cobertura completa:** Evalúa si el sistema encuentra todos los resultados relevantes
2. **Útil para comparar algoritmos:** Permite ver qué sistema encuentra más resultados

### ⚠️ Limitaciones Críticas para Búsqueda Semántica

1. **❌ PROBLEMA PRINCIPAL: Requiere conocer TODOS los resultados relevantes**
   - En búsqueda semántica, es imposible saber cuántos resultados relevantes existen
   - No hay un "conjunto de verdad" (ground truth) predefinido
   - Requeriría evaluar manualmente TODOS los envíos del sistema para cada consulta

2. **Impracticable a escala:**
   - Con 215 envíos en el sistema, tendrías que evaluar todos para cada consulta
   - No escalable para producción

3. **Subjetivo:**
   - La "relevancia" es subjetiva y depende del usuario
   - Diferentes usuarios pueden tener diferentes criterios

### 🎯 Cuándo SÍ se puede usar Recall

**Solo en contextos controlados:**
- ✅ Dataset de evaluación con ground truth conocido (benchmarks académicos)
- ✅ Evaluación de laboratorio con conjunto de pruebas pequeño
- ✅ Cuando tienes feedback completo del usuario para todas las consultas

**❌ NO adecuado para:**
- Evaluación en producción
- Sistema en uso real
- Evaluación continua del sistema

---

## 📊 3. MRR (Mean Reciprocal Rank) ⭐ RECOMENDADA

### Definición
**Inverso de la posición del primer resultado relevante, promediado sobre múltiples consultas.**

**Fórmula:**
```
MRR = (1/N) × Σ(1 / posición_primer_relevante_i)

Donde:
- N = número de consultas
- posición_primer_relevante_i = posición del primer resultado relevante en la consulta i
```

**Rango:** `[0, 1]`
- `1.0` = El primer resultado siempre es relevante (perfecto)
- `0.0` = Nunca hay resultados relevantes en los primeros lugares (muy malo)

### Ejemplo Práctico

```
Consulta 1: "envíos a Quito"
Resultados: [HAW001, HAW002, HAW003, HAW004, HAW005]
Relevantes: HAW002 (posición 2)
RR1 = 1/2 = 0.50

Consulta 2: "celulares del mes anterior"
Resultados: [HAW010, HAW011, HAW012]
Relevantes: HAW010 (posición 1)
RR2 = 1/1 = 1.00

Consulta 3: "productos electrónicos"
Resultados: [HAW020, HAW021, HAW022, HAW023]
Relevantes: HAW023 (posición 4)
RR3 = 1/4 = 0.25

MRR = (0.50 + 1.00 + 0.25) / 3 = 0.58
```

### ✅ Ventajas (Ideal para Búsqueda Semántica)

1. **✅ Solo requiere el primer resultado relevante:**
   - No necesitas evaluar todos los resultados
   - No necesitas conocer todos los relevantes existentes

2. **✅ Fácil de obtener con feedback del usuario:**
   - Puedes usar clicks (primer click = primer relevante)
   - Puedes usar calificaciones (primer resultado con rating alto)
   - Puedes usar interacciones (primer resultado que el usuario ve)

3. **✅ Evalúa calidad del ranking:**
   - Mide qué tan bien está ordenado el primer resultado relevante
   - Refleja la experiencia del usuario (encuentra rápido lo que busca)

4. **✅ Escalable:**
   - Funciona con cualquier cantidad de resultados
   - No requiere evaluación completa del sistema

5. **✅ Estándar en búsqueda:**
   - Ampliamente usada en sistemas de recomendación
   - Métrica común en benchmarks de información retrieval

### ⚠️ Limitaciones

1. **Solo considera el primer resultado relevante:**
   - No importa si hay más resultados relevantes después
   - No distingue entre tener 1 o 10 resultados relevantes

2. **Requiere al menos un resultado relevante:**
   - Si no hay resultados relevantes, MRR = 0 (no distingue entre consultas sin resultados vs resultados mal ordenados)

### 🎯 Variantes de MRR

#### MRR@K
**Solo considera los primeros K resultados.**

```
MRR@K = (1/N) × Σ(1 / min(posición_primer_relevante_i, K+1))

Si el primer relevante está en posición > K, se cuenta como si estuviera en K+1
```

**Ejemplo con K=5:**
```
Consulta 1: Primer relevante en posición 2 → 1/2 = 0.50
Consulta 2: Primer relevante en posición 7 → 1/6 = 0.17 (se cuenta como posición 6)
```

---

## 📊 Métricas Adicionales Recomendadas

### 4. NDCG (Normalized Discounted Cumulative Gain) ⭐ MUY RECOMENDADA

### Definición
**Evalúa la calidad del ranking considerando la posición y relevancia de cada resultado.**

**Fórmula:**
```
DCG@K = Σ(i=1 to K) (relevancia_i / log2(i+1))
NDCG@K = DCG@K / IDCG@K

Donde:
- relevancia_i = nivel de relevancia del resultado en posición i (0, 1, 2, 3, ...)
- IDCG = DCG ideal (mejor ranking posible)
```

**Rango:** `[0, 1]`
- `1.0` = Ranking perfecto
- `0.0` = Ranking muy malo

### Ventajas

1. **✅ Considera múltiples niveles de relevancia:** Puedes usar 0, 1, 2, 3 (no relevante, poco, medio, muy relevante)
2. **✅ Penaliza resultados relevantes en posiciones bajas:** Más realista
3. **✅ Normalizado:** Comparables entre diferentes consultas
4. **✅ Estándar en información retrieval:** Usada en competencias académicas

### Ejemplo

```
Consulta: "envíos a Quito"
Resultados con relevancia:
1. HAW001 - relevancia 3 (muy relevante) → gain = 3/log2(2) = 3.00
2. HAW002 - relevancia 1 (poco relevante) → gain = 1/log2(3) = 0.63
3. HAW003 - relevancia 3 (muy relevante) → gain = 3/log2(4) = 1.50
4. HAW004 - relevancia 0 (no relevante) → gain = 0/log2(5) = 0.00

DCG@4 = 3.00 + 0.63 + 1.50 + 0.00 = 5.13

IDCG@4 (ranking ideal): [3, 3, 1, 0] = 3.00 + 1.50 + 0.63 + 0.00 = 5.13

NDCG@4 = 5.13 / 5.13 = 1.00 (ranking perfecto)
```

---

### 5. MAP (Mean Average Precision)

### Definición
**Promedio de precision en cada posición donde hay un resultado relevante.**

**Fórmula:**
```
AP = (1/R) × Σ(k=1 to n) Precision@k × relevante_k

Donde:
- R = número total de resultados relevantes
- relevante_k = 1 si el resultado en posición k es relevante, 0 si no
- Precision@k = precision considerando los primeros k resultados

MAP = Promedio de AP sobre todas las consultas
```

**Ventajas:**
- ✅ Considera múltiples resultados relevantes
- ✅ Evalúa calidad del ranking completo
- ✅ Estándar en evaluación de sistemas de búsqueda

**Limitaciones:**
- ⚠️ Requiere conocer todos los resultados relevantes (como Recall)

---

## 🎯 Recomendaciones para tu Sistema

### ✅ Métricas ADECUADAS (Orden de Prioridad)

1. **MRR (Mean Reciprocal Rank)** ⭐⭐⭐
   - **Prioridad:** ALTA
   - **Razón:** Ideal para búsqueda, solo requiere primer resultado relevante
   - **Implementación:** Usar feedback del usuario (clicks, calificaciones)

2. **NDCG@K** ⭐⭐⭐
   - **Prioridad:** ALTA
   - **Razón:** Evalúa ranking completo con múltiples niveles de relevancia
   - **Implementación:** Usar calificaciones de relevancia (0-3 o 0-5)

3. **Precision@K** ⭐⭐
   - **Prioridad:** MEDIA
   - **Razón:** Útil para evaluar top K resultados
   - **Implementación:** Feedback binario (relevante/no relevante)

### ⚠️ Métricas LIMITADAS

4. **Recall** ❌
   - **Prioridad:** BAJA (solo para evaluación controlada)
   - **Razón:** Requiere conocer TODOS los resultados relevantes (impracticable)
   - **Cuándo usar:** Solo en benchmarks académicos con ground truth

5. **MAP (Mean Average Precision)** ⚠️
   - **Prioridad:** MEDIA-BAJA
   - **Razón:** También requiere ground truth completo
   - **Cuándo usar:** Si tienes evaluación exhaustiva con usuarios

---

## 📝 Implementación Práctica

### Opción 1: Feedback Implícito (Recomendado para Producción)

**Usar interacciones del usuario:**
- Clicks en resultados
- Tiempo de visualización
- Descargas/impresiones
- Navegación (si clickea un resultado y luego busca otro, el primero no era relevante)

**Implementación:**
```python
# Calcular MRR con clicks
def calcular_mrr_con_clicks(consultas_resultados_clicks):
    """
    consultas_resultados_clicks: [
        {
            'consulta': "envíos a Quito",
            'resultados': [HAW001, HAW002, HAW003, ...],
            'clicks': [HAW002]  # Usuario clickeó HAW002
        },
        ...
    ]
    """
    reciprocal_ranks = []
    
    for consulta_data in consultas_resultados_clicks:
        resultados = consulta_data['resultados']
        clicks = consulta_data['clicks']
        
        if clicks:
            primer_click = clicks[0]
            posicion = resultados.index(primer_click) + 1  # +1 porque empieza en 1
            reciprocal_ranks.append(1.0 / posicion)
        else:
            reciprocal_ranks.append(0.0)  # No hubo clicks = no relevante
    
    return sum(reciprocal_ranks) / len(reciprocal_ranks)
```

### Opción 2: Feedback Explícito (Recomendado para Evaluación)

**Usar calificaciones del usuario:**
- Botón "Útil" / "No útil"
- Rating 1-5 estrellas
- Calificación de relevancia (0-3)

**Implementación:**
```python
# Calcular NDCG con calificaciones
def calcular_ndcg_con_calificaciones(resultados, calificaciones, k=10):
    """
    resultados: Lista de IDs de resultados en orden de ranking
    calificaciones: Dict {resultado_id: relevancia (0-3)}
    k: Número de resultados a considerar
    """
    dcg = 0.0
    for i, resultado_id in enumerate(resultados[:k], 1):
        relevancia = calificaciones.get(resultado_id, 0)
        dcg += relevancia / math.log2(i + 1)
    
    # IDCG: ordenar calificaciones de mayor a menor
    relevancias_ideales = sorted(calificaciones.values(), reverse=True)[:k]
    idcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(relevancias_ideales))
    
    return dcg / idcg if idcg > 0 else 0.0
```

### Opción 3: Evaluación Manual (Solo para Pruebas)

**Evaluar manualmente un conjunto de consultas:**
- Seleccionar 20-50 consultas representativas
- Evaluar manualmente qué resultados son relevantes
- Calcular todas las métricas

---

## 📊 Resumen Comparativo

| Métrica | Requiere Ground Truth | Adecuada para Producción | Facilidad Implementación | Considera Ranking |
|---------|----------------------|-------------------------|-------------------------|-------------------|
| **MRR** | ❌ No (solo primer relevante) | ✅✅✅ Sí | ✅✅✅ Fácil | ✅ Sí (posición) |
| **NDCG** | ⚠️ Parcial (calificaciones) | ✅✅✅ Sí | ✅✅ Media | ✅✅✅ Sí (múltiples posiciones) |
| **Precision@K** | ⚠️ Parcial (feedback top K) | ✅✅ Sí | ✅✅✅ Fácil | ✅ Sí (top K) |
| **Recall** | ❌❌ Sí (todos los relevantes) | ❌ No | ❌ Difícil | ❌ No |
| **MAP** | ❌❌ Sí (todos los relevantes) | ⚠️ Limitada | ❌ Difícil | ✅✅ Sí |

---

## ✅ Conclusión y Recomendación Final

### Para tu Sistema de Búsqueda Semántica:

**Métricas Recomendadas (en orden de prioridad):**

1. **MRR (Mean Reciprocal Rank)** ⭐⭐⭐
   - Implementar primero
   - Usar feedback implícito (clicks)
   - Fácil de implementar y muy adecuada para búsqueda

2. **NDCG@10** ⭐⭐⭐
   - Implementar segundo
   - Usar feedback explícito (calificaciones) o implícito (tiempo de visualización)
   - Evalúa ranking completo

3. **Precision@5 y Precision@10** ⭐⭐
   - Implementar como complemento
   - Útil para evaluar los resultados más importantes

**NO Recomendar:**
- ❌ **Recall:** Requiere conocer TODOS los resultados relevantes (impracticable)
- ⚠️ **MAP:** Similar a Recall, requiere ground truth completo

### Justificación para tu Tesis:

> "Se seleccionaron MRR y NDCG@K como métricas principales de evaluación porque: (1) MRR mide la calidad del ranking evaluando la posición del primer resultado relevante, siendo ideal para sistemas de búsqueda donde el usuario busca encontrar rápidamente información útil; (2) NDCG@K evalúa la calidad del ranking completo considerando múltiples niveles de relevancia y penalizando resultados relevantes en posiciones bajas; (3) Ambas métricas pueden calcularse con feedback del usuario (clicks, calificaciones) sin requerir un ground truth completo, siendo prácticas para evaluación en producción. Se descartó Recall debido a que requiere conocer todos los resultados relevantes existentes en el sistema, lo cual es impracticable en un entorno de producción con cientos de envíos."

---

## 🔄 Proceso de Evaluación Implementado y Tabla Comparativa

### Flujo para identificar la eficiencia del panel semántico

1. **Definir pruebas controladas**  
   Crear consultas de prueba con su *ground truth* (lista de IDs de envíos relevantes) en el dashboard de métricas (Pruebas Controladas Semánticas).

2. **Ejecutar evaluaciones**  
   - Desde el **frontend**: pestaña "Métricas semánticas del sistema" → ejecutar cada prueba controlada.  
   - Desde **consola**:  
     `python manage.py evaluar_panel_semantico --ejecutar`  
     (ejecuta todas las pruebas activas y calcula MRR, nDCG@10, Precision@5).

3. **Ver resultados**  
   - **API**: `GET /api/metricas/metricas-semanticas/reporte-comparativo/?fecha_desde=&fecha_hasta=`  
     Devuelve `filas` (tabla por evaluación) y `resumen` (promedios e interpretación global).  
   - **Frontend**: pestaña "Métricas semánticas del sistema" → bloque **"Eficiencia del panel semántico"** con tabla comparativa y resumen.  
   - **Consola**: el comando `evaluar_panel_semantico` imprime la tabla en terminal; opción `--exportar reporte.csv` guarda CSV.

4. **Interpretación**  
   - **MRR ≥ 0.7**: Bueno (el primer resultado relevante suele estar arriba).  
   - **nDCG@10 ≥ 0.6**: Bueno (ranking de calidad).  
   - **Precision@5 ≥ 0.5**: Bueno (varios relevantes en el top 5).  
   El reporte asigna a cada fila y al resumen una etiqueta: *Bueno*, *Regular* o *Mejorable*.

### Ejemplo de tabla comparativa de resultados

| ID | Consulta                    | Fecha       | MRR   | nDCG@10 | Precision@5 | Interpretación |
|----|-----------------------------|------------|-------|---------|-------------|----------------|
| 1  | envíos a Quito              | 2025-01-28 | 0.833 | 0.72    | 0.60        | Bueno          |
| 2  | celulares del mes anterior  | 2025-01-28 | 1.000 | 0.85    | 0.80        | Bueno          |
| 3  | productos electrónicos      | 2025-01-28 | 0.250 | 0.41    | 0.20        | Mejorable      |
| **Resumen** | **3 evaluaciones**   |            | **0.69** | **0.66** | **0.53**   | **Aceptable**  |

- **Resumen**: total de evaluaciones, promedios de MRR / nDCG@10 / Precision@5 e interpretación global (Eficiente / Aceptable / Mejorable).

### Ubicación en el código

- **Cálculo de métricas**: `backend/apps/metricas/utils.py` (`calcular_mrr`, `calcular_ndcg_k`, `calcular_precision_k`, `interpretar_metrica`).  
- **Reporte comparativo**: `backend/apps/metricas/repositories.py` → `MetricaSemanticaRepository.obtener_reporte_comparativo`.  
- **API**: `GET .../metricas-semanticas/reporte-comparativo/`.  
- **Comando**: `python manage.py evaluar_panel_semantico [--ejecutar] [--exportar archivo.csv]`.

---

## 📚 Referencias

1. **Manning et al. (2008)** - "Introduction to Information Retrieval"
   - Capítulo 8: Evaluation in information retrieval

2. **Järvelin & Kekäläinen (2002)** - "Cumulated gain-based evaluation of IR techniques"
   - Introducción de NDCG

3. **Voorhees (1999)** - "The TREC-8 Question Answering Track Report"
   - Uso de MRR en evaluación de sistemas de búsqueda

4. **Croft et al. (2010)** - "Search Engines: Information Retrieval in Practice"
   - Capítulo sobre evaluación de sistemas de búsqueda


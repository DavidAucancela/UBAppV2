# Resumen: Métricas de Evaluación para Búsqueda Semántica

## ⚠️ Respuesta Directa: ¿Cuál NO es adecuada?

**❌ RECALL NO ES ADECUADA** para evaluación en producción.

**Razón:** Requiere conocer **TODOS** los resultados relevantes que existen en el sistema, lo cual es:
- Impracticable (tendrías que evaluar manualmente todos los envíos para cada consulta)
- No escalable (con 215+ envíos es inviable)
- Requiere ground truth completo (imposible en producción)

---

## 📊 Resumen de Métricas

### 1. Precision (Precisión) ⚠️ LIMITADA

**Definición:** Proporción de resultados recuperados que son relevantes.

**Fórmula:**
```
Precision = Resultados Relevantes Recuperados / Total Resultados Recuperados
```

**Rango:** `[0, 1]`

**✅ Ventajas:**
- Fácil de entender
- No requiere conocer todos los relevantes (solo los recuperados)

**⚠️ Limitaciones:**
- Requiere feedback para saber qué es relevante
- No mide cobertura

**🎯 Variante Recomendada: Precision@K**
```
Precision@K = Relevantes en top K / K
```
Evalúa los primeros K resultados (más útil para búsqueda).

---

### 2. Recall (Exhaustividad) ❌ NO ADECUADA

**Definición:** Proporción de resultados relevantes recuperados del total de relevantes existentes.

**Fórmula:**
```
Recall = Resultados Relevantes Recuperados / Total Resultados Relevantes Existentes
```

**Rango:** `[0, 1]`

**❌ PROBLEMA PRINCIPAL:**
- Requiere conocer **TODOS** los resultados relevantes que existen
- En búsqueda semántica es **IMPOSIBLE** saber cuántos resultados relevantes existen
- Requeriría evaluar manualmente todos los envíos del sistema para cada consulta

**Cuándo SÍ se puede usar:**
- ✅ Solo en benchmarks académicos con ground truth predefinido
- ✅ Evaluación de laboratorio con conjunto pequeño y controlado
- ❌ NO para producción o evaluación continua

---

### 3. MRR (Mean Reciprocal Rank) ✅ ADECUADA - RECOMENDADA

**Definición:** Inverso de la posición del primer resultado relevante, promediado sobre consultas.

**Fórmula:**
```
MRR = (1/N) × Σ(1 / posición_primer_relevante_i)
```

**Rango:** `[0, 1]`
- `1.0` = Primer resultado siempre es relevante (perfecto)
- `0.0` = Nunca hay resultados relevantes en los primeros lugares

**Ejemplo:**
```
Consulta 1: Primer relevante en posición 2 → RR = 1/2 = 0.50
Consulta 2: Primer relevante en posición 1 → RR = 1/1 = 1.00
Consulta 3: Primer relevante en posición 4 → RR = 1/4 = 0.25

MRR = (0.50 + 1.00 + 0.25) / 3 = 0.58
```

**✅ Ventajas (Ideal para Búsqueda):**
- Solo requiere el primer resultado relevante (no todos)
- Fácil de obtener con feedback (clicks, calificaciones)
- Evalúa calidad del ranking (experiencia del usuario)
- Escalable y práctico para producción
- Estándar en sistemas de búsqueda

**⚠️ Limitación:**
- Solo considera el primer resultado relevante (no importa si hay más después)

---

## 🎯 Métricas Adicionales Recomendadas

### 4. NDCG@K (Normalized Discounted Cumulative Gain) ⭐⭐ MUY RECOMENDADA

**Definición:** Evalúa la calidad del ranking considerando posición y relevancia de múltiples resultados.

**Fórmula:**
```
DCG@K = Σ(i=1 to K) (relevancia_i / log2(i+1))
NDCG@K = DCG@K / IDCG@K
```

**✅ Ventajas:**
- Considera múltiples niveles de relevancia (0, 1, 2, 3...)
- Penaliza resultados relevantes en posiciones bajas
- Normalizado (comparables entre consultas)
- Estándar en información retrieval

**Ejemplo:**
```
Resultados con relevancia:
1. relevancia 3 → gain = 3/log2(2) = 3.00
2. relevancia 1 → gain = 1/log2(3) = 0.63
3. relevancia 3 → gain = 3/log2(4) = 1.50

DCG@3 = 3.00 + 0.63 + 1.50 = 5.13
IDCG@3 (ideal) = 5.13
NDCG@3 = 5.13 / 5.13 = 1.00 (perfecto)
```

---

## 📊 Comparativa Rápida

| Métrica | Ground Truth Completo | Producción | Facilidad | Ranking |
|---------|----------------------|------------|-----------|---------|
| **MRR** | ❌ No | ✅✅✅ | ✅✅✅ | ✅ |
| **NDCG@K** | ⚠️ Parcial | ✅✅✅ | ✅✅ | ✅✅✅ |
| **Precision@K** | ⚠️ Parcial | ✅✅ | ✅✅✅ | ✅ |
| **Recall** | ❌❌ Sí | ❌ | ❌ | ❌ |

---

## ✅ Recomendación Final

### Para tu Sistema (Orden de Prioridad):

1. **MRR (Mean Reciprocal Rank)** ⭐⭐⭐
   - Implementar primero
   - Usar feedback implícito (clicks del usuario)
   - Ideal para búsqueda semántica

2. **NDCG@10** ⭐⭐⭐
   - Implementar segundo
   - Usar feedback explícito (calificaciones) o implícito (tiempo de visualización)
   - Evalúa ranking completo

3. **Precision@5 y Precision@10** ⭐⭐
   - Implementar como complemento
   - Evalúa top K resultados

**NO usar:**
- ❌ **Recall:** Requiere ground truth completo (impracticable)
- ⚠️ **MAP:** Similar a Recall, requiere ground truth completo

---

## 📝 Cita para Tesis

> "Se seleccionaron MRR y NDCG@K como métricas principales de evaluación. MRR mide la posición del primer resultado relevante, siendo ideal para búsqueda donde el usuario busca encontrar información rápidamente. NDCG@K evalúa el ranking completo considerando múltiples niveles de relevancia. Ambas métricas pueden calcularse con feedback del usuario sin requerir ground truth completo, siendo prácticas para producción. Se descartó Recall porque requiere conocer todos los resultados relevantes existentes, lo cual es impracticable en producción."

---

## 🔧 Implementación Rápida

### MRR con Clicks (Feedback Implícito)

```python
def calcular_mrr(consultas_resultados_clicks):
    """
    consultas_resultados_clicks: [
        {
            'resultados': [HAW001, HAW002, HAW003, ...],
            'clicks': [HAW002]  # Usuario clickeó HAW002
        },
        ...
    ]
    """
    reciprocal_ranks = []
    for data in consultas_resultados_clicks:
        if data['clicks']:
            pos = data['resultados'].index(data['clicks'][0]) + 1
            reciprocal_ranks.append(1.0 / pos)
        else:
            reciprocal_ranks.append(0.0)
    return sum(reciprocal_ranks) / len(reciprocal_ranks)
```

### NDCG@K con Calificaciones

```python
import math

def calcular_ndcg(resultados, calificaciones, k=10):
    """
    resultados: Lista de IDs en orden de ranking
    calificaciones: Dict {resultado_id: relevancia (0-3)}
    """
    dcg = sum(calificaciones.get(r, 0) / math.log2(i+2) 
              for i, r in enumerate(resultados[:k]))
    relevancias_ideales = sorted(calificaciones.values(), reverse=True)[:k]
    idcg = sum(r / math.log2(i+2) for i, r in enumerate(relevancias_ideales))
    return dcg / idcg if idcg > 0 else 0.0
```


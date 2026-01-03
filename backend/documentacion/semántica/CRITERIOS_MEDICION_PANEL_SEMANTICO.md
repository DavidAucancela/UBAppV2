# 📊 Criterios de Medición del Panel Semántico

## 📋 Resumen Ejecutivo

El sistema de búsqueda semántica calcula **múltiples métricas de similitud** para cada resultado de búsqueda. Estas métricas se calculan **por cada consulta** y permiten evaluar la relevancia de los envíos encontrados desde diferentes perspectivas matemáticas.

---

## 🔢 Métricas Aplicadas (Por Cada Resultado)

### 1. **Cosine Similarity (Similitud Coseno)** - Métrica Principal ⭐

**Ubicación**: `backend/apps/busqueda/semantic/vector_search.py` - Línea 179-185

**Fórmula**: `cos(θ) = (A · B) / (||A|| × ||B||)`

**Características**:
- **Rango**: `[-1, 1]`
- **1.0**: Vectores idénticos (máxima similitud semántica)
- **0.0**: Vectores ortogonales (sin relación)
- **-1.0**: Vectores opuestos

**Ventajas**:
- ✅ Normalizada (rango acotado)
- ✅ Invariante a escala (ignora magnitud)
- ✅ Estándar en NLP (Word2Vec, BERT, OpenAI)
- ✅ Mide similitud semántica direccional

**Código**:
```python
cosine_similarity = np.dot(consulta_vec, envio_vec) / (consulta_norm * envio_norm)
```

---

### 2. **Dot Product (Producto Punto)**

**Ubicación**: `backend/apps/busqueda/semantic/vector_search.py` - Línea 187-189

**Fórmula**: `A · B = Σ(Ai × Bi)`

**Características**:
- **Rango**: `[0, ∞]`
- **Mayor valor**: Más similar
- **0**: Sin similitud

**Limitación**: 
- ⚠️ Depende de la magnitud de los vectores
- ⚠️ Vectores más largos tienen productos punto más altos, incluso si no son más similares semánticamente

**Código**:
```python
dot_product = float(np.dot(consulta_vec, envio_vec))
```

---

### 3. **Euclidean Distance (Distancia Euclidiana)**

**Ubicación**: `backend/apps/busqueda/semantic/vector_search.py` - Línea 191-193

**Fórmula**: `d = √(Σ(Ai - Bi)²)`

**Características**:
- **Rango**: `[0, ∞]`
- **0**: Vectores idénticos
- **Mayor valor**: Más diferente

**Limitación**:
- ⚠️ Requiere normalización adicional para comparación
- ⚠️ Sensible a la escala de los vectores

**Código**:
```python
euclidean_distance = float(np.linalg.norm(consulta_vec - envio_vec))
```

---

### 4. **Manhattan Distance (Distancia Manhattan/L1)**

**Ubicación**: `backend/apps/busqueda/semantic/vector_search.py` - Línea 195-197

**Fórmula**: `d = Σ|Ai - Bi|`

**Características**:
- **Rango**: `[0, ∞]`
- **0**: Vectores idénticos
- **Mayor valor**: Más diferente

**Limitación**:
- ⚠️ Similar a euclidean, menos sensible a outliers pero aún requiere normalización
- ⚠️ Suma de diferencias absolutas, no captura bien la similitud direccional

**Código**:
```python
manhattan_distance = float(np.sum(np.abs(consulta_vec - envio_vec)))
```

---

### 5. **Score Combinado** - Métrica Final para Ordenamiento

**Ubicación**: `backend/apps/busqueda/semantic/vector_search.py` - Línea 249-251

**Fórmula**: `score_combinado = (cosine + 1) / 2 + boost_exactas`

**Componentes**:
1. **Cosine normalizado**: `(cosine_similarity + 1) / 2` → Convierte `[-1, 1]` a `[0, 1]`
2. **Boost por coincidencias exactas**: Hasta `0.15` (normal) o `0.25` (productos)
3. **Boost adicional por productos**: Hasta `0.10` adicionales

**Características**:
- **Rango**: `[0, 1]`
- **Mayor valor**: Mayor relevancia
- **Umbral mínimo**: `0.35` (normal) o `0.30` (productos)

**Código**:
```python
cosine_normalizado = (cosine_similarity + 1) / 2
score_combinado = min(cosine_normalizado + boost_exactas, 1.0)
```

---

### 6. **Boost por Coincidencias Exactas**

**Ubicación**: `backend/apps/busqueda/semantic/vector_search.py` - Línea 200-247

**Proceso**:
1. Busca coincidencias exactas de palabras entre la consulta y el texto indexado
2. Calcula un score de coincidencias (0.0 a 1.0)
3. Aplica boost base:
   - **0.15** para consultas normales
   - **0.25** para consultas de productos
4. Boost adicional para productos si hay coincidencias en descripciones

**Ejemplo**:
```
Consulta: "envíos a Quito"
Texto indexado: "HAWB: ABC123 | Ciudad: Quito | Estado: Entregado"
Coincidencias: "Quito" → boost = 0.15
```

---

## 📊 Estructura de Datos de Cada Resultado

Cada resultado de búsqueda incluye todas estas métricas:

```json
{
  "envio": {...},
  "puntuacionSimilitud": 0.9200,        // Score combinado (principal)
  "cosineSimilarity": 0.8500,           // Similitud coseno [-1, 1]
  "dotProduct": 12.5000,                // Producto punto [0, ∞]
  "euclideanDistance": 0.4500,           // Distancia euclidiana [0, ∞]
  "manhattanDistance": 2.1000,           // Distancia Manhattan [0, ∞]
  "scoreCombinado": 0.9200,              // Score final [0, 1]
  "boostExactas": 0.0700,                // Boost aplicado
  "boostProductos": 0.0500,              // Boost adicional por productos
  "coincidenciasExactas": 0.5000,        // Score de coincidencias
  "analisisMetricas": {...},             // Análisis comparativo detallado
  "fragmentosRelevantes": [...],         // Fragmentos destacados
  "razonRelevancia": "...",              // Explicación textual
  "textoIndexado": "..."                  // Texto usado para embedding
}
```

---

## 👁️ Cómo Visualizar los Resultados

### 1. **Visualización en la Tabla de Resultados** (Frontend)

**Ubicación**: `frontend/src/app/components/busqueda-semantica/busqueda-semantica.component.html` - Línea 502-514

**Lo que se muestra**:
- ✅ **Barra visual de relevancia**: Muestra el `scoreCombinado` como porcentaje
- ✅ **Color dinámico**: Verde (alta), Amarillo (media), Rojo (baja)
- ✅ **Porcentaje**: Formato `XX%` de similitud

**Código HTML**:
```html
<td *ngIf="configuracion.mostrarPuntuacion" class="celda-relevancia">
  <div class="indicador-relevancia">
    <div class="barra-relevancia">
      <div 
        class="relleno-relevancia"
        [style.width.%]="resultado.puntuacionSimilitud * 100"
        [style.background-color]="obtenerColorSimilitud(resultado.puntuacionSimilitud)"
      ></div>
    </div>
    <span class="texto-relevancia">
      {{ formatearPorcentajeSimilitud(resultado.puntuacionSimilitud) }}
    </span>
  </div>
</td>
```

---

### 2. **Métricas Agregadas en el Header** (Por Consulta)

**Ubicación**: `frontend/src/app/components/busqueda-semantica/busqueda-semantica.component.html` - Línea 448-463

**Lo que se muestra**:
- ✅ **Modelo utilizado**: `text-embedding-3-small`
- ✅ **Tiempo de respuesta**: En milisegundos (ms)
- ✅ **Costo de consulta**: En USD
- ✅ **Tokens utilizados**: Número de tokens

**Ejemplo visual**:
```
🔍 5 resultado(s) encontrado(s)
💻 Modelo: text-embedding-3-small
⏱️ 156ms
💰 Costo: $0.0001
# 10 tokens
```

---

### 3. **Análisis Comparativo de Métricas** (Disponible en API)

**Ubicación**: `backend/apps/busqueda/services.py` - Línea 527-699

**Endpoint**: `GET /api/busqueda/semantica/analisis-metricas/`

**Contenido**:
- Comparación detallada de las 4 métricas
- Justificación de por qué cosine similarity es la mejor
- Interpretación de valores
- Referencias académicas
- Fórmulas matemáticas

**Estructura del análisis**:
```json
{
  "metricaSeleccionada": "cosine_similarity",
  "justificacion": {
    "teorica": "...",
    "practica": "...",
    "ventajas": [...],
    "referenciasAcademicas": [...]
  },
  "comparacion": {
    "cosine": {...},
    "dotProduct": {...},
    "euclidean": {...},
    "manhattan": {...}
  },
  "scoreCombinado": {
    "valor": 0.92,
    "porcentaje": 92.0,
    "formula": "score_combinado = (cosine + 1) / 2 + boost_exactas",
    "componentes": {...}
  },
  "conclusion": {...}
}
```

**Nota**: Este análisis está disponible en cada resultado individual en el campo `analisisMetricas`, pero actualmente **no se muestra en el frontend**. Se puede acceder mediante la API.

---

### 4. **Métricas Agregadas del Usuario**

**Endpoint**: `GET /api/busqueda/semantica/metricas/`

**Ubicación**: `backend/apps/busqueda/services.py` - Línea 752-760

**Respuesta**:
```json
{
  "totalBusquedas": 150,
  "tiempoPromedioRespuesta": 280.5,
  "totalEmbeddings": 1250
}
```

**Uso**: Estadísticas generales de todas las búsquedas del usuario.

---

## ✅ Confirmación: Métricas por Cada Consulta

**SÍ, estas métricas se calculan para cada consulta y cada resultado**:

1. **Por cada consulta**:
   - Se genera un embedding de la consulta
   - Se calculan métricas agregadas (tiempo, costo, tokens)
   - Se guarda en el historial con todas las métricas

2. **Por cada resultado de la consulta**:
   - Se calculan las 4 métricas de similitud (cosine, dot product, euclidean, manhattan)
   - Se calcula el boost por coincidencias exactas
   - Se calcula el score combinado
   - Se genera el análisis comparativo de métricas
   - Se extraen fragmentos relevantes
   - Se genera la razón de relevancia

**Ejemplo de flujo**:
```
Consulta: "envíos entregados en Quito"
  ↓
Resultado 1:
  - cosineSimilarity: 0.85
  - dotProduct: 12.5
  - euclideanDistance: 0.45
  - manhattanDistance: 2.1
  - scoreCombinado: 0.92
  - boostExactas: 0.07
  - analisisMetricas: {...}

Resultado 2:
  - cosineSimilarity: 0.78
  - dotProduct: 10.2
  - euclideanDistance: 0.58
  - manhattanDistance: 2.8
  - scoreCombinado: 0.85
  - boostExactas: 0.07
  - analisisMetricas: {...}
```

---

## 🔍 Dónde Encontrar las Métricas en el Código

### Backend

1. **Cálculo de métricas**: 
   - `backend/apps/busqueda/semantic/vector_search.py` - Línea 144-266

2. **Análisis comparativo**:
   - `backend/apps/busqueda/services.py` - Línea 440-699

3. **Formateo de resultados**:
   - `backend/apps/busqueda/services.py` - Línea 377-435

4. **Endpoints**:
   - `backend/apps/busqueda/views.py` - Línea 260-291 (búsqueda)
   - `backend/apps/busqueda/views.py` - Línea 372-376 (métricas)
   - `backend/apps/busqueda/views.py` - Línea 400-422 (análisis)

### Frontend

1. **Visualización de resultados**:
   - `frontend/src/app/components/busqueda-semantica/busqueda-semantica.component.html` - Línea 502-514

2. **Métricas agregadas**:
   - `frontend/src/app/components/busqueda-semantica/busqueda-semantica.component.html` - Línea 448-463

3. **Modelos TypeScript**:
   - `frontend/src/app/models/busqueda-semantica.ts` - Línea 74-138

---

## 📝 Notas Importantes

1. **Métrica Principal**: El sistema usa `scoreCombinado` para ordenar y filtrar resultados, que combina cosine similarity normalizado con boost por coincidencias exactas.

2. **Umbral Adaptativo**: Si hay más de 3 resultados, se aplica un umbral adaptativo basado en el percentil 75 de los scores.

3. **Análisis Detallado**: Cada resultado incluye `analisisMetricas` con justificación académica, pero actualmente **no se muestra en el frontend**. Se puede acceder mediante la API o agregando una sección en el modal de detalles.

4. **Métricas por Consulta**: Todas las métricas se calculan y guardan para cada búsqueda individual, permitiendo análisis posterior y optimización.

---

## 🚀 Recomendaciones para Mejorar la Visualización

1. **Agregar sección de métricas detalladas en el modal de detalles**:
   - Mostrar todas las métricas (cosine, dot product, euclidean, manhattan)
   - Mostrar el análisis comparativo (`analisisMetricas`)
   - Mostrar gráficos comparativos

2. **Panel de métricas expandible**:
   - Botón para expandir/colapsar métricas detalladas
   - Tabla comparativa de las 4 métricas
   - Visualización gráfica (barras, radar chart)

3. **Exportar métricas**:
   - Descargar CSV con todas las métricas
   - Generar PDF con análisis comparativo

---

**Última actualización**: Diciembre 2024





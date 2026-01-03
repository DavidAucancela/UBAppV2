# 🔍 Proceso Detallado de Búsqueda Semántica

## 📋 Resumen Ejecutivo

El sistema de búsqueda semántica utiliza embeddings de OpenAI para convertir consultas en lenguaje natural en vectores de alta dimensionalidad, permitiendo encontrar envíos relevantes basándose en similitud semántica en lugar de coincidencias exactas de texto.

---

## 🔄 Flujo Completo del Proceso

### Fase 1: Recepción y Validación de la Consulta

**Ubicación**: `backend/apps/busqueda/views.py` - Método `busqueda_semantica()` (Línea 260-291)

1. **Endpoint**: `POST /api/busqueda/semantica/`
2. **Validación**:
   - Verifica que el campo `texto` esté presente
   - Valida parámetros opcionales (`limite`, `modeloEmbedding`, `filtrosAdicionales`)
3. **Autenticación**: Requiere token JWT válido

**Código relevante**:
```python
consulta_texto = request.data.get('texto', '').strip()
if not consulta_texto:
    return Response({'error': 'El campo "texto" es requerido'}, 
                    status=status.HTTP_400_BAD_REQUEST)
```

---

### Fase 2: Procesamiento de la Consulta

**Ubicación**: `backend/apps/busqueda/services.py` - Método `buscar()` (Línea 128-286)

#### 2.1 Validación del Modelo de Embedding

```python
if modelo_embedding is None:
    modelo_embedding = EmbeddingService.get_modelo_default()  # text-embedding-3-small
else:
    modelo_embedding = EmbeddingService.validar_modelo(modelo_embedding)
```

**Modelos disponibles**:
- `text-embedding-3-small` (1536 dimensiones) - **Por defecto, más económico**
- `text-embedding-3-large` (3072 dimensiones) - Mayor precisión, más costoso
- `text-embedding-ada-002` (1536 dimensiones) - Modelo legacy

#### 2.2 Procesamiento de Texto

**Ubicación**: `backend/apps/busqueda/semantic/text_processor.py`

```python
consulta_procesada = TextProcessor.procesar_texto(consulta)
```

**Procesos aplicados**:
1. **Normalización**: Convertir a minúsculas
2. **Limpieza**: Eliminar caracteres especiales innecesarios
3. **Tokenización**: Dividir en palabras/tokens
4. **Lematización** (opcional): Reducir palabras a su raíz

**Ejemplo**:
```
Input:  "Envíos entregados en Quito la semana pasada"
Output: "envios entregados en quito la semana pasada"
```

---

### Fase 3: Filtrado de Envíos por Permisos y Criterios

**Ubicación**: `backend/apps/busqueda/services.py` - Método `_obtener_envios_filtrados()` (Línea 289-297)

```python
envios_queryset = BusquedaSemanticaService._obtener_envios_filtrados(
    usuario, filtros or {}
)
```

**Filtros aplicados**:
1. **Permisos del usuario**:
   - **Admin (rol=1)**: Ve todos los envíos
   - **Gerente (rol=2)**: Ve todos excepto admins
   - **Digitador (rol=3)**: Ve todos los envíos
   - **Comprador (rol=4)**: Solo sus propios envíos

2. **Filtros adicionales** (opcionales):
   - `fechaDesde`: Fecha de inicio
   - `fechaHasta`: Fecha de fin
   - `estado`: Estado del envío (pendiente, entregado, etc.)
   - `ciudadDestino`: Ciudad de destino

**Código**:
```python
return envio_repository.filtrar_por_criterios_multiples(
    usuario=usuario,
    estado=filtros.get('estado'),
    fecha_desde=filtros.get('fechaDesde'),
    fecha_hasta=filtros.get('fechaHasta'),
    ciudad_destino=filtros.get('ciudadDestino')
)
```

---

### Fase 4: Generación del Embedding de la Consulta

**Ubicación**: `backend/apps/busqueda/semantic/embedding_service.py`

```python
embedding_resultado = EmbeddingService.generar_embedding(
    consulta_procesada, modelo_embedding
)
embedding_consulta = embedding_resultado['embedding']
tokens_consulta = embedding_resultado['tokens']
costo_consulta = embedding_resultado['costo']
```

#### 4.1 Proceso de Generación

1. **Llamada a OpenAI API**:
   - Endpoint: `https://api.openai.com/v1/embeddings`
   - Modelo: `text-embedding-3-small` (por defecto)
   - Input: Texto procesado de la consulta

2. **Respuesta de OpenAI**:
   ```json
   {
     "data": [{
       "embedding": [0.123, -0.456, 0.789, ...],  // 1536 valores
       "index": 0
     }],
     "usage": {
       "prompt_tokens": 10,
       "total_tokens": 10
     }
   }
   ```

3. **Extracción de datos**:
   - **Embedding**: Vector de 1536 dimensiones (float32)
   - **Tokens**: Número de tokens utilizados
   - **Costo**: Calculado según precio del modelo

#### 4.2 Cálculo de Costo

**Precios por modelo** (por 1,000 tokens):
- `text-embedding-3-small`: $0.00002
- `text-embedding-3-large`: $0.00013
- `text-embedding-ada-002`: $0.0001

**Fórmula**:
```python
costo = (tokens / 1000) * precio_por_1k_tokens
```

---

### Fase 5: Búsqueda de Envíos Similares

**Ubicación**: `backend/apps/busqueda/services.py` - Método `_buscar_envios_similares()` (Línea 300-375)

#### 5.1 Obtención de Embeddings de Envíos

```python
embeddings_envios = embedding_repository.obtener_embeddings_para_busqueda(
    envios_limitados,
    modelo=modelo_embedding,
    limite=MAX_ENVIOS_A_PROCESAR  # 300 envíos máximo
)
```

**Optimización**:
- Solo se usan embeddings **ya generados** (no se generan en tiempo real)
- Límite de 300 envíos para mantener rendimiento
- Los embeddings deben generarse previamente con: `python manage.py generar_embeddings`

**Estructura de datos**:
```python
embeddings_envios = [
    (envio_id, vector_embedding, objeto_envio),
    (envio_id, vector_embedding, objeto_envio),
    ...
]
```

#### 5.2 Obtención de Textos Indexados

```python
envio_ids = [e[0] for e in embeddings_envios]
textos_indexados = embedding_repository.obtener_textos_indexados(envio_ids)
```

**Texto indexado**: Texto completo que se usó para generar el embedding del envío, incluyendo:
- HAWB (número de envío)
- Información del comprador
- Ciudad de destino
- Estado
- Descripción de productos
- Etc.

**Ejemplo**:
```
"HAWB: ABC123 | Comprador: Juan Pérez | Ciudad: Quito | Estado: Entregado | 
Productos: Laptop, Mouse, Teclado | Peso: 5.5 kg"
```

---

### Fase 6: Cálculo de Similitudes Vectoriales

**Ubicación**: `backend/apps/busqueda/semantic/vector_search.py` - Método `calcular_similitudes()` (Línea 144-266)

#### 6.1 Cálculo de Múltiples Métricas

Para cada envío, se calculan **4 métricas de similitud**:

##### 6.1.1 Cosine Similarity (Métrica Principal)

**Fórmula**: `cos(θ) = (A · B) / (||A|| × ||B||)`

**Código**:
```python
cosine_similarity = np.dot(consulta_vec, envio_vec) / (consulta_norm * envio_norm)
```

**Características**:
- Rango: `[-1, 1]`
- `1.0` = Vectores idénticos (máxima similitud)
- `0.0` = Vectores ortogonales (sin relación)
- `-1.0` = Vectores opuestos

**Ventajas**:
- Normalizada (rango acotado)
- Invariante a escala (ignora magnitud)
- Estándar en NLP

##### 6.1.2 Dot Product (Producto Punto)

**Fórmula**: `A · B = Σ(Ai × Bi)`

**Código**:
```python
dot_product = np.dot(consulta_vec, envio_vec)
```

**Características**:
- Rango: `[0, ∞]`
- Mayor valor = más similar
- Depende de la magnitud de los vectores

**Limitación**: Vectores más largos tienen productos punto más altos, incluso si no son más similares semánticamente.

##### 6.1.3 Euclidean Distance (Distancia Euclidiana)

**Fórmula**: `d = √(Σ(Ai - Bi)²)`

**Código**:
```python
euclidean_distance = np.linalg.norm(consulta_vec - envio_vec)
```

**Características**:
- Rango: `[0, ∞]`
- `0` = Vectores idénticos
- Mayor valor = más diferente
- Mide distancia "en línea recta" en el espacio vectorial

**Limitación**: Requiere normalización adicional para comparación, sensible a la escala.

##### 6.1.4 Manhattan Distance (Distancia Manhattan)

**Fórmula**: `d = Σ|Ai - Bi|`

**Código**:
```python
manhattan_distance = np.sum(np.abs(consulta_vec - envio_vec))
```

**Características**:
- Rango: `[0, ∞]`
- `0` = Vectores idénticos
- Mayor valor = más diferente
- Suma de diferencias absolutas por componente

**Limitación**: Similar a euclidean, menos sensible a outliers pero aún requiere normalización.

#### 6.2 Boost por Coincidencias Exactas

**Ubicación**: `backend/apps/busqueda/semantic/vector_search.py` (Línea 200-247)

```python
coincidencias_score = TextProcessor.calcular_coincidencias_exactas(
    texto_consulta,
    textos_indexados[envio_id]
)

boost_exactas = coincidencias_score * boost_base
```

**Proceso**:
1. Busca coincidencias exactas de palabras entre la consulta y el texto indexado
2. Calcula un score de coincidencias (0.0 a 1.0)
3. Aplica un boost base (0.15 normal, 0.25 para productos)
4. Boost adicional para productos si hay coincidencias en descripciones

**Ejemplo**:
```
Consulta: "envíos a Quito"
Texto indexado: "HAWB: ABC123 | Ciudad: Quito | Estado: Entregado"
Coincidencias: "Quito" → boost = 0.15
```

#### 6.3 Score Combinado

**Fórmula**: `score_combinado = (cosine + 1) / 2 + boost_exactas`

**Código**:
```python
cosine_normalizado = (cosine_similarity + 1) / 2  # Normalizar de [-1,1] a [0,1]
score_combinado = min(cosine_normalizado + boost_exactas, 1.0)
```

**Explicación**:
1. Normaliza cosine similarity de `[-1, 1]` a `[0, 1]`
2. Suma el boost por coincidencias exactas
3. Limita el máximo a 1.0

**Ventaja**: Combina similitud semántica (cosine) con coincidencias textuales (boost).

---

### Fase 7: Filtrado por Umbral

**Ubicación**: `backend/apps/busqueda/semantic/vector_search.py` - Método `aplicar_umbral()` (Línea 311-358)

```python
umbral_base = 0.30 if es_consulta_productos else 0.35
resultados_filtrados = vector_search.aplicar_umbral(
    resultados_similitud,
    umbral_base=umbral_base,
    usar_adaptativo=True
)
```

#### 7.1 Umbral Adaptativo

Si hay más de 3 resultados:
1. Ordena los scores de mayor a menor
2. Calcula el percentil 75 (25% más bajos)
3. Usa el máximo entre el percentil 75 y el umbral base

**Ejemplo**:
```
Scores: [0.92, 0.85, 0.78, 0.65, 0.45, 0.30]
Percentil 75 (índice 25%): 0.65
Umbral adaptativo: max(0.65, 0.35) = 0.65
Resultados filtrados: [0.92, 0.85, 0.78, 0.65]  # Solo >= 0.65
```

#### 7.2 Umbrales por Tipo de Consulta

- **Consultas normales**: Umbral base = 0.35
- **Consultas de productos**: Umbral base = 0.30 (más permisivo)

---

### Fase 8: Ordenamiento de Resultados

**Ubicación**: `backend/apps/busqueda/semantic/vector_search.py` - Método `ordenar_por_metrica()` (Línea 268-309)

```python
resultados_ordenados = vector_search.ordenar_por_metrica(
    resultados_filtrados,
    metrica='score_combinado',
    limite=limite
)
```

**Proceso**:
1. Ordena por `score_combinado` descendente (mayor a menor)
2. Limita a `limite` resultados (default: 20)

**Resultado**: Lista de envíos ordenados por relevancia semántica.

---

### Fase 9: Formateo de Resultados

**Ubicación**: `backend/apps/busqueda/services.py` - Método `_formatear_resultados()` (Línea 377-435)

#### 9.1 Extracción de Fragmentos Relevantes

```python
fragmentos = TextProcessor.extraer_fragmentos(texto_consulta, texto_indexado)
```

Identifica las partes del texto indexado que son más relevantes para la consulta.

**Ejemplo**:
```
Consulta: "envíos a Quito"
Fragmentos: ["Ciudad: Quito", "Comprador: Juan Pérez (Quito)"]
```

#### 9.2 Generación de Razón de Relevancia

```python
razon = TextProcessor.generar_razon_relevancia(
    texto_consulta, envio, resultado['score_combinado']
)
```

Genera una explicación textual de por qué el envío es relevante.

**Ejemplo**:
```
"Coincide con: ciudad Quito, estado entregado"
```

#### 9.3 Análisis Comparativo de Métricas

```python
analisis_metricas = BusquedaSemanticaService._generar_analisis_metricas(resultado)
```

Genera análisis detallado de las 4 métricas calculadas, justificando por qué cosine similarity es la mejor.

**Estructura del análisis**:
```json
{
  "metricas": {
    "cosineSimilarity": {...},
    "dotProduct": {...},
    "euclideanDistance": {...},
    "manhattanDistance": {...},
    "scoreCombinado": {...}
  },
  "justificacion": {
    "metricaSeleccionada": "cosine_similarity",
    "razonBreve": "...",
    "comparacionRapida": {...},
    "conclusion": "..."
  }
}
```

#### 9.4 Estructura Final del Resultado

Cada resultado incluye:

```json
{
  "envio": {...},                    // Datos del envío
  "puntuacionSimilitud": 0.9200,     // Score combinado
  "cosineSimilarity": 0.8500,        // Similitud coseno
  "dotProduct": 12.5000,             // Producto punto
  "euclideanDistance": 0.4500,        // Distancia euclidiana
  "manhattanDistance": 2.1000,      // Distancia Manhattan
  "scoreCombinado": 0.9200,         // Score final
  "boostExactas": 0.0700,           // Boost aplicado
  "analisisMetricas": {...},         // Análisis comparativo
  "fragmentosRelevantes": [...],     // Fragmentos destacados
  "razonRelevancia": "...",         // Explicación textual
  "textoIndexado": "..."             // Texto usado para embedding
}
```

---

### Fase 10: Guardado en Historial

**Ubicación**: `backend/apps/busqueda/services.py` - Método `buscar()` (Línea 226-243)

```python
busqueda = embedding_busqueda_repository.crear(
    usuario=usuario,
    consulta=consulta,  # Consulta original
    resultados_encontrados=len(resultados),
    tiempo_respuesta=tiempo_respuesta,
    filtros_aplicados=filtros,
    modelo_utilizado=modelo_embedding,
    costo_consulta=costo_consulta,
    tokens_utilizados=tokens_consulta,
    resultados_json=resultados
)

# Guardar el embedding de la consulta
busqueda.set_vector(embedding_consulta)
busqueda.save()
```

**Datos guardados**:
- Consulta original del usuario
- Embedding vectorial de la consulta
- Número de resultados encontrados
- Tiempo de respuesta (ms)
- Modelo utilizado
- Costo de la consulta (USD)
- Tokens utilizados
- Resultados completos (JSON)

---

### Fase 11: Logging y Métricas

**Ubicación**: `backend/apps/busqueda/services.py` - Método `buscar()` (Línea 245-275)

```python
BaseService.log_operacion(
    operacion='buscar_semantica',
    entidad='BusquedaSemantica',
    usuario_id=usuario.id,
    detalles={...}
)

BaseService.log_metrica(
    metrica='busqueda_semantica_tiempo',
    valor=tiempo_respuesta,
    unidad='ms',
    ...
)
```

**Métricas registradas**:
- Tiempo de respuesta
- Costo de la consulta
- Número de resultados
- Modelo utilizado

---

### Fase 12: Respuesta Final

**Estructura de la respuesta**:

```json
{
  "consulta": "envíos entregados en Quito",
  "resultados": [
    {
      "envio": {...},
      "puntuacionSimilitud": 0.9200,
      "cosineSimilarity": 0.8500,
      "dotProduct": 12.5000,
      "euclideanDistance": 0.4500,
      "manhattanDistance": 2.1000,
      "scoreCombinado": 0.9200,
      "analisisMetricas": {
        "metricas": {...},
        "justificacion": {...}
      },
      "fragmentosRelevantes": [...],
      "razonRelevancia": "..."
    },
    ...
  ],
  "totalEncontrados": 5,
  "tiempoRespuesta": 156,
  "modeloUtilizado": "text-embedding-3-small",
  "costoConsulta": 0.0001,
  "tokensUtilizados": 10,
  "busquedaId": 123
}
```

---

## 📊 Diagrama de Flujo

```
1. Usuario envía consulta
   ↓
2. Validación y autenticación
   ↓
3. Procesamiento de texto (normalización, limpieza)
   ↓
4. Filtrado de envíos (permisos + criterios)
   ↓
5. Generación de embedding de consulta (OpenAI API)
   ↓
6. Obtención de embeddings de envíos (base de datos)
   ↓
7. Cálculo de similitudes (4 métricas)
   ↓
8. Aplicación de boost por coincidencias exactas
   ↓
9. Cálculo de score combinado
   ↓
10. Filtrado por umbral adaptativo
   ↓
11. Ordenamiento por score_combinado
   ↓
12. Formateo de resultados (fragmentos, razones, análisis)
   ↓
13. Guardado en historial
   ↓
14. Logging de métricas
   ↓
15. Respuesta al usuario
```

---

## 🔑 Puntos Clave del Proceso

### 1. **Optimización de Rendimiento**
- Límite de 300 envíos a procesar
- Solo usa embeddings pre-generados (no genera en tiempo real)
- Cálculo vectorial optimizado con NumPy

### 2. **Métricas Múltiples**
- Se calculan 4 métricas para cada resultado
- Cosine similarity es la métrica principal
- Score combinado mejora precisión con boost

### 3. **Análisis Automático**
- Cada resultado incluye análisis comparativo de métricas
- Justificación automática de cosine similarity
- Información útil para documentación académica

### 4. **Trazabilidad Completa**
- Cada búsqueda se guarda en historial
- Incluye embedding, métricas, costo, tiempo
- Permite análisis posterior y optimización

---

## 📝 Referencias de Código

- **Endpoint principal**: `backend/apps/busqueda/views.py` - Línea 260-291
- **Lógica de negocio**: `backend/apps/busqueda/services.py` - Línea 128-286
- **Cálculo de similitudes**: `backend/apps/busqueda/semantic/vector_search.py` - Línea 144-266
- **Generación de embeddings**: `backend/apps/busqueda/semantic/embedding_service.py`
- **Procesamiento de texto**: `backend/apps/busqueda/semantic/text_processor.py`
- **Formateo de resultados**: `backend/apps/busqueda/services.py` - Línea 377-435
- **Análisis de métricas**: `backend/apps/busqueda/services.py` - Línea 440-690

---

**Última actualización**: Diciembre 2024


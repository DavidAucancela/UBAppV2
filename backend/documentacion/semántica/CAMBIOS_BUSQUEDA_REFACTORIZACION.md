# 📋 Resumen de Refactorización del Sistema de Búsqueda

## 🎯 Objetivo
Refactorizar el sistema de búsqueda para mejorar la nomenclatura, almacenar embeddings de consultas y agregar funcionalidad de descarga de PDFs.

---

## 📊 Explicación de Algoritmos de Similitud

### ¿Para qué se calculan?
Los algoritmos de similitud se calculan para **comparar el embedding de la consulta del usuario con los embeddings de cada envío** y determinar qué tan relevante es cada resultado.

### Algoritmos Implementados

#### 1. **Cosine Similarity (Similitud Coseno)** ⭐ PRINCIPAL
- **Propósito**: Mide el ángulo entre dos vectores
- **Uso**: Métrica PRINCIPAL para ordenar resultados
- **Rango**: [-1, 1], donde 1 = idéntico, 0 = ortogonal, -1 = opuesto
- **Fórmula**: `dot(A, B) / (||A|| * ||B||)`
- **Por qué es útil**: No depende de la magnitud del vector, solo de su dirección

#### 2. **Dot Product (Producto Punto)**
- **Propósito**: Medida bruta de similitud considerando magnitud
- **Uso**: Métrica alternativa
- **Rango**: [0, ∞), mayor es más similar
- **Fórmula**: `dot(A, B)`

#### 3. **Euclidean Distance (Distancia Euclidiana)**
- **Propósito**: Distancia geométrica entre vectores
- **Uso**: Menor distancia = más similar
- **Rango**: [0, ∞), 0 = idéntico
- **Fórmula**: `sqrt(sum((A - B)²))`

#### 4. **Manhattan Distance (Distancia Manhattan)**
- **Propósito**: Suma de diferencias absolutas (distancia L1)
- **Uso**: Similar a Euclidean pero más simple
- **Rango**: [0, ∞), menor es mejor
- **Fórmula**: `sum(|A - B|)`

#### 5. **Boost por Coincidencias Exactas**
- **Propósito**: Premiar cuando hay palabras exactas en común
- **Uso**: Mejora resultados cuando hay matches literales
- **Bonus**: Hasta +0.15 puntos adicionales
- **Ejemplo**: Si búsqueda tiene "Quito" y texto también → +bonus

#### 6. **Score Combinado** ⭐ MÉTRICA FINAL
- **Propósito**: Combina cosine normalizado + boost
- **Uso**: **ESTA ES LA MÉTRICA QUE ORDENA LOS RESULTADOS FINALES**
- **Fórmula**: `((cosine + 1) / 2) + boost_exactas`
- **Rango**: [0, 1], mayor es mejor

---

## 🔄 Cambios en Nombres de Tablas

| Tabla Anterior | Tabla Nueva | Modelo |
|----------------|-------------|--------|
| `historial_semantica` | `busqueda_tradicional` | `BusquedaTradicional` |
| `busqueda_semantica` | `embedding_busqueda` | `EmbeddingBusqueda` |
| `feed_semantica` | ❌ **ELIMINADA** | - |
| `embedding_busqueda` (sugerencias) | `historial_semantica` | `HistorialSemantica` |

### Justificación de los Cambios

1. **`busqueda_tradicional`**: Nombre más claro que refleja que son búsquedas tradicionales por texto.

2. **`embedding_busqueda`**: Ahora almacena el **embedding de la consulta** además del historial, siendo más que un simple historial.

3. **`historial_semantica`**: Anteriormente llamada "sugerencias", ahora refleja mejor su propósito de sugerencias históricas.

4. **Tabla `feed_semantica` eliminada**: Se eliminó el feedback semántico para simplificar el sistema.

---

## 📦 Nuevas Funcionalidades

### 1. Almacenamiento de Embeddings de Consultas

**Antes:**
- Solo se guardaba el **texto** de la consulta
- El embedding se generaba cada vez y se descartaba

**Ahora:**
```python
class EmbeddingBusqueda(models.Model):
    # ... campos existentes ...
    
    # ✅ NUEVO: Campo vectorial para almacenar embedding de la consulta
    embedding_vector = VectorField(
        dimensions=1536,
        verbose_name="Vector de Embedding de la Consulta"
    )
    
    # ✅ NUEVO: Resultados completos para PDF
    resultados_json = models.JSONField(
        verbose_name="Resultados en JSON"
    )
```

**Beneficios:**
- ✅ Reutilizar embeddings de consultas similares
- ✅ Analizar patrones de búsqueda
- ✅ Mejorar recomendaciones
- ✅ Generar PDFs con resultados completos

### 2. Generación de PDFs

Se creó un nuevo servicio `PDFBusquedaService` que permite:

#### PDF de Búsqueda Tradicional
- Información de la búsqueda
- Resultados por tipo (envíos, usuarios, productos)
- Tablas con datos relevantes
- Footer con fecha de generación

#### PDF de Búsqueda Semántica
- Información de la búsqueda
- Métricas de IA (tokens, costo, tiempo)
- Resultados con métricas de similitud:
  - Score Combinado
  - Cosine Similarity
  - Euclidean Distance
  - Boost por coincidencias exactas
- Explicación de cada métrica

**Endpoints creados:**
```python
# Descargar PDF de búsqueda tradicional
GET /api/busqueda/{id}/descargar-pdf/

# Descargar PDF de búsqueda semántica
GET /api/busqueda/semantica/{busqueda_id}/descargar-pdf/
```

---

## 🗂️ Archivos Modificados/Creados

### Archivos Modificados

1. **`backend/apps/busqueda/models.py`**
   - Renombrado `HistorialBusqueda` → `BusquedaTradicional`
   - Renombrado `BusquedaSemantica` → `EmbeddingBusqueda`
   - Renombrado `SugerenciaSemantica` → `HistorialSemantica`
   - Eliminado `FeedbackSemantico`
   - Agregado campo `embedding_vector` a `EmbeddingBusqueda`
   - Agregado campo `resultados_json` a ambos modelos
   - Agregado campo `veces_usada` a `HistorialSemantica`

2. **`backend/apps/busqueda/repositories.py`**
   - Actualizado todos los nombres de clases de repositorio
   - Eliminado `FeedbackSemanticoRepository`
   - Actualizado singletons al final del archivo

3. **`backend/apps/busqueda/services.py`**
   - Actualizado imports de repositorios
   - Modificado para guardar `resultados_json`
   - Modificado para guardar `embedding_vector` de consultas
   - Eliminado método `registrar_feedback`
   - Actualizado todas las referencias a repositorios

4. **`backend/apps/busqueda/serializers.py`**
   - Renombrado todos los serializers
   - Agregados nuevos campos en serializers

5. **`backend/apps/busqueda/views.py`**
   - Actualizado imports
   - Eliminado endpoint de feedback
   - Agregados dos nuevos endpoints para descargar PDFs
   - Actualizado todas las referencias a modelos/serializers

6. **`backend/apps/busqueda/admin.py`**
   - Actualizado todos los admins con nuevos nombres
   - Agregados campos nuevos en fieldsets

### Archivos Creados

1. **`backend/apps/busqueda/migrations/0009_refactorizar_tablas_busqueda.py`**
   - Migración completa para renombrar tablas
   - Agregar nuevos campos
   - Eliminar modelo FeedbackSemantico
   - Actualizar índices

2. **`backend/apps/busqueda/pdf_service.py`** ✨ NUEVO
   - Servicio para generación de PDFs
   - Dos métodos principales:
     - `generar_pdf_busqueda_tradicional()`
     - `generar_pdf_busqueda_semantica()`
   - Usa ReportLab para generar PDFs profesionales

3. **`backend/documentacion/CAMBIOS_BUSQUEDA_REFACTORIZACION.md`** (este archivo)
   - Documentación completa de todos los cambios

---

## 🚀 Pasos para Aplicar los Cambios

### 1. Aplicar Migraciones

```bash
cd backend
python manage.py migrate busqueda
```

### 2. Verificar Tablas Renombradas

```sql
-- Verificar que las tablas existen con los nuevos nombres
SELECT * FROM busqueda_tradicional LIMIT 5;
SELECT * FROM embedding_busqueda LIMIT 5;
SELECT * FROM historial_semantica LIMIT 5;

-- Verificar que el campo embedding_vector existe
\d embedding_busqueda
```

### 3. Probar Endpoints

```bash
# Búsqueda tradicional
curl -X POST http://localhost:8000/api/busqueda/buscar/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"q": "test", "tipo": "general"}'

# Búsqueda semántica
curl -X POST http://localhost:8000/api/busqueda/semantica/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"consulta": "envíos en Quito", "limite": 20}'

# Descargar PDF tradicional (ID = 1)
curl -X GET http://localhost:8000/api/busqueda/1/descargar-pdf/ \
  -H "Authorization: Bearer TOKEN" \
  --output busqueda.pdf

# Descargar PDF semántico (ID = 1)
curl -X GET http://localhost:8000/api/busqueda/semantica/1/descargar-pdf/ \
  -H "Authorization: Bearer TOKEN" \
  --output busqueda_semantica.pdf
```

---

## 📊 Estructura de Datos

### EmbeddingBusqueda (Búsqueda Semántica)

```json
{
  "id": 1,
  "usuario": 5,
  "consulta": "envíos entregados en Quito la semana pasada",
  "embedding_vector": [0.123, -0.456, ...],  // Vector de 1536 dimensiones
  "resultados_encontrados": 15,
  "tiempo_respuesta": 1250,  // ms
  "fecha_busqueda": "2025-11-26T10:30:00Z",
  "filtros_aplicados": {
    "estado": "entregado",
    "ciudadDestino": "Quito"
  },
  "modelo_utilizado": "text-embedding-3-small",
  "costo_consulta": 0.00002,
  "tokens_utilizados": 50,
  "resultados_json": [
    {
      "envio": {...},
      "scoreCombinado": 0.8523,
      "cosineSimilarity": 0.7856,
      "dotProduct": 325.67,
      "euclideanDistance": 12.34,
      "manhattanDistance": 45.67,
      "boostExactas": 0.15
    }
  ]
}
```

### BusquedaTradicional

```json
{
  "id": 1,
  "usuario": 5,
  "termino_busqueda": "ABC123",
  "tipo_busqueda": "envios",
  "fecha_busqueda": "2025-11-26T10:30:00Z",
  "resultados_encontrados": 3,
  "resultados_json": {
    "envios": [
      {
        "hawb": "ABC123",
        "comprador_nombre": "Juan Pérez",
        "estado_display": "Entregado"
      }
    ]
  }
}
```

---

## 🎨 Flujo de Búsqueda Semántica (Actualizado)

```
1. Usuario envía consulta
   ↓
2. Generar embedding de consulta con OpenAI
   ↓
3. Guardar embedding en base de datos ✅ NUEVO
   ↓
4. Buscar envíos con embeddings similares
   ↓
5. Calcular 6 métricas de similitud:
   - Cosine Similarity
   - Dot Product
   - Euclidean Distance
   - Manhattan Distance
   - Boost por coincidencias exactas
   - Score Combinado (FINAL)
   ↓
6. Ordenar por Score Combinado
   ↓
7. Guardar resultados en resultados_json ✅ NUEVO
   ↓
8. Retornar resultados al usuario
   ↓
9. Usuario puede descargar PDF ✅ NUEVO
```

---

## ✅ Checklist de Verificación

- [x] Modelos renombrados y actualizados
- [x] Migración creada y probada
- [x] Repositorios actualizados
- [x] Servicios actualizados
- [x] Serializers actualizados
- [x] Views actualizados
- [x] Admin actualizado
- [x] Servicio de PDF creado
- [x] Endpoints de descarga creados
- [x] Documentación completa
- [x] Sin errores de linting

---

## 🔗 Referencias

- **Modelos**: `backend/apps/busqueda/models.py`
- **Servicios**: `backend/apps/busqueda/services.py`
- **PDF Service**: `backend/apps/busqueda/pdf_service.py`
- **Views**: `backend/apps/busqueda/views.py`
- **Migración**: `backend/apps/busqueda/migrations/0009_refactorizar_tablas_busqueda.py`

---

## 📞 Soporte

Si encuentras algún problema con la refactorización:

1. Verificar que las migraciones se aplicaron correctamente
2. Revisar logs del servidor para errores
3. Verificar que reportlab está instalado: `pip list | grep reportlab`
4. Consultar la documentación de OpenAI para embeddings

---

**Fecha de implementación**: 26 de noviembre de 2025
**Autor**: Sistema de Refactorización Automática
**Versión**: 1.0.0


# 📚 Guía Completa: Swagger UI y Referencias para Tesis

## 🎯 Parte 1: Guía de Uso de Swagger UI

### 1.1 Acceso a Swagger UI

**URLs disponibles:**
- **Swagger UI**: `http://127.0.0.1:8000/api/schema/swagger-ui/`
- **ReDoc** (alternativa): `http://127.0.0.1:8000/api/redoc/`
- **Esquema OpenAPI JSON**: `http://127.0.0.1:8000/api/schema/`

### 1.2 Navegación en Swagger UI

1. **Panel izquierdo**: Lista de endpoints organizados por tags (autenticacion, usuarios, envios, busqueda, etc.)
2. **Panel central**: Documentación detallada de cada endpoint
3. **Panel derecho**: Esquema de la API (opcional)

### 1.3 Autenticación JWT - Método 1: Botón "Authorize"

#### Paso 1: Obtener Token de Acceso

1. **Busca el endpoint de autenticación**:
   - En el panel izquierdo, busca la sección **"autenticacion"**
   - Expande el endpoint `POST /api/token/` o `POST /api/usuarios/login/`

2. **Haz clic en "Try it out"** (botón azul en la parte superior del endpoint)

3. **Completa los campos**:
   ```json
   {
     "username": "tu_usuario",
     "password": "tu_contraseña"
   }
   ```

4. **Haz clic en "Execute"** (botón verde)

5. **Copia el token** de la respuesta:
   ```json
   {
     "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
   }
   ```
   ⚠️ **Importante**: Copia el valor de `access`, no `refresh`

#### Paso 2: Configurar Autorización

1. **Haz clic en el botón "Authorize"** (🔒) en la parte superior derecha de Swagger UI

2. **En el campo "Value"**, pega el token de acceso:
   ```
   eyJ0eXAiOiJKV1QiLCJhbGc...
   ```

3. **NO agregues "Bearer"** - Swagger UI lo agrega automáticamente

4. **Haz clic en "Authorize"** y luego en "Close"

5. **¡Listo!** Ahora todos los endpoints protegidos usarán este token automáticamente

### 1.4 Autenticación JWT - Método 2: Header Manual

Si prefieres agregar el token manualmente en cada request:

1. **Obtén el token** siguiendo el Paso 1 del método anterior

2. **En cualquier endpoint**, haz clic en "Try it out"

3. **En la sección "Parameters"**, busca el campo de autorización

4. **Agrega el header manualmente**:
   - Key: `Authorization`
   - Value: `Bearer eyJ0eXAiOiJKV1QiLCJhbGc...` (incluye "Bearer " antes del token)

### 1.5 Probar Endpoints

#### Ejemplo: Búsqueda Semántica

1. **Busca el endpoint**: `POST /api/busqueda/semantica/`

2. **Haz clic en "Try it out"**

3. **Completa el Request body**:
   ```json
   {
     "texto": "envíos entregados en Quito",
     "limite": 10,
     "modeloEmbedding": "text-embedding-3-small",
     "filtrosAdicionales": {
       "fechaDesde": "2024-01-01",
       "estado": "entregado"
     }
   }
   ```

4. **Haz clic en "Execute"**

5. **Revisa la respuesta**:
   - **Code**: Código de estado HTTP (200 = éxito)
   - **Response body**: Datos JSON con los resultados
   - **Response headers**: Headers de la respuesta

### 1.6 Endpoints Importantes para Probar

#### Autenticación
- `POST /api/token/` - Obtener token JWT (TokenObtainPairView)
- `POST /api/usuarios/login/` - Login personalizado con límite de intentos
- `POST /api/token/refresh/` - Renovar token

#### Búsqueda Semántica
- `POST /api/busqueda/semantica/` - Búsqueda semántica principal
- `GET /api/busqueda/semantica/metricas/` - Métricas de búsquedas
- `GET /api/busqueda/semantica/analisis-metricas/` - Análisis comparativo
- `GET /api/busqueda/semantica/historial/` - Historial de búsquedas

#### Búsqueda Tradicional
- `GET /api/busqueda/buscar/?q=termino&tipo=general` - Búsqueda tradicional

### 1.7 Tips y Trucos

1. **Token expirado**: Si recibes `401 Unauthorized`, renueva el token con `POST /api/token/refresh/`

2. **Ver esquema completo**: Haz clic en "Schema" en cualquier endpoint para ver la estructura de datos

3. **Exportar documentación**: Puedes descargar el esquema OpenAPI desde `/api/schema/` en formato JSON

4. **Copiar cURL**: Cada request muestra el comando cURL equivalente que puedes copiar

---

## 📖 Parte 2: Referencias para Tesis

### 2.1 Modelos de Datos (Models)

#### Ubicación: `backend/apps/busqueda/models.py`

#### Modelos Clave para Referenciar:

##### 1. **EnvioEmbedding** (Líneas 38-91)
**¿Por qué referenciarlo?**
- Evidencia de implementación de embeddings vectoriales
- Demuestra integración con pgvector (base de datos vectorial)
- Muestra configuración del modelo de embedding (1536 dimensiones para text-embedding-3-small)
- Incluye métricas precalculadas (cosine_similarity_avg)

**Cita en tesis:**
```markdown
El modelo `EnvioEmbedding` (ver Anexo X, Línea 38-91) almacena los vectores 
de embedding generados para cada envío, utilizando pgvector como extensión 
de PostgreSQL para almacenamiento nativo de vectores. Este modelo materializa 
la fase de modelado de CRISP-DM, donde se selecciona y configura el modelo 
text-embedding-3-small de OpenAI con 1536 dimensiones.
```

**Campos importantes:**
- `embedding_vector`: VectorField de 1536 dimensiones
- `modelo_usado`: Modelo de embedding utilizado
- `texto_indexado`: Texto procesado para generar el embedding
- `cosine_similarity_avg`: Métrica precalculada

##### 2. **EmbeddingBusqueda** (Líneas 93-201)
**¿Por qué referenciarlo?**
- Almacena historial de búsquedas semánticas
- Incluye embedding de la consulta del usuario
- Registra métricas de rendimiento (tiempo, costo, tokens)
- Evidencia de trazabilidad del proceso

**Cita en tesis:**
```markdown
El modelo `EmbeddingBusqueda` (Anexo X, Línea 93-201) registra cada búsqueda 
semántica realizada, almacenando tanto el embedding de la consulta como las 
métricas de rendimiento (tiempo de respuesta, costo de OpenAI, tokens utilizados), 
permitiendo análisis posterior y optimización del sistema.
```

##### 3. **BusquedaTradicional** (Líneas 9-31)
**¿Por qué referenciarlo?**
- Comparación entre búsqueda tradicional y semántica
- Base para análisis comparativo de resultados

### 2.2 Serializers (DTOs - Data Transfer Objects)

#### Ubicación: `backend/apps/busqueda/serializers.py`

#### Serializers Clave:

##### 1. **EmbeddingBusquedaSerializer** (Líneas 29-38)
**¿Por qué referenciarlo?**
- Define la estructura de datos para búsquedas semánticas
- Muestra qué información se expone a través de la API
- Evidencia de diseño de interfaz de datos

**Cita en tesis:**
```markdown
El serializer `EmbeddingBusquedaSerializer` (Anexo Y, Línea 29-38) define 
la estructura de datos que se transfiere entre el backend y el frontend, 
incluyendo métricas de rendimiento, modelo utilizado y resultados encontrados, 
facilitando la integración y el análisis de resultados.
```

##### 2. **BusquedaTradicionalSerializer** (Líneas 9-19)
**¿Por qué referenciarlo?**
- Comparación de estructuras de datos
- Evidencia de diseño de API REST

### 2.3 Servicios (Lógica de Negocio)

#### Ubicación: `backend/apps/busqueda/services.py`

#### Servicios Clave:

##### 1. **BusquedaSemanticaService** (Líneas 121-600+)
**¿Por qué referenciarlo?**
- Contiene toda la lógica de búsqueda semántica
- Orquesta el proceso completo: embeddings → búsqueda vectorial → formateo
- Incluye el método `_generar_analisis_metricas()` que justifica la elección de cosine similarity

**Cita en tesis:**
```markdown
El servicio `BusquedaSemanticaService` (Anexo Z, Línea 121-600+) implementa 
la lógica de negocio para búsquedas semánticas, orquestando el proceso completo 
desde la generación de embeddings hasta la presentación de resultados. Este 
servicio incluye análisis comparativo de métricas que justifica técnicamente 
la elección de cosine similarity como métrica principal.
```

**Métodos importantes:**
- `buscar()`: Método principal de búsqueda
- `_generar_analisis_metricas()`: Análisis comparativo de métricas
- `_formatear_resultados()`: Formateo de resultados para frontend

##### 2. **VectorSearchService** (Ubicación: `backend/apps/busqueda/semantic/vector_search.py`)
**¿Por qué referenciarlo?**
- Implementa las estrategias de similitud (Cosine, Euclidean, Manhattan, Dot Product)
- Evidencia de comparación de múltiples métricas
- Muestra cálculo de score combinado

**Cita en tesis:**
```markdown
El servicio `VectorSearchService` (Anexo W, Línea 126-410) implementa múltiples 
estrategias de similitud (Cosine Similarity, Euclidean Distance, Manhattan Distance, 
Dot Product), permitiendo comparación empírica y justificación de la elección de 
cosine similarity como métrica óptima para búsqueda semántica.
```

### 2.4 Endpoints API (Views)

#### Ubicación: `backend/apps/busqueda/views.py`

#### Endpoints Clave:

##### 1. **busqueda_semantica** (Líneas 260-291)
**¿Por qué referenciarlo?**
- Endpoint principal de búsqueda semántica
- Documentado con drf-spectacular (OpenAPI/Swagger)
- Muestra integración frontend-backend

**Cita en tesis:**
```markdown
El endpoint `POST /api/busqueda/semantica/` (Anexo V, Línea 260-291) expone 
la funcionalidad de búsqueda semántica a través de una API REST documentada 
con OpenAPI 3.0, permitiendo integración con cualquier cliente HTTP y 
facilitando la documentación técnica del sistema.
```

##### 2. **analisis_comparativo_metricas** (Líneas 378-463)
**¿Por qué referenciarlo?**
- Endpoint dedicado para análisis académico
- Retorna justificación técnica de métricas
- Útil para documentación y presentación

**Cita en tesis:**
```markdown
El endpoint `GET /api/busqueda/semantica/analisis-metricas/` (Anexo V, Línea 378-463) 
proporciona un análisis comparativo detallado de las métricas de similitud, 
incluyendo justificación teórica y práctica de la elección de cosine similarity, 
facilitando la documentación académica y técnica del sistema.
```

### 2.5 Arquitectura y Patrones

#### Patrón Repository
**Ubicación**: `backend/apps/busqueda/repositories.py`

**¿Por qué referenciarlo?**
- Evidencia de arquitectura en capas
- Separación de responsabilidades
- Facilita testing y mantenibilidad

**Cita en tesis:**
```markdown
El sistema implementa el patrón Repository (Anexo R) para abstraer el acceso 
a datos, separando la lógica de negocio de la persistencia, facilitando el 
testing, mantenibilidad y evolución del sistema.
```

#### Patrón Service
**Ubicación**: `backend/apps/busqueda/services.py`

**¿Por qué referenciarlo?**
- Lógica de negocio centralizada
- Reutilización de código
- Facilita testing unitario

### 2.6 Documentación OpenAPI/Swagger

#### Ubicación: Generado automáticamente desde `views.py` con `@extend_schema`

**¿Por qué referenciarlo?**
- Documentación automática de la API
- Especificación OpenAPI 3.0
- Evidencia de buenas prácticas de documentación

**Cita en tesis:**
```markdown
La API está completamente documentada usando OpenAPI 3.0 (Swagger), generando 
documentación interactiva disponible en `/api/schema/swagger-ui/`. Esta 
documentación incluye esquemas de datos, ejemplos de requests/responses y 
descripciones detalladas de cada endpoint, facilitando la integración y el 
mantenimiento del sistema.
```

### 2.7 Configuración y Tecnologías

#### Configuración JWT
**Ubicación**: `backend/settings.py` (Líneas 251-265)

**¿Por qué referenciarlo?**
- Evidencia de implementación de seguridad
- Configuración de tokens JWT
- Tiempos de expiración y renovación

**Cita en tesis:**
```markdown
El sistema implementa autenticación JWT (JSON Web Tokens) configurada en 
settings.py (Anexo S, Línea 251-265), con tokens de acceso de 60 minutos 
y tokens de renovación de 1 día, siguiendo mejores prácticas de seguridad 
para APIs REST.
```

#### Configuración de Embeddings
**Ubicación**: `backend/apps/busqueda/semantic/embedding_service.py`

**¿Por qué referenciarlo?**
- Configuración de modelos de OpenAI
- Gestión de costos y tokens
- Selección de modelos

### 2.8 Estructura de Respuestas API

#### Ejemplo: Respuesta de Búsqueda Semántica

**Estructura completa** (incluye análisis de métricas):
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
      "analisisMetricas": {
        "metricaSeleccionada": "cosine_similarity",
        "justificacion": {
          "teorica": "...",
          "practica": "...",
          "ventajas": [...],
          "referenciasAcademicas": [...]
        },
        "comparacion": {...},
        "conclusion": {...}
      }
    }
  ],
  "totalEncontrados": 5,
  "tiempoRespuesta": 156,
  "modeloUtilizado": "text-embedding-3-small",
  "costoConsulta": 0.0001,
  "tokensUtilizados": 10
}
```

**¿Por qué referenciarlo?**
- Muestra estructura completa de datos
- Evidencia de análisis comparativo integrado
- Demuestra trazabilidad (costo, tokens, tiempo)

### 2.9 Métricas y Análisis

#### Análisis Comparativo de Métricas
**Ubicación**: `backend/apps/busqueda/services.py` - Método `_generar_analisis_metricas()`

**¿Por qué referenciarlo?**
- Justificación técnica de cosine similarity
- Comparación con otras métricas
- Referencias académicas incluidas

**Cita en tesis:**
```markdown
El sistema incluye análisis comparativo automático de métricas (Anexo Z, 
método _generar_analisis_metricas) que compara cosine similarity con 
euclidean distance, manhattan distance y dot product, proporcionando 
justificación teórica y práctica de la elección de cosine similarity, 
incluyendo referencias a trabajos académicos relevantes (Mikolov et al. 2013, 
Devlin et al. 2018, OpenAI 2023).
```

---

## 📋 Parte 3: Checklist para Referencias en Tesis

### ✅ Modelos de Datos
- [ ] `EnvioEmbedding` - Almacenamiento de embeddings
- [ ] `EmbeddingBusqueda` - Historial de búsquedas
- [ ] `BusquedaTradicional` - Comparación con búsqueda tradicional

### ✅ Capa de Servicios
- [ ] `BusquedaSemanticaService` - Lógica principal
- [ ] `VectorSearchService` - Cálculo de similitudes
- [ ] `EmbeddingService` - Generación de embeddings
- [ ] `TextProcessor` - Procesamiento de texto

### ✅ API y Endpoints
- [ ] Endpoint de búsqueda semántica
- [ ] Endpoint de análisis de métricas
- [ ] Endpoint de métricas generales
- [ ] Documentación OpenAPI/Swagger

### ✅ Arquitectura
- [ ] Patrón Repository
- [ ] Patrón Service
- [ ] Separación de responsabilidades

### ✅ Configuración
- [ ] JWT Authentication
- [ ] Configuración de modelos OpenAI
- [ ] Configuración de base de datos vectorial (pgvector)

### ✅ Análisis y Métricas
- [ ] Análisis comparativo de métricas
- [ ] Justificación de cosine similarity
- [ ] Métricas de rendimiento (tiempo, costo, tokens)

---

## 🎓 Parte 4: Ejemplos de Citas para Tesis

### Ejemplo 1: Arquitectura del Sistema
```markdown
El sistema implementa una arquitectura en capas siguiendo el patrón 
Repository-Service (ver Anexo X: repositories.py y services.py), 
separando la lógica de negocio de la persistencia de datos y facilitando 
el mantenimiento y testing del sistema.
```

### Ejemplo 2: Implementación de Embeddings
```markdown
Los embeddings se almacenan utilizando pgvector, una extensión de PostgreSQL 
para almacenamiento nativo de vectores (Anexo Y: models.py, modelo EnvioEmbedding, 
línea 47-53). Esta implementación permite búsquedas vectoriales eficientes 
directamente en la base de datos, evitando la necesidad de sistemas externos 
de búsqueda vectorial.
```

### Ejemplo 3: Justificación de Métricas
```markdown
La elección de cosine similarity como métrica principal se justifica mediante 
un análisis comparativo automático (Anexo Z: services.py, método 
_generar_analisis_metricas, línea 440-600+), que compara esta métrica con 
euclidean distance, manhattan distance y dot product, demostrando que cosine 
similarity es la más adecuada para búsqueda semántica debido a su normalización, 
invariante a escala y amplia adopción en NLP.
```

### Ejemplo 4: API REST Documentada
```markdown
La API REST está completamente documentada usando OpenAPI 3.0 (Swagger), 
disponible en http://127.0.0.1:8000/api/schema/swagger-ui/. Esta documentación 
incluye esquemas de datos, ejemplos de requests/responses y descripciones 
detalladas de cada endpoint, facilitando la integración y el mantenimiento 
del sistema.
```

---

## 📝 Notas Finales

1. **Anexos**: Crea anexos numerados (Anexo A, B, C, etc.) con el código relevante
2. **Líneas específicas**: Siempre menciona las líneas de código cuando sea posible
3. **Diagramas**: Considera crear diagramas de arquitectura basados en la estructura del código
4. **Capturas**: Incluye capturas de pantalla de Swagger UI mostrando los endpoints
5. **Ejemplos**: Incluye ejemplos de requests/responses reales en los anexos

---

## 🔗 URLs Útiles

- **Swagger UI**: http://127.0.0.1:8000/api/schema/swagger-ui/
- **ReDoc**: http://127.0.0.1:8000/api/redoc/
- **OpenAPI JSON**: http://127.0.0.1:8000/api/schema/
- **Admin Django**: http://127.0.0.1:8000/admin/

---

**Última actualización**: Diciembre 2024


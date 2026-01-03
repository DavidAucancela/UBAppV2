# 🧠 Guía Completa de Búsqueda Semántica - Universal Box

## 🎯 Guías de Inicio Rápido

- **⚡ [Respuesta Rápida Supabase](./RESPUESTA_RAPIDA_SUPABASE.md)** - Responde dónde se guardan los embeddings y cambios necesarios (5 min)
- **📋 [Migración a Supabase](./MIGRACION_SUPABASE.md)** - Guía paso a paso para migrar a Supabase (15 min)
- **🎨 [Resumen Visual](./RESUMEN_VISUAL.md)** - Diagramas y comparaciones visuales (10 min)
- **📚 [README Supabase](./README_SUPABASE.md)** - Índice completo de toda la documentación (2 min)

## 🔧 Herramientas

- **`backend/verificar_supabase.py`** - Script de verificación automática de configuración

## 📋 Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Uso del Sistema](#uso-del-sistema)
5. [Métricas de Similitud](#métricas-de-similitud)
6. [Generación de Embeddings](#generación-de-embeddings)
7. [Optimización y Mejores Prácticas](#optimización-y-mejores-prácticas)

---

## 🎯 Descripción General

Sistema de búsqueda semántica completo que permite encontrar envíos usando lenguaje natural, utilizando **OpenAI Embeddings** y **PostgreSQL con pgvector** para almacenamiento y cálculo de similitudes vectoriales.

### Características Principales

✅ **Generación automática de embeddings** al crear envíos  
✅ **Múltiples métricas de similitud** (Cosine, Dot Product, Euclidean, Manhattan)  
✅ **Búsqueda en lenguaje natural** con IA  
✅ **Almacenamiento vectorial nativo** con pgvector  
✅ **Métricas de rendimiento** (precisión, costo, velocidad)  
✅ **Interfaz moderna** en Angular con visualización de resultados  

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Angular)                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Busqueda Semantica Component                          │     │
│  │  - Input de consulta en lenguaje natural              │     │
│  │  - Visualización de resultados con métricas           │     │
│  │  - Configuración de modelos y umbrales                │     │
│  └────────────────────────────────────────────────────────┘     │
└────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP/REST API
┌────────────────────────────────▼────────────────────────────────┐
│                      BACKEND (Django REST)                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  BusquedaViewSet                                       │     │
│  │  - /api/busqueda/semantica/ (POST)                    │     │
│  │  - Generación de embedding de consulta                │     │
│  │  - Cálculo de similitudes múltiples                   │     │
│  └────────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  utils_embeddings.py                                   │     │
│  │  - generar_embedding_envio()                          │     │
│  │  - calcular_similitudes()                             │     │
│  │  - ordenar_por_metrica()                              │     │
│  └────────────────────────────────────────────────────────┘     │
└────────────────┬───────────────┬────────────────────────────────┘
                 │               │
        ┌────────▼─────┐  ┌─────▼──────────┐
        │   OpenAI API │  │  SUPABASE ✨   │
        │   Embeddings │  │  PostgreSQL +  │
        │              │  │    pgvector    │
        │ text-emb-3-  │  │                │
        │    small     │  │  EnvioEmbedding│
        │  (1536 dims) │  │  VectorField   │
        │              │  │  (SSL Required)│
        └──────────────┘  └────────────────┘
```

### Flujo de Datos

```
1. CARGA DE ENVÍO (Manual/Excel)
   ↓
2. Crear Envio → generar_embedding_envio()
   ↓
3. Generar texto descriptivo del envío
   ↓
4. Llamada a OpenAI API → Embedding (1536 dims)
   ↓
5. Guardar en EnvioEmbedding (VectorField pgvector)

─────────────────────────────────────

1. BÚSQUEDA SEMÁNTICA
   ↓
2. Usuario ingresa consulta: "envíos pesados a Quito"
   ↓
3. Generar embedding de consulta (OpenAI)
   ↓
4. Buscar envíos con embeddings en BD
   ↓
5. Calcular similitudes:
      - Cosine Similarity
      - Dot Product
      - Euclidean Distance
      - Manhattan Distance
   ↓
6. Filtrar por umbral (ej: cosine >= 0.3)
   ↓
7. Ordenar por métrica seleccionada
   ↓
8. Retornar top N resultados con métricas
```

---

## 🚀 Instalación y Configuración

### 1. Requisitos Previos

```bash
- Python 3.11+
- PostgreSQL 14+
- Node.js 18+
- API Key de OpenAI
```

### 2. Configurar Backend

#### 2.1 Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

**Nuevas dependencias incluidas:**
- `psycopg2-binary==2.9.9` - Driver PostgreSQL
- `pgvector==0.2.5` - Soporte de vectores en Postgres
- `openai==1.12.0` - Cliente OpenAI
- `numpy==1.26.4` - Cálculos vectoriales

#### 2.2 Configurar PostgreSQL con pgvector

**Opción A: Usar Supabase (Recomendado) ✨**

Supabase ya incluye pgvector pre-instalado. Solo necesitas:

```bash
# 1. Obtener credenciales de Supabase:
#    - Ve a https://app.supabase.com → Tu proyecto
#    - Settings → Database → Connection string
#    - Copia: host, user, password, dbname

# 2. Verificar que pgvector esté habilitado (SQL Editor):
CREATE EXTENSION IF NOT EXISTS vector;
SELECT * FROM pg_extension WHERE extname = 'vector';
```

**⚠️ Importante para Supabase:**
```python
# En backend/settings.py agregar SSL:
DATABASES = {
    'default': {
        # ...
        'OPTIONS': {
            'sslmode': 'require',  # REQUERIDO para Supabase
        }
    }
}
```

📚 **Guía completa de migración:** Ver `MIGRACION_SUPABASE.md`

**Opción B: PostgreSQL Local**

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-14-pgvector

# macOS
brew install pgvector

# Windows: Descargar desde https://github.com/pgvector/pgvector/releases
```

**Conectar y habilitar:**

```sql
-- Conectar a tu base de datos
psql -U postgres -d equityDB

-- Habilitar extensión
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar
SELECT * FROM pg_extension WHERE extname = 'vector';
```

#### 2.3 Configurar variables de entorno

Crear/editar `backend/.env`:

```env
# Base de datos
DB_NAME=equityDB
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

# OpenAI API
OPENAI_API_KEY=sk-proj-tu-key-de-openai-aqui
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536

# Django
SECRET_KEY=tu-secret-key
DEBUG=True
```

#### 2.4 Ejecutar migraciones

```bash
cd backend

# Migración para habilitar pgvector
python manage.py migrate busqueda 0006_habilitar_pgvector

# Migración para actualizar modelos
python manage.py migrate busqueda 0007_actualizar_embedding_pgvector

# Todas las migraciones
python manage.py migrate
```

#### 2.5 Generar embeddings para envíos existentes

```bash
# Generar embeddings para todos los envíos sin embedding
python manage.py generar_embeddings_masivo

# Con opciones avanzadas
python manage.py generar_embeddings_masivo --modelo text-embedding-3-small --batch-size 50 --delay 0.1

# Forzar regeneración de todos
python manage.py generar_embeddings_masivo --forzar

# Procesar solo un envío específico
python manage.py generar_embeddings_masivo --hawb ABC123456

# Limitar cantidad (para pruebas)
python manage.py generar_embeddings_masivo --limite 10
```

**Parámetros del comando:**
- `--forzar`: Regenera embeddings existentes
- `--modelo`: Modelo OpenAI (text-embedding-3-small, text-embedding-3-large)
- `--limite`: Número máximo de envíos a procesar
- `--hawb`: HAWB específico a procesar
- `--batch-size`: Tamaño de lote (por defecto 50)
- `--delay`: Retraso entre llamadas en segundos (por defecto 0.1)

### 3. Configurar Frontend

```bash
cd frontend
npm install
```

**Archivos actualizados:**
- `src/app/models/busqueda-semantica.ts` - Interfaces con nuevas métricas
- `src/app/services/api.service.ts` - Cliente API
- `src/app/components/busqueda-semantica/` - Componente principal

---

## 💻 Uso del Sistema

### Backend - API Endpoints

#### 1. Búsqueda Semántica

**Endpoint:** `POST /api/busqueda/semantica/`

**Request Body:**
```json
{
  "texto": "envíos pesados entregados en Quito esta semana",
  "limite": 20,
  "modeloEmbedding": "text-embedding-3-small",
  "filtrosAdicionales": {
    "fechaDesde": "2025-01-01",
    "estado": "entregado",
    "ciudadDestino": "Quito"
  }
}
```

**Response:**
```json
{
  "consulta": "envíos pesados entregados en Quito esta semana",
  "resultados": [
    {
      "envio": { /* datos del envío */ },
      "puntuacionSimilitud": 0.8524,
      "cosineSimilarity": 0.8524,
      "dotProduct": 125.67,
      "euclideanDistance": 12.34,
      "manhattanDistance": 45.67,
      "scoreCombinado": 0.9262,
      "fragmentosRelevantes": [
        "...Ciudad destino: Quito...",
        "...Peso: 15.5 kg..."
      ],
      "razonRelevancia": "Coincide con: ciudad Quito, estado Entregado",
      "textoIndexado": "HAWB: ABC123 | Comprador: Juan Pérez | Ciudad destino: Quito..."
    }
  ],
  "totalEncontrados": 15,
  "tiempoRespuesta": 245,
  "modeloUtilizado": "text-embedding-3-small",
  "costoConsulta": 0.000012,
  "tokensUtilizados": 45,
  "busquedaId": 123
}
```

#### 2. Obtener Historial

**Endpoint:** `GET /api/busqueda/semantica/historial/`

```json
[
  {
    "id": 123,
    "consulta": "envíos pesados entregados en Quito",
    "fecha": "2025-11-20T10:30:00Z",
    "totalResultados": 15,
    "tiempoRespuesta": 245,
    "modeloUtilizado": "text-embedding-3-small",
    "costoConsulta": 0.000012,
    "tokensUtilizados": 45
  }
]
```

#### 3. Métricas

**Endpoint:** `GET /api/busqueda/semantica/metricas/`

```json
{
  "totalBusquedas": 150,
  "tiempoPromedioRespuesta": 280.5,
  "totalFeedback": 45,
  "feedbackPositivo": 38,
  "feedbackNegativo": 7,
  "totalEmbeddings": 1250
}
```

### Frontend - Uso del Componente

```html
<!-- Búsqueda unificada (recomendado) -->
<app-busqueda-unificada></app-busqueda-unificada>

<!-- Solo búsqueda semántica -->
<app-busqueda-semantica></app-busqueda-semantica>
```

**Navegación:**
```
http://localhost:4200/busqueda-unificada
```

---

## 📊 Métricas de Similitud

### 1. Cosine Similarity (Similitud Coseno)

**Fórmula:** `cos(θ) = (A · B) / (||A|| × ||B||)`

**Rango:** [-1, 1]
- **1.0**: Vectores idénticos (máxima similitud)
- **0.0**: Vectores ortogonales (sin relación)
- **-1.0**: Vectores opuestos

**Uso:** Métrica principal, ignora la magnitud de los vectores.

**Ejemplo:**
```
Consulta: "envíos pesados"
Resultado 1: "HAWB: ABC | Peso: 25 kg" → 0.85 (muy similar)
Resultado 2: "HAWB: XYZ | Peso: 2 kg"  → 0.45 (poco similar)
```

### 2. Dot Product (Producto Punto)

**Fórmula:** `A · B = Σ(Ai × Bi)`

**Rango:** [0, ∞]
- **Mayor valor**: Más similar
- **0**: Sin similitud

**Uso:** Considera tanto dirección como magnitud.

### 3. Euclidean Distance (Distancia Euclidiana)

**Fórmula:** `d = sqrt(Σ(Ai - Bi)²)`

**Rango:** [0, ∞]
- **0**: Vectores idénticos
- **Mayor valor**: Más diferente

**Uso:** Distancia geométrica en espacio vectorial.

### 4. Manhattan Distance (Distancia Manhattan/L1)

**Fórmula:** `d = Σ|Ai - Bi|`

**Rango:** [0, ∞]
- **0**: Vectores idénticos
- **Mayor valor**: Más diferente

**Uso:** Suma de diferencias absolutas.

### Comparación de Métricas

| Métrica | Mejor para | Ventajas | Desventajas |
|---------|------------|----------|-------------|
| **Cosine** | Búsqueda semántica general | No afectada por magnitud, estable | Ignora longitud del vector |
| **Dot Product** | Cuando magnitud importa | Rápido de calcular | Sensible a escala |
| **Euclidean** | Distancias geométricas | Intuitiva | Sensible a outliers |
| **Manhattan** | Datos de alta dimensión | Menos sensible a outliers | Menos precisa |

### Umbrales Recomendados

```python
# Cosine Similarity
umbral_excelente = 0.8  # Muy relevante
umbral_bueno = 0.6      # Relevante
umbral_aceptable = 0.3  # Mínimamente relevante

# Sistema usa por defecto: 0.3
```

---

## 🔧 Generación de Embeddings

### Proceso Automático

Los embeddings se generan automáticamente cuando se crea un envío:

```python
# En views.py y utils_importacion.py
def create(self, request, *args, **kwargs):
    envio = serializer.save()
    
    # Generar embedding automáticamente
    try:
        generar_embedding_envio(envio)
    except Exception as e:
        # No falla la creación si falla el embedding
        print(f"Advertencia: {e}")
```

### Contenido del Embedding

El texto indexado incluye:

```python
texto = " | ".join([
    f"HAWB: {envio.hawb}",
    f"Comprador: {envio.comprador.nombre}",
    f"Ciudad destino: {envio.comprador.ciudad}",
    f"Estado: {envio.get_estado_display()}",
    f"Fecha: {envio.fecha_emision}",
    f"Peso: {envio.peso_total} kg",
    f"Valor: ${envio.valor_total}",
    f"Productos: {descripciones}",
    f"Categorías: {categorias}",
    f"Observaciones: {envio.observaciones}"
])
```

### Modelos Disponibles

| Modelo | Dimensiones | Costo/1M tokens | Velocidad | Precisión |
|--------|-------------|-----------------|-----------|-----------|
| **text-embedding-3-small** | 1536 | $0.02 | ⚡⚡⚡ | ⭐⭐⭐ |
| **text-embedding-3-large** | 3072 | $0.13 | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| **text-embedding-ada-002** | 1536 | $0.10 | ⚡⚡ | ⭐⭐⭐ |

**Recomendación:** `text-embedding-3-small` para la mayoría de casos.

---

## ⚡ Optimización y Mejores Prácticas

### 1. Costos

```python
# Cálculo de costo estimado
tokens_promedio_por_envio = 100
costo_por_1k_tokens = 0.00002  # text-embedding-3-small

# Para 1000 envíos:
costo_total = (1000 * 100 / 1000) * 0.00002
# = 100 tokens * 0.00002 = $0.002 (0.2 centavos)

# Para 10,000 envíos: ~$2
```

**Estrategias de ahorro:**
- Generar embeddings solo una vez
- Usar `text-embedding-3-small` por defecto
- Implementar caché de resultados frecuentes
- Batch processing para generación masiva

### 2. Velocidad

**Optimizaciones implementadas:**

```python
# 1. Limitar envíos a procesar
envios_queryset[:500]  # Máximo 500 envíos por búsqueda

# 2. Select related / Prefetch related
envios = Envio.objects.all()
    .select_related('comprador')
    .prefetch_related('productos')

# 3. Índices en base de datos
class Meta:
    indexes = [
        models.Index(fields=['modelo_usado']),
        models.Index(fields=['fecha_generacion']),
    ]

# 4. Delay entre llamadas API
time.sleep(0.1)  # Evitar rate limits
```

### 3. Precisión

**Mejorar resultados:**

```python
# 1. Ajustar umbral de similitud
umbral_minimo = 0.3  # Por defecto
umbral_estricto = 0.6  # Para resultados más precisos

# 2. Combinar múltiples métricas
# Usar cosine como principal + euclidean para desempatar

# 3. Feedback del usuario
# Registrar qué resultados fueron relevantes
enviarFeedbackSemantico(resultado_id, es_relevante=True)

# 4. Regenerar embeddings periódicamente
python manage.py generar_embeddings_masivo --forzar
```

### 4. Escalabilidad

**Para grandes volúmenes (>10,000 envíos):**

```python
# 1. Usar índices vectoriales de pgvector
# CREATE INDEX ON envioembedding USING ivfflat (embedding_vector vector_cosine_ops);

# 2. Procesamiento asíncrono
from celery import shared_task

@shared_task
def generar_embedding_async(envio_id):
    envio = Envio.objects.get(id=envio_id)
    generar_embedding_envio(envio)

# 3. Caché de Redis para búsquedas frecuentes
# cache.set(f"busqueda:{hash(consulta)}", resultados, timeout=3600)
```

### 5. Monitoreo

```python
# Métricas a monitorear:
- Tiempo promedio de búsqueda
- Tasa de éxito (resultados encontrados / búsquedas)
- Costo acumulado por mes
- Feedback positivo vs negativo
- Embeddings generados vs total de envíos
```

---

## 📈 Métricas del Sistema

### Precisión

```
Precisión = Resultados Relevantes / Total Resultados
```

**Objetivo:** > 80% de resultados relevantes

### Costo

```
Costo mensual estimado:
- 1000 envíos nuevos/mes: ~$0.20
- 10,000 búsquedas/mes: ~$2.00
Total: ~$2.20/mes
```

### Velocidad

```
Tiempos objetivo:
- Generación embedding: < 500ms
- Búsqueda (100 envíos): < 300ms
- Búsqueda (1000 envíos): < 1000ms
```

---

## 🐛 Troubleshooting

### 🔧 Script de Verificación Automática

```bash
# Ejecuta este script para diagnosticar todos los problemas
python backend/verificar_supabase.py
```

Este script verifica automáticamente:
- ✅ Conexión a base de datos
- ✅ pgvector instalado
- ✅ Tablas creadas correctamente
- ✅ OpenAI API configurada
- ✅ SSL habilitado (Supabase)
- ✅ Embeddings de prueba funcionando

---

### Error: "OpenAI API key no configurada"

```bash
# Verificar .env
cat backend/.env | grep OPENAI

# Debe mostrar:
OPENAI_API_KEY=sk-proj-...
```

### Error: "pgvector extension not found"

```sql
-- Para Supabase: Ve a SQL Editor y ejecuta:
CREATE EXTENSION IF NOT EXISTS vector;

-- Para PostgreSQL local:
psql -U postgres -d equityDB

-- Verificar extensión
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Si no existe, instalar
CREATE EXTENSION vector;
```

### Error: "SSL connection is required" (Supabase)

```python
# En backend/settings.py
DATABASES = {
    'default': {
        # ... otras configuraciones
        'OPTIONS': {
            'sslmode': 'require',  # ⚠️ AGREGAR ESTO
        }
    }
}
```

### Error: "could not connect to server" (Supabase)

1. **Verifica la URL de Supabase:**
   ```env
   DB_HOST=db.xxxxxxxxxxxxxx.supabase.co
   ```

2. **Verifica la contraseña:**
   - Settings → Database → Reset Database Password

3. **Verifica que tu IP esté permitida:**
   - Settings → Database → Connection pooling
   - Agrega tu IP o usa `0.0.0.0/0` (solo para desarrollo)

4. **Prueba la conexión:**
   ```bash
   python backend/verificar_supabase.py
   ```

### Error: "No se generan embeddings automáticamente"

```python
# Verificar que la función está siendo llamada
# En views.py, agregar log:
print(f"Generando embedding para envío {envio.hawb}")
generar_embedding_envio(envio)
print(f"Embedding generado exitosamente")
```

### Búsquedas muy lentas

```python
# 1. Verificar número de envíos procesados
print(f"Procesando {envios_queryset.count()} envíos")

# 2. Limitar a 500
envios_queryset[:500]

# 3. Verificar índices en BD
# python manage.py dbshell
# SELECT * FROM pg_indexes WHERE tablename = 'busqueda_envioembedding';
```

---

## ✅ Checklist de Implementación

### Base de Datos
- [ ] PostgreSQL/Supabase con pgvector instalado y habilitado
- [ ] SSL configurado (si usas Supabase: `sslmode=require`)
- [ ] Conexión a base de datos funcionando
- [ ] Migraciones ejecutadas correctamente

### Backend
- [ ] Variables de entorno configuradas (OPENAI_API_KEY, DB_HOST, etc.)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Embeddings generados para envíos existentes
- [ ] API de búsqueda semántica respondiendo correctamente

### Frontend
- [ ] Componente de búsqueda semántica integrado
- [ ] Frontend actualizado con nuevas métricas
- [ ] Interfaz mostrando resultados correctamente

### Verificación
- [ ] Ejecutar: `python backend/verificar_supabase.py` ✅ 100%
- [ ] Prueba de búsqueda semántica funcionando
- [ ] Métricas de costo/velocidad/precisión monitoreadas

### Opcional (Optimización)
- [ ] Índices vectoriales creados (para >1000 envíos)
- [ ] Caché de resultados implementado
- [ ] Feedback de usuarios configurado

---

## 📚 Recursos Adicionales

### Documentación Externa
- [OpenAI Embeddings Documentation](https://platform.openai.com/docs/guides/embeddings)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Supabase Vector Guide](https://supabase.com/docs/guides/ai/vector-columns)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Angular Documentation](https://angular.io/docs)

### Archivos Importantes del Proyecto

**Backend:**
- `backend/apps/busqueda/models.py` - Modelos de embeddings y búsqueda
- `backend/apps/busqueda/views.py` - API de búsqueda semántica
- `backend/apps/busqueda/utils_embeddings.py` - Utilidades para embeddings
- `backend/management/commands/generar_embeddings_masivo.py` - Comando para generación masiva
- `backend/verificar_supabase.py` - Script de verificación ⭐
- `backend/.env` - Variables de entorno (crear desde .env.example)
- `backend/settings.py` - Configuración de Django

**Frontend:**
- `frontend/src/app/models/busqueda-semantica.ts` - Interfaces TypeScript
- `frontend/src/app/services/api.service.ts` - Cliente API
- `frontend/src/app/components/busqueda-semantica/` - Componente de búsqueda

**Documentación:**
- `GUIA_BUSQUEDA_SEMANTICA_COMPLETA.md` - Esta guía (principal)
- `MIGRACION_SUPABASE.md` - Guía de migración a Supabase ⭐
- `RESUMEN_IMPLEMENTACION.md` - Resumen técnico

---

## 🎓 Próximos Pasos

1. **Implementar caché de resultados** para búsquedas frecuentes
2. **Agregar análisis de sentimiento** en observaciones
3. **Dashboard de métricas** en tiempo real
4. **Reentrenamiento periódico** de embeddings
5. **A/B testing** de diferentes modelos

---

**Desarrollado por:** Universal Box Development Team  
**Fecha:** Noviembre 2025  
**Versión:** 1.0.0


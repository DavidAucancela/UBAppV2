# 🔍 Módulo de Búsqueda Semántica

## 📍 Ubicación
- **Frontend:** `frontend/src/app/components/busqueda-semantica/`
- **Backend:** `backend/apps/busqueda/`
- **Ruta:** `/busqueda-semantica`

## 🎯 Funcionalidad
Búsqueda avanzada de envíos usando embeddings y búsqueda vectorial para encontrar resultados por similitud semántica, no solo por palabras clave exactas.

## 📁 Estructura de Archivos

### Frontend
```
busqueda-semantica/
├── busqueda-semantica.component.ts
├── busqueda-semantica.component.html
└── busqueda-semantica.component.css
```

### Backend
```
busqueda/
├── semantic/
│   ├── views.py          # ViewSets de búsqueda
│   ├── serializers.py    # Serializers de búsqueda
│   ├── text_processor.py # Procesamiento de texto
│   └── embeddings.py     # Generación de embeddings
├── models.py             # Modelos relacionados
└── services.py           # Lógica de negocio
```

## 🔑 Componentes Clave

### 1. Procesamiento de Texto
**Archivo:** `backend/apps/busqueda/semantic/text_processor.py`
- Limpieza de texto
- Normalización
- Tokenización
- Preparación para embeddings

### 2. Generación de Embeddings
**Archivo:** `backend/apps/busqueda/semantic/embeddings.py`
- Uso de modelos de IA para generar embeddings
- Almacenamiento en base de datos
- Actualización de embeddings

### 3. Búsqueda Vectorial
**Archivo:** `backend/apps/busqueda/semantic/views.py`
- Búsqueda por similitud coseno
- Ranking de resultados
- Filtrado y paginación

## 📊 Métricas
- **MRR (Mean Reciprocal Rank)**
- **nDCG@10 (Normalized Discounted Cumulative Gain)**
- **Precision@5**

## 🚀 Prompts Útiles

1. **"Muéstrame cómo se generan los embeddings para un envío"**
2. **"Cómo funciona la búsqueda vectorial en el backend"**
3. **"Dónde se procesa el texto antes de generar embeddings"**
4. **"Cómo se calculan las métricas de búsqueda semántica"**
5. **"Cómo se integra la búsqueda semántica en el frontend"**

## 🔗 Relaciones
- **Envios:** Los embeddings se generan para cada envío
- **Dashboard:** Las métricas se muestran en actividades-sistema
- **API:** Endpoints en `/api/busqueda/semantica/`


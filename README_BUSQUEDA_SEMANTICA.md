# 🚀 Búsqueda Semántica - Inicio Rápido

## ⚡ Instalación Rápida (5 minutos)

### Windows

```powershell
cd backend
.\setup_busqueda_semantica.ps1
```

### Linux/Mac

```bash
cd backend
chmod +x setup_busqueda_semantica.sh
./setup_busqueda_semantica.sh
```

---

## 🎯 ¿Qué hace este sistema?

Permite buscar envíos usando **lenguaje natural** con inteligencia artificial:

**Antes (Búsqueda Tradicional):**
```
Campo HAWB: "ABC123"
Campo Estado: "Entregado"
Campo Ciudad: "Quito"
```

**Ahora (Búsqueda Semántica):**
```
"Busca envíos entregados en Quito la semana pasada con peso mayor a 10 kg"
```

---

## 🏗️ Arquitectura Simplificada

```
Usuario escribe consulta
    ↓
OpenAI genera embedding de la consulta (vector de 1536 números)
    ↓
PostgreSQL + pgvector busca envíos similares
    ↓
Sistema calcula similitudes (Cosine, Euclidean, etc.)
    ↓
Retorna resultados ordenados por relevancia
```

---

## 📋 Requisitos Previos

1. **PostgreSQL 14+** con extensión `pgvector`
2. **Python 3.11+**
3. **OpenAI API Key** ([Obtener aquí](https://platform.openai.com/api-keys))

---

## 🔧 Configuración Manual

### 1. Habilitar pgvector en PostgreSQL

```sql
-- Conectar a tu base de datos
psql -U postgres -d equityDB

-- Habilitar extensión
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 2. Configurar .env

```env
# Backend/.env
OPENAI_API_KEY=sk-proj-tu-key-aqui
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536

DB_NAME=equityDB
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

### 3. Instalar dependencias

```bash
cd backend
pip install psycopg2-binary==2.9.9 pgvector==0.2.5
```

### 4. Ejecutar migraciones

```bash
python manage.py migrate busqueda
```

### 5. Generar embeddings

```bash
# Para todos los envíos
python manage.py generar_embeddings_masivo

# Solo 10 para prueba
python manage.py generar_embeddings_masivo --limite 10
```

---

## 🧪 Prueba Rápida

### 1. Iniciar servidor

```bash
cd backend
python manage.py runserver
```

### 2. Hacer una búsqueda

**Con cURL:**

```bash
curl -X POST http://localhost:8000/api/busqueda/semantica/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN" \
  -d '{
    "texto": "envíos entregados en Quito esta semana",
    "limite": 10
  }'
```

**Con Python:**

```python
import requests

response = requests.post(
    'http://localhost:8000/api/busqueda/semantica/',
    headers={'Authorization': 'Bearer TU_TOKEN'},
    json={
        'texto': 'envíos pesados pendientes para Guayaquil',
        'limite': 20
    }
)

resultados = response.json()
print(f"Encontrados: {resultados['totalEncontrados']}")
print(f"Tiempo: {resultados['tiempoRespuesta']}ms")
print(f"Costo: ${resultados['costoConsulta']}")
```

**Respuesta esperada:**

```json
{
  "consulta": "envíos entregados en Quito esta semana",
  "resultados": [
    {
      "envio": {
        "id": 123,
        "hawb": "ABC123456",
        "comprador": "Juan Pérez",
        "ciudad": "Quito",
        "estado": "entregado"
      },
      "cosineSimilarity": 0.8524,
      "dotProduct": 125.67,
      "euclideanDistance": 12.34,
      "razonRelevancia": "Coincide con: ciudad Quito, estado Entregado"
    }
  ],
  "totalEncontrados": 15,
  "tiempoRespuesta": 245,
  "costoConsulta": 0.000012
}
```

---

## 💡 Ejemplos de Consultas

```
✅ "envíos entregados en Quito la semana pasada"
✅ "paquetes pendientes con peso mayor a 10 kg"
✅ "envíos de Juan Pérez retrasados"
✅ "busca todos los envíos de electrónica a Guayaquil"
✅ "paquetes cancelados este mes"
✅ "envíos urgentes de ayer"
```

---

## 📊 Métricas de Similitud

El sistema calcula **4 métricas** para cada resultado:

| Métrica | Descripción | Rango | Mejor valor |
|---------|-------------|-------|-------------|
| **Cosine Similarity** | Ángulo entre vectores | [-1, 1] | 1 (idéntico) |
| **Dot Product** | Producto punto | [0, ∞] | Mayor es mejor |
| **Euclidean Distance** | Distancia geométrica | [0, ∞] | 0 (idéntico) |
| **Manhattan Distance** | Suma diferencias | [0, ∞] | 0 (idéntico) |

**Por defecto se usa Cosine Similarity** (la más común para embeddings).

---

## 💰 Costos

Con `text-embedding-3-small`:

| Operación | Tokens | Costo |
|-----------|--------|-------|
| Generar 1 embedding | ~100 | $0.000002 |
| 1,000 envíos | 100,000 | $0.002 (~0.2¢) |
| 10,000 búsquedas | 500,000 | $0.01 (1¢) |

**Costo mensual estimado:** $2-5 para uso normal.

---

## 🎨 Frontend (Angular)

El componente ya está integrado:

```typescript
// Navegar a:
http://localhost:4200/busqueda-unificada

// O usar el componente directamente:
<app-busqueda-semantica></app-busqueda-semantica>
```

**Funcionalidades del frontend:**
- ✅ Input de lenguaje natural
- ✅ Sugerencias automáticas
- ✅ Visualización de métricas
- ✅ Historial de búsquedas
- ✅ Filtros opcionales
- ✅ Comparación de modelos
- ✅ Métricas de costo/velocidad

---

## 🔍 Comandos Útiles

```bash
# Ver todos los embeddings generados
python manage.py shell
>>> from apps.busqueda.models import EnvioEmbedding
>>> EnvioEmbedding.objects.count()

# Regenerar embeddings (útil tras actualizar datos)
python manage.py generar_embeddings_masivo --forzar

# Generar solo un envío específico
python manage.py generar_embeddings_masivo --hawb ABC123456

# Ver métricas del sistema
curl http://localhost:8000/api/busqueda/semantica/metricas/ \
  -H "Authorization: Bearer TU_TOKEN"
```

---

## 🐛 Troubleshooting

### Error: "pgvector extension not found"

```sql
-- Solución:
psql -U postgres -d equityDB -c "CREATE EXTENSION vector;"
```

### Error: "OpenAI API key no configurada"

```bash
# Verificar .env
cat backend/.env | grep OPENAI_API_KEY

# Debe mostrar:
OPENAI_API_KEY=sk-proj-...
```

### Búsquedas sin resultados

```bash
# Verificar que hay embeddings generados
python manage.py shell
>>> from apps.busqueda.models import EnvioEmbedding
>>> print(f"Embeddings: {EnvioEmbedding.objects.count()}")

# Si es 0, generar:
python manage.py generar_embeddings_masivo
```

### Búsquedas muy lentas (>2s)

- Limitar envíos procesados (ya implementado: máximo 500)
- Crear índices vectoriales en PostgreSQL:

```sql
CREATE INDEX ON busqueda_envioembedding 
USING ivfflat (embedding_vector vector_cosine_ops);
```

---

## 📚 Documentación Completa

Ver: `GUIA_BUSQUEDA_SEMANTICA_COMPLETA.md`

Incluye:
- Arquitectura detallada
- Configuración avanzada
- Optimización de rendimiento
- Mejores prácticas
- Ejemplos completos

---

## ✅ Checklist de Verificación

- [ ] PostgreSQL corriendo con pgvector habilitado
- [ ] Variables de entorno configuradas (.env)
- [ ] Migraciones ejecutadas
- [ ] Al menos 10 embeddings generados
- [ ] Prueba de búsqueda exitosa
- [ ] Frontend funcionando (opcional)

---

## 🎓 Próximos Pasos

1. **Generar embeddings** para todos los envíos existentes
2. **Probar diferentes consultas** para ver la precisión
3. **Monitorear costos** en OpenAI Dashboard
4. **Implementar feedback** para mejorar resultados
5. **Configurar caché** para búsquedas frecuentes

---

## 📞 Soporte

Si tienes problemas:

1. Revisa `GUIA_BUSQUEDA_SEMANTICA_COMPLETA.md`
2. Verifica logs del servidor Django
3. Confirma que PostgreSQL tiene pgvector
4. Valida OpenAI API Key

---

**¡Listo para usar búsqueda semántica! 🎉**

Desarrollado por Universal Box Development Team


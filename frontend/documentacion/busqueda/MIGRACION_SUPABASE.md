# 🚀 Migración a Supabase - Búsqueda Semántica

## ✅ Cambios Necesarios para Supabase

### 1. Verificar Configuración de Base de Datos

Supabase ya tiene **pgvector habilitado**, pero debes asegurarte de que la conexión esté correctamente configurada.

#### Actualizar `backend/settings.py`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='postgres'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),  # URL de Supabase
        'PORT': env('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'require',  # ⚠️ IMPORTANTE para Supabase
        }
    }
}
```

#### Actualizar `backend/.env`

```env
# Supabase Database Connection
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=tu_supabase_password
DB_HOST=db.xxxxxxxxxxxxxx.supabase.co  # Tu URL de Supabase
DB_PORT=5432

# OpenAI API
OPENAI_API_KEY=sk-proj-tu-key-de-openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536

# Django
SECRET_KEY=tu-secret-key
DEBUG=True
```

**📍 Obtener credenciales de Supabase:**
1. Ve a tu proyecto en https://app.supabase.com
2. Settings → Database
3. Copia la **Connection string** (modo directo)
4. Extrae: host, user, password, dbname

---

### 2. Verificar que pgvector esté Habilitado

Conéctate a tu base de datos Supabase y ejecuta:

```sql
-- Verificar si pgvector está instalado
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Si no está, habilitarlo (normalmente ya está en Supabase)
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar versión
SELECT extversion FROM pg_extension WHERE extname = 'vector';
```

✅ **Supabase incluye pgvector por defecto**, así que este paso solo es verificación.

---

### 3. Ejecutar Migraciones

```bash
cd backend

# Ejecutar todas las migraciones
python manage.py migrate

# Verificar que las tablas se crearon correctamente
python manage.py dbshell
```

En el shell de PostgreSQL:

```sql
-- Verificar que la tabla de embeddings existe
\dt busqueda_envioembedding

-- Ver estructura de la tabla
\d busqueda_envioembedding

-- Verificar que el campo vector existe
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'busqueda_envioembedding';
```

Deberías ver el campo `embedding_vector` de tipo `USER-DEFINED` (que es el tipo vector de pgvector).

---

### 4. Crear Índices Vectoriales (Opcional pero Recomendado)

Para mejorar el rendimiento en búsquedas grandes (>1000 envíos), crea índices vectoriales:

```sql
-- Conectar a Supabase (SQL Editor o psql)

-- Índice IVFFlat para búsqueda rápida por similitud coseno
CREATE INDEX IF NOT EXISTS idx_envioembedding_vector_cosine
ON busqueda_envioembedding
USING ivfflat (embedding_vector vector_cosine_ops)
WITH (lists = 100);

-- Índice para búsqueda por producto punto
CREATE INDEX IF NOT EXISTS idx_envioembedding_vector_ip
ON busqueda_envioembedding
USING ivfflat (embedding_vector vector_ip_ops)
WITH (lists = 100);

-- Índice para distancia euclidiana
CREATE INDEX IF NOT EXISTS idx_envioembedding_vector_l2
ON busqueda_envioembedding
USING ivfflat (embedding_vector vector_l2_ops)
WITH (lists = 100);
```

**Notas sobre índices:**
- `lists = 100` es apropiado para ~10,000 registros
- Para más registros, usa `lists = sqrt(registros)`
- Los índices IVFFlat son aproximados pero muy rápidos
- Solo crea índices después de tener algunos embeddings generados

---

### 5. Actualizar el Modelo (Si es Necesario)

El modelo actual ya está compatible con Supabase. Solo verifica que `pgvector.django` esté instalado:

```bash
pip install pgvector==0.2.5
```

**Modelo actual (`backend/apps/busqueda/models.py`):**

```python
from pgvector.django import VectorField

class EnvioEmbedding(models.Model):
    envio = models.OneToOneField('archivos.Envio', on_delete=models.CASCADE, related_name='embedding')
    
    # ✅ Campo compatible con Supabase pgvector
    embedding_vector = VectorField(
        dimensions=1536,
        null=True,
        blank=True
    )
    
    texto_indexado = models.TextField()
    fecha_generacion = models.DateTimeField(auto_now=True)
    modelo_usado = models.CharField(max_length=100, default='text-embedding-3-small')
```

**✅ No necesitas cambiar nada en el modelo.**

---

### 6. Generar Embeddings para Envíos Existentes

```bash
cd backend

# Generar embeddings para todos los envíos
python manage.py generar_embeddings_masivo

# O con opciones
python manage.py generar_embeddings_masivo --limite 10 --delay 0.2
```

---

### 7. Probar la Búsqueda Semántica

#### Desde el Frontend:

```
http://localhost:4200/busqueda-unificada
```

Prueba consultas como:
- "envíos pesados a Quito"
- "paquetes entregados esta semana"
- "envíos pendientes de Juan Pérez"

#### Desde la API directamente:

```bash
curl -X POST http://localhost:8000/api/busqueda/semantica/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tu_token" \
  -d '{
    "texto": "envíos pesados a Quito",
    "limite": 10
  }'
```

---

## 🔍 Diferencias entre PostgreSQL Local y Supabase

| Aspecto | PostgreSQL Local | Supabase |
|---------|------------------|----------|
| **pgvector** | Requiere instalación manual | ✅ Ya incluido |
| **SSL** | Opcional | ⚠️ Requerido (`sslmode=require`) |
| **Host** | `localhost` | `db.xxxxx.supabase.co` |
| **Puerto** | `5432` | `5432` |
| **Extensiones** | Necesitas instalarlas | Mayoría pre-instaladas |
| **Backups** | Manual | Automático |
| **Escalabilidad** | Manual | Automática |

---

## 🚨 Problemas Comunes y Soluciones

### Error: "SSL connection required"

```python
# En settings.py
DATABASES = {
    'default': {
        # ...
        'OPTIONS': {
            'sslmode': 'require',  # ⚠️ Agregar esto
        }
    }
}
```

### Error: "pgvector extension not found"

```sql
-- Conectar a Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

### Error: "could not connect to server"

Verifica:
1. URL de Supabase correcta en `.env`
2. Contraseña correcta
3. IP permitida en Supabase (Settings → Database → Connection pooling)
4. Puerto 5432 abierto en tu firewall

### Error: "Invalid dimensions for model"

```python
# En .env, asegúrate de que coincida con el modelo
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536  # 1536 para small, 3072 para large
```

---

## ✅ Checklist de Migración

- [ ] Credenciales de Supabase configuradas en `.env`
- [ ] `sslmode=require` agregado en `settings.py`
- [ ] Verificado que pgvector está habilitado
- [ ] Migraciones ejecutadas correctamente
- [ ] Tabla `busqueda_envioembedding` creada
- [ ] Campo `embedding_vector` existe y es tipo vector
- [ ] Índices vectoriales creados (opcional)
- [ ] Embeddings generados para envíos existentes
- [ ] Búsqueda semántica probada y funcionando
- [ ] API de OpenAI funcionando correctamente

---

## 📊 Monitoreo en Supabase

### Ver estadísticas de uso:

```sql
-- Cantidad de embeddings generados
SELECT COUNT(*) FROM busqueda_envioembedding;

-- Modelos usados
SELECT modelo_usado, COUNT(*) as cantidad
FROM busqueda_envioembedding
GROUP BY modelo_usado;

-- Embeddings más recientes
SELECT 
    e.hawb,
    ee.fecha_generacion,
    ee.modelo_usado
FROM busqueda_envioembedding ee
JOIN archivos_envio e ON ee.envio_id = e.id
ORDER BY ee.fecha_generacion DESC
LIMIT 10;

-- Tamaño de la tabla
SELECT 
    pg_size_pretty(pg_total_relation_size('busqueda_envioembedding')) as tamaño_total;
```

---

## 🎯 Ventajas de Usar Supabase

✅ **pgvector pre-instalado** - No necesitas instalar nada  
✅ **Backups automáticos** - Tus datos están seguros  
✅ **Escalabilidad** - Crece con tu aplicación  
✅ **Dashboard integrado** - Monitoreo fácil  
✅ **API REST automática** - Si quieres usarla (opcional)  
✅ **Edge Functions** - Para procesamiento serverless  
✅ **Real-time** - Para actualizaciones en vivo (opcional)  

---

## 📚 Recursos Adicionales

- [Documentación Supabase Vector](https://supabase.com/docs/guides/ai/vector-columns)
- [pgvector en Supabase](https://supabase.com/blog/openai-embeddings-postgres-vector)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)

---

## 🎓 Próximos Pasos

1. **Monitorear costos de OpenAI** - Revisa tu uso en https://platform.openai.com/usage
2. **Ajustar umbrales** - Experimenta con diferentes umbrales de similitud
3. **Crear caché** - Para búsquedas frecuentes (Redis recomendado)
4. **A/B Testing** - Prueba diferentes modelos de embedding
5. **Feedback del usuario** - Mejora los resultados con feedback

---

**✅ Tu sistema ya está listo para funcionar con Supabase!**


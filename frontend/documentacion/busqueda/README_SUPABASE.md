# 📚 Documentación de Búsqueda Semántica con Supabase

## 🎯 ¿Por dónde empiezo?

### Para respuestas rápidas (⚡ 5 minutos)
→ **[RESPUESTA_RAPIDA_SUPABASE.md](./RESPUESTA_RAPIDA_SUPABASE.md)**

Responde:
- ¿Dónde se guardan los embeddings?
- ¿Qué cambios necesito para Supabase?
- Pasos rápidos de implementación

### Para migración paso a paso (📋 15 minutos)
→ **[MIGRACION_SUPABASE.md](./MIGRACION_SUPABASE.md)**

Incluye:
- Configuración detallada de Supabase
- Actualización de settings.py
- Creación de índices vectoriales
- Troubleshooting completo

### Para entender todo el sistema (📖 30 minutos)
→ **[GUIA_BUSQUEDA_SEMANTICA_COMPLETA.md](./GUIA_BUSQUEDA_SEMANTICA_COMPLETA.md)**

Cubre:
- Arquitectura completa del sistema
- Métricas de similitud (cosine, euclidean, etc.)
- Generación de embeddings
- Optimización y mejores prácticas

---

## 🚀 Quick Start

```bash
# 1. Verificar que todo esté configurado
python backend/verificar_supabase.py

# 2. Si hay errores, seguir MIGRACION_SUPABASE.md

# 3. Generar embeddings para envíos existentes
python manage.py generar_embeddings_masivo --limite 10

# 4. Probar búsqueda
# Frontend: http://localhost:4200/busqueda-unificada
```

---

## 📂 Archivos de Documentación

| Archivo | Descripción | Tiempo |
|---------|-------------|--------|
| **RESPUESTA_RAPIDA_SUPABASE.md** | Respuestas directas + quick start | ⚡ 5 min |
| **MIGRACION_SUPABASE.md** | Guía paso a paso de migración | 📋 15 min |
| **GUIA_BUSQUEDA_SEMANTICA_COMPLETA.md** | Documentación completa del sistema | 📖 30 min |
| **RESUMEN_IMPLEMENTACION.md** | Resumen técnico de implementación | 📊 10 min |

---

## 🔑 Conceptos Clave

### Embedding de Envío
- ✅ **Se guarda permanentemente** en Supabase
- 📍 Tabla: `busqueda_envioembedding`
- 📏 Campo: `embedding_vector` (VECTOR de 1536 dimensiones)
- ⏱️ Se genera: Al crear o importar un envío
- 💰 Costo: Una vez por envío (~$0.0002)

### Embedding de Consulta
- ❌ **NO se guarda** (solo en memoria)
- 🔄 Se genera: Cada vez que se hace una búsqueda
- 📝 Solo se guarda el historial (texto + metadata)
- 💰 Costo: Cada búsqueda (~$0.00002)

---

## 🛠️ Herramientas

### Script de Verificación
```bash
python backend/verificar_supabase.py
```

Verifica automáticamente:
- ✅ Conexión a Supabase
- ✅ pgvector habilitado
- ✅ Tablas creadas
- ✅ OpenAI configurado
- ✅ SSL funcionando

### Comandos de Gestión

```bash
# Generar embeddings para todos los envíos
python manage.py generar_embeddings_masivo

# Generar solo para nuevos envíos
python manage.py generar_embeddings_masivo --limite 50

# Forzar regeneración
python manage.py generar_embeddings_masivo --forzar

# Generar para un envío específico
python manage.py generar_embeddings_masivo --hawb ABC123456
```

---

## 🔧 Configuración Requerida

### Backend (.env)
```env
# Supabase
DB_HOST=db.xxxxxxxxxxxxxx.supabase.co
DB_PASSWORD=tu_password
DB_NAME=postgres
DB_USER=postgres
DB_PORT=5432

# OpenAI
OPENAI_API_KEY=sk-proj-tu-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### Backend (settings.py)
```python
DATABASES = {
    'default': {
        # ...
        'OPTIONS': {
            'sslmode': 'require',  # ⚠️ REQUERIDO
        }
    }
}
```

---

## 📊 Flujo de Datos

### Crear Envío
```
Usuario → Crear Envío → Generar Texto → OpenAI API → Embedding
                                                         ↓
                                    Supabase ← busqueda_envioembedding
```

### Buscar Envío
```
Usuario → Consulta → OpenAI API → Embedding (temporal)
                                        ↓
                      Buscar en Supabase (embeddings guardados)
                                        ↓
                      Calcular similitudes (cosine, euclidean, etc.)
                                        ↓
                      Retornar resultados ordenados
```

---

## 🎯 Checklist de Implementación

- [ ] Credenciales de Supabase en `.env`
- [ ] SSL habilitado en `settings.py`
- [ ] OpenAI API key configurada
- [ ] Ejecutar: `python backend/verificar_supabase.py` → 100% ✅
- [ ] Ejecutar migraciones: `python manage.py migrate`
- [ ] Generar embeddings: `python manage.py generar_embeddings_masivo`
- [ ] Probar búsqueda en frontend

---

## 🐛 Solución de Problemas

### Error: SSL connection required
```python
# En settings.py
'OPTIONS': {'sslmode': 'require'}
```

### Error: pgvector not found
```sql
-- En Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

### Error: No embeddings found
```bash
python manage.py generar_embeddings_masivo --limite 10
```

### Error: OpenAI API key invalid
```bash
# Verifica tu key en: https://platform.openai.com/api-keys
# Verifica créditos: https://platform.openai.com/usage
```

---

## 📈 Monitoreo

### Ver embeddings generados
```sql
-- En Supabase SQL Editor
SELECT COUNT(*) FROM busqueda_envioembedding;

SELECT 
    e.hawb,
    ee.modelo_usado,
    ee.fecha_generacion
FROM busqueda_envioembedding ee
JOIN archivos_envio e ON ee.envio_id = e.id
ORDER BY ee.fecha_generacion DESC
LIMIT 10;
```

### Métricas de búsqueda
```bash
# API endpoint
GET /api/busqueda/semantica/metricas/
```

---

## 🆘 ¿Necesitas Ayuda?

1. **Ejecuta el script de verificación:**
   ```bash
   python backend/verificar_supabase.py
   ```

2. **Revisa la sección Troubleshooting en:**
   - `MIGRACION_SUPABASE.md` → Problemas de configuración
   - `GUIA_BUSQUEDA_SEMANTICA_COMPLETA.md` → Problemas de búsqueda

3. **Verifica logs del servidor:**
   ```bash
   python manage.py runserver
   # Revisa errores en la consola
   ```

---

## 🎓 Recursos Externos

- [Supabase Vector Guide](https://supabase.com/docs/guides/ai/vector-columns)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [pgvector GitHub](https://github.com/pgvector/pgvector)

---

**✨ Tu sistema de búsqueda semántica está listo para funcionar con Supabase!**


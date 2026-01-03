# ⚡ Respuesta Rápida: Configurar Supabase para Búsqueda Semántica

## 📍 Respuestas a tus Preguntas

### 1. ¿Dónde se guarda el embedding de un envío?

**Se guarda en la tabla `busqueda_envioembedding` en Supabase:**

```sql
-- Estructura de la tabla
CREATE TABLE busqueda_envioembedding (
    id SERIAL PRIMARY KEY,
    envio_id INTEGER UNIQUE NOT NULL,
    embedding_vector VECTOR(1536),  -- ⭐ Aquí se guarda el embedding
    texto_indexado TEXT NOT NULL,
    fecha_generacion TIMESTAMP,
    modelo_usado VARCHAR(100)
);
```

**Código Python (modelo Django):**
```python
class EnvioEmbedding(models.Model):
    envio = models.OneToOneField('archivos.Envio', on_delete=models.CASCADE)
    embedding_vector = VectorField(dimensions=1536)  # ⭐ Vector de 1536 dimensiones
    texto_indexado = models.TextField()
    modelo_usado = models.CharField(max_length=100)
```

**✅ Se guarda PERMANENTEMENTE en Supabase** cuando creas o importas un envío.

---

### 2. ¿Dónde se guarda el embedding de una consulta?

**❌ NO se guarda permanentemente.**

El embedding de una consulta se genera **en tiempo real** cada vez que haces una búsqueda:

```python
# En views.py - método _generar_embedding()
embedding_resultado = self._generar_embedding(consulta_texto, modelo_embedding)
embedding_consulta = embedding_resultado['embedding']  # ⭐ Se usa aquí

# Se usa para calcular similitud con los embeddings de envíos
resultados = calcular_similitudes(embedding_consulta, embeddings_envios)

# ❌ No se guarda en la base de datos
```

**Lo único que se guarda de la consulta es el historial:**
```python
BusquedaSemantica.objects.create(
    usuario=request.user,
    consulta=consulta_texto,  # ✅ Solo el texto
    resultados_encontrados=len(resultados),
    tiempo_respuesta=tiempo_respuesta,
    costo_consulta=costo_consulta
    # ❌ NO se guarda el vector embedding
)
```

---

## 🔧 Cambios Necesarios para Supabase

### ✅ Buenas Noticias

**Tu código actual YA FUNCIONA con Supabase sin cambios mayores.**

Supabase incluye:
- ✅ pgvector pre-instalado
- ✅ PostgreSQL 14+
- ✅ Todas las extensiones necesarias

### ⚠️ Único Cambio Requerido: SSL

**En `backend/settings.py`:**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='postgres'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'require',  # ⭐ AGREGAR ESTA LÍNEA
        }
    }
}
```

**En `backend/.env`:**

```env
# Supabase Connection (obtén estos valores de tu proyecto Supabase)
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=tu_supabase_password_aqui
DB_HOST=db.xxxxxxxxxxxxxx.supabase.co  # ⭐ Cambia por tu URL de Supabase
DB_PORT=5432

# OpenAI (sin cambios)
OPENAI_API_KEY=sk-proj-tu-key-aqui
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536
```

---

## 📋 Pasos para Implementar

### 1. Obtener Credenciales de Supabase

```
1. Ve a https://app.supabase.com
2. Selecciona tu proyecto
3. Settings → Database
4. Copia la "Connection string" (modo directo)
5. Extrae: host, user, password
```

### 2. Actualizar Configuración

```bash
# Editar backend/.env
DB_HOST=db.xxxxxxxxxxxxxx.supabase.co
DB_PASSWORD=tu_password_de_supabase
```

```python
# Editar backend/settings.py
DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require'
}
```

### 3. Verificar pgvector en Supabase

```sql
-- En Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 4. Ejecutar Migraciones

```bash
cd backend
python manage.py migrate
```

### 5. Verificar Todo con el Script

```bash
# ⭐ Ejecuta el script de verificación automática
python backend/verificar_supabase.py
```

Este script verifica:
- ✅ Conexión a Supabase
- ✅ pgvector habilitado
- ✅ Tablas creadas
- ✅ OpenAI configurado
- ✅ SSL funcionando
- ✅ Embedding de prueba

### 6. Generar Embeddings

```bash
# Generar embeddings para todos los envíos existentes
python manage.py generar_embeddings_masivo

# O con límite para pruebas
python manage.py generar_embeddings_masivo --limite 10
```

### 7. Probar Búsqueda

```bash
# Iniciar backend
python manage.py runserver

# Iniciar frontend (en otra terminal)
cd frontend
npm start

# Abrir en navegador
http://localhost:4200/busqueda-unificada
```

---

## 🎯 Resumen Visual del Flujo

```
┌──────────────────────────────────────────────────────────┐
│ 1. CREAR ENVÍO                                           │
├──────────────────────────────────────────────────────────┤
│ Usuario crea envío (manual o Excel)                     │
│         ↓                                                │
│ Backend genera texto descriptivo                         │
│         ↓                                                │
│ OpenAI genera embedding (1536 dims)                      │
│         ↓                                                │
│ ✅ Se guarda en Supabase → busqueda_envioembedding      │
│    (embedding_vector de tipo VECTOR)                     │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ 2. BUSCAR ENVÍO                                          │
├──────────────────────────────────────────────────────────┤
│ Usuario escribe: "envíos pesados a Quito"               │
│         ↓                                                │
│ Backend genera embedding de consulta (OpenAI)            │
│         ↓                                                │
│ ❌ NO se guarda (solo se usa en memoria)                │
│         ↓                                                │
│ Backend busca en Supabase todos los embeddings          │
│         ↓                                                │
│ Calcula similitudes (cosine, euclidean, etc.)           │
│         ↓                                                │
│ Retorna top N resultados ordenados                       │
│         ↓                                                │
│ ✅ Se guarda solo el HISTORIAL (texto + metadata)       │
│    NO el vector embedding                                │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 Tabla Comparativa

| Concepto | Embedding de Envío | Embedding de Consulta |
|----------|-------------------|----------------------|
| **¿Se guarda?** | ✅ Sí, permanentemente | ❌ No, solo en memoria |
| **¿Dónde?** | Supabase → `busqueda_envioembedding` | En memoria RAM durante la búsqueda |
| **¿Cuándo se genera?** | Al crear/importar envío | Cada vez que buscas |
| **Tabla/Modelo** | `EnvioEmbedding` | No tiene modelo |
| **Campo** | `embedding_vector` | Variable temporal |
| **Costo OpenAI** | Una vez por envío | Cada búsqueda |
| **Dimensiones** | 1536 | 1536 |

---

## 🚀 Comandos Rápidos

```bash
# Verificar configuración completa
python backend/verificar_supabase.py

# Generar embeddings
python manage.py generar_embeddings_masivo --limite 50

# Ver embeddings en base de datos
python manage.py dbshell
SELECT COUNT(*) FROM busqueda_envioembedding;

# Ejecutar búsqueda de prueba (curl)
curl -X POST http://localhost:8000/api/busqueda/semantica/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tu_token" \
  -d '{"texto": "envíos pesados", "limite": 10}'
```

---

## 📚 Documentación Completa

- **Guía principal:** `GUIA_BUSQUEDA_SEMANTICA_COMPLETA.md`
- **Migración detallada:** `MIGRACION_SUPABASE.md`
- **Script de verificación:** `backend/verificar_supabase.py`

---

## ✅ ¿Todo Funcionando?

Ejecuta:
```bash
python backend/verificar_supabase.py
```

Deberías ver:
```
✅ Conectado a PostgreSQL
✅ Usando Supabase ✨
✅ pgvector instalado
✅ Tabla busqueda_envioembedding existe
✅ Campo embedding_vector existe
✅ OPENAI_API_KEY configurada
✅ SSL configurado correctamente
✅ Embedding generado exitosamente

🎉 ¡TODO ESTÁ CONFIGURADO CORRECTAMENTE!
```

---

**¿Necesitas ayuda?** Revisa:
1. `MIGRACION_SUPABASE.md` - Troubleshooting detallado
2. Ejecuta `python backend/verificar_supabase.py` para diagnóstico
3. Verifica logs: `python manage.py runserver` (busca errores)


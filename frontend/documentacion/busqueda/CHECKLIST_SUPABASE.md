# ✅ Checklist de Migración a Supabase

## 📋 Instrucciones

Marca cada item al completarlo. Ejecuta los comandos en orden.

---

## 1️⃣ Configurar Supabase

### 1.1 Obtener Credenciales

- [ ] Ir a https://app.supabase.com
- [ ] Seleccionar tu proyecto (o crear uno nuevo)
- [ ] Ir a **Settings → Database**
- [ ] Copiar **Connection string** (modo directo)
- [ ] Anotar:
  ```
  Host: db.______________________.supabase.co
  User: postgres
  Password: ____________________
  Database: postgres
  Port: 5432
  ```

### 1.2 Verificar pgvector

- [ ] Ir a **SQL Editor** en Supabase
- [ ] Ejecutar:
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  SELECT * FROM pg_extension WHERE extname = 'vector';
  ```
- [ ] Verificar que retorna una fila con la extensión `vector`

---

## 2️⃣ Actualizar Backend

### 2.1 Configurar Variables de Entorno

- [ ] Abrir `backend/.env`
- [ ] Actualizar credenciales de base de datos:
  ```env
  DB_HOST=db.xxxxxxxxxxxxxx.supabase.co
  DB_USER=postgres
  DB_PASSWORD=tu_password_supabase
  DB_NAME=postgres
  DB_PORT=5432
  ```

- [ ] Verificar OpenAI API Key:
  ```env
  OPENAI_API_KEY=sk-proj-tu-key-aqui
  OPENAI_EMBEDDING_MODEL=text-embedding-3-small
  OPENAI_EMBEDDING_DIMENSIONS=1536
  ```

### 2.2 Configurar SSL en settings.py

- [ ] Abrir `backend/settings.py`
- [ ] Buscar la sección `DATABASES`
- [ ] Agregar/actualizar la sección `OPTIONS`:
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

### 2.3 Instalar Dependencias

- [ ] Ejecutar:
  ```bash
  cd backend
  pip install -r requirements.txt
  ```

- [ ] Verificar que estén instaladas:
  - `psycopg2-binary==2.9.9`
  - `pgvector==0.2.5`
  - `openai==1.12.0`
  - `numpy==1.26.4`

---

## 3️⃣ Verificar Configuración

### 3.1 Ejecutar Script de Verificación

- [ ] Ejecutar:
  ```bash
  python backend/verificar_supabase.py
  ```

- [ ] Verificar que todas las comprobaciones pasen (✅):
  - [ ] ✅ Conectado a PostgreSQL
  - [ ] ✅ Usando Supabase
  - [ ] ✅ pgvector instalado
  - [ ] ✅ Tabla busqueda_envioembedding existe
  - [ ] ✅ Campo embedding_vector existe
  - [ ] ✅ OPENAI_API_KEY configurada
  - [ ] ✅ Conexión a OpenAI API exitosa
  - [ ] ✅ SSL configurado correctamente
  - [ ] ✅ Embedding generado exitosamente

### 3.2 Si Hay Errores

**Error de conexión:**
- [ ] Verificar credenciales en `.env`
- [ ] Verificar que tu IP esté permitida en Supabase
- [ ] Ir a Settings → Database → Connection pooling

**Error de pgvector:**
- [ ] Ejecutar en Supabase SQL Editor:
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  ```

**Error de SSL:**
- [ ] Verificar que agregaste `'sslmode': 'require'` en settings.py

**Error de OpenAI:**
- [ ] Verificar API key en https://platform.openai.com/api-keys
- [ ] Verificar créditos en https://platform.openai.com/usage

---

## 4️⃣ Ejecutar Migraciones

- [ ] Ejecutar:
  ```bash
  cd backend
  python manage.py migrate
  ```

- [ ] Verificar que no hay errores
- [ ] Verificar en Supabase que las tablas se crearon:
  - [ ] `busqueda_envioembedding`
  - [ ] `busqueda_busquedasemantica`
  - [ ] `busqueda_feedbacksemantico`

---

## 5️⃣ Generar Embeddings

### 5.1 Prueba con Pocos Registros

- [ ] Ejecutar:
  ```bash
  python manage.py generar_embeddings_masivo --limite 10
  ```

- [ ] Verificar que se generan correctamente
- [ ] Ver logs de:
  - Cantidad de envíos procesados
  - Tokens utilizados
  - Costo estimado
  - Embeddings generados exitosamente

### 5.2 Generar para Todos los Envíos

- [ ] Ejecutar (puede tardar varios minutos):
  ```bash
  python manage.py generar_embeddings_masivo
  ```

- [ ] Esperar a que termine el proceso
- [ ] Verificar resumen final:
  - Total procesados
  - Exitosos
  - Fallidos
  - Costo total

### 5.3 Verificar en Base de Datos

- [ ] En Supabase SQL Editor ejecutar:
  ```sql
  SELECT COUNT(*) FROM busqueda_envioembedding;
  ```

- [ ] Verificar que coincide con el número de envíos

---

## 6️⃣ Crear Índices (Opcional - Para >1000 registros)

- [ ] Si tienes más de 1000 envíos, ejecutar en Supabase SQL Editor:
  ```sql
  -- Índice para similitud coseno
  CREATE INDEX IF NOT EXISTS idx_envioembedding_vector_cosine
  ON busqueda_envioembedding
  USING ivfflat (embedding_vector vector_cosine_ops)
  WITH (lists = 100);

  -- Índice para producto punto
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

- [ ] Verificar que se crearon:
  ```sql
  SELECT indexname FROM pg_indexes 
  WHERE tablename = 'busqueda_envioembedding';
  ```

---

## 7️⃣ Probar Búsqueda Semántica

### 7.1 Desde Backend (API)

- [ ] Iniciar servidor:
  ```bash
  python manage.py runserver
  ```

- [ ] Probar endpoint con curl:
  ```bash
  curl -X POST http://localhost:8000/api/busqueda/semantica/ \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer tu_token" \
    -d '{
      "texto": "envíos pesados a Quito",
      "limite": 10
    }'
  ```

- [ ] Verificar respuesta con:
  - [ ] `resultados` con al menos 1 envío
  - [ ] `totalEncontrados` > 0
  - [ ] `tiempoRespuesta` < 1000ms
  - [ ] `costoConsulta` > 0

### 7.2 Desde Frontend

- [ ] Iniciar frontend:
  ```bash
  cd frontend
  npm start
  ```

- [ ] Abrir en navegador:
  ```
  http://localhost:4200/busqueda-unificada
  ```

- [ ] Probar búsquedas:
  - [ ] "envíos pesados"
  - [ ] "paquetes entregados en Quito"
  - [ ] "envíos pendientes de [nombre_comprador]"

- [ ] Verificar que:
  - [ ] Se muestran resultados
  - [ ] Las métricas aparecen (cosine, euclidean, etc.)
  - [ ] Los fragmentos relevantes se destacan
  - [ ] El tiempo de respuesta es razonable

---

## 8️⃣ Verificación Final

### 8.1 Métricas del Sistema

- [ ] Verificar en el frontend o ejecutar:
  ```bash
  curl http://localhost:8000/api/busqueda/semantica/metricas/ \
    -H "Authorization: Bearer tu_token"
  ```

- [ ] Verificar que muestre:
  - [ ] `totalBusquedas` > 0
  - [ ] `totalEmbeddings` = número de envíos
  - [ ] `tiempoPromedioRespuesta` < 1000ms

### 8.2 Historial de Búsquedas

- [ ] Verificar que las búsquedas se guardan:
  ```sql
  SELECT * FROM busqueda_busquedasemantica 
  ORDER BY fecha_busqueda DESC 
  LIMIT 5;
  ```

### 8.3 Prueba de Estrés (Opcional)

- [ ] Hacer 10 búsquedas consecutivas
- [ ] Verificar que todas respondan correctamente
- [ ] Verificar tiempos de respuesta consistentes

---

## 9️⃣ Monitoreo y Mantenimiento

### 9.1 Configurar Alertas (Opcional)

- [ ] En Supabase: Dashboard → Monitor
- [ ] Configurar alertas para:
  - [ ] Uso de CPU > 80%
  - [ ] Uso de almacenamiento > 80%
  - [ ] Errores de conexión

### 9.2 Backups

- [ ] Verificar que Supabase tenga backups automáticos habilitados
- [ ] Settings → Database → Backups
- [ ] Configurar retención de backups (7 días recomendado)

### 9.3 Monitoreo de Costos OpenAI

- [ ] Ir a https://platform.openai.com/usage
- [ ] Verificar uso mensual
- [ ] Configurar alertas de gasto si es necesario

---

## 🎉 ¡Completado!

Si todos los items están marcados, tu sistema de búsqueda semántica está **completamente configurado y funcionando con Supabase**.

### 📊 Resumen

```
Total de pasos completados: ___/90

Secciones:
1. Supabase configurado        ✅ / ❌
2. Backend actualizado         ✅ / ❌
3. Configuración verificada    ✅ / ❌
4. Migraciones ejecutadas      ✅ / ❌
5. Embeddings generados        ✅ / ❌
6. Índices creados (opcional)  ✅ / ❌
7. Búsqueda probada            ✅ / ❌
8. Verificación final          ✅ / ❌
9. Monitoreo configurado       ✅ / ❌
```

---

## 🆘 ¿Problemas?

Si algún paso falló:

1. **Ejecutar diagnóstico:**
   ```bash
   python backend/verificar_supabase.py
   ```

2. **Revisar logs:**
   ```bash
   python manage.py runserver
   # Ver errores en la consola
   ```

3. **Consultar documentación:**
   - `MIGRACION_SUPABASE.md` → Troubleshooting detallado
   - `RESPUESTA_RAPIDA_SUPABASE.md` → Soluciones rápidas

4. **Verificar configuración:**
   - [ ] `.env` con credenciales correctas
   - [ ] `settings.py` con SSL habilitado
   - [ ] OpenAI API key válida
   - [ ] pgvector habilitado en Supabase

---

## 📚 Próximos Pasos

- [ ] Implementar caché de resultados (Redis)
- [ ] Configurar feedback de usuarios
- [ ] Crear dashboard de métricas
- [ ] A/B testing con diferentes modelos
- [ ] Optimizar índices vectoriales

---

**✨ ¡Felicitaciones! Tu sistema está listo para producción.**


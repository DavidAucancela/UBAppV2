# 🧠 Búsqueda Semántica Implementada - Backend

## ✅ Estado: COMPLETADO

La funcionalidad de búsqueda semántica ha sido completamente implementada en el backend utilizando **OpenAI Embeddings**.

---

## 📋 Resumen de Implementación

### 1. Dependencias Instaladas ✅
- `openai==1.12.0` - Cliente de OpenAI para embeddings
- `numpy==1.26.4` - Procesamiento numérico para vectores

### 2. Configuración ✅

**Archivo:** `backend/settings.py`

```python
# Configuración de OpenAI para búsqueda semántica
OPENAI_API_KEY = 'sk-proj-k0L-7LqiRAKER0gD5VFRpOdVkoD1J1k-...'
OPENAI_EMBEDDING_MODEL = 'text-embedding-3-small'  # Modelo económico y rápido
OPENAI_EMBEDDING_DIMENSIONS = 1536
```

### 3. Modelos Creados ✅

**Archivo:** `backend/apps/busqueda/models.py`

1. **EnvioEmbedding** - Almacena vectores de embeddings de envíos
2. **BusquedaSemantica** - Historial de búsquedas semánticas
3. **FeedbackSemantico** - Feedback de usuarios sobre resultados
4. **SugerenciaSemantica** - Sugerencias predefinidas de búsqueda

### 4. Endpoints Implementados ✅

**Archivo:** `backend/apps/busqueda/views.py`

#### Endpoint Principal
```
POST /api/busqueda/semantica/
```

**Request Body:**
```json
{
  "texto": "envíos entregados en Quito la semana pasada",
  "limite": 20,
  "filtrosAdicionales": {
    "fechaDesde": "2025-01-01",
    "estado": "entregado"
  }
}
```

**Response:**
```json
{
  "consulta": "envíos entregados en Quito la semana pasada",
  "resultados": [
    {
      "envio": {
        "id": 1,
        "hawb": "HAWB001",
        "comprador_info": {...},
        "estado": "entregado",
        ...
      },
      "puntuacionSimilitud": 0.92,
      "fragmentosRelevantes": [
        "Envío a Quito",
        "Entregado el 12 de enero"
      ],
      "razonRelevancia": "Coincide con: ciudad Quito, estado Entregado"
    }
  ],
  "totalEncontrados": 5,
  "tiempoRespuesta": 156,
  "modeloUtilizado": "text-embedding-3-small",
  "busquedaId": 123
}
```

#### Otros Endpoints

```bash
# Sugerencias
GET /api/busqueda/semantica/sugerencias/?q=envios

# Historial
GET /api/busqueda/semantica/historial/
POST /api/busqueda/semantica/historial/
DELETE /api/busqueda/semantica/historial/

# Feedback
POST /api/busqueda/semantica/feedback/
{
  "resultadoId": 123,
  "esRelevante": true,
  "busquedaId": 456,
  "puntuacionSimilitud": 0.85
}

# Métricas
GET /api/busqueda/semantica/metricas/
```

### 5. Comando de Management ✅

**Archivo:** `backend/apps/busqueda/management/commands/generar_embeddings.py`

```bash
# Generar embeddings para todos los envíos sin embedding
python manage.py generar_embeddings

# Regenerar todos los embeddings
python manage.py generar_embeddings --regenerar

# Generar con límite
python manage.py generar_embeddings --limite 100
```

### 6. Admin de Django ✅

Todos los modelos están registrados en el admin con interfaces completas:
- `/admin/busqueda/busquedasemantica/`
- `/admin/busqueda/envioembedding/`
- `/admin/busqueda/feedbacksemantico/`
- `/admin/busqueda/sugerenciasemantica/`

### 7. Migraciones ✅

```bash
# Migraciones aplicadas:
- 0003_sugerenciasemantica_busquedasemantica_envioembedding_and_more.py
- 0004_cargar_sugerencias_iniciales.py (10 sugerencias predefinidas)
```

---

## 🚀 Cómo Usar

### Paso 1: Generar Embeddings Iniciales

Antes de usar la búsqueda semántica, debes generar embeddings para tus envíos existentes:

```bash
cd backend
python manage.py generar_embeddings
```

**Nota:** Este proceso puede tardar dependiendo de la cantidad de envíos. La API de OpenAI se procesa de forma eficiente con pausas para no saturar.

### Paso 2: Probar el Endpoint

Puedes probar el endpoint con cualquier cliente HTTP (Postman, Insomnia, curl):

```bash
curl -X POST http://localhost:8000/api/busqueda/semantica/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "paquetes para Quito",
    "limite": 10
  }'
```

### Paso 3: El Frontend Ya Está Listo

El componente de frontend `busqueda-semantica.component.ts` ya está implementado y listo para usar. Solo asegúrate de que el backend esté corriendo.

---

## 🔧 Funcionamiento Técnico

### 1. Generación de Embeddings

Cuando se crea un envío o se ejecuta el comando, se genera un texto descriptivo:

```
HAWB: ABC123 | Comprador: Juan Pérez | Ciudad: Quito | 
Estado: Entregado | Fecha: 2025-01-15 | Peso: 5.5 kg | 
Valor: $120.00 | Productos: Laptop, Mouse inalámbrico
```

Este texto se envía a OpenAI para generar un vector de 1536 dimensiones que representa semánticamente el envío.

### 2. Búsqueda por Similitud

Cuando un usuario busca, el proceso es:

1. **Consulta del usuario:** "envíos para Quito"
2. **Generar embedding** de la consulta usando OpenAI
3. **Calcular similitud coseno** entre el embedding de la consulta y todos los embeddings de envíos
4. **Ordenar por similitud** y retornar los más relevantes
5. **Extraer fragmentos** que coinciden con la consulta
6. **Generar explicación** de por qué cada resultado es relevante

### 3. Optimizaciones

- **Caché de Embeddings:** Los embeddings se generan una vez y se reutilizan
- **Actualización Automática:** Al modificar un envío, su embedding se regenera automáticamente
- **Límite de Procesamiento:** Por defecto se procesan máximo 500 envíos por búsqueda para mantener performance
- **Umbral de Similitud:** Solo se muestran resultados con similitud >= 30%

---

## 📊 Ejemplos de Búsquedas

### Búsquedas por Ciudad
```
"envíos a Quito"
"paquetes para Guayaquil"
"envíos costa ecuatoriana"
```

### Búsquedas por Estado
```
"envíos pendientes"
"paquetes entregados"
"envíos en tránsito"
"envíos cancelados"
```

### Búsquedas Temporales
```
"envíos de esta semana"
"paquetes del mes pasado"
"envíos recientes"
```

### Búsquedas por Comprador
```
"envíos de María González"
"paquetes de Juan Pérez"
```

### Búsquedas Complejas
```
"envíos entregados en Quito esta semana"
"paquetes pendientes para la costa"
"envíos de electrónica del último mes"
```

---

## 🎯 Sugerencias Predefinidas Cargadas

El sistema viene con 10 sugerencias predefinidas:

1. ✅ "envíos entregados esta semana"
2. ⏰ "paquetes pendientes de entrega"
3. 📍 "envíos a Quito"
4. 📍 "envíos a Guayaquil"
5. 🚚 "envíos en tránsito"
6. 📅 "paquetes del último mes"
7. ❌ "envíos cancelados"
8. 📍 "envíos a Cuenca"
9. 💻 "paquetes de electrónica"
10. 💰 "envíos de mayor valor"

Puedes administrar estas sugerencias desde el admin de Django.

---

## 🔐 Seguridad y Permisos

### Filtrado por Rol

El sistema respeta los permisos de usuario:

- **Compradores:** Solo ven sus propios envíos
- **Digitadores:** Ven envíos de compradores
- **Gerentes:** Ven todos excepto administradores
- **Administradores:** Ven todo

### Autenticación

Todos los endpoints requieren autenticación JWT:

```python
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}
```

---

## 💰 Costos de OpenAI

### Modelo: text-embedding-3-small

- **Precio:** $0.00002 por 1,000 tokens (~750 palabras)
- **Ejemplo:** 1,000 envíos ≈ $0.20 USD
- **Búsquedas:** Prácticamente gratis (cada búsqueda cuesta ~$0.00002)

**Recomendación:** Este modelo es muy económico y suficiente para la mayoría de aplicaciones.

---

## 🐛 Solución de Problemas

### Error: "OpenAI API key not found"

**Solución:** Verifica que la API key esté configurada en `settings.py` o en tu archivo `.env`

```bash
# En .env
OPENAI_API_KEY=sk-proj-...
```

### Error: "No embeddings found"

**Solución:** Ejecuta el comando para generar embeddings:

```bash
python manage.py generar_embeddings
```

### Resultados No Relevantes

**Solución:** Ajusta el umbral de similitud en las vistas:

```python
# En views.py, línea ~520
if similitud >= 0.3:  # Aumentar a 0.5 o 0.6
```

### Búsqueda Lenta

**Soluciones:**
1. Limitar cantidad de envíos procesados (actualmente 500)
2. Implementar índices en la base de datos
3. Usar caché para búsquedas frecuentes

---

## 📈 Métricas y Monitoreo

El endpoint de métricas proporciona información útil:

```bash
GET /api/busqueda/semantica/metricas/
```

**Response:**
```json
{
  "totalBusquedas": 156,
  "tiempoPromedioRespuesta": 245.5,
  "totalFeedback": 45,
  "feedbackPositivo": 38,
  "feedbackNegativo": 7,
  "totalEmbeddings": 1200
}
```

---

## 🔄 Mantenimiento

### Actualizar Embeddings Periódicamente

Si modificas muchos envíos, regenera los embeddings:

```bash
python manage.py generar_embeddings --regenerar
```

### Limpiar Historial Antiguo

Puedes crear un comando de management para limpiar búsquedas antiguas:

```python
# Ejemplo: eliminar búsquedas de más de 90 días
from django.utils import timezone
from datetime import timedelta

fecha_limite = timezone.now() - timedelta(days=90)
BusquedaSemantica.objects.filter(fecha_busqueda__lt=fecha_limite).delete()
```

---

## 📚 Recursos Adicionales

### Documentación OpenAI
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [text-embedding-3-small](https://platform.openai.com/docs/models/embeddings)

### Tutoriales Relacionados
- [Búsqueda Semántica con Python](https://cookbook.openai.com/examples/semantic_search)
- [Similitud Coseno Explicada](https://en.wikipedia.org/wiki/Cosine_similarity)

---

## ✅ Checklist de Implementación

- [x] Instalar dependencias (openai, numpy)
- [x] Configurar API key en settings.py
- [x] Crear modelos de base de datos
- [x] Implementar vistas y serializers
- [x] Crear comando de management
- [x] Registrar modelos en admin
- [x] Aplicar migraciones
- [x] Cargar sugerencias iniciales
- [x] Documentar implementación

---

## 🎉 ¡Listo para Usar!

El backend de búsqueda semántica está **completamente funcional** y listo para ser usado por el frontend.

### Próximos Pasos Recomendados:

1. ✅ Ejecutar: `python manage.py generar_embeddings`
2. ✅ Probar endpoint con Postman/Insomnia
3. ✅ Verificar que el frontend se conecte correctamente
4. ✅ Capacitar a los usuarios finales

---

**Desarrollado con ❤️ para Universal Box**  
*Versión 1.0.0 - Octubre 2025*




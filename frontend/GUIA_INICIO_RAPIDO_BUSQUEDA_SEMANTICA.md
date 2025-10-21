# 🚀 Guía de Inicio Rápido - Búsqueda Semántica

## ⚡ Implementación Completada

La búsqueda semántica con OpenAI está **100% funcional** en backend y frontend.

---

## 📋 Pasos para Usar

### 1️⃣ Verificar Configuración (YA HECHO ✅)

```bash
# La API key ya está configurada en backend/settings.py
OPENAI_API_KEY = 'sk-proj-k0L-7LqiRAKER0gD5VFRpOdVkoD1J1k-...'
```

### 2️⃣ Iniciar el Backend

```bash
cd backend
python manage.py runserver
```

El servidor estará disponible en: `http://localhost:8000`

### 3️⃣ Generar Embeddings de Envíos Existentes

**Abrir una nueva terminal:**

```bash
cd backend
python manage.py generar_embeddings
```

Este comando:
- 📊 Procesará todos los envíos existentes
- 🧠 Generará embeddings usando OpenAI
- 💾 Los guardará en la base de datos
- ⏱️ Tiempo estimado: ~2 segundos por envío

**Ejemplo de salida:**
```
📦 Procesando 50 envíos...
Progreso: 10/50 (20.0%) - Procesados: 10, Errores: 0
Progreso: 20/50 (40.0%) - Procesados: 20, Errores: 0
...
✅ PROCESO COMPLETADO
Total procesados: 50
Errores: 0
Tiempo total: 98.45 segundos
```

### 4️⃣ Iniciar el Frontend

```bash
cd frontend
npm start
# o
ng serve
```

El frontend estará disponible en: `http://localhost:4200`

### 5️⃣ Acceder a la Búsqueda Semántica

1. **Iniciar sesión** en la aplicación
2. **Navegar** a una de estas rutas:
   - `/busqueda-semantica` - Búsqueda semántica standalone
   - `/busqueda` - Búsqueda unificada (recomendado)

---

## 🎯 Probar la Funcionalidad

### Desde el Frontend

1. En la interfaz, verás un campo de búsqueda con placeholder:  
   *"Buscar envíos usando lenguaje natural..."*

2. **Ejemplos de búsquedas:**
   ```
   envíos a Quito
   paquetes pendientes
   envíos entregados esta semana
   paquetes para María González
   envíos de electrónica
   ```

3. Los resultados mostrarán:
   - 📦 Información del envío
   - 📊 Porcentaje de similitud (0-100%)
   - 🔍 Fragmentos relevantes destacados
   - 💡 Razón de relevancia

### Desde Postman/Insomnia

**Endpoint:** `POST http://localhost:8000/api/busqueda/semantica/`

**Headers:**
```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN",
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "texto": "envíos a Quito",
  "limite": 10
}
```

**Respuesta esperada:**
```json
{
  "consulta": "envíos a Quito",
  "resultados": [
    {
      "envio": {
        "id": 1,
        "hawb": "ABC123",
        "comprador_info": {
          "nombre": "Juan Pérez",
          "ciudad": "Quito"
        },
        "estado": "entregado"
      },
      "puntuacionSimilitud": 0.92,
      "fragmentosRelevantes": [
        "Ciudad: Quito",
        "Comprador: Juan Pérez"
      ],
      "razonRelevancia": "Coincide con: ciudad Quito"
    }
  ],
  "totalEncontrados": 5,
  "tiempoRespuesta": 156,
  "modeloUtilizado": "text-embedding-3-small"
}
```

---

## 🔍 Endpoints Disponibles

### 1. Búsqueda Semántica Principal
```http
POST /api/busqueda/semantica/
```

### 2. Sugerencias
```http
GET /api/busqueda/semantica/sugerencias/?q=envios
```

### 3. Historial
```http
GET /api/busqueda/semantica/historial/
POST /api/busqueda/semantica/historial/
DELETE /api/busqueda/semantica/historial/
```

### 4. Feedback
```http
POST /api/busqueda/semantica/feedback/
```

### 5. Métricas
```http
GET /api/busqueda/semantica/metricas/
```

---

## 🎨 Características del Frontend

### ✨ Sugerencias Inteligentes
- 10 sugerencias predefinidas
- Autocompletado mientras escribes
- Organizado por categorías (ciudad, estado, fecha)

### 📚 Historial de Búsquedas
- Últimas 10 búsquedas
- Click para repetir
- Opción de limpiar historial

### 📊 Múltiples Vistas de Resultados
- **Tarjetas:** Vista detallada con fragmentos
- **Lista:** Vista intermedia compacta
- **Tabla:** Vista de máxima densidad

### 🔍 Filtros Adicionales (Opcional)
- Rango de fechas
- Estado del envío
- Ciudad de destino
- Combinables con búsqueda semántica

### 👍 Sistema de Feedback
- Botones "relevante" / "no relevante"
- Mejora continua del sistema

---

## 🛠️ Comandos Útiles

### Generar Embeddings

```bash
# Generar embeddings para envíos sin embedding
python manage.py generar_embeddings

# Regenerar TODOS los embeddings
python manage.py generar_embeddings --regenerar

# Generar solo 50 envíos (para pruebas)
python manage.py generar_embeddings --limite 50

# Ajustar tamaño de lote
python manage.py generar_embeddings --batch-size 20
```

### Verificar Estado

```bash
# Ver embeddings en el admin
# http://localhost:8000/admin/busqueda/envioembedding/

# Ver búsquedas realizadas
# http://localhost:8000/admin/busqueda/busquedasemantica/

# Ver sugerencias
# http://localhost:8000/admin/busqueda/sugerenciasemantica/
```

---

## 📊 Monitoreo

### Métricas del Sistema

```bash
# Llamar al endpoint de métricas
curl -X GET http://localhost:8000/api/busqueda/semantica/metricas/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Métricas disponibles:**
- Total de búsquedas realizadas
- Tiempo promedio de respuesta
- Total de feedback (positivo/negativo)
- Total de embeddings generados

---

## 💡 Tips de Uso

### Para Usuarios Finales

**✅ Búsquedas Efectivas:**
- "envíos entregados en Quito esta semana"
- "paquetes pendientes para María González"
- "envíos retrasados a la costa"

**❌ Evitar:**
- Consultas muy vagas: "envíos"
- Códigos exactos (usar búsqueda tradicional)
- Consultas muy largas (>100 palabras)

### Para Desarrolladores

**Optimizar Performance:**
1. Mantener embeddings actualizados
2. Limpiar historial antiguo periódicamente
3. Ajustar umbral de similitud según necesidad
4. Monitorear uso de API de OpenAI

---

## 🐛 Solución de Problemas Comunes

### "No se encuentran resultados"

1. ✅ Verificar que los embeddings estén generados
2. ✅ Revisar permisos del usuario
3. ✅ Probar con búsquedas más simples

### "Error de conexión con OpenAI"

1. ✅ Verificar la API key en settings.py
2. ✅ Verificar conexión a internet
3. ✅ Revisar créditos de OpenAI

### "Búsqueda muy lenta"

1. ✅ Reducir límite de envíos procesados
2. ✅ Verificar cantidad de envíos en la BD
3. ✅ Considerar usar índices en PostgreSQL

---

## 📁 Archivos Importantes

```
backend/
├── apps/busqueda/
│   ├── models.py                    # Modelos de BD
│   ├── views.py                     # Lógica de búsqueda
│   ├── serializers.py               # Serializers
│   ├── admin.py                     # Admin de Django
│   ├── management/commands/
│   │   └── generar_embeddings.py    # Comando para generar embeddings
│   └── migrations/
│       ├── 0003_...                 # Migración de modelos
│       └── 0004_...                 # Sugerencias iniciales
├── settings.py                      # Configuración de OpenAI
└── BUSQUEDA_SEMANTICA_IMPLEMENTADA.md

frontend/
├── src/app/
│   ├── components/
│   │   ├── busqueda-semantica/      # Componente principal
│   │   └── busqueda-unificada/      # Componente integrador
│   ├── models/
│   │   └── busqueda-semantica.ts    # Interfaces TypeScript
│   └── services/
│       └── api.service.ts           # Servicios API
└── MODULO_BUSQUEDA_SEMANTICA_README.md
```

---

## ✅ Checklist de Verificación

Antes de usar en producción:

- [ ] ✅ Backend corriendo sin errores
- [ ] ✅ Frontend corriendo sin errores
- [ ] ✅ Embeddings generados para todos los envíos
- [ ] ✅ Prueba de búsqueda exitosa desde frontend
- [ ] ✅ Prueba de búsqueda exitosa desde Postman
- [ ] ✅ Verificar sugerencias funcionando
- [ ] ✅ Verificar historial funcionando
- [ ] ✅ Verificar feedback funcionando
- [ ] ✅ Revisar métricas
- [ ] ✅ Capacitar usuarios finales

---

## 📞 Soporte

### Documentación Completa
- `backend/BUSQUEDA_SEMANTICA_IMPLEMENTADA.md` - Documentación técnica backend
- `frontend/MODULO_BUSQUEDA_SEMANTICA_README.md` - Documentación frontend

### Recursos Externos
- [OpenAI Platform](https://platform.openai.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Angular Documentation](https://angular.io/docs)

---

## 🎉 ¡Todo Listo!

La búsqueda semántica está **completamente funcional**. Solo necesitas:

1. ✅ Iniciar el backend
2. ✅ Generar embeddings
3. ✅ Iniciar el frontend
4. ✅ ¡Empezar a buscar!

**Disfruta de la búsqueda inteligente con IA!** 🚀🧠✨

---

*Desarrollado para Universal Box - Sistema de Gestión de Envíos*  
*Versión 1.0.0 - Octubre 2025*




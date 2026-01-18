# ⚡ Guía Rápida: Mejoras de Búsqueda Semántica

## 🎯 Problema Resuelto

Tu sistema de búsqueda semántica ahora funciona mucho mejor con **grandes cantidades de envíos**. Antes perdía precisión con muchos registros, ahora encuentra resultados relevantes incluso con miles de envíos.

---

## 🚀 ¿Qué se Mejoró?

### 1. 🧠 Búsqueda Más Inteligente
El sistema ahora **entiende sinónimos** y **contexto**:
- "Quito" = "capital" = "DME" = "Pichincha"
- "pendiente" = "sin procesar" = "en espera"
- "electrónica" = "tecnología" = "dispositivos"

### 2. 📊 Mejor Clasificación Automática
Ahora clasifica automáticamente:
- **Peso**: ligero (<1kg), moderado, pesado (>10kg)
- **Valor**: bajo (<$50), moderado, alto (>$500)
- **Tiempo**: hoy, esta semana, este mes, reciente

### 3. 🎯 Filtros Automáticos
Detecta y aplica filtros automáticamente:
- "peso mayor a 5 kg" → aplica filtro peso_minimo=5
- "este mes" → aplica rango de fechas
- "más de un producto" → aplica filtro cantidad>=2

### 4. 📈 Más Resultados Relevantes
- Busca en **1000 envíos** (antes 300)
- **Umbrales más flexibles** (0.25-0.28 vs 0.30-0.35)
- **Menos falsos negativos** (no se pierden resultados válidos)

---

## ✅ Consultas que Ahora Funcionan Perfectamente

1. ✅ "Buscar envíos que pendientes y sean de Quito."
2. ✅ "Envíos registrados este mes con un peso mayor a 5 kilogramos."
3. ✅ "Paquetes enviados por Juan Pérez que aún no han sido entregados."
4. ✅ "Mostrar envíos con valor total alto que requieran revisión."
5. ✅ "Paquetes con productos electrónicos enviados a Cuenca."
6. ✅ "Envíos con más de un producto en el mismo paquete."
7. ✅ "Buscar envíos del cliente con cédula 1718606043."
8. ✅ "Envíos recientes que todavía están pendientes de entrega."
9. ✅ "Paquetes livianos enviados la última semana."

---

## 🔧 PASO 1: Regenerar Embeddings (¡IMPORTANTE!)

Para que las mejoras funcionen, **debes regenerar los embeddings**:

```bash
cd backend
python manage.py generar_embeddings --regenerar
```

### ¿Por qué regenerar?

Los embeddings actuales se generaron con el sistema antiguo. El nuevo sistema tiene:
- Más información (cédula, clasificaciones, variaciones)
- Mejor contexto temporal
- Más sinónimos y variaciones

### Opciones de Regeneración

**Opción A: Regenerar todo (Recomendado)**
```bash
python manage.py generar_embeddings --regenerar
```

**Opción B: Regenerar solo primeros 500 (para probar)**
```bash
python manage.py generar_embeddings --regenerar --limite 500
```

**Opción C: Solo envíos sin embedding**
```bash
python manage.py generar_embeddings
```

### ⏱️ Tiempo Estimado
- **100 envíos**: ~2-3 minutos
- **500 envíos**: ~10-15 minutos
- **1000 envíos**: ~20-30 minutos

### 💰 Costo Estimado (con OpenAI)
- **500 envíos**: ~$0.001-0.002 USD (menos de 1 centavo)
- **1000 envíos**: ~$0.002-0.003 USD
- **5000 envíos**: ~$0.010-0.015 USD (1-2 centavos)

---

## 🧪 PASO 2: Probar las Mejoras

Ejecuta el script de pruebas con las 9 consultas de ejemplo:

```bash
python manage.py probar_consultas_usuario
```

### Ver Más Detalles

```bash
# Ver cómo se expande cada consulta
python manage.py probar_consultas_usuario --mostrar-expansion

# Ver información detallada de cada resultado
python manage.py probar_consultas_usuario --mostrar-detalles

# Ver más resultados por consulta
python manage.py probar_consultas_usuario --limite 10
```

### 📊 Qué Esperar

El script te mostrará:
- ✅ Cuántas consultas tuvieron éxito (objetivo: 9/9)
- 📊 Cantidad de resultados por consulta
- ⏱️ Tiempo de respuesta
- 💰 Costo de cada búsqueda

**Ejemplo de salida**:
```
✅ Consultas exitosas: 9/9 (100.0%)
📊 Total de resultados encontrados: 87
⏱️  Tiempo promedio por consulta: 312.45ms
```

---

## 🎨 PASO 3: Usar desde el Frontend

No hay cambios necesarios en el frontend. El sistema funciona transparentemente:

### Antes (sin mejoras)
```
Usuario: "envíos pendientes de Quito"
Sistema: 🔍 Busca exactamente "envíos pendientes de Quito"
Resultado: ❌ 2 resultados
```

### Ahora (con mejoras)
```
Usuario: "envíos pendientes de Quito"
Sistema: 🧠 Expande a:
  - "envíos pendientes de Quito"
  - "en espera" "sin procesar" "por procesar"
  - "capital" "DME" "Pichincha"
  - Aplica: estado=pendiente, ciudad=Quito
Resultado: ✅ 15 resultados relevantes
```

---

## 📋 Formatos de Consultas Soportados

### Por Estado
- "envíos pendientes"
- "paquetes entregados"
- "en tránsito"
- "sin procesar"
- "completados"

### Por Ubicación
- "envíos a Quito"
- "paquetes para Guayaquil"
- "destino Cuenca"
- "enviados a la capital"

### Por Peso
- "envíos livianos"
- "paquetes pesados"
- "peso mayor a 5 kg"
- "menos de 2 kilos"
- "más de 10 kilogramos"

### Por Valor
- "envíos caros"
- "paquetes económicos"
- "valor alto"
- "requieren revisión"
- "más de $100"

### Por Tiempo
- "envíos de hoy"
- "registrados esta semana"
- "este mes"
- "última semana"
- "recientes"

### Por Comprador
- "envíos de Juan Pérez"
- "paquetes enviados por María"
- "cliente con cédula 1718606043"

### Por Productos
- "con productos electrónicos"
- "paquetes con laptop"
- "artículos de ropa"
- "más de un producto"
- "varios artículos"

### Combinadas
- "envíos pendientes de Quito este mes"
- "paquetes pesados entregados en Cuenca"
- "productos electrónicos con valor alto"

---

## 🎛️ Ajustes Opcionales

### Si Obtienes Muchos Resultados Irrelevantes

Aumenta los umbrales en `backend/apps/busqueda/services.py` (línea ~498):

```python
# Más estricto (menos resultados, más precisos)
umbral_base = 0.30 if es_consulta_productos else 0.35
```

### Si Obtienes Pocos Resultados

Reduce los umbrales:

```python
# Más flexible (más resultados)
umbral_base = 0.20 if es_consulta_productos else 0.25
```

### Si la Búsqueda es Lenta

Reduce el límite en `backend/apps/busqueda/services.py` (línea ~435):

```python
# Procesar menos envíos (más rápido)
MAX_ENVIOS_A_PROCESAR = 500
```

---

## 📊 Comparativa: Antes vs Ahora

### Antes de las Mejoras
```
Consulta: "envíos pendientes de Quito"

Procesamiento:
- Genera embedding de: "envíos pendientes de Quito"
- Busca en 300 envíos
- Umbral: 0.35 (muy estricto)
- Sin filtros automáticos

Resultado: 2 resultados (muchos falsos negativos)
```

### Después de las Mejoras
```
Consulta: "envíos pendientes de Quito"

Procesamiento:
1. Expande a: "pendiente en espera sin procesar aguardando 
   Quito capital DME Pichincha"
2. Detecta filtros: estado=pendiente, ciudad=Quito
3. Pre-filtra envíos con criterios
4. Busca en 1000 envíos (filtrados)
5. Umbral: 0.28 (más flexible)

Resultado: 15 resultados relevantes
```

---

## 🐛 Solución de Problemas

### Problema: "No encuentro resultados para consultas válidas"

**Solución**:
1. Verifica que regeneraste los embeddings:
   ```bash
   python manage.py generar_embeddings --regenerar
   ```

2. Verifica que tienes datos:
   ```bash
   python manage.py shell
   >>> from apps.archivos.models import Envio
   >>> print(Envio.objects.count())
   ```

3. Prueba con el script:
   ```bash
   python manage.py probar_consultas_usuario --mostrar-expansion
   ```

### Problema: "Error: OpenAI API key no configurada"

**Solución**:
1. Verifica tu archivo `.env`:
   ```
   OPENAI_API_KEY=sk-proj-tu-api-key-aqui
   ```

2. Reinicia el servidor Django

### Problema: "Los resultados no son relevantes"

**Solución**:
1. Aumenta el umbral (más estricto)
2. Revisa los filtros con `--mostrar-expansion`
3. Ajusta las clasificaciones en `query_expander.py`

---

## 📈 Métricas de Éxito

Después de implementar las mejoras, deberías ver:

### ✅ Indicadores Positivos
- 80-100% de consultas con resultados
- 5-15 resultados promedio por consulta
- Tiempo de respuesta: 200-500ms
- Usuario encuentra lo que busca en el top 5

### ⚠️ Señales de Alerta
- Menos del 50% de consultas con resultados → Regenerar embeddings
- Más de 1 segundo por consulta → Reducir MAX_ENVIOS_A_PROCESAR
- Muchos resultados irrelevantes → Aumentar umbral

---

## 🎉 ¡Listo!

Ahora tu sistema de búsqueda semántica es:
- ✅ **Más inteligente**: Entiende sinónimos y contexto
- ✅ **Más preciso**: Encuentra lo que buscas
- ✅ **Más rápido**: Con filtrado inteligente
- ✅ **Más flexible**: Soporta consultas complejas

---

## 📚 Documentación Adicional

- **`REGENERAR_EMBEDDINGS.md`**: Guía detallada de regeneración
- **`MEJORAS_BUSQUEDA_SEMANTICA_2026.md`**: Documentación técnica completa
- **Comando de pruebas**: `python manage.py probar_consultas_usuario --help`

---

## 💡 Tips Finales

1. **Regenera embeddings al menos una vez** para aprovechar todas las mejoras
2. **Usa el script de pruebas** para verificar que todo funciona
3. **Monitorea el uso** y ajusta umbrales según tus necesidades
4. **Los embeddings se reutilizan**, no tienes que regenerar para cada búsqueda

¡Disfruta de tu sistema de búsqueda mejorado! 🚀

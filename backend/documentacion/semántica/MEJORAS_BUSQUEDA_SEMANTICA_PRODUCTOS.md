# 🚀 Mejoras en Búsqueda Semántica para Productos

## 📋 Resumen

Este documento describe las mejoras implementadas en el sistema de búsqueda semántica para mejorar la capacidad de responder preguntas sobre productos.

---

## ✅ Mejoras Implementadas

### 1. **Mejora en el Texto Indexado de Productos**

**Archivo:** `backend/apps/busqueda/semantic/text_processor.py`

#### Cambios Realizados:

1. **Inclusión de todos los productos** (no solo 5)
   - Antes: Solo se indexaban los primeros 5 productos
   - Ahora: Se indexan todos los productos del envío

2. **Información detallada de cada producto**
   - Descripción completa con peso, cantidad y valor individual
   - Ejemplo: "Laptop Dell peso 2.5kg cantidad 1 valor $1200"

3. **Sinónimos de categorías**
   - Se agregaron sinónimos para cada categoría de producto:
     - **Electrónica**: electrónica, electrónicos, tecnología, tecnológico, dispositivos, gadgets
     - **Ropa**: vestimenta, prendas, indumentaria, textiles, moda
     - **Hogar**: artículos para el hogar, decoración, muebles, utensilios
     - **Deportes**: artículos deportivos, equipamiento deportivo, deportivo, fitness
     - **Otros**: misceláneos, varios, diversos

4. **Múltiples formas de indexar productos**
   - Lista completa: "Productos incluidos: laptop, mouse, teclado"
   - Versión corta: "Contiene: laptop, mouse"
   - Con detalles: "Productos con detalles: laptop peso 2.5kg..."
   - Individual: "Producto: laptop", "Producto: mouse" (para mejor matching)

5. **Información agregada**
   - Peso total de productos
   - Valor total de productos
   - Cantidad total de artículos

#### Ejemplo de Texto Indexado Mejorado:

```
Antes:
Productos incluidos: laptop, mouse, teclado | Categorías de productos: Electrónica

Ahora:
Productos incluidos: laptop, mouse, teclado | 
Contiene: laptop, mouse, teclado | 
Productos con detalles: laptop peso 2.5kg cantidad 1 valor $1200 | mouse peso 0.2kg cantidad 2 valor $50 | 
Producto: laptop | Producto: mouse | Producto: teclado |
Categorías de productos: Electrónica | 
Tipos de productos: electrónica, electrónicos, tecnología, tecnológico, dispositivos, gadgets |
Cantidad total de productos: 4 | 
Peso total productos: 3.2 kg | 
Valor total productos: $1300
```

---

### 2. **Mejora en la Razón de Relevancia**

**Archivo:** `backend/apps/busqueda/semantic/text_processor.py`

#### Cambios Realizados:

1. **Detección mejorada de productos**
   - Coincidencia exacta en descripción
   - Coincidencia parcial por palabras clave
   - Detección de categorías y sinónimos

2. **Detección de características numéricas**
   - Detecta consultas sobre peso de productos
   - Detecta consultas sobre valor/precio de productos

3. **Múltiples razones de relevancia**
   - Puede detectar múltiples productos coincidentes
   - Incluye información de categoría y tipo de producto

#### Ejemplo de Razón de Relevancia Mejorada:

```
Antes:
Coincide con: producto laptop

Ahora:
Coincide con: producto 'laptop', categoría electrónica, tipo de producto dispositivos, producto con peso 2.5kg
```

---

### 3. **Script de Prueba para Evaluar Consultas**

**Archivo:** `backend/apps/busqueda/management/commands/probar_busqueda_productos.py`

#### Características:

- Prueba diferentes tipos de consultas sobre productos
- Clasifica resultados en: exitosas, sin resultados, con resultados bajos
- Genera un resumen con estadísticas y recomendaciones
- Organiza las pruebas por categorías:
  - Consultas básicas de productos
  - Consultas con descripción específica
  - Consultas con características numéricas
  - Consultas combinadas (producto + ubicación)
  - Consultas con sinónimos
  - Consultas con preguntas
  - Consultas complejas

#### Uso:

```bash
# Probar con usuario admin (por defecto)
python manage.py probar_busqueda_productos

# Probar con otro usuario
python manage.py probar_busqueda_productos --usuario nombre_usuario

# Cambiar límite de resultados
python manage.py probar_busqueda_productos --limite 10
```

---

## 🔍 Procesos Identificados para Mejorar

### 1. **Regeneración de Embeddings**

**Problema:** Los embeddings existentes no incluyen las mejoras realizadas.

**Solución:** Regenerar los embeddings de todos los envíos:

```bash
# Regenerar todos los embeddings
python manage.py generar_embeddings --regenerar

# O regenerar solo los que no tienen embedding
python manage.py generar_embeddings
```

**Nota:** Este proceso puede tardar varios minutos dependiendo de la cantidad de envíos.

---

### 2. **Umbral de Similitud**

**Problema:** El umbral actual (0.35) puede ser demasiado alto para algunas consultas sobre productos.

**Recomendación:** 
- Considerar un umbral adaptativo más bajo para consultas sobre productos
- Implementar diferentes umbrales según el tipo de consulta

**Ubicación:** `backend/apps/busqueda/services.py` línea 347

```python
# Actual
resultados_filtrados = vector_search.aplicar_umbral(
    resultados_similitud,
    umbral_base=0.35,
    usar_adaptativo=True
)

# Sugerencia: Umbral más bajo para consultas sobre productos
umbral_base = 0.30 if 'producto' in texto_consulta.lower() else 0.35
```

---

### 3. **Boost para Coincidencias de Productos**

**Problema:** Las coincidencias exactas de productos no tienen suficiente boost.

**Recomendación:** Aumentar el boost para coincidencias de productos en el cálculo de similitud.

**Ubicación:** `backend/apps/busqueda/semantic/vector_search.py`

```python
# Actual: boost_exactas = coincidencias_score * 0.15
# Sugerencia: boost más alto para productos
if 'producto' in texto_consulta.lower():
    boost_exactas = coincidencias_score * 0.25
else:
    boost_exactas = coincidencias_score * 0.15
```

---

### 4. **Límite de Productos en Búsqueda**

**Problema:** El sistema limita a procesar solo 200 envíos (línea 307 de `services.py`).

**Recomendación:** 
- Aumentar el límite si hay muchos envíos
- Implementar paginación en la búsqueda vectorial
- Usar índices vectoriales (como Pinecone o Weaviate) para mejor rendimiento

---

## 📊 Tipos de Consultas que Funcionan Mejor

### ✅ Consultas que Funcionan Bien:

1. **Consultas básicas de categoría:**
   - "productos electrónicos"
   - "ropa"
   - "artículos para el hogar"

2. **Consultas con descripción específica:**
   - "laptop"
   - "camiseta"
   - "smartphone"

3. **Consultas con sinónimos:**
   - "electrónica" (sinónimo de "electronica")
   - "vestimenta" (sinónimo de "ropa")
   - "dispositivos" (sinónimo de "electronica")

4. **Consultas combinadas:**
   - "productos electrónicos en Quito"
   - "ropa entregada"

### ⚠️ Consultas que Pueden Mejorar:

1. **Consultas con características numéricas:**
   - "productos con peso mayor a 5kg" (requiere procesamiento adicional)
   - "productos de valor alto" (subjetivo)

2. **Consultas con preguntas:**
   - "¿qué productos hay?" (muy genérica)
   - "muéstrame productos de electrónica" (funciona pero puede mejorar)

3. **Consultas complejas:**
   - "productos electrónicos entregados la semana pasada" (requiere filtros de fecha)

---

## ✅ Mejoras Adicionales Implementadas

### 1. **Umbral Adaptativo para Consultas de Productos**

**Archivo:** `backend/apps/busqueda/services.py`

- **Implementado:** Umbral más bajo (0.30) para consultas sobre productos vs 0.35 para consultas generales
- **Beneficio:** Permite encontrar más resultados relevantes para consultas de productos
- **Detección automática:** El sistema detecta automáticamente si una consulta es sobre productos

### 2. **Boost Aumentado para Coincidencias de Productos**

**Archivo:** `backend/apps/busqueda/semantic/vector_search.py`

- **Implementado:** Boost aumentado de 0.15 a 0.25 para consultas de productos
- **Boost adicional:** Hasta 0.10 puntos adicionales por coincidencias específicas en descripciones de productos
- **Total posible:** Hasta 0.35 puntos adicionales para productos vs 0.15 para consultas generales

### 3. **Detección Inteligente de Consultas sobre Productos**

**Archivo:** `backend/apps/busqueda/semantic/vector_search.py`

- **Implementado:** Función `_es_consulta_productos()` que detecta automáticamente consultas sobre productos
- **Palabras clave detectadas:** producto, artículos, laptop, smartphone, ropa, electrónica, etc.
- **Patrones de preguntas:** Detecta "qué productos", "muéstrame productos", etc.

### 4. **Detección de Consultas Numéricas**

**Archivo:** `backend/apps/busqueda/semantic/text_processor.py`

- **Implementado:** Detección de consultas con información numérica (peso, valor, precio)
- **Patrones detectados:**
  - Peso: "5kg", "mayor a 5kg", "peso 10"
  - Valor: "$100", "valor alto", "más de $50"
  - Comparaciones: "mayor a", "menor a", "más de"
- **Boost numérico:** Hasta 0.2 puntos adicionales por coincidencias numéricas

### 5. **Límite de Procesamiento Aumentado**

**Archivo:** `backend/apps/busqueda/services.py`

- **Implementado:** Aumentado de 200 a 300 envíos procesados
- **Beneficio:** Mejor cobertura de resultados, especialmente importante para productos

## 🎯 Próximos Pasos Recomendados

### Corto Plazo:

1. ✅ **Completado:** Mejorar texto indexado de productos
2. ✅ **Completado:** Mejorar razón de relevancia
3. ✅ **Completado:** Crear script de prueba
4. ✅ **Completado:** Implementar umbral adaptativo para productos
5. ✅ **Completado:** Aumentar boost para productos
6. ✅ **Completado:** Mejorar detección de consultas numéricas
7. ⏳ **Pendiente:** Regenerar embeddings con las mejoras
8. ⏳ **Pendiente:** Ejecutar pruebas y analizar resultados

### Mediano Plazo:

1. ⏳ Agregar más sinónimos según uso real
2. ⏳ Implementar aprendizaje de feedback del usuario
3. ⏳ Optimizar rendimiento con índices vectoriales

### Largo Plazo:

1. Implementar índice vectorial dedicado (Pinecone, Weaviate)
2. Entrenar modelo específico para productos
3. Implementar aprendizaje de feedback del usuario
4. Agregar búsqueda híbrida (semántica + tradicional)

---

## 📝 Notas Importantes

1. **Regeneración de Embeddings:** Las mejoras en el texto indexado solo se aplicarán a nuevos embeddings. Es necesario regenerar los existentes para ver las mejoras.

2. **Costo de OpenAI:** Cada regeneración de embeddings tiene un costo asociado. Considera regenerar solo los envíos más recientes o importantes.

3. **Rendimiento:** El procesamiento de más información de productos puede aumentar ligeramente el tiempo de búsqueda, pero mejora significativamente la precisión.

4. **Pruebas:** Ejecuta el script de prueba regularmente para monitorear el rendimiento del sistema y detectar áreas de mejora.

---

## 🔗 Archivos Modificados

1. `backend/apps/busqueda/semantic/text_processor.py`
   - Método `generar_texto_envio()` mejorado (más información de productos)
   - Método `generar_razon_relevancia()` mejorado (mejor detección de productos)
   - Método `calcular_coincidencias_exactas()` mejorado (detección numérica)

2. `backend/apps/busqueda/semantic/vector_search.py`
   - Boost aumentado para productos (0.25 vs 0.15)
   - Boost adicional por coincidencias específicas de productos
   - Nueva función `_es_consulta_productos()` para detección automática

3. `backend/apps/busqueda/services.py`
   - Umbral adaptativo para consultas de productos (0.30 vs 0.35)
   - Límite de procesamiento aumentado (300 vs 200)
   - Nueva función `_es_consulta_productos()` para detección

4. `backend/apps/busqueda/management/commands/probar_busqueda_productos.py`
   - Nuevo script de prueba completo

---

## 📞 Soporte

Para preguntas o problemas relacionados con estas mejoras, consulta:
- Documentación de búsqueda semántica: `backend/documentacion/BUSQUEDA_SEMANTICA_IMPLEMENTADA.md`
- Logs del sistema: `logs/app.log`
- Errores: `logs/errors.log`


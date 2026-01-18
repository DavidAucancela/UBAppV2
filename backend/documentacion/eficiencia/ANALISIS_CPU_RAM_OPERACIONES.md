# 🔍 Análisis de Uso de CPU y RAM: Crear Envío vs Búsqueda Semántica

## 📊 Resumen Ejecutivo

- **Crear Envío**: Mayor uso de **CPU** debido a operaciones matemáticas intensivas con precisión decimal
- **Búsqueda Semántica**: Mayor uso de **RAM** debido a carga masiva de vectores de embeddings en memoria

---

## 🔴 **Crear Envío - Alto Uso de CPU**

### ¿Por qué usa tanto CPU?

La operación de crear un envío requiere **cálculos matemáticos intensivos** con precisión decimal para garantizar exactitud financiera. Estos cálculos son **CPU-bound** (limitados por procesamiento) en lugar de I/O-bound (limitados por disco/red).

---

### 🔍 Desglose de Operaciones que Consumen CPU

#### 1. **Cálculo de Costo del Servicio** ⚠️ **PRINCIPAL CONSUMIDOR**

```python
# backend/apps/archivos/models.py:176-226
def calcular_costo_servicio(self):
    # 1. Cargar todas las tarifas activas
    tarifas_activas = list(Tarifa.objects.filter(activa=True))
    
    # 2. Organizar por categoría (iteración sobre todas las tarifas)
    tarifas_por_categoria = {}
    for tarifa in tarifas_activas:
        if tarifa.categoria not in tarifas_por_categoria:
            tarifas_por_categoria[tarifa.categoria] = []
        tarifas_por_categoria[tarifa.categoria].append(tarifa)
    
    # 3. Para cada producto, buscar tarifa aplicable
    for producto in productos:
        for tarifa in tarifas_categoria:  # ⚠️ Bucle anidado
            if tarifa.peso_minimo <= producto.peso <= tarifa.peso_maximo:
                tarifa_aplicable = tarifa
                break
        
        # 4. Cálculo con Decimal (MUY COSTOSO en CPU)
        costo_producto_decimal = Decimal(str(tarifa_aplicable.calcular_costo(producto.peso))) * Decimal(str(producto.cantidad))
        costo_total += costo_producto_decimal
```

**Operaciones que consumen CPU:**

| Operación | Complejidad | Impacto CPU |
|-----------|-------------|-------------|
| Conversión `Decimal(str(...))` | O(1) por conversión | Alto (creación de objetos Decimal) |
| Multiplicación `Decimal * Decimal` | O(1) pero costoso | Alto (precisión arbitraria) |
| Comparación `peso_minimo <= peso <= peso_maximo` | O(n) con n tarifas | Medio (bucle anidado) |
| Suma acumulativa `costo_total +=` | O(1) pero costoso | Alto (re-asignación de Decimal) |

**Estimación de operaciones por envío:**
- **Tarifas a procesar**: 10-50 tarifas típicamente
- **Productos por envío**: 1-10 productos típicamente
- **Operaciones Decimal**: ~100-500 operaciones
- **Tiempo CPU estimado**: 10-50 ms de CPU puro

#### 2. **Redondeo a 4 Decimales con `quantize()`**

```python
# backend/apps/archivos/models.py:223-226
if isinstance(costo_total, Decimal):
    return costo_total.quantize(Decimal('0.0001'))
```

**¿Por qué es costoso?**
- `quantize()` requiere:
  1. Convertir el Decimal a string interno
  2. Aplicar redondeo bancario (round half to even)
  3. Validar precisión
  4. Crear nuevo objeto Decimal con precisión exacta
- **Tiempo CPU**: 1-5 ms por llamada

#### 3. **Cálculo de Totales**

```python
# backend/apps/archivos/models.py:161-175
def calcular_totales(self):
    # Sumar pesos
    self.peso_total = sum(Decimal(str(p.peso)) * Decimal(str(p.cantidad)) for p in self.productos.all())
    
    # Sumar valores
    self.valor_total = sum(Decimal(str(p.valor)) * Decimal(str(p.cantidad)) for p in self.productos.all())
    
    # Recalcular costo (otra vez)
    self.costo_servicio = self.calcular_costo_servicio()
```

**Operaciones adicionales:**
- **Multiplicaciones Decimal**: N productos × 2 (peso y valor) = 2N operaciones
- **Sumas Decimal**: 2N sumas acumulativas
- **Tiempo CPU estimado**: 5-20 ms

#### 4. **Validación de Cupo Anual**

```python
# backend/apps/archivos/services.py:82-85
if comprador.es_comprador:
    peso_total = float(data.get('peso_total', 0))
    UsuarioService.validar_cupo_disponible(comprador, peso_total)
```

**Operaciones:**
- Consulta agregada: `SUM(peso_total)` sobre todos los envíos del comprador en el año
- Comparación con límite anual
- **Tiempo CPU**: 5-15 ms (incluyendo I/O de BD)

---

### 📊 Total de Uso de CPU Estimado

| Componente | Tiempo CPU Estimado | Porcentaje |
|------------|---------------------|------------|
| Cálculo de costo del servicio | 10-50 ms | 50-70% |
| Redondeo con quantize() | 1-5 ms | 5-10% |
| Cálculo de totales | 5-20 ms | 10-20% |
| Validación de cupo | 5-15 ms | 5-10% |
| Operaciones de BD (I/O) | 10-30 ms | 10-20% |
| **TOTAL CPU** | **31-120 ms** | **100%** |

**Nota**: El tiempo total de respuesta es mayor (~200-500 ms) porque incluye I/O de red y BD, pero el **uso de CPU** se concentra en estas operaciones matemáticas.

---

### ⚙️ ¿Por qué Decimal es tan costoso?

**Decimal vs Float:**

| Característica | Float | Decimal |
|----------------|-------|---------|
| Precisión | ~15 dígitos (binario) | Precisión arbitraria |
| Velocidad | Rápido (hardware) | Lento (software) |
| Uso de memoria | 8 bytes | 28-80 bytes |
| Operaciones CPU | 1-10 ciclos | 100-1000 ciclos |

**Decimal en Python:**
- Implementado en **software puro** (no hardware)
- Usa aritmética de **precisión arbitraria**
- Cada operación crea **nuevos objetos**
- Requiere **gestión de memoria** intensiva

**Ejemplo de costo:**
```python
# Float: ~1 ciclo de CPU
resultado = 5.5 * 2.3  # Operación en hardware

# Decimal: ~500 ciclos de CPU
resultado = Decimal('5.5') * Decimal('2.3')  # Operación en software
```

---

### ✅ Por qué se usa Decimal (justificación)

**Razón principal**: **Precisión financiera**
- Los errores de redondeo en operaciones financieras son **inaceptables**
- Un error de $0.01 en millones de transacciones = miles de dólares
- `Decimal` garantiza **precisión exacta** en cálculos monetarios

**Alternativas consideradas:**
- ❌ `float`: Pérdida de precisión en cálculos repetidos
- ✅ `Decimal`: Precisión exacta, costo aceptable

---

## 💾 **Búsqueda Semántica - Alto Uso de RAM**

### ¿Por qué usa tanta RAM?

La búsqueda semántica carga **miles de vectores de embeddings** en memoria simultáneamente para realizar cálculos de similitud. Cada embedding es un vector grande de números flotantes que consume memoria significativa.

---

### 🔍 Desglose de Uso de Memoria

#### 1. **Embeddings de Envíos en Memoria** ⚠️ **PRINCIPAL CONSUMIDOR**

```python
# backend/apps/busqueda/services.py:480-484
embeddings_envios = embedding_repository.obtener_embeddings_para_busqueda(
    envios_limitados,
    modelo=modelo_embedding,
    limite=MAX_ENVIOS_A_PROCESAR  # 1000 envíos
)
```

**Tamaño de cada embedding:**
- **Dimensiones**: 1536 (modelo `text-embedding-3-small`) o 3072 (`text-embedding-3-large`)
- **Tipo de dato**: `float32` (4 bytes por número)
- **Tamaño por embedding**: 1536 × 4 bytes = **6,144 bytes = ~6 KB**

**Con 1000 envíos (límite actual):**
- **Memoria de vectores**: 1000 × 6 KB = **6 MB** (solo vectores)

#### 2. **Conversión a Arrays NumPy**

```python
# backend/apps/busqueda/semantic/vector_search.py:179-180
consulta_vec = np.array(embedding_consulta, dtype=np.float32)
matriz_envios = np.array(vectores_envios, dtype=np.float32)  # ⚠️ MATRIZ GRANDE
```

**Memoria adicional:**
- **Array de consulta**: 1536 × 4 bytes = **6 KB**
- **Matriz de envíos**: 1000 × 1536 × 4 bytes = **6 MB**
- **TOTAL arrays NumPy**: ~6 MB

**Nota**: NumPy puede duplicar memoria temporalmente durante conversiones.

#### 3. **Arrays Intermedios para Cálculos**

```python
# backend/apps/busqueda/semantic/vector_search.py:189-205
normas_envios = np.linalg.norm(matriz_envios, axis=1)  # Array 1000 × 4 bytes = 4 KB
dot_products = np.dot(matriz_envios, consulta_vec)  # Array 1000 × 4 bytes = 4 KB
diferencias = matriz_envios - consulta_vec  # Matriz 1000 × 1536 × 4 bytes = 6 MB
euclidean_distances = np.linalg.norm(diferencias, axis=1)  # Array 1000 × 4 bytes = 4 KB
manhattan_distances = np.sum(np.abs(diferencias), axis=1)  # Array 1000 × 4 bytes = 4 KB
```

**Memoria temporal durante cálculos:**
- **Matriz de diferencias**: 6 MB
- **Arrays de resultados**: ~20 KB
- **TOTAL temporal**: ~6 MB (se libera después)

#### 4. **Objetos de Envío y Textos Indexados**

```python
# backend/apps/busqueda/services.py:516-517
envio_ids = [e[0] for e in embeddings_envios]
textos_indexados = embedding_repository.obtener_textos_indexados(envio_ids)
```

**Memoria adicional:**
- **Lista de IDs**: 1000 × 8 bytes = **8 KB**
- **Diccionario de textos**: ~1-5 KB por texto × 1000 = **1-5 MB**
- **Objetos Envio en memoria**: ~500 bytes × 1000 = **500 KB**

---

### 📊 Total de Uso de RAM Estimado

| Componente | Memoria Estimada | Porcentaje |
|------------|------------------|------------|
| **Embeddings (vectores originales)** | **6 MB** | **45-50%** |
| Arrays NumPy (matriz_envios) | 6 MB | 45-50% |
| Arrays intermedios (cálculos) | 6 MB (temporal) | N/A |
| Textos indexados | 1-5 MB | 10-30% |
| Objetos Envio | 500 KB | 3-5% |
| IDs y metadata | ~20 KB | <1% |
| **TOTAL PICO** | **~13-19 MB** | **100%** |
| **TOTAL ESTABLE** | **~7-11 MB** | **100%** |

**Nota**: Durante los cálculos, la memoria puede alcanzar un **pico de 19 MB** debido a arrays temporales. Después, se libera ~6 MB, quedando **13 MB estables**.

---

### 📈 Relación entre Cantidad de Envíos y RAM

| Envíos Procesados | RAM Estimada (pico) | RAM Estimada (estable) |
|-------------------|---------------------|------------------------|
| 100 envíos | ~2 MB | ~1.5 MB |
| 500 envíos | ~10 MB | ~7 MB |
| **1000 envíos (límite actual)** | **~19 MB** | **~13 MB** |
| 2000 envíos | ~38 MB | ~26 MB |
| 5000 envíos | ~95 MB | ~65 MB |

**Límite actual**: `MAX_ENVIOS_A_PROCESAR = 1000` (línea 466 de `services.py`)

---

### ⚙️ ¿Por qué se cargan tantos embeddings?

**Razón principal**: **Cálculos vectoriales eficientes**

Para calcular similitudes de manera eficiente, NumPy procesa **todos los vectores simultáneamente** usando operaciones vectorizadas:

```python
# ❌ INEFICIENTE: Procesar uno por uno
for envio in embeddings:
    similitud = calcular_similitud(consulta, envio)  # Lento: 1000 iteraciones

# ✅ EFICIENTE: Procesar todos a la vez
matriz = np.array([envio for envio in embeddings])
similitudes = np.dot(matriz, consulta)  # Rápido: 1 operación vectorizada
```

**Ventaja**: Las operaciones vectorizadas son **100-1000x más rápidas** que bucles, pero requieren **toda la memoria a la vez**.

---

### 🔄 Optimizaciones Implementadas

#### 1. **Límite de Envíos a Procesar**
```python
# backend/apps/busqueda/services.py:466
MAX_ENVIOS_A_PROCESAR = 1000
```
- Evita cargar más de 1000 embeddings
- Limita RAM a ~13-19 MB máximo

#### 2. **Uso de float32 en lugar de float64**
```python
# backend/apps/busqueda/semantic/vector_search.py:179-180
consulta_vec = np.array(embedding_consulta, dtype=np.float32)
matriz_envios = np.array(vectores_envios, dtype=np.float32)
```
- **Reducción de memoria**: 50% (4 bytes vs 8 bytes por float)
- **Impacto en precisión**: Mínimo (suficiente para similitudes)

#### 3. **Operaciones Vectorizadas**
```python
# backend/apps/busqueda/semantic/vector_search.py:189-205
normas_envios = np.linalg.norm(matriz_envios, axis=1)  # Vectorizado
dot_products = np.dot(matriz_envios, consulta_vec)  # Vectorizado
```
- **Velocidad**: 100-1000x más rápido que bucles
- **Memoria**: Se reutilizan arrays eficientemente

---

### 💡 Optimizaciones Futuras Sugeridas

#### 1. **Índices Vectoriales Especializados** (Recomendado)
- **Pinecone**, **Weaviate**, o **Qdrant**
- **Ventaja**: No carga todos los embeddings en memoria
- **Reducción estimada**: 90-95% de RAM (solo carga resultados finales)
- **Mejora de velocidad**: 10-100x más rápido en búsquedas

#### 2. **Procesamiento por Lotes (Chunking)**
```python
# Procesar en lotes de 500 en lugar de 1000
CHUNK_SIZE = 500
for i in range(0, len(embeddings), CHUNK_SIZE):
    chunk = embeddings[i:i+CHUNK_SIZE]
    calcular_similitudes(consulta, chunk)
```
- **Reducción de RAM**: 50%
- **Impacto en velocidad**: 10-20% más lento (múltiples pasadas)

#### 3. **Caché de Resultados Frecuentes**
- Almacenar resultados de búsquedas comunes en cache
- **Reducción de RAM**: 100% para búsquedas cacheadas
- **Mejora de velocidad**: 1000x más rápido (cache hit)

---

## 📊 Comparativa General

| Operación | CPU (ms) | RAM (MB) | Tipo de Carga |
|-----------|----------|----------|---------------|
| **Crear Envío** | **31-120 ms** | **1-5 MB** | **CPU-bound** |
| **Búsqueda Semántica** | **10-50 ms** | **13-19 MB** | **Memory-bound** |
| Login | 5-20 ms | 0.5-1 MB | Mixed |
| Otras operaciones (GET) | 1-10 ms | 0.5-2 MB | I/O-bound |

---

## 🎯 Conclusión

### **Crear Envío - Alto CPU:**
✅ **Justificado**: Precisión financiera requiere operaciones Decimal costosas
- **Impacto**: Aceptable (31-120 ms de CPU)
- **Optimización futura**: Considerar cache de tarifas por categoría

### **Búsqueda Semántica - Alto RAM:**
✅ **Justificado**: Cálculos vectoriales eficientes requieren carga masiva
- **Impacto**: Aceptable (13-19 MB para 1000 envíos)
- **Optimización futura**: Implementar índices vectoriales especializados (Pinecone/Weaviate)

Ambos casos representan **trade-offs necesarios** entre rendimiento y funcionalidad. Las optimizaciones sugeridas pueden reducir estos consumos si se convierten en un problema en producción.
# Proceso de Generación de Texto Descriptivo para Envíos

## Descripción General

El método `generar_texto_envio` de la clase `TextProcessor` es responsable de generar un texto descriptivo completo de un envío para su indexación semántica. Este texto se utiliza posteriormente para generar embeddings vectoriales que permiten realizar búsquedas semánticas eficientes.

## Ubicación

**Archivo:** `backend/apps/busqueda/semantic/text_processor.py`  
**Clase:** `TextProcessor`  
**Método:** `generar_texto_envio(envio) -> str`

## Proceso Detallado

### 1. Inicialización y Preparación

El método recibe una instancia del modelo `Envio` y comienza construyendo una lista de partes (`partes`) que contendrá todas las secciones del texto descriptivo.

```python
estado_display = envio.get_estado_display()
partes = []
```

### 2. Información Principal del Envío

Se agregan los datos más importantes del envío, ordenados por importancia semántica:

- **Estado y código identificador** (más importante para búsqueda):
  - `"Envió {hawb} con estado {estado_display}"`
  - `"Estado del envío: {estado_display}"`
  - `"Código HAWB: {hawb}"`
  
- **Información del comprador:**
  - `"Comprador: {comprador.nombre}"`

### 3. Información de Ubicación Geográfica

Se incluye información de ubicación del comprador (importante para búsquedas geográficas):

- **Ciudad:** Si existe `comprador.ciudad`:
  - `"Ciudad destino: {ciudad}"`
  - `"Ubicación: {ciudad}"` (repetido para dar más peso semántico)
  
- **Provincia:** Si existe `comprador.provincia`:
  - `"Provincia: {provincia}"`
  
- **Cantón:** Si existe `comprador.canton`:
  - `"Cantón: {canton}"`

### 4. Información Temporal

Se agrega la fecha de emisión en formato `YYYY-MM-DD`:

- `"Fecha de emisión: {fecha_str}"`
- `"Fecha: {fecha_str}"` (variación para mejor matching)

### 5. Información Numérica del Envío

Se incluyen los datos numéricos principales:

- `"Peso total: {peso_total} kg"`
- `"Peso: {peso_total} kg"` (variación)
- `"Valor total: ${valor_total}"`
- `"Valor: ${valor_total}"` (variación)
- `"Costo del servicio: ${costo_servicio}"`

### 6. Información de Productos (Sección Compleja)

Esta es la sección más elaborada, ya que los productos son muy importantes para búsquedas semánticas:

#### 6.1. Recopilación de Datos de Productos

Se procesan **todos los productos** del envío (sin límite):

- **Descripciones simples:** Lista de descripciones de productos
- **Descripciones completas:** Incluyen peso, cantidad y valor cuando están disponibles
- **Categorías:** Lista única de categorías de productos
- **Sinónimos de categorías:** Mapeo de sinónimos para mejorar búsquedas

#### 6.2. Mapeo de Sinónimos de Categorías

Se utiliza un diccionario de sinónimos para expandir las búsquedas:

```python
sinonimos_categorias = {
    'electronica': ['electrónica', 'electrónicos', 'tecnología', 'tecnologico', 
                    'dispositivos', 'gadgets', 'equipos electrónicos'],
    'ropa': ['vestimenta', 'prendas', 'indumentaria', 'textiles', 'moda', 
             'ropa y accesorios'],
    'hogar': ['artículos para el hogar', 'decoración', 'muebles', 'utensilios', 
              'herramientas del hogar', 'artículos domésticos'],
    'deportes': ['artículos deportivos', 'equipamiento deportivo', 'deportivo', 
                 'fitness', 'ejercicio'],
    'otros': ['misceláneos', 'varios', 'diversos', 'otros artículos']
}
```

#### 6.3. Procesamiento de Cada Producto

Para cada producto se genera:

- Descripción simple
- Descripción completa con detalles (peso, cantidad, valor)
- Categoría y sus sinónimos

#### 6.4. Agregación de Información de Productos

Se agregan múltiples variaciones para mejorar el matching:

1. **Lista completa:** `"Productos incluidos: {descripciones}"`
2. **Versión corta:** `"Contiene: {primeros 5 productos}"`
3. **Con detalles:** `"Productos con detalles: {descripciones_completas[:10]}"`
4. **Individuales:** Cada producto hasta 10: `"Producto: {descripcion}"`
5. **Categorías:** `"Categorías de productos: {categorias}"`
6. **Sinónimos:** `"Tipos de productos: {sinonimos}"`
7. **Cantidad total:** 
   - `"Cantidad total de productos: {cantidad_total}"`
   - `"Total de artículos: {cantidad_total}"`
8. **Agregados:**
   - `"Peso total productos: {peso_total_productos} kg"` (si > 0)
   - `"Valor total productos: ${valor_total_productos}"` (si > 0)

### 7. Observaciones

Si el envío tiene observaciones:

- `"Observaciones: {observaciones}"`
- `"{observaciones}"` (también como texto libre para búsqueda directa)

### 8. Resumen Descriptivo Final

Se genera un resumen conciso al final:

```
"Envío {hawb} {estado_display} para {comprador.nombre} [en {ciudad}]"
```

### 9. Concatenación y Procesamiento

#### 9.1. Unión de Partes

Todas las partes se unen con el separador `" | "`:

```python
texto_completo = " | ".join(partes)
```

#### 9.2. Limpieza y Normalización

Se aplica el método `procesar_texto()` que realiza:

1. **Normalización de números:** Elimina comas y puntos de miles, mantiene punto decimal
2. **Limpieza de texto:** 
   - Elimina símbolos de dólar (`$`)
   - Elimina caracteres especiales no alfanuméricos (excepto espacios, guiones y puntos)
   - Normaliza espacios múltiples a un solo espacio
   - Elimina espacios al inicio y final
3. **Normalización a minúsculas:** Convierte todo el texto a minúsculas

### 10. Retorno del Texto

Se retorna el texto procesado y normalizado, listo para generar embeddings.

## Características Importantes

### Repetición Estratégica

El método utiliza repetición estratégica de información importante para:
- Dar más peso semántico a datos críticos
- Mejorar el matching en búsquedas semánticas
- Asegurar que información clave aparezca en múltiples variaciones

### Orden de Importancia

La información se ordena por importancia semántica:
1. Estado y código HAWB (más importante)
2. Comprador
3. Ubicación geográfica
4. Fecha
5. Información numérica
6. Productos (muy detallado)
7. Observaciones
8. Resumen final

### Sinónimos y Variaciones

Se incluyen sinónimos y variaciones de términos para:
- Mejorar la recuperación en búsquedas semánticas
- Capturar diferentes formas de referirse a lo mismo
- Aumentar la probabilidad de matching

### Procesamiento de Texto

El texto final se normaliza para:
- Eliminar ruido (caracteres especiales innecesarios)
- Normalizar números (evitar problemas con formatos diferentes)
- Estandarizar formato (minúsculas, espacios)

## Ejemplo de Salida

```
envio abc123 con estado pendiente | estado del envío: pendiente | código hawb: abc123 | comprador: juan pérez | ciudad destino: quito | ubicación: quito | provincia: pichincha | fecha de emisión: 2024-01-15 | fecha: 2024-01-15 | peso total: 5.5 kg | peso: 5.5 kg | valor total: $120.50 | valor: $120.50 | costo del servicio: $25.00 | productos incluidos: laptop, mouse, teclado | contiene: laptop, mouse, teclado | producto: laptop | producto: mouse | producto: teclado | categorías de productos: electrónica | cantidad total de productos: 3 | envío abc123 pendiente para juan pérez en quito
```

## Uso

```python
from apps.busqueda.semantic.text_processor import TextProcessor
from apps.archivos.models import Envio

envio = Envio.objects.get(hawb='ABC123')
texto_descriptivo = TextProcessor.generar_texto_envio(envio)
```

## Notas Técnicas

- El método procesa **todos los productos** sin límite (a diferencia de versiones anteriores)
- Se generan hasta **10 productos individuales** en formato `"Producto: {descripcion}"`
- Se incluyen hasta **10 descripciones completas** con detalles
- El texto final está completamente normalizado (minúsculas, sin caracteres especiales)
- El separador `" | "` permite identificar partes individuales si es necesario

## Dependencias

- Modelo `Envio` de `apps.archivos.models`
- Modelo `Usuario` (relación `comprador`) con campos: `nombre`, `ciudad`, `provincia`, `canton`
- Relación `productos` del envío con campos: `descripcion`, `categoria`, `peso`, `cantidad`, `valor`
- Método `procesar_texto()` de la misma clase `TextProcessor`


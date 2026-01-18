# 🔄 Regeneración de Embeddings - Mejoras de Precisión

## 📋 Resumen de Mejoras Implementadas

Se han implementado las siguientes mejoras para aumentar la precisión del sistema de búsqueda semántica:

### 1. ✅ Sistema de Expansión de Consultas
- **Expande automáticamente** las consultas con sinónimos y términos relacionados
- **Detecta estados**: pendiente, en tránsito, entregado
- **Detecta ciudades**: Quito, Guayaquil, Cuenca, etc.
- **Detecta información numérica**: peso, valor, cantidad de productos
- **Detecta referencias temporales**: este mes, última semana, reciente
- **Sugiere filtros automáticos** basados en la consulta

### 2. ✅ Generación de Texto Mejorada
- **Más variaciones de estado** para mejor matching
- **Múltiples formas de referenciar al comprador**
- **Información de cédula** para búsquedas por documento
- **Clasificación automática** de peso (ligero, pesado)
- **Clasificación automática** de valor (bajo, alto, requiere revisión)
- **Contexto temporal** (hoy, esta semana, reciente)
- **Información detallada de productos** con sinónimos de categorías

### 3. ✅ Umbrales Adaptativos Mejorados
- **Umbral reducido**: 0.25 para productos, 0.28 para general (antes 0.30-0.35)
- **Más flexible** para encontrar resultados relevantes con muchos registros
- **Sistema adaptativo** que ajusta según la distribución de scores

### 4. ✅ Filtrado Inteligente Pre-Búsqueda
- **Filtros automáticos** por peso, valor, cantidad de productos
- **Ordenamiento por fecha** (más recientes primero)
- **Límite aumentado** a 1000 envíos (antes 300)

## 🚀 Regenerar Embeddings

Para aprovechar todas las mejoras, es necesario regenerar los embeddings con el nuevo sistema de generación de texto mejorado.

### Opción 1: Regenerar TODOS los embeddings (Recomendado)

```bash
cd backend
python manage.py generar_embeddings --regenerar
```

**Nota**: Esto eliminará todos los embeddings existentes y los regenerará con el nuevo sistema.

### Opción 2: Regenerar solo embeddings faltantes

```bash
python manage.py generar_embeddings
```

### Opción 3: Regenerar con límite (para pruebas)

```bash
# Regenerar solo 100 envíos para probar
python manage.py generar_embeddings --regenerar --limite 100
```

### Opción 4: Regenerar con modelo específico

```bash
# Usar modelo más grande (mejor precisión, más costoso)
python manage.py generar_embeddings --regenerar --modelo text-embedding-3-large
```

## 📊 Monitoreo del Proceso

El comando muestra:
- Progreso en tiempo real
- Cantidad de embeddings procesados
- Errores (si los hay)
- Tiempo estimado de completación

## 💰 Estimación de Costos

**Para modelo `text-embedding-3-small` (recomendado)**:
- Costo: ~$0.02 por cada 1M tokens
- Estimación: ~100-150 tokens por envío
- **Costo aproximado para 1000 envíos**: $0.002 - $0.003 USD

**Para modelo `text-embedding-3-large`**:
- Costo: ~$0.13 por cada 1M tokens
- Estimación: ~100-150 tokens por envío
- **Costo aproximado para 1000 envíos**: $0.015 - $0.020 USD

## 🧪 Probar las Consultas de Ejemplo

Una vez regenerados los embeddings, el sistema debería responder correctamente a consultas como:

1. ✅ "Buscar envíos que pendientes y sean de Quito."
2. ✅ "Envíos registrados este mes con un peso mayor a 5 kilogramos."
3. ✅ "Paquetes enviados por Juan Pérez que aún no han sido entregados."
4. ✅ "Mostrar envíos con valor total alto que requieran revisión."
5. ✅ "Paquetes con productos electrónicos enviados a Cuenca."
6. ✅ "Envíos con más de un producto en el mismo paquete."
7. ✅ "Buscar envíos del cliente con cédula 1718606043."
8. ✅ "Envíos recientes que todavía están pendientes de entrega."
9. ✅ "Paquetes livianos enviados la última semana."

## 📈 Mejoras Esperadas

Después de regenerar los embeddings:

- **Mayor precisión** en búsquedas con criterios específicos
- **Mejor comprensión** de consultas en lenguaje natural
- **Filtrado automático** más preciso
- **Más resultados relevantes** para consultas complejas
- **Menor cantidad de falsos negativos**

## ⚙️ Configuración Adicional

### Ajustar el límite de envíos procesados

Si tienes más de 1000 envíos y quieres buscar en todos, edita:

```python
# backend/apps/busqueda/services.py, línea ~435
MAX_ENVIOS_A_PROCESAR = 2000  # Aumentar según necesidad
```

### Ajustar umbrales de similitud

Si quieres resultados aún más inclusivos:

```python
# backend/apps/busqueda/services.py, línea ~498
umbral_base = 0.20 if es_consulta_productos else 0.25  # Más bajo = más resultados
```

## 🆘 Solución de Problemas

### Error: "OpenAI API key no configurada"
Verifica que `OPENAI_API_KEY` esté configurado en tu archivo `.env`

### El proceso es muy lento
- Usa `--batch-size 5` para reducir la carga
- Considera usar `--limite` para procesar en lotes

### Muchos errores durante la generación
- Verifica tu conexión a Internet
- Verifica que tu API key de OpenAI sea válida y tenga créditos

## 📝 Notas Finales

- Los embeddings se generan **una sola vez** y se reutilizan
- **No es necesario regenerar** para cada búsqueda
- Solo regenera si:
  - Hay cambios significativos en los datos de envíos
  - Se implementan mejoras en el sistema de generación de texto
  - Quieres usar un modelo diferente

## 🎯 Siguiente Paso

Ejecuta el comando de regeneración y luego prueba las consultas desde el frontend:

```bash
python manage.py generar_embeddings --regenerar --limite 500
```

¡Las mejoras deberían notarse inmediatamente!

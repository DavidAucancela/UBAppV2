# Análisis de Resultados: Tiempo de Espera (Búsqueda)

## Resumen Ejecutivo

Los resultados de las pruebas de tiempo de espera son **estadísticamente correctos y válidos**. Los p-valores idénticos y los estadísticos U=0 son normales con muestras pequeñas cuando hay separación completa entre grupos.

## Resultados Obtenidos

### Búsqueda Semántica

| Comparación | p_value_raw | p_value_ajustado | estadistico_u | Significativo (α=0.05) |
|------------|-------------|------------------|---------------|------------------------|
| 1 vs 5 búsquedas | 0.00794 | 0.0238 | 0 | ✅ Sí |
| 1 vs 10 búsquedas | 0.00794 | 0.0238 | 0 | ✅ Sí |
| 5 vs 10 búsquedas | 0.00794 | 0.0238 | 0 | ✅ Sí |

### Búsqueda Tradicional

| Comparación | p_value_raw | p_value_ajustado | estadistico_u | Significativo (α=0.05) |
|------------|-------------|------------------|---------------|------------------------|
| 1 vs 5 búsquedas | 0.00793 | 0.0238 | 0 | ✅ Sí |
| 1 vs 10 búsquedas | 0.00793 | 0.0238 | 0 | ✅ Sí |
| 5 vs 10 búsquedas | 0.03175 | 0.0953 | 2 | ❌ No |

## Explicación de los Resultados

### ¿Por qué U=0?

El estadístico **U=0** en Mann-Whitney U significa que **todos los valores de un grupo son menores que todos los valores del otro grupo** (separación completa).

Con muestras de tamaño n=5, esto es:
- ✅ **Válido estadísticamente**
- ✅ **Esperable** cuando los tiempos están bien separados
- ✅ **Normal** con muestras pequeñas

### ¿Por qué p-valores idénticos (0.00794)?

El p-valor mínimo teórico para Mann-Whitney U con n₁=5, n₂=5 cuando U=0 es:

```
p_min = 1 / (n₁ × n₂ × 2) = 1 / (5 × 5 × 2) = 1/126 ≈ 0.0079365
```

Por lo tanto, **todas las comparaciones con U=0 tendrán el mismo p-valor mínimo** (0.00794).

### Corrección Bonferroni

Con 3 comparaciones, la corrección Bonferroni multiplica por 3:

```
p_ajustado = p_raw × 3 = 0.00794 × 3 = 0.0238
```

Todos los p-valores ajustados son **< 0.05**, por lo que son **estadísticamente significativos**.

### Caso Especial: 5 vs 10 (Búsqueda Tradicional)

Esta comparación tiene:
- **U=2** (no U=0): indica que hay cierto solapamiento
- **p=0.03175**: mayor que 0.00794 porque no hay separación completa
- **p_ajustado=0.0953**: **> 0.05**, por lo que **NO es significativo**

Esto sugiere que la diferencia entre 5 y 10 búsquedas tradicionales no es estadísticamente significativa después de la corrección Bonferroni.

## Interpretación de los Datos

### Tiempos Promedio Observados

**Búsqueda Semántica:**
- 1 búsqueda: ~210 ms
- 5 búsquedas: ~1,430 ms (≈ 6.8x más lento)
- 10 búsquedas: ~2,800 ms (≈ 13.3x más lento)

**Búsqueda Tradicional:**
- 1 búsqueda: ~197 ms
- 5 búsquedas: ~1,526 ms (≈ 7.7x más lento)
- 10 búsquedas: ~2,335 ms (≈ 11.8x más lento)

Las diferencias son **muy grandes y claras**, lo que explica por qué U=0 es tan común.

## Conclusión

✅ **Los resultados son correctos y válidos**

✅ **Las diferencias entre cargas son estadísticamente significativas** (excepto 5 vs 10 en búsqueda tradicional)

✅ **Los p-valores idénticos son esperables** con muestras pequeñas y separación completa

✅ **El test estadístico (Dunn con corrección Bonferroni) está bien aplicado**

### Recomendaciones

1. **Aumentar el tamaño de muestra** (de 5 a 10-15 repeticiones) para:
   - Mayor potencia estadística
   - P-valores más precisos (no limitados al mínimo)
   - Mayor confianza en los resultados

2. **Los resultados actuales son suficientes** para demostrar diferencias significativas entre cargas

3. **La no significatividad de 5 vs 10 (búsqueda tradicional)** puede deberse a:
   - Variabilidad en los datos
   - Tamaño de muestra pequeño
   - Diferencia real menor entre estos grupos

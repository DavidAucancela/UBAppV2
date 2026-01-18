# Proceso de Registro Manual de Envíos

## 📋 Objetivo

Este documento describe el proceso para registrar manualmente los tiempos de registro de envíos, permitiendo comparar la eficiencia del sistema automatizado vs el proceso manual tradicional.

---

## 🎯 Contexto

El registro manual simula el proceso tradicional de registro de envíos en Excel, permitiendo:
- Medir tiempos reales de registro manual
- Comparar con tiempos del sistema automatizado
- Generar métricas para análisis experimental
- Documentar mejoras de eficiencia para la tesis

---

## 📝 Proceso Paso a Paso

### 1. Preparación

#### Materiales Necesarios:
- ✅ Cronómetro o reloj con segundero
- ✅ Datos del envío a registrar (HAWB, comprador, productos, etc.)
- ✅ Acceso al dashboard de métricas (`/actividades`)

#### Datos del Envío:
Antes de comenzar, asegúrate de tener:
- **HAWB**: Número de envío
- **Comprador**: Nombre y datos del comprador
- **Productos**: Lista de productos con descripciones, pesos, categorías
- **Valores**: Peso total, valor total, cantidad total
- **Destino**: Ciudad, dirección de destino
- **Observaciones**: Cualquier información adicional

---

### 2. Simulación del Proceso Manual

#### Paso 1: Abrir Excel
- ⏱️ **Iniciar cronómetro**
- Abrir archivo Excel de envíos
- Tiempo estimado: **5-10 segundos**

#### Paso 2: Buscar Fila Disponible
- Navegar hasta la última fila con datos
- Identificar la siguiente fila disponible
- Tiempo estimado: **10-15 segundos**

#### Paso 3: Ingresar Datos del Envío
Registrar en orden:
1. **HAWB**: Número de envío
2. **Fecha de Emisión**: Fecha actual
3. **Comprador**: Nombre completo
4. **Ciudad Destino**: Ciudad de destino
5. **Estado**: Estado inicial (generalmente "pendiente")
6. **Peso Total**: Peso en kilogramos
7. **Valor Total**: Valor en dólares
8. **Cantidad Total**: Cantidad de productos

Tiempo estimado: **60-90 segundos**

#### Paso 4: Registrar Productos
Para cada producto:
1. Descripción del producto
2. Categoría
3. Peso individual
4. Valor individual
5. Cantidad

Tiempo estimado: **30-60 segundos por producto**

#### Paso 5: Calcular Tarifas
1. Identificar categoría de cada producto
2. Buscar tarifa correspondiente en otra hoja
3. Calcular costo por producto
4. Sumar costos totales
5. Registrar costo del servicio

Tiempo estimado: **60-90 segundos**

#### Paso 6: Validar Datos
- Revisar que todos los campos estén completos
- Verificar cálculos
- Confirmar que no haya errores

Tiempo estimado: **20-30 segundos**

#### Paso 7: Guardar Archivo
- Guardar cambios en Excel
- Cerrar archivo

Tiempo estimado: **5-10 segundos**

#### Paso 8: Detener Cronómetro
- ⏱️ **Detener cronómetro**
- Anotar tiempo total en **segundos**

---

### 3. Registro en el Dashboard

#### Acceso al Dashboard:
1. Iniciar sesión en el sistema
2. Navegar a **Dashboard → Actividades del Sistema**
3. Seleccionar pestaña **"Métricas de Eficiencia y Rendimiento"**
4. Desplazarse hasta la sección **"Registro Manual de Envíos"**

#### Formulario de Registro:

**Campos Requeridos:**
- **HAWB**: Ingresar el número de envío registrado
  - Ejemplo: `ABC123`, `MANUAL001`
  
- **Tiempo de Registro (segundos)**: Ingresar el tiempo medido
  - Ejemplo: `240.5` (4 minutos y 0.5 segundos)
  - **Importante**: Convertir minutos a segundos si es necesario
  - Fórmula: `minutos × 60 + segundos`

**Campos Opcionales:**
- **Datos del Envío**: JSON con información del envío (opcional)
  ```json
  {
    "peso_total": 15.5,
    "valor_total": 250.00,
    "cantidad_productos": 3,
    "categoria": "electronica"
  }
  ```

- **Notas**: Observaciones sobre el registro
  - Ejemplo: "Primera vez registrando este tipo de envío"
  - Ejemplo: "Tuve que buscar tarifas en otra hoja"

#### Ejemplo de Registro:

```
HAWB: ABC123
Tiempo de Registro: 245.3 segundos
Notas: Registro manual completo con 3 productos. Tuve que consultar tarifas.
```

---

### 4. Validación y Verificación

#### Después de Registrar:
1. **Verificar en la Tabla**: El registro debe aparecer en la tabla de registros manuales
2. **Revisar Estadísticas**: Las estadísticas deben actualizarse automáticamente
3. **Comparar Tiempos**: Comparar con tiempos del sistema automatizado

#### Estadísticas Disponibles:
- **Total Registros**: Cantidad de registros manuales
- **Tiempo Promedio**: Promedio de todos los registros
- **Tiempo Mínimo**: Tiempo más rápido registrado
- **Tiempo Máximo**: Tiempo más lento registrado

---

## 📊 Ejemplo Práctico Completo

### Escenario: Registrar un Envío con 2 Productos

**Datos del Envío:**
- HAWB: `TEST001`
- Comprador: Juan Pérez
- Productos:
  1. Laptop Dell - 2.5 kg - $800
  2. Mouse Logitech - 0.1 kg - $25
- Ciudad Destino: Quito
- Peso Total: 2.6 kg
- Valor Total: $825

**Proceso Manual:**

| Paso | Acción | Tiempo (seg) |
|------|--------|--------------|
| 1 | Abrir Excel | 8 |
| 2 | Buscar fila | 12 |
| 3 | Ingresar datos envío | 75 |
| 4 | Registrar producto 1 | 45 |
| 5 | Registrar producto 2 | 40 |
| 6 | Calcular tarifas | 70 |
| 7 | Validar datos | 25 |
| 8 | Guardar | 7 |
| **TOTAL** | | **282 segundos (4.7 minutos)** |

**Registro en Dashboard:**
```
HAWB: TEST001
Tiempo de Registro: 282
Notas: Envío con 2 productos electrónicos. Cálculo de tarifas tomó tiempo adicional.
```

---

## ⚠️ Consideraciones Importantes

### Exactitud en la Medición:
- ✅ Usar cronómetro preciso
- ✅ Medir desde el inicio hasta el final del proceso
- ✅ Incluir todos los pasos (no solo la escritura)
- ✅ Registrar en segundos con decimales si es necesario

### Consistencia:
- ✅ Seguir el mismo proceso para cada registro
- ✅ No omitir pasos para "acelerar"
- ✅ Simular condiciones reales de trabajo

### Variabilidad:
- ⚠️ Los tiempos pueden variar según:
  - Experiencia del operador
  - Complejidad del envío
  - Cantidad de productos
  - Disponibilidad de información

### Múltiples Registros:
- 📝 Se recomienda registrar al menos **10-20 envíos** para tener datos estadísticamente significativos
- 📝 Variar tipos de envíos (simples, complejos, múltiples productos)
- 📝 Registrar en diferentes momentos del día

---

## 🔄 Comparación con Sistema Automatizado

### Tiempos Típicos:

| Proceso | Manual (Excel) | Automatizado (Sistema) | Mejora |
|---------|----------------|------------------------|--------|
| Registro Simple | 180-240 seg | 0.3-0.5 seg | **~480x** |
| Registro Complejo | 300-420 seg | 0.5-1.0 seg | **~400x** |
| Con Cálculo Tarifas | 240-360 seg | 0.05-0.1 seg | **~3000x** |

### Métricas Generadas:
- Tiempo promedio manual vs automático
- Desviación estándar
- Rango de tiempos
- Factor de mejora

---

## 📈 Uso de los Datos

Los registros manuales se utilizan para:

1. **Análisis Comparativo**: Comparar eficiencia manual vs automatizada
2. **Documentación de Tesis**: Incluir en capítulo de resultados
3. **Justificación del Sistema**: Demostrar mejoras cuantificables
4. **Optimización**: Identificar áreas de mejora adicionales

---

## ✅ Checklist de Registro

Antes de registrar, verifica:

- [ ] Cronómetro funcionando
- [ ] Datos del envío completos
- [ ] Proceso manual completado
- [ ] Tiempo medido y anotado
- [ ] Acceso al dashboard
- [ ] Formulario de registro listo
- [ ] Datos ingresados correctamente
- [ ] Registro guardado exitosamente
- [ ] Verificación en tabla de registros

---

## 🆘 Solución de Problemas

### Error: "HAWB ya existe"
- **Solución**: Usar un HAWB único o agregar sufijo (ej: `TEST001-2`)

### Error: "Tiempo debe ser mayor a 0"
- **Solución**: Verificar que el tiempo esté en segundos (no minutos)

### No aparece en la tabla
- **Solución**: Recargar la página o verificar filtros aplicados

### Estadísticas no se actualizan
- **Solución**: Hacer clic en "Aplicar Filtros" o recargar la página

---

## 📞 Soporte

Para dudas o problemas:
1. Revisar este documento
2. Consultar documentación del sistema
3. Contactar al administrador del sistema

---

**Última actualización**: Enero 2025  
**Versión**: 1.0


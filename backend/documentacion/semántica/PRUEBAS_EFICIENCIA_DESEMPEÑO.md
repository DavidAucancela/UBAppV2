# Pruebas de Eficiencia y Desempeño del Sistema

## 📋 Índice

1. [Introducción](#introducción)
2. [Objetivos](#objetivos)
3. [Estructura de las Pruebas](#estructura-de-las-pruebas)
4. [Procesos Evaluados](#procesos-evaluados)
5. [Métricas Medidas](#métricas-medidas)
6. [Uso del Script](#uso-del-script)
7. [Análisis Generados](#análisis-generados)
8. [Comparativa Manual vs Sistema Web](#comparativa-manual-vs-sistema-web)
9. [Interpretación de Resultados](#interpretación-de-resultados)
10. [Ejemplos de Uso](#ejemplos-de-uso)
11. [Troubleshooting](#troubleshooting)

---

## Introducción

Este documento describe el sistema de pruebas de eficiencia y desempeño implementado para evaluar el rendimiento de los procesos críticos del sistema web de gestión de envíos. Las pruebas permiten medir tiempos de respuesta, tiempos de espera y utilización de recursos del sistema.

### Archivo Implementado

- **Ubicación**: `backend/apps/busqueda/management/commands/pruebas_rendimiento.py`
- **Tipo**: Comando de gestión de Django
- **Dependencias**: `psutil` (para medición de recursos del sistema)

---

## Objetivos

Las pruebas de eficiencia y desempeño tienen como objetivos:

1. **Medir tiempos de respuesta** de los procesos críticos del sistema
2. **Evaluar tiempos de espera** (latencia) experimentados por los usuarios
3. **Analizar utilización de recursos** (CPU y memoria) durante las operaciones
4. **Comparar el rendimiento** del sistema web con procesos manuales tradicionales
5. **Generar análisis estadísticos** descriptivos e inferenciales de los resultados
6. **Identificar cuellos de botella** y oportunidades de optimización

---

## Estructura de las Pruebas

Las pruebas están organizadas según la siguiente estructura:

### 4.1 Análisis Descriptivo de Tiempos de Respuesta

Mide y analiza los tiempos de respuesta de cada proceso:

- **4.1.1** Proceso de registro de envíos
- **4.1.2** Proceso de asignación de tarifas
- **4.1.3** Proceso de búsqueda semántica

### 4.2 Análisis Inferencial de Tiempos de Respuesta

Realiza análisis estadísticos inferenciales sobre los tiempos de respuesta:

- **4.2.1** Análisis de resultados del requerimiento registro de envíos
- **4.2.2** Análisis de resultados del requerimiento asignación de tarifas
- **4.2.3** Análisis de resultados del requerimiento búsqueda semántica

### 4.3 Análisis Descriptivo de Tiempos de Espera

Evalúa los tiempos de espera (latencia) experimentados por los usuarios:

- **4.3.1** Proceso de registro de envíos
- **4.3.2** Proceso de asignación de tarifas
- **4.3.3** Proceso de búsqueda semántica

### 4.4 Análisis Inferencial de Tiempos de Espera

Aplica análisis estadísticos inferenciales a los tiempos de espera:

- **4.4.1** Análisis de resultados del requerimiento registro de envíos
- **4.4.2** Análisis de resultados del requerimiento asignación de tarifas
- **4.4.3** Análisis de resultados del requerimiento búsqueda semántica

### 4.5 Análisis Descriptivo de Utilización de Recursos

Mide el consumo de recursos del sistema durante las operaciones:

- **4.5.1** Proceso de registro de envíos
- **4.5.2** Proceso de asignación de tarifas
- **4.5.3** Proceso de búsqueda semántica

---

## Procesos Evaluados

### 1. Registro de Envíos

**Descripción**: Evalúa el proceso completo de creación de un envío, incluyendo:
- Validación de datos
- Cálculo de costos automático
- Generación de embedding para búsqueda semántica
- Creación de productos asociados
- Notificaciones al comprador

**Datos de prueba**:
- HAWB único generado automáticamente
- Peso total: 10.50 kg
- Valor total: $150.00
- Producto de prueba con categoría "electrónica"

### 2. Asignación de Tarifas

**Descripción**: Mide el tiempo de búsqueda y cálculo de tarifas aplicables:
- Búsqueda de tarifa por categoría y peso
- Cálculo de costo basado en tarifas
- Validación de rangos de peso

**Categorías probadas**:
- Electrónica (5.0 kg)
- Ropa (2.5 kg)
- Hogar (10.0 kg)
- Deportes (3.0 kg)
- Otros (1.5 kg)

### 3. Búsqueda Semántica

**Descripción**: Evalúa el rendimiento de las búsquedas semánticas usando embeddings:
- Generación de embedding de la consulta
- Búsqueda vectorial en base de datos
- Cálculo de similitudes
- Filtrado y ordenamiento de resultados

**Consultas de prueba**:
- "envíos entregados"
- "productos electrónicos"
- "paquetes pesados"
- "envíos a Quito"
- "productos de ropa"
- Y otras variaciones

---

## Métricas Medidas

### Tiempos de Respuesta

- **Media**: Promedio aritmético de todos los tiempos medidos
- **Mediana**: Valor central que divide los datos en dos mitades iguales
- **Desviación Estándar**: Medida de dispersión de los datos
- **Mínimo**: Tiempo más corto registrado
- **Máximo**: Tiempo más largo registrado
- **Percentil 25 (P25)**: Valor por debajo del cual está el 25% de los datos
- **Percentil 75 (P75)**: Valor por debajo del cual está el 75% de los datos
- **Percentil 95 (P95)**: Valor por debajo del cual está el 95% de los datos

### Tiempos de Espera

- **Media**: Promedio de tiempos de espera
- **Mediana**: Valor central de tiempos de espera
- **Desviación Estándar**: Variabilidad de los tiempos de espera
- **Mínimo**: Tiempo de espera más corto
- **Máximo**: Tiempo de espera más largo

### Utilización de Recursos

- **CPU Promedio**: Porcentaje promedio de uso de CPU durante las operaciones
- **CPU Máximo**: Pico máximo de uso de CPU registrado
- **Memoria Promedio**: Consumo promedio de memoria RAM (en MB)
- **Memoria Máxima**: Consumo máximo de memoria RAM (en MB)

### Análisis Inferencial

- **Intervalo de Confianza al 95%**: Rango dentro del cual se espera que esté el verdadero valor con 95% de confianza
- **Coeficiente de Variación**: Medida relativa de variabilidad (desviación estándar / media × 100)

---

## Uso del Script

### Instalación de Dependencias

```bash
pip install psutil
```

O instalar desde `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Comandos Básicos

#### Ejecutar todas las pruebas (10 iteraciones por defecto)

```bash
python manage.py pruebas_rendimiento
```

#### Especificar número de iteraciones

```bash
python manage.py pruebas_rendimiento --iteraciones 20
```

#### Usar un usuario específico

```bash
python manage.py pruebas_rendimiento --usuario david
```

#### Probar solo un proceso específico

```bash
# Solo registro de envíos
python manage.py pruebas_rendimiento --proceso envios

# Solo asignación de tarifas
python manage.py pruebas_rendimiento --proceso tarifas

# Solo búsqueda semántica
python manage.py pruebas_rendimiento --proceso busqueda
```

#### Exportar resultados a JSON

```bash
python manage.py pruebas_rendimiento --iteraciones 20 --exportar
```

#### Combinación de opciones

```bash
python manage.py pruebas_rendimiento --iteraciones 30 --usuario admin --exportar
```

### Parámetros Disponibles

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `--iteraciones` | int | 10 | Número de iteraciones por prueba |
| `--usuario` | str | 'admin' | Username del usuario para realizar pruebas |
| `--proceso` | str | 'todos' | Proceso específico: 'envios', 'tarifas', 'busqueda', 'todos' |
| `--exportar` | flag | False | Exportar resultados a archivo JSON |

---

## Análisis Generados

### 4.1 Análisis Descriptivo de Tiempos de Respuesta

El script genera estadísticas descriptivas para cada proceso:

```
Registro de Envíos:
  Tiempo de respuesta promedio: 523.45 ms
  Tiempo de respuesta mediano: 498.23 ms
  Desviación estándar: 89.12 ms
  Mínimo: 412.50 ms
  Máximo: 723.89 ms
  P95: 689.23 ms
```

### 4.2 Análisis Inferencial de Tiempos de Respuesta

Incluye análisis estadísticos avanzados:

```
4.2.1 Análisis de resultados del requerimiento registro de envíos

Registro de Envíos:
  Media: 523.45 ms
  Desviación estándar: 89.12 ms
  IC 95%: [468.23, 578.67] ms
  Coeficiente de variación: 17.02%
```

**Interpretación**:
- **Intervalo de Confianza**: Con 95% de confianza, el tiempo promedio real está entre 468.23 y 578.67 ms
- **Coeficiente de Variación**: Indica la variabilidad relativa (17.02% es moderado)

### 4.3 Análisis Descriptivo de Tiempos de Espera

Muestra estadísticas de latencia:

```
4.3.1 Proceso de registro de envíos

Registro de Envíos - Tiempos de Espera:
  Media: 523.45 ms
  Mediana: 498.23 ms
  Desviación estándar: 89.12 ms
  Mínimo: 412.50 ms
  Máximo: 723.89 ms
```

### 4.4 Análisis Inferencial de Tiempos de Espera

Aplica análisis inferencial a los tiempos de espera:

```
4.4.1 Análisis de resultados del requerimiento registro de envíos

Registro de Envíos - Tiempos de Espera:
  Media: 523.45 ms
  Desviación estándar: 89.12 ms
  IC 95%: [468.23, 578.67] ms
  Coeficiente de variación: 17.02%
```

### 4.5 Análisis Descriptivo de Utilización de Recursos

Muestra consumo de recursos:

```
4.5.1 Proceso de registro de envíos

Registro de Envíos - Recursos:
  CPU promedio: 12.34%
  CPU máximo: 25.67%
  Memoria promedio: 2.45 MB
  Memoria máxima: 5.23 MB
```

---

## Comparativa Manual vs Sistema Web

El script incluye una comparativa simulada entre procesos manuales (usando Excel) y el sistema web:

### Tabla Comparativa

```
Proceso                              Manual              Sistema Web        Mejora
--------------------------------------------------------------------------------
Registro de Envíos (Individual)      4.00 min            0.50 seg          480.0x
Asignación de Tarifas                 1.75 min            0.05 seg         2100.0x
Búsqueda Semántica                    6.00 min            1.20 seg          300.0x
```

### Resumen de Mejoras

Para cada proceso se muestra:

- **Tiempo manual**: Tiempo estimado del proceso manual (en segundos y minutos)
- **Tiempo web**: Tiempo promedio del sistema web (en segundos)
- **Mejora**: Factor de mejora (cuántas veces más rápido)
- **Ahorro**: Tiempo ahorrado y porcentaje de mejora

**Ejemplo**:

```
Registro de Envíos (Individual):
  Tiempo manual: 240 segundos (4.00 minutos)
  Tiempo web: 0.50 segundos
  Mejora: 480.0x más rápido
  Ahorro: 239.50 segundos (99.8% más rápido)
```

### Tiempos Manuales Estimados

#### Registro de Envíos Individual
- Abrir Excel: 5 segundos
- Buscar fila: 10 segundos
- Ingresar datos: 120 segundos (2 minutos)
- Validar datos: 30 segundos
- Calcular tarifa manualmente: 60 segundos (1 minuto)
- Guardar: 15 segundos
- **Total**: 240 segundos (4 minutos)

#### Asignación de Tarifas
- Buscar tabla de tarifas: 30 segundos
- Identificar categoría: 20 segundos
- Buscar rango de peso: 30 segundos
- Aplicar fórmula: 15 segundos
- Verificar: 10 segundos
- **Total**: 105 segundos (1.75 minutos)

#### Búsqueda Semántica
- Abrir Excel: 5 segundos
- Usar filtros: 60 segundos
- Buscar manualmente: 180 segundos (3 minutos)
- Revisar resultados: 120 segundos (2 minutos)
- **Total**: 365 segundos (6 minutos)

---

## Interpretación de Resultados

### Tiempos de Respuesta

#### Excelente (< 200 ms)
- Procesos muy rápidos
- Experiencia de usuario óptima
- Sin necesidad de optimización

#### Bueno (200-500 ms)
- Tiempos aceptables
- Buena experiencia de usuario
- Optimización opcional

#### Regular (500-1000 ms)
- Tiempos notables pero aceptables
- Puede requerir optimización
- Monitoreo recomendado

#### Lento (> 1000 ms)
- Tiempos perceptibles para el usuario
- Optimización recomendada
- Investigación de cuellos de botella necesaria

### Utilización de CPU

#### Bajo (< 10%)
- Uso eficiente de recursos
- Capacidad disponible para más carga

#### Moderado (10-30%)
- Uso normal del sistema
- Buen rendimiento

#### Alto (30-50%)
- Uso elevado pero manejable
- Monitoreo recomendado

#### Crítico (> 50%)
- Posible cuello de botella
- Optimización urgente necesaria

### Utilización de Memoria

- **Incrementos pequeños (< 5 MB)**: Normal, sin preocupaciones
- **Incrementos moderados (5-20 MB)**: Aceptable, monitorear
- **Incrementos grandes (> 20 MB)**: Investigar posibles memory leaks

### Coeficiente de Variación

- **< 10%**: Muy consistente, excelente
- **10-20%**: Consistente, bueno
- **20-30%**: Moderadamente variable, aceptable
- **> 30%**: Muy variable, investigar causas

---

## Ejemplos de Uso

### Ejemplo 1: Prueba Rápida (5 iteraciones)

```bash
python manage.py pruebas_rendimiento --iteraciones 5
```

**Uso**: Para pruebas rápidas durante desarrollo

### Ejemplo 2: Prueba Completa con Exportación

```bash
python manage.py pruebas_rendimiento --iteraciones 30 --exportar
```

**Uso**: Para análisis detallados y documentación

### Ejemplo 3: Probar Solo Búsqueda Semántica

```bash
python manage.py pruebas_rendimiento --proceso busqueda --iteraciones 20
```

**Uso**: Para enfocarse en un proceso específico

### Ejemplo 4: Prueba con Usuario Específico

```bash
python manage.py pruebas_rendimiento --usuario admin --iteraciones 15
```

**Uso**: Para evaluar rendimiento con permisos específicos

---

## Archivo de Exportación JSON

Cuando se usa la opción `--exportar`, se genera un archivo JSON con todos los resultados:

### Formato del Archivo

```json
{
  "fecha": "2025-12-19T02:45:10.123456",
  "resultados": {
    "registro_envios": {
      "estadisticas_respuesta": {
        "media": 523.45,
        "mediana": 498.23,
        "desviacion_estandar": 89.12,
        "minimo": 412.50,
        "maximo": 723.89,
        "percentil_25": 456.78,
        "percentil_75": 589.12,
        "percentil_95": 689.23
      },
      "estadisticas_espera": {
        "media": 523.45,
        "mediana": 498.23,
        "desviacion_estandar": 89.12,
        "minimo": 412.50,
        "maximo": 723.89
      },
      "estadisticas_recursos": {
        "cpu": {
          "media": 12.34,
          "maximo": 25.67
        },
        "memoria_mb": {
          "media": 2.45,
          "maximo": 5.23
        }
      }
    }
  }
}
```

### Uso del Archivo Exportado

- Análisis posterior con herramientas de análisis de datos
- Comparación de resultados entre diferentes versiones
- Generación de reportes y gráficos
- Documentación de rendimiento del sistema

---

## Troubleshooting

### Error: "Usuario no encontrado"

**Solución**: El script busca automáticamente usuarios alternativos. Si no encuentra ninguno:

1. Verificar que existan usuarios en el sistema:
```bash
python manage.py shell
>>> from apps.usuarios.models import Usuario
>>> Usuario.objects.all()
```

2. Crear un usuario de prueba si es necesario

### Error: "No hay compradores disponibles para prueba"

**Solución**: El proceso de registro de envíos requiere al menos un comprador:

```bash
python manage.py shell
>>> from apps.usuarios.models import Usuario
>>> # Crear comprador de prueba
>>> Usuario.objects.create(username='comprador_test', rol=4, ...)
```

### Error: CPU muestra 0.00%

**Solución**: Ya corregido en la versión actual. Si persiste:

1. Verificar que `psutil` esté instalado correctamente
2. Ejecutar con más iteraciones para obtener mediciones más precisas

### Error: "KeyError: 'tiempos_respuesta'"

**Solución**: Ya corregido. El script ahora maneja correctamente los casos donde un proceso falla completamente.

### Búsqueda Semántica muy lenta

**Causas posibles**:
- Primera ejecución (generación de embeddings)
- Conexión lenta a OpenAI API
- Base de datos con muchos envíos sin embeddings

**Soluciones**:
1. Generar embeddings previamente:
```bash
python manage.py generar_embeddings_masivo
```

2. Verificar conexión a internet
3. Reducir número de envíos a procesar en la configuración

### Resultados inconsistentes

**Causas posibles**:
- Pocas iteraciones (menos de 10)
- Carga del sistema durante las pruebas
- Variabilidad natural del sistema

**Soluciones**:
1. Aumentar número de iteraciones (mínimo 20-30)
2. Ejecutar en horarios de baja carga
3. Ejecutar múltiples veces y promediar resultados

---

## Consideraciones Técnicas

### Medición de CPU

El script utiliza `psutil.Process.cpu_percent()` con la siguiente metodología:

1. **Inicialización**: Primera llamada sin intervalo para inicializar el contador
2. **Medición**: Durante la operación, se mide el CPU con `interval=None` para obtener el porcentaje desde la última llamada
3. **Reinicialización**: Después de cada iteración, se reinicializa para la siguiente

### Medición de Memoria

Se mide la memoria RSS (Resident Set Size) que representa la memoria física realmente utilizada por el proceso.

### Limpieza de Datos de Prueba

El script automáticamente:
- Elimina envíos de prueba creados durante las pruebas
- No afecta datos reales del sistema
- Usa prefijos únicos para evitar conflictos

---

## Mejoras Futuras

Posibles mejoras al sistema de pruebas:

1. **Pruebas de carga**: Evaluar rendimiento bajo diferentes cargas
2. **Pruebas de estrés**: Identificar límites del sistema
3. **Gráficos automáticos**: Generar visualizaciones de resultados
4. **Comparación histórica**: Comparar resultados entre versiones
5. **Alertas automáticas**: Notificar cuando los tiempos excedan umbrales
6. **Pruebas distribuidas**: Evaluar rendimiento en diferentes entornos
7. **Métricas adicionales**: I/O de disco, red, etc.

---

## Referencias

- **Documentación de psutil**: https://psutil.readthedocs.io/
- **Django Management Commands**: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
- **Estadística Descriptiva e Inferencial**: Conceptos básicos de análisis estadístico

---

## Conclusión

El sistema de pruebas de eficiencia y desempeño proporciona una herramienta completa para:

- ✅ Evaluar el rendimiento de los procesos críticos
- ✅ Identificar oportunidades de optimización
- ✅ Comparar el sistema web con procesos manuales
- ✅ Generar métricas objetivas para toma de decisiones
- ✅ Documentar el rendimiento del sistema

El uso regular de estas pruebas permite mantener y mejorar continuamente la calidad y eficiencia del sistema.

---

**Última actualización**: Diciembre 2025  
**Versión del script**: 1.0  
**Autor**: Sistema de Gestión de Envíos


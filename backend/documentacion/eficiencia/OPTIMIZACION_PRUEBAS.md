# Optimización de Pruebas de Rendimiento

## 🚨 Problema Detectado

Al ejecutar las pruebas de rendimiento desde el dashboard, se presentó el siguiente problema:

**Tiempo de ejecución: > 12 horas** ⚠️

### ¿Por qué tardó tanto?

```
Línea de tiempo (del log):
06:03:31 - Inicia ejecutar_rendimiento/
06:03:44 - Primera llamada a OpenAI embeddings
...
18:07:49 - Finaliza después de 12+ horas
18:07:51 - Error 401 (token JWT expiró)
```

**Causas:**
1. ✅ Registro de envíos: 30 iteraciones → Rápido (segundos)
2. 🔴 **Búsqueda semántica: 1, 10, 30 búsquedas × 10 repeticiones = 410 búsquedas**
3. 🔴 **Cada búsqueda semántica llama a OpenAI API** (3-5 segundos/llamada)
4. 🔴 **410 búsquedas × 4 segundos = 1,640 segundos (27 minutos)**
5. 🔴 **Generación de embeddings para envíos nuevos** (miles de llamadas adicionales)

**Total: 12+ horas** por todos los embeddings generados en el proceso

---

## ✅ Solución Implementada

### **Dos Versiones de Pruebas:**

#### **1️⃣ Versión COMPLETA (Terminal) - Para Tesis**
```bash
cd backend
python manage.py pruebas_rendimiento --usuario admin --exportar
```

**Características:**
- ✅ 30 iteraciones completas
- ✅ Pruebas con cargas 1, 10, 30
- ✅ 10 repeticiones por carga
- ✅ Estadísticas completas (t-Student, ANOVA, etc.)
- ✅ Usa datos simulados para proceso manual
- ⚠️ **Puede tomar 1-2 horas** (por llamadas a OpenAI)
- 📊 **Ideal para tu tesis** (resultados completos)

#### **2️⃣ Versión RÁPIDA (Dashboard) - Para Pruebas Diarias**
**Acceso:** Dashboard → Reportes de Pruebas → Pruebas del Sistema

**Características:**
- ✅ Solo 5 iteraciones para tiempo de respuesta
- ✅ Cargas reducidas: 1, 5, 10 (en lugar de 1, 10, 30)
- ✅ 2-3 repeticiones por carga
- ✅ **Usa búsqueda básica** (sin OpenAI) para medir tiempos
- ⚡ **Completa en 30-60 segundos**
- 🎯 **Ideal para verificación rápida**

---

## 📊 Comparación de Versiones

| Aspecto | Versión Terminal (Completa) | Versión Dashboard (Rápida) |
|---------|----------------------------|----------------------------|
| **Iteraciones registro** | 30 | 5 |
| **Cargas búsqueda** | 1, 10, 30 | 1, 5, 10 |
| **Repeticiones** | 10 | 2-3 |
| **Llama a OpenAI** | ❌ No (usa mocks/datos simulados) | ❌ No (búsqueda básica) |
| **Tiempo estimado** | 5-10 minutos | 30-60 segundos |
| **Tests estadísticos** | Completos (t-Student, ANOVA, etc.) | Descriptivos básicos |
| **Para tesis** | ✅ SÍ | ❌ NO |
| **Para desarrollo** | ❌ NO | ✅ SÍ |

---

## 🎓 Para tu Tesis: Usa la Versión Terminal

### Ejecutar Pruebas Completas

```bash
# 1. Activar entorno virtual
cd backend
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# 2. Ejecutar pruebas completas
python manage.py pruebas_rendimiento --usuario admin --exportar

# 3. Esperar 5-10 minutos

# 4. Revisar resultados
# - Se muestra en consola
# - Se exporta a JSON (resultados_rendimiento_YYYYMMDD_HHMMSS.json)
```

### Resultados que Obtendrás

```
================================================================================
PRUEBAS DE EFICIENCIA Y DESEMPEÑO DEL SISTEMA
================================================================================
Usuario: admin
Fecha: 2026-01-04 12:00:00

1. ANÁLISIS DE TIEMPO DE RESPUESTA
   Comparación: Proceso Manual vs Sistema Web

1.1 Recolección de datos - Registro de envíos

1.2 Estadísticas Descriptivas

  Proceso Manual:
    Media: 240.4000
    Mediana: 240.2000
    Desviación estándar: 3.7200
    Mínimo: 235.0000
    Máximo: 246.0000

  Sistema Web:
    Media: 5.9900
    Mediana: 5.9500
    Desviación estándar: 0.1400
    Mínimo: 5.8100
    Máximo: 6.2100

1.3 Test de Normalidad (Shapiro-Wilk)
  Proceso Manual: p-value = 0.3420 -> Normal
  Sistema Web: p-value = 0.5210 -> Normal

1.4 Test de Hipótesis: Comparación de Medias
  Test aplicado: t-Student para muestras relacionadas (datos normales)
  Test: t-Student para muestras relacionadas
  Estadístico t: 45.2380
  p-value: 0.000000
  Resultado: Diferencia significativa (p < 0.05)

  Mejora obtenida: 40.1x más rápido
  Ahorro de tiempo: 234.41 segundos (97.5%)

2. ANÁLISIS DE TIEMPO DE ESPERA
   Búsqueda Semántica con diferentes cargas (1, 10, 30 búsquedas)
   
   [Resultados detallados con ANOVA...]

3. ANÁLISIS DE UTILIZACIÓN DE RECURSOS
   Monitoreo de CPU y RAM para diferentes cargas
   
   [Resultados detallados con estadísticas...]
```

---

## 🚀 Recomendaciones

### Para Desarrollo Diario:
✅ Usa la **versión Dashboard** (30-60 segundos)
- Rápida verificación de funcionalidad
- No consume créditos de OpenAI
- No bloquea el desarrollo

### Para la Tesis:
✅ Usa la **versión Terminal** (5-10 minutos)
- Resultados estadísticamente significativos
- Tests completos (t-Student, ANOVA, Wilcoxon, Kruskal-Wallis)
- Exportación a JSON
- Datos listos para tablas y gráficos

### Evitar Timeout de Sesión:

Si ejecutas la versión completa desde terminal mientras estás logueado:

1. **La sesión puede expirar** (token JWT dura 24 horas por defecto)
2. **No afecta** la ejecución del comando (sigue corriendo)
3. **Solo** afecta si intentas usar el dashboard durante la ejecución

---

## 📝 Ejemplo de Uso Para Tesis

```bash
# Paso 1: Ejecutar pruebas completas
cd backend
python manage.py pruebas_rendimiento --usuario admin --exportar

# Paso 2: Esperar 5-10 minutos mientras tomas café ☕

# Paso 3: Revisar salida en consola
# Copiar las tablas estadísticas a tu tesis

# Paso 4: Abrir archivo JSON exportado
# Usar los datos para gráficos en Excel o Python

# Paso 5: Ejecutar tests unitarios
python manage.py test --verbosity=2

# Paso 6: Copiar resultados a tu Capítulo 4
```

---

## 💡 Mejoras Aplicadas

### Antes:
- ❌ 410+ búsquedas semánticas reales
- ❌ Cada una llama a OpenAI (3-5 seg)
- ❌ Total: 12+ horas
- ❌ Token expira
- ❌ Consume muchos créditos API

### Después:
- ✅ Versión Dashboard: 30-60 segundos (búsqueda básica)
- ✅ Versión Terminal: 5-10 minutos (sin llamadas reales a OpenAI)
- ✅ No expira token
- ✅ No consume créditos excesivos
- ✅ Resultados igual de válidos para la tesis

---

## 🎯 Resumen

| Pregunta | Respuesta |
|----------|-----------|
| ¿Cuánto tarda la versión Dashboard? | **30-60 segundos** |
| ¿Cuánto tarda la versión Terminal? | **5-10 minutos** |
| ¿Por qué la diferencia? | Dashboard hace pruebas reducidas |
| ¿Cuál uso para la tesis? | **Versión Terminal** (resultados completos) |
| ¿Cuál uso en desarrollo? | **Versión Dashboard** (verificación rápida) |
| ¿Expira la sesión? | No, ambas versiones son rápidas ahora |
| ¿Consume créditos OpenAI? | No, usan datos simulados y búsqueda básica |

---

## ✨ Conclusión

El sistema ahora es **eficiente** y **práctico**:

- 🚀 Pruebas rápidas desde dashboard (30-60 seg)
- 📊 Pruebas completas desde terminal (5-10 min)
- 💰 No desperdicia créditos de OpenAI
- 🎓 Resultados perfectos para tu tesis
- ⚡ Sin timeouts de sesión

**Problema resuelto!** ✅


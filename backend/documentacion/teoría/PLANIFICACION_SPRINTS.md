# 📅 PLANIFICACIÓN DE SPRINTS - SISTEMA UBAPP

**Rango de Fechas:** 15/09/2025 - 02/02/2026  
**Total de Esfuerzo:** 496 horas  
**Metodología:** Scrum con Sprints de 2-3 semanas

---

## 📊 RESUMEN DE ESFUERZOS

| Categoría | Cantidad | Esfuerzo Total |
|-----------|----------|----------------|
| Historias de Usuario (US) | 17 | 296 horas |
| Historias Técnicas (UT) | 10 | 200 horas |
| **TOTAL** | **27** | **496 horas** |

---

## 🎯 SPRINTS DETALLADOS

### SPRINT 0: Análisis y Planificación
**Fecha Inicio:** 15/09/2025  
**Fecha Fin:** 29/09/2025  
**Esfuerzo Total:** 32 horas  
**Objetivo:** Establecer fundamentos del proyecto

| Identificador | Detalle | Tipo | Esfuerzo | Prioridad |
|---------------|---------|------|----------|-----------|
| UT-01 | Requisitos del sistema | HT | 8 | Alta |
| UT-02 | Arquitectura del sistema | HT | 8 | Alta |
| UT-03 | Modelo de procesos | HT | 16 | Media |

**Entregables:**
- Documento de requisitos del sistema
- Arquitectura del sistema definida
- Modelo de procesos documentado
- Product Backlog refinado

---

### SPRINT 1: Infraestructura Base y Autenticación
**Fecha Inicio:** 29/09/2025  
**Fecha Fin:** 17/10/2025  
**Esfuerzo Total:** 40 horas  
**Objetivo:** Establecer la base técnica y sistema de autenticación

| Identificador | Detalle | Tipo | Esfuerzo | Prioridad |
|---------------|---------|------|----------|-----------|
| US-01 | Inicio de sesión | HU | 8 | Alta |
| US-02 | Asignar roles | HU | 8 | Alta |
| US-15 | Acceso por roles | HU | 8 | Alta |
| US-16 | Restablecer contraseña | HU | 8 | Media |
| US-14 | Canal de comunicación segura | HU | 8 | Alta |

**Entregables:**
- Sistema de autenticación JWT funcional
- Gestión de roles y permisos
- Restablecimiento de contraseña
- Comunicación segura implementada

---

### SPRINT 2: Base de Datos y Modelos Core
**Fecha Inicio:** 17/10/2025  
**Fecha Fin:** 31/10/2025  
**Esfuerzo Total:** 32 horas  
**Objetivo:** Diseñar e implementar la estructura de datos base

| Identificador | Detalle | Tipo | Esfuerzo | Prioridad |
|---------------|---------|------|----------|-----------|
| UT-04 | Generar texto indexado de envíos | HT | 24 | Alta |
| US-17 | Registro de logs | HU | 32 | Media |

**Entregables:**
- Modelos de base de datos implementados
- Sistema de indexación de texto para envíos
- Sistema de logging operativo

---

### SPRINT 3: CRUD Básico de Envíos
**Fecha Inicio:** 31/10/2025  
**Fecha Fin:** 14/11/2025  
**Esfuerzo Total:** 40 horas  
**Objetivo:** Funcionalidades básicas de gestión de envíos

| Identificador | Detalle | Tipo | Esfuerzo | Prioridad |
|---------------|---------|------|----------|-----------|
| US-03 | Registrar envíos | HU | 16 | Alta |
| US-04 | Actualizar envíos | HU | 8 | Alta |
| US-05 | Eliminar envíos | HU | 8 | Media |
| US-12 | Detalle de los envíos | HU | 8 | Alta |

**Entregables:**
- CRUD completo de envíos
- Validaciones y reglas de negocio
- API REST funcional para envíos

---

### SPRINT 4: Visualización y Consulta de Envíos
**Fecha Inicio:** 14/11/2025  
**Fecha Fin:** 28/11/2025  
**Esfuerzo Total:** 48 horas  
**Objetivo:** Visualización y consulta de información de envíos

| Identificador | Detalle | Tipo | Esfuerzo | Prioridad |
|---------------|---------|------|----------|-----------|
| US-06 | Visualizar envíos | HU | 32 | Alta |
| US-07 | Historial de envíos | HU | 16 | Media |

**Entregables:**
- Interfaz de visualización de envíos
- Historial completo de envíos
- Filtros y paginación

---

### SPRINT 5: Carga Masiva y Reportes
**Fecha Inicio:** 28/11/2025  
**Fecha Fin:** 12/12/2025  
**Esfuerzo Total:** 40 horas  
**Objetivo:** Importación masiva y generación de reportes

| Identificador | Detalle | Tipo | Esfuerzo | Prioridad |
|---------------|---------|------|----------|-----------|
| US-08 | Carga de envíos por archivo Excel | HU | 24 | Alta |
| US-09 | Descargar reportes de envíos | HU | 8 | Media |
| US-13 | Actualizar el estado de los envíos | HU | 16 | Media |

**Entregables:**
- Importación masiva desde Excel
- Generación de reportes en PDF/Excel
- Actualización de estados de envíos

---

### SPRINT 6: Infraestructura de Búsqueda Semántica
**Fecha Inicio:** 12/12/2025  
**Fecha Fin:** 26/12/2025  
**Esfuerzo Total:** 64 horas  
**Objetivo:** Implementar la base para búsqueda semántica

| Identificador | Detalle | Tipo | Esfuerzo | Prioridad |
|---------------|---------|------|----------|-----------|
| UT-05 | Generación de embeddings | HT | 40 | Alta |
| UT-06 | Generar texto indexado de envíos manuales | HT | 32 | Media |

**Entregables:**
- Sistema de generación de embeddings
- Indexación de texto para búsqueda semántica
- Integración con OpenAI API

---

### SPRINT 7: Búsqueda Semántica Básica
**Fecha Inicio:** 26/12/2025  
**Fecha Fin:** 09/01/2026  
**Esfuerzo Total:** 80 horas  
**Objetivo:** Implementar búsqueda semántica funcional

| Identificador | Detalle | Tipo | Esfuerzo | Prioridad |
|---------------|---------|------|----------|-----------|
| US-10 | Búsqueda semántica | HU | 80 | Alta |

**Entregables:**
- Búsqueda semántica operativa
- Interfaz de búsqueda intuitiva
- Resultados con scoring de relevancia

---

### SPRINT 8: Búsqueda Semántica Avanzada
**Fecha Inicio:** 09/01/2026  
**Fecha Fin:** 23/01/2026  
**Esfuerzo Total:** 32 horas  
**Objetivo:** Búsqueda semántica con parámetros y filtros

| Identificador | Detalle | Tipo | Esfuerzo | Prioridad |
|---------------|---------|------|----------|-----------|
| US-11 | Búsqueda semántica con parámetros | HU | 16 | Alta |
| UT-08 | Métricas de pruebas | HT | 16 | Alta |

**Entregables:**
- Búsqueda semántica con filtros avanzados
- Sistema de métricas de pruebas
- Dashboard de métricas

---

### SPRINT 9: Pruebas y Optimización
**Fecha Inicio:** 23/01/2026  
**Fecha Fin:** 31/01/2026  
**Esfuerzo Total:** 80 horas  
**Objetivo:** Pruebas, optimización y validación del sistema

| Identificador | Detalle | Tipo | Esfuerzo | Prioridad |
|---------------|---------|------|----------|-----------|
| UT-07 | Reporte de pruebas | HT | 8 | Media |
| UT-09 | Comportamiento temporal | HT | 24 | Alta |
| UT-10 | Utilización de recursos | HT | 24 | Alta |
| Validación | Validación y verificación del sistema | - | 24 | Alta |

**Entregables:**
- Reportes de pruebas completos
- Análisis de comportamiento temporal
- Optimización de recursos
- Sistema validado y verificado

---

### SPRINT 10: Cierre y Entrega
**Fecha Inicio:** 31/01/2026  
**Fecha Fin:** 02/02/2026  
**Esfuerzo Total:** 6 horas  
**Objetivo:** Finalización y entrega del proyecto

| Identificador | Detalle | Tipo | Esfuerzo | Prioridad |
|---------------|---------|------|----------|-----------|
| Cierre-01 | Pruebas de aceptación | - | 4 | Alta |
| Cierre-02 | Presentación final de la aplicación | - | 2 | Alta |

**Entregables:**
- Pruebas de aceptación completadas
- Documentación final
- Presentación del sistema

---

## 📈 DISTRIBUCIÓN DE ESFUERZO POR SPRINT

| Sprint | Nombre | Esfuerzo (horas) | Duración (días) |
|--------|--------|------------------|-----------------|
| Sprint 0 | Análisis y Planificación | 32 | 15 |
| Sprint 1 | Infraestructura Base y Autenticación | 40 | 19 |
| Sprint 2 | Base de Datos y Modelos Core | 32 | 15 |
| Sprint 3 | CRUD Básico de Envíos | 40 | 15 |
| Sprint 4 | Visualización y Consulta de Envíos | 48 | 15 |
| Sprint 5 | Carga Masiva y Reportes | 40 | 15 |
| Sprint 6 | Infraestructura de Búsqueda Semántica | 64 | 15 |
| Sprint 7 | Búsqueda Semántica Básica | 80 | 15 |
| Sprint 8 | Búsqueda Semántica Avanzada | 32 | 15 |
| Sprint 9 | Pruebas y Optimización | 80 | 9 |
| Sprint 10 | Cierre y Entrega | 6 | 3 |
| **TOTAL** | | **494** | **146** |

---

## 🔄 DEPENDENCIAS ENTRE SPRINTS

```
Sprint 0 (Análisis)
    ↓
Sprint 1 (Infraestructura Base)
    ↓
Sprint 2 (Base de Datos)
    ↓
Sprint 3 (CRUD Envíos) ──┐
    ↓                    │
Sprint 4 (Visualización) │
    ↓                    │
Sprint 5 (Carga Masiva)  │
    ↓                    │
Sprint 6 (Infraestructura Semántica)
    ↓                    │
Sprint 7 (Búsqueda Semántica Básica)
    ↓                    │
Sprint 8 (Búsqueda Semántica Avanzada)
    ↓                    │
Sprint 9 (Pruebas) ──────┘
    ↓
Sprint 10 (Cierre)
```

---

## 📋 CRITERIOS DE AGRUPACIÓN

### Por Funcionalidad Relacionada
- **Sprint 1:** Todas las historias de autenticación y seguridad
- **Sprint 3:** Operaciones CRUD básicas de envíos
- **Sprint 4:** Visualización y consulta
- **Sprint 6-8:** Búsqueda semántica (infraestructura → básica → avanzada)

### Por Dependencias Técnicas
- **Sprint 0:** Fundamentos técnicos (requisitos, arquitectura)
- **Sprint 2:** Base de datos e indexación (requerido para búsqueda)
- **Sprint 6:** Infraestructura de embeddings (requerido para búsqueda semántica)

### Por Prioridad
- Historias de **Alta prioridad** se priorizan en sprints tempranos
- Historias de **Media prioridad** se distribuyen en sprints intermedios
- Sprint 9 concentra pruebas y optimización

---

## ✅ DEFINICIÓN DE TERMINADO (DoD)

Para cada sprint, se considera completado cuando:
- ✅ Todas las historias del sprint están implementadas
- ✅ Código revisado y aprobado
- ✅ Pruebas unitarias pasando (>80% cobertura)
- ✅ Documentación actualizada
- ✅ Integración continua sin errores
- ✅ Demo realizada al Product Owner

---

## 📊 MÉTRICAS DE SEGUIMIENTO

- **Velocidad del equipo:** Esfuerzo completado por sprint
- **Burndown chart:** Seguimiento de esfuerzo restante
- **Cumplimiento de fechas:** % de sprints entregados a tiempo
- **Calidad:** Número de bugs encontrados vs. corregidos

---

**Última actualización:** 2025-01-XX  
**Versión:** 1.0


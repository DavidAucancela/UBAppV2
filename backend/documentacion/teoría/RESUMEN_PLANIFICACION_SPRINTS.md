# 📊 RESUMEN EJECUTIVO - PLANIFICACIÓN DE SPRINTS

## 📅 INFORMACIÓN GENERAL

- **Fecha Inicio Proyecto:** 15/09/2025
- **Fecha Fin Proyecto:** 02/02/2026
- **Duración Total:** 140 días (20 semanas)
- **Total de Esfuerzo:** 494 horas
- **Total de Historias:** 27 (17 HU + 10 HT)

---

## 🎯 TABLA DE SPRINTS

| Sprint | Nombre | Fecha Inicio | Fecha Fin | Duración (días) | Esfuerzo (horas) | Historias | Tipo Principal |
|--------|--------|--------------|-----------|-----------------|------------------|-----------|----------------|
| **Sprint 0** | Análisis y Planificación | 15/09/2025 | 29/09/2025 | 15 | 32 | 3 HT | Técnico |
| **Sprint 1** | Infraestructura Base y Autenticación | 29/09/2025 | 17/10/2025 | 19 | 40 | 5 HU | Funcional |
| **Sprint 2** | Base de Datos y Modelos Core | 17/10/2025 | 31/10/2025 | 15 | 32 | 1 HT + 1 HU | Técnico |
| **Sprint 3** | CRUD Básico de Envíos | 31/10/2025 | 14/11/2025 | 15 | 40 | 4 HU | Funcional |
| **Sprint 4** | Visualización y Consulta de Envíos | 14/11/2025 | 28/11/2025 | 15 | 48 | 2 HU | Funcional |
| **Sprint 5** | Carga Masiva y Reportes | 28/11/2025 | 12/12/2025 | 15 | 40 | 3 HU | Funcional |
| **Sprint 6** | Infraestructura de Búsqueda Semántica | 12/12/2025 | 26/12/2025 | 15 | 64 | 2 HT | Técnico |
| **Sprint 7** | Búsqueda Semántica Básica | 26/12/2025 | 09/01/2026 | 15 | 80 | 1 HU | Funcional |
| **Sprint 8** | Búsqueda Semántica Avanzada | 09/01/2026 | 23/01/2026 | 15 | 32 | 1 HU + 1 HT | Funcional |
| **Sprint 9** | Pruebas y Optimización | 23/01/2026 | 31/01/2026 | 9 | 80 | 3 HT + Validación | Técnico |
| **Sprint 10** | Cierre y Entrega | 31/01/2026 | 02/02/2026 | 3 | 6 | 2 Tareas | Cierre |
| **TOTAL** | | | | **146** | **494** | **27** | |

---

## 📋 DETALLE DE HISTORIAS POR SPRINT

### Sprint 0: Análisis y Planificación (32 horas)
| ID | Nombre | Tipo | Esfuerzo | Prioridad |
|----|--------|------|----------|-----------|
| UT-01 | Requisitos del sistema | HT | 8 | Alta |
| UT-02 | Arquitectura del sistema | HT | 8 | Alta |
| UT-03 | Modelo de procesos | HT | 16 | Media |

### Sprint 1: Infraestructura Base y Autenticación (40 horas)
| ID | Nombre | Tipo | Esfuerzo | Prioridad |
|----|--------|------|----------|-----------|
| US-01 | Inicio de sesión | HU | 8 | Alta |
| US-02 | Asignar roles | HU | 8 | Alta |
| US-15 | Acceso por roles | HU | 8 | Alta |
| US-16 | Restablecer contraseña | HU | 8 | Media |
| US-14 | Canal de comunicación segura | HU | 8 | Alta |

### Sprint 2: Base de Datos y Modelos Core (32 horas)
| ID | Nombre | Tipo | Esfuerzo | Prioridad |
|----|--------|------|----------|-----------|
| UT-04 | Generar texto indexado de envíos | HT | 24 | Alta |
| US-17 | Registro de logs | HU | 32 | Media |

### Sprint 3: CRUD Básico de Envíos (40 horas)
| ID | Nombre | Tipo | Esfuerzo | Prioridad |
|----|--------|------|----------|-----------|
| US-03 | Registrar envíos | HU | 16 | Alta |
| US-04 | Actualizar envíos | HU | 8 | Alta |
| US-05 | Eliminar envíos | HU | 8 | Media |
| US-12 | Detalle de los envíos | HU | 8 | Alta |

### Sprint 4: Visualización y Consulta de Envíos (48 horas)
| ID | Nombre | Tipo | Esfuerzo | Prioridad |
|----|--------|------|----------|-----------|
| US-06 | Visualizar envíos | HU | 32 | Alta |
| US-07 | Historial de envíos | HU | 16 | Media |

### Sprint 5: Carga Masiva y Reportes (40 horas)
| ID | Nombre | Tipo | Esfuerzo | Prioridad |
|----|--------|------|----------|-----------|
| US-08 | Carga de envíos por archivo Excel | HU | 24 | Alta |
| US-09 | Descargar reportes de envíos | HU | 8 | Media |
| US-13 | Actualizar el estado de los envíos | HU | 16 | Media |

### Sprint 6: Infraestructura de Búsqueda Semántica (64 horas)
| ID | Nombre | Tipo | Esfuerzo | Prioridad |
|----|--------|------|----------|-----------|
| UT-05 | Generación de embeddings | HT | 40 | Alta |
| UT-06 | Generar texto indexado de envíos manuales | HT | 32 | Media |

### Sprint 7: Búsqueda Semántica Básica (80 horas)
| ID | Nombre | Tipo | Esfuerzo | Prioridad |
|----|--------|------|----------|-----------|
| US-10 | Búsqueda semántica | HU | 80 | Alta |

### Sprint 8: Búsqueda Semántica Avanzada (32 horas)
| ID | Nombre | Tipo | Esfuerzo | Prioridad |
|----|--------|------|----------|-----------|
| US-11 | Búsqueda semántica con parámetros | HU | 16 | Alta |
| UT-08 | Métricas de pruebas | HT | 16 | Alta |

### Sprint 9: Pruebas y Optimización (80 horas)
| ID | Nombre | Tipo | Esfuerzo | Prioridad |
|----|--------|------|----------|-----------|
| UT-07 | Reporte de pruebas | HT | 8 | Media |
| UT-09 | Comportamiento temporal | HT | 24 | Alta |
| UT-10 | Utilización de recursos | HT | 24 | Alta |
| Validación | Validación y verificación del sistema | - | 24 | Alta |

### Sprint 10: Cierre y Entrega (6 horas)
| ID | Nombre | Tipo | Esfuerzo | Prioridad |
|----|--------|------|----------|-----------|
| Cierre-01 | Pruebas de aceptación | - | 4 | Alta |
| Cierre-02 | Presentación final de la aplicación | - | 2 | Alta |

---

## 📈 DISTRIBUCIÓN DE ESFUERZO

### Por Tipo de Historia
- **Historias de Usuario (HU):** 296 horas (60%)
- **Historias Técnicas (HT):** 200 horas (40%)

### Por Prioridad
- **Alta:** 376 horas (76%)
- **Media:** 120 horas (24%)

### Por Fase del Proyecto
- **Fase Inicial (Sprints 0-2):** 104 horas (21%)
- **Fase Desarrollo Core (Sprints 3-5):** 128 horas (26%)
- **Fase Búsqueda Semántica (Sprints 6-8):** 176 horas (36%)
- **Fase Finalización (Sprints 9-10):** 86 horas (17%)

---

## 🔄 HITOS PRINCIPALES

| Hito | Fecha | Sprint | Descripción |
|------|-------|--------|-------------|
| **Hito 1: Fundamentos** | 29/09/2025 | Sprint 0 | Arquitectura y requisitos definidos |
| **Hito 2: Autenticación** | 17/10/2025 | Sprint 1 | Sistema de autenticación operativo |
| **Hito 3: CRUD Completo** | 14/11/2025 | Sprint 3 | Gestión básica de envíos funcional |
| **Hito 4: Visualización** | 28/11/2025 | Sprint 4 | Interfaz de visualización completa |
| **Hito 5: Carga Masiva** | 12/12/2025 | Sprint 5 | Importación masiva operativa |
| **Hito 6: Infraestructura IA** | 26/12/2025 | Sprint 6 | Sistema de embeddings implementado |
| **Hito 7: Búsqueda Semántica** | 09/01/2026 | Sprint 7 | Búsqueda semántica básica funcional |
| **Hito 8: Búsqueda Avanzada** | 23/01/2026 | Sprint 8 | Búsqueda con parámetros operativa |
| **Hito 9: Sistema Validado** | 31/01/2026 | Sprint 9 | Sistema probado y optimizado |
| **Hito 10: Entrega Final** | 02/02/2026 | Sprint 10 | Proyecto completado y entregado |

---

## ⚠️ RIESGOS Y CONSIDERACIONES

### Riesgos Identificados
1. **Sprint 7 (Búsqueda Semántica):** Esfuerzo alto (80h) - Requiere monitoreo cercano
2. **Sprint 9 (Pruebas):** Múltiples actividades técnicas - Requiere coordinación
3. **Dependencias:** Búsqueda semántica depende de infraestructura previa

### Recomendaciones
- Realizar daily standups para identificar bloqueos temprano
- Buffer de tiempo en Sprint 7 para imprevistos
- Revisión continua de dependencias entre sprints
- Pruebas incrementales desde Sprint 3

---

**Versión:** 1.0  
**Fecha:** 2025-01-XX


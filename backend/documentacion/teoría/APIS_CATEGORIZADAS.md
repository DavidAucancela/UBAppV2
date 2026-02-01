# 📚 APIs del Backend - Documentación Completa

**Última actualización**: 27 de Enero, 2026  
**Total de endpoints documentados**: 100+

---

## 🔐 1. Autenticación y Tokens

### Base URL: `/api/token/`

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| POST | `/api/token/` | Obtener token de acceso (login) | No requerida |
| POST | `/api/token/refresh/` | Refrescar token de acceso | No requerida |

---

## 🏥 2. Health Check

### Base URL: `/api/health/`

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/health/health/` | Verificar estado del sistema (DB, cache) | No requerida |

---

## 👥 3. Usuarios

### Base URL: `/api/usuarios/`

#### Autenticación y Registro
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| POST | `/api/usuarios/auth/login/` | Iniciar sesión | No requerida |
| POST | `/api/usuarios/auth/logout/` | Cerrar sesión | Requerida |
| POST | `/api/usuarios/auth/register/` | Registrar comprador | No requerida |
| POST | `/api/usuarios/auth/reset-password/` | Solicitar restablecimiento de contraseña | No requerida |
| POST | `/api/usuarios/auth/verify-email/` | Verificar si un correo existe | No requerida |

#### Gestión de Usuarios (CRUD)
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/usuarios/` | Listar usuarios | Autenticado |
| POST | `/api/usuarios/` | Crear usuario | Solo Admin |
| GET | `/api/usuarios/{id}/` | Obtener usuario | Autenticado |
| PUT/PATCH | `/api/usuarios/{id}/` | Actualizar usuario | Autenticado |
| DELETE | `/api/usuarios/{id}/` | Eliminar usuario | Solo Admin |

#### Acciones Personalizadas de Usuarios
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/usuarios/perfil/` | Obtener perfil del usuario actual | Autenticado |
| PUT/PATCH | `/api/usuarios/actualizar_perfil/` | Actualizar perfil del usuario actual | Autenticado |
| POST | `/api/usuarios/cambiar_password/` | Cambiar contraseña del usuario actual | Autenticado |
| POST | `/api/usuarios/{id}/activar_desactivar/` | Activar/desactivar usuario | Admin/Gerente |
| GET | `/api/usuarios/compradores/` | Listar solo compradores | Autenticado |
| GET | `/api/usuarios/por_rol/?rol={rol}` | Filtrar usuarios por rol | Autenticado |
| GET | `/api/usuarios/estadisticas/` | Estadísticas de usuarios por rol | Admin/Gerente |
| GET | `/api/usuarios/mapa_compradores/?ciudad={ciudad}` | Compradores con ubicación para mapa | Autenticado |
| GET | `/api/usuarios/{id}/envios_comprador/` | Envíos de un comprador específico | Autenticado |
| GET | `/api/usuarios/dashboard_usuario/?anio={anio}` | Dashboard del usuario con estadísticas | Autenticado |
| GET | `/api/usuarios/mis_envios/?estado={estado}&fecha_desde={fecha}&fecha_hasta={fecha}` | Envíos del usuario actual | Autenticado |
| GET | `/api/usuarios/estadisticas_cupo/?anio={anio}` | Estadísticas del cupo anual | Autenticado |

#### Ubicaciones
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/usuarios/ubicaciones/provincias/` | Obtener provincias de Ecuador | No requerida |
| GET | `/api/usuarios/ubicaciones/cantones/?provincia={provincia}` | Obtener cantones por provincia | No requerida |
| GET | `/api/usuarios/ubicaciones/ciudades/?canton={canton}` | Obtener ciudades por cantón | No requerida |
| GET | `/api/usuarios/ubicaciones/coordenadas/?ciudad={ciudad}` | Obtener coordenadas de una ciudad | No requerida |

---

## 📦 4. Envíos

### Base URL: `/api/envios/envios/`

#### CRUD de Envíos
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/envios/envios/` | Listar envíos | Autenticado |
| POST | `/api/envios/envios/` | Crear envío | Autenticado |
| GET | `/api/envios/envios/{id}/` | Obtener envío | Autenticado |
| PUT/PATCH | `/api/envios/envios/{id}/` | Actualizar envío | Autenticado |
| DELETE | `/api/envios/envios/{id}/` | Eliminar envío | Autenticado |

#### Acciones Personalizadas de Envíos
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| POST | `/api/envios/envios/{id}/cambiar_estado/` | Cambiar estado del envío | Autenticado |
| GET | `/api/envios/envios/mis_envios/` | Envíos del usuario actual (comprador) | Solo Comprador |
| GET | `/api/envios/envios/por_estado/?estado={estado}` | Filtrar envíos por estado | Autenticado |
| GET | `/api/envios/envios/estadisticas/` | Estadísticas de envíos | Admin/Gerente/Digitador |
| POST | `/api/envios/envios/calcular_costo/` | Calcular costo sin crear envío | Autenticado |
| GET | `/api/envios/envios/exportar/?formato={excel\|csv\|pdf}&estado={estado}` | Exportar envíos | Autenticado |
| GET | `/api/envios/envios/{id}/comprobante/` | Generar comprobante PDF | Autenticado |

**Filtros disponibles:**
- `?estado={estado}` - Filtrar por estado
- `?comprador={id}` - Filtrar por comprador
- `?search={termino}` - Búsqueda en HAWB y nombre del comprador
- `?ordering={campo}` - Ordenar por fecha_emision, valor_total, peso_total

---

## 🛍️ 5. Productos

### Base URL: `/api/envios/productos/`

#### CRUD de Productos
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/envios/productos/` | Listar productos | Autenticado |
| POST | `/api/envios/productos/` | Crear producto | Autenticado |
| GET | `/api/envios/productos/{id}/` | Obtener producto | Autenticado |
| PUT/PATCH | `/api/envios/productos/{id}/` | Actualizar producto | Autenticado |
| DELETE | `/api/envios/productos/{id}/` | Eliminar producto | Autenticado |

#### Acciones Personalizadas de Productos
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/envios/productos/por_categoria/?categoria={categoria}` | Filtrar productos por categoría | Autenticado |
| GET | `/api/envios/productos/estadisticas/` | Estadísticas de productos | Admin/Gerente/Digitador |

**Filtros disponibles:**
- `?categoria={categoria}` - Filtrar por categoría
- `?envio={id}` - Filtrar por envío
- `?search={termino}` - Búsqueda en descripción y HAWB del envío
- `?ordering={campo}` - Ordenar por descripcion, valor, peso

---

## 💰 6. Tarifas

### Base URL: `/api/envios/tarifas/`

#### CRUD de Tarifas
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/envios/tarifas/` | Listar tarifas | Autenticado |
| POST | `/api/envios/tarifas/` | Crear tarifa | Autenticado |
| GET | `/api/envios/tarifas/{id}/` | Obtener tarifa | Autenticado |
| PUT/PATCH | `/api/envios/tarifas/{id}/` | Actualizar tarifa | Autenticado |
| DELETE | `/api/envios/tarifas/{id}/` | Eliminar tarifa | Autenticado |

#### Acciones Personalizadas de Tarifas
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/envios/tarifas/por_categoria/?categoria={categoria}` | Obtener tarifas activas por categoría | Autenticado |
| POST | `/api/envios/tarifas/buscar_tarifa/` | Buscar tarifa aplicable (categoría y peso) | Autenticado |

**Filtros disponibles:**
- `?categoria={categoria}` - Filtrar por categoría
- `?activa={true\|false}` - Filtrar por estado activo
- `?ordering={campo}` - Ordenar por categoria, peso_minimo, precio_por_kg

---

## 📊 7. Importación Excel

### Base URL: `/api/envios/importaciones-excel/`

#### CRUD de Importaciones
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/envios/importaciones-excel/` | Listar importaciones | Autenticado |
| POST | `/api/envios/importaciones-excel/` | Subir archivo Excel | Autenticado |
| GET | `/api/envios/importaciones-excel/{id}/` | Obtener importación | Autenticado |
| PUT/PATCH | `/api/envios/importaciones-excel/{id}/` | Actualizar importación | Autenticado |
| DELETE | `/api/envios/importaciones-excel/{id}/` | Eliminar importación | Autenticado |

#### Acciones Personalizadas de Importaciones
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/envios/importaciones-excel/{id}/preview/?limite={limite}` | Vista previa del archivo Excel | Autenticado |
| POST | `/api/envios/importaciones-excel/{id}/validar/` | Validar datos del archivo | Autenticado |
| POST | `/api/envios/importaciones-excel/{id}/procesar/` | Procesar e importar datos | Autenticado |
| GET | `/api/envios/importaciones-excel/{id}/reporte_errores/` | Generar reporte de errores | Autenticado |
| GET | `/api/envios/importaciones-excel/estadisticas/` | Estadísticas de importaciones | Autenticado |

**Filtros disponibles:**
- `?estado={estado}` - Filtrar por estado (pendiente, validando, validado, procesando, completado, error)
- `?usuario={id}` - Filtrar por usuario
- `?ordering={campo}` - Ordenar por fecha_creacion, fecha_completado

---

## 🔍 8. Búsqueda

### Base URL: `/api/busqueda/`

#### Búsqueda Tradicional
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/busqueda/buscar/?q={termino}&tipo={general\|usuarios\|envios\|productos}` | Búsqueda tradicional | Autenticado |
| GET | `/api/busqueda/historial/` | Historial de búsquedas | Autenticado |
| DELETE | `/api/busqueda/limpiar_historial/` | Limpiar historial | Autenticado |
| GET | `/api/busqueda/estadisticas/` | Estadísticas de búsquedas | Autenticado |

#### Búsqueda Semántica
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| POST | `/api/busqueda/semantica/` | Búsqueda semántica de envíos | Autenticado |
| GET | `/api/busqueda/semantica/sugerencias/?q={termino}` | Obtener sugerencias | Autenticado |
| GET | `/api/busqueda/semantica/historial/` | Historial de búsquedas semánticas | Autenticado |
| POST | `/api/busqueda/semantica/historial/` | Guardar búsqueda en historial | Autenticado |
| DELETE | `/api/busqueda/semantica/historial/` | Limpiar historial semántico | Autenticado |
| GET | `/api/busqueda/semantica/metricas/` | Métricas de búsquedas semánticas | Autenticado |
| GET | `/api/busqueda/semantica/estadisticas-embeddings/` | Estadísticas de embeddings de envíos | Autenticado |
| POST | `/api/busqueda/semantica/generar-embeddings/` | Generar embeddings pendientes | Autenticado |
| GET | `/api/busqueda/semantica/analisis-metricas/` | Análisis comparativo de métricas | Autenticado |
| GET | `/api/busqueda/{id}/descargar-pdf/` | Descargar PDF de búsqueda tradicional | Autenticado |
| GET | `/api/busqueda/semantica/{busqueda_id}/descargar-pdf/` | Descargar PDF de búsqueda semántica | Autenticado |

**Ejemplo de búsqueda semántica:**
```json
POST /api/busqueda/semantica/
{
  "texto": "envíos entregados en Quito la semana pasada",
  "limite": 20,
  "filtrosAdicionales": {
    "fechaDesde": "2025-01-01",
    "estado": "entregado",
    "ciudadDestino": "Quito"
  }
}
```

---

## 🔔 9. Notificaciones

### Base URL: `/api/notificaciones/`

#### CRUD de Notificaciones
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/notificaciones/` | Listar notificaciones del usuario | Autenticado |
| GET | `/api/notificaciones/{id}/` | Obtener notificación | Autenticado |
| DELETE | `/api/notificaciones/{id}/` | Eliminar notificación | Autenticado |

#### Acciones Personalizadas de Notificaciones
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/notificaciones/contador/` | Contador de notificaciones no leídas | Autenticado |
| PATCH | `/api/notificaciones/{id}/marcar-leida/` | Marcar notificación como leída | Autenticado |
| POST | `/api/notificaciones/marcar-todas-leidas/` | Marcar todas como leídas | Autenticado |

---

## 📊 10. Métricas

### Base URL: `/api/metricas/`

#### Pruebas Controladas Semánticas
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/metricas/pruebas-controladas/` | Listar pruebas controladas | Autenticado |
| POST | `/api/metricas/pruebas-controladas/` | Crear prueba controlada | Autenticado |
| GET | `/api/metricas/pruebas-controladas/{id}/` | Obtener prueba controlada | Autenticado |
| PUT/PATCH | `/api/metricas/pruebas-controladas/{id}/` | Actualizar prueba controlada | Autenticado |
| DELETE | `/api/metricas/pruebas-controladas/{id}/` | Eliminar prueba controlada | Autenticado |
| POST | `/api/metricas/pruebas-controladas/{id}/ejecutar/` | Ejecutar prueba controlada | Solo Admin |

**Filtros disponibles:**
- `?activa={true\|false}` - Filtrar por estado activo

#### Métricas Semánticas
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/metricas/metricas-semanticas/` | Listar métricas semánticas | Autenticado |
| GET | `/api/metricas/metricas-semanticas/{id}/` | Obtener métrica semántica | Autenticado |
| GET | `/api/metricas/metricas-semanticas/estadisticas/?fecha_desde={fecha}&fecha_hasta={fecha}` | Estadísticas agregadas | Autenticado |

**Filtros disponibles:**
- `?fecha_desde={fecha}` - Filtrar desde fecha
- `?fecha_hasta={fecha}` - Filtrar hasta fecha

#### Registros de Generación de Embeddings
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/metricas/registros-embedding/` | Listar registros de embeddings | Autenticado |
| GET | `/api/metricas/registros-embedding/{id}/` | Obtener registro de embedding | Autenticado |
| GET | `/api/metricas/registros-embedding/estadisticas/` | Estadísticas de generación | Autenticado |

**Filtros disponibles:**
- `?estado={estado}` - Filtrar por estado
- `?tipo_proceso={tipo}` - Filtrar por tipo de proceso

#### Pruebas de Carga
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/metricas/pruebas-carga/` | Listar pruebas de carga | Autenticado |
| POST | `/api/metricas/pruebas-carga/` | Crear prueba de carga | Autenticado |
| GET | `/api/metricas/pruebas-carga/{id}/` | Obtener prueba de carga | Autenticado |
| PUT/PATCH | `/api/metricas/pruebas-carga/{id}/` | Actualizar prueba de carga | Autenticado |
| DELETE | `/api/metricas/pruebas-carga/{id}/` | Eliminar prueba de carga | Autenticado |
| POST | `/api/metricas/pruebas-carga/ejecutar_busqueda/` | Ejecutar prueba de carga de búsqueda | Solo Admin |

**Filtros disponibles:**
- `?tipo_prueba={tipo}` - Filtrar por tipo de prueba
- `?nivel_carga={nivel}` - Filtrar por nivel de carga
- `?fecha_desde={fecha}` - Filtrar desde fecha
- `?fecha_hasta={fecha}` - Filtrar hasta fecha

#### Métricas de Rendimiento
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/metricas/metricas-rendimiento/` | Listar métricas de rendimiento | Autenticado |
| GET | `/api/metricas/metricas-rendimiento/{id}/` | Obtener métrica de rendimiento | Autenticado |
| GET | `/api/metricas/metricas-rendimiento/estadisticas/?proceso={proceso}&nivel_carga={nivel}` | Estadísticas de rendimiento | Autenticado |

**Filtros disponibles:**
- `?proceso={proceso}` - Filtrar por proceso
- `?nivel_carga={nivel}` - Filtrar por nivel de carga
- `?fecha_desde={fecha}` - Filtrar desde fecha
- `?fecha_hasta={fecha}` - Filtrar hasta fecha

#### Registros Manuales de Envíos
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/metricas/registros-manuales/` | Listar registros manuales | Autenticado |
| POST | `/api/metricas/registros-manuales/` | Crear registro manual | Autenticado |
| GET | `/api/metricas/registros-manuales/{id}/` | Obtener registro manual | Autenticado |
| PUT/PATCH | `/api/metricas/registros-manuales/{id}/` | Actualizar registro manual | Autenticado |
| DELETE | `/api/metricas/registros-manuales/{id}/` | Eliminar registro manual | Autenticado |
| POST | `/api/metricas/registros-manuales/registrar/` | Registrar tiempo de registro manual | Autenticado |
| GET | `/api/metricas/registros-manuales/estadisticas/` | Estadísticas de registros manuales | Autenticado |

#### Exportación de Métricas
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/metricas/exportacion/metricas_semanticas/?fecha_desde={fecha}&fecha_hasta={fecha}` | Exportar métricas semánticas a CSV | Solo Admin |
| GET | `/api/metricas/exportacion/metricas_rendimiento/?fecha_desde={fecha}&fecha_hasta={fecha}` | Exportar métricas de rendimiento a CSV | Solo Admin |
| GET | `/api/metricas/exportacion/pruebas_carga/` | Exportar pruebas de carga a CSV | Solo Admin |

#### Pruebas del Sistema
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| POST | `/api/metricas/pruebas-sistema/ejecutar_rendimiento/` | Ejecutar pruebas de rendimiento (versión rápida) | Solo Admin |
| POST | `/api/metricas/pruebas-sistema/ejecutar_tests/` | Ejecutar tests unitarios del sistema | Solo Admin |
| GET | `/api/metricas/pruebas-sistema/listar_tests/` | Listar todos los tests disponibles | Solo Admin |
| GET | `/api/metricas/pruebas-sistema/estadisticas_pruebas/` | Estadísticas de las últimas pruebas | Solo Admin |
| GET | `/api/metricas/pruebas-sistema/pruebas_rendimiento_guardadas/` | Listar pruebas de rendimiento guardadas | Solo Admin |
| GET | `/api/metricas/pruebas-sistema/{id}/detalle_prueba_rendimiento/` | Detalle completo de una prueba | Solo Admin |
| GET | `/api/metricas/pruebas-sistema/detalles_procesos/?codigo_proceso={codigo}&prueba_id={id}` | Detalles de procesos de rendimiento | Solo Admin |
| POST | `/api/metricas/pruebas-sistema/ejecutar_rendimiento_completo/` | Ejecutar pruebas de rendimiento completas (ISO 25010) | Solo Admin |

---

## 📖 11. Documentación API

### Base URL: `/api/`

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/schema/` | Esquema OpenAPI | No requerida |
| GET | `/api/docs/` | Documentación Swagger UI | No requerida |
| GET | `/api/redoc/` | Documentación ReDoc | No requerida |
| GET | `/api/schema/swagger-ui/` | Swagger UI alternativo | No requerida |

---

## 🔑 12. Permisos y Roles

### Roles del Sistema:
1. **Admin (rol=1)**: Acceso completo al sistema
2. **Gerente (rol=2)**: Puede ver todos excepto admins
3. **Digitador (rol=3)**: Puede ver todos los envíos y productos
4. **Comprador (rol=4)**: Solo puede ver sus propios envíos y productos

### Autenticación:
- Todas las APIs requieren autenticación JWT excepto las marcadas como "No requerida"
- Incluir el token en el header: `Authorization: Bearer {token}`
- Obtener token mediante: `POST /api/token/` con `username` y `password`

---

## 📝 Notas Importantes

1. **Paginación**: La mayoría de endpoints de listado están paginados (10 elementos por página por defecto)
2. **Filtros**: Muchos endpoints soportan filtros mediante query parameters
3. **Búsqueda**: Varios endpoints tienen búsqueda integrada con el parámetro `search`
4. **Ordenamiento**: Se puede ordenar con el parámetro `ordering`
5. **Formato de Fechas**: Usar formato ISO 8601 (YYYY-MM-DD)
6. **Exportación**: Los envíos se pueden exportar en Excel, CSV o PDF
7. **Importación**: Se puede importar envíos desde archivos Excel con validación previa

---

## 🚀 Ejemplos de Uso

### Login
```bash
POST /api/token/
{
  "username": "usuario",
  "password": "contraseña"
}
```

### Crear Envío
```bash
POST /api/envios/envios/
Authorization: Bearer {token}
{
  "hawb": "HAWB123456",
  "comprador": 1,
  "peso_total": 10.5,
  "valor_total": 150.00,
  "estado": "pendiente",
  "productos": [
    {
      "descripcion": "Producto ejemplo",
      "categoria": "electronica",
      "peso": 5.0,
      "cantidad": 2,
      "valor": 75.00
    }
  ]
}
```

### Búsqueda Semántica
```bash
POST /api/busqueda/semantica/
Authorization: Bearer {token}
{
  "texto": "envíos pesados de electrónicos",
  "limite": 10,
  "filtrosAdicionales": {
    "estado": "en_transito"
  }
}
```

---

---

## 📋 Resumen de Endpoints por Categoría

| Categoría | Cantidad | Base URL |
|-----------|----------|----------|
| Autenticación y Tokens | 2 | `/api/token/` |
| Health Check | 1 | `/api/health/` |
| Usuarios | 20+ | `/api/usuarios/` |
| Envíos | 10+ | `/api/envios/envios/` |
| Productos | 8+ | `/api/envios/productos/` |
| Tarifas | 8+ | `/api/envios/tarifas/` |
| Importación Excel | 10+ | `/api/envios/importaciones-excel/` |
| Búsqueda | 15+ | `/api/busqueda/` |
| Notificaciones | 6+ | `/api/notificaciones/` |
| Métricas | 30+ | `/api/metricas/` |
| Documentación API | 4 | `/api/` |
| **TOTAL** | **100+** | - |

---

## 📝 Notas Adicionales

### Endpoints de Búsqueda Semántica
- La búsqueda semántica utiliza embeddings de OpenAI
- Modelos disponibles: `text-embedding-3-small`, `text-embedding-3-large`, `text-embedding-ada-002`
- Rate limit: 30 búsquedas/minuto debido al costo de OpenAI
- Los embeddings se generan automáticamente o manualmente mediante el endpoint correspondiente

### Endpoints de Exportación
- Los envíos se pueden exportar en formato Excel (.xlsx), CSV o PDF
- Las métricas se pueden exportar en formato CSV
- Los comprobantes de envíos se generan en formato PDF

### Endpoints de Pruebas y Métricas
- Los endpoints de pruebas requieren permisos de administrador
- Las pruebas de rendimiento pueden tardar varios minutos
- Los resultados se guardan automáticamente para análisis posterior

### Paginación
- La mayoría de endpoints de listado están paginados (10 elementos por página por defecto)
- Se puede ajustar con parámetros `?page={numero}` y `?page_size={tamaño}`

### Filtros Comunes
- `?search={termino}` - Búsqueda general
- `?ordering={campo}` - Ordenamiento (prefijo `-` para descendente)
- `?page={numero}` - Número de página
- `?page_size={tamaño}` - Tamaño de página

---

**Última actualización**: 27 de Enero, 2026  
**Generado desde**: Código fuente del backend (urls.py, views.py)



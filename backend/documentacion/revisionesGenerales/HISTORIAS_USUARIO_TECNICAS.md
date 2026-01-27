# 📖 HISTORIAS DE USUARIO E HISTORIAS TÉCNICAS

## 📌 INFORMACIÓN GENERAL

**Sistema:** Sistema de Gestión de Envíos con Búsqueda Semántica  
**Versión del Documento:** 2.0  
**Fecha:** Enero 2026  
**Alcance:** MVP (Minimum Viable Product)

---

## ✅ DEFINICIÓN DE "DONE"

Una historia se considera **completa (Done)** cuando cumple con todos los siguientes criterios:

1. **Código implementado:** El código está escrito, revisado y cumple con los estándares de calidad establecidos.
2. **Pruebas realizadas:** Se han ejecutado pruebas unitarias y de integración, y todas pasan exitosamente.
3. **Criterios de aceptación cumplidos:** Todos los criterios de aceptación de la historia han sido validados.
4. **Documentación actualizada:** La documentación técnica y de usuario ha sido actualizada si es necesario.
5. **Revisión de código:** El código ha sido revisado por al menos otro desarrollador.
6. **Sin errores críticos:** No existen errores críticos o bloqueantes en la funcionalidad implementada.
7. **Integración completa:** La funcionalidad está integrada correctamente con el resto del sistema.
8. **Desplegado en ambiente de pruebas:** La funcionalidad está disponible en el ambiente de pruebas para validación.

---

## 👤 HISTORIAS DE USUARIO

### Resumen de Historias de Usuario

| Identificador | Nombre de la historia | Prioridad | Esfuerzo (horas) |
|---|---|---|---|
| US-01 | Inicio de sesión | Alta | 8 |
| US-02 | Asignar roles | Alta | 8 |
| US-03 | Registrar envíos | Alta | 16 |
| US-04 | Actualizar envíos | Alta | 8 |
| US-05 | Eliminar envíos | Media | 8 |
| US-06 | Visualizar envíos | Alta | 32 |
| US-07 | Historial de envíos | Media | 16 |
| US-08 | Carga de envíos por archivo Excel | Alta | 24 |
| US-09 | Descargar reportes de envíos | Media | 8 |
| US-10 | Búsqueda semántica | Alta | 80 |
| US-11 | Búsqueda semántica con parámetros | Alta | 16 |
| US-12 | Detalle de los envíos | Alta | 8 |
| US-13 | Actualizar el estado de los envíos | Media | 16 |
| US-14 | Canal de comunicación segura | Alta | 8 |
| US-15 | Acceso por roles | Alta | 8 |
| US-16 | Restablecer contraseña | Media | 8 |
| US-17 | Registro de logs | Media | 32 |
| **Total** | **17 historias de usuario** | | **296 horas** |

---

### EPIC-01: Autenticación y Gestión de Usuarios

#### US-01: Inicio de sesión
**Tipo:** Usuario  
**Descripción:** Como **usuario** quiero **iniciar sesión en el sistema** para **acceder a mis funcionalidades según mi rol**.  
**Prioridad:** Alta  
**Esfuerzo:** 8 horas

**Criterios de Aceptación:**
1. El sistema permite iniciar sesión con username y contraseña.
2. El sistema retorna tokens JWT (access token y refresh token) al autenticarse exitosamente.
3. El sistema bloquea el acceso después de 5 intentos fallidos por 15 minutos.
4. El sistema muestra mensajes de error apropiados (credenciales inválidas, cuenta bloqueada, usuario desactivado).
5. El sistema valida que el usuario esté activo antes de permitir el inicio de sesión.
6. El sistema registra todos los intentos de inicio de sesión (exitosos y fallidos) en logs.

---

#### US-02: Asignar roles
**Tipo:** Usuario  
**Descripción:** Como **administrador** quiero **asignar roles a usuarios** para **controlar el acceso y permisos en el sistema**.  
**Prioridad:** Alta  
**Esfuerzo:** 8 horas

**Criterios de Aceptación:**
1. El sistema permite asignar roles durante la creación o actualización de usuarios.
2. El sistema define cuatro roles: Administrador (rol=1), Gerente (rol=2), Digitador (rol=3), y Comprador (rol=4).
3. El sistema valida que solo usuarios con rol de Administrador puedan asignar roles de Administrador.
4. El sistema proporciona métodos de consulta para verificar el rol de un usuario.
5. El sistema permite filtrar usuarios por rol mediante endpoints específicos.
6. El sistema registra los cambios de rol en el log de auditoría.

---

#### US-15: Acceso por roles
**Tipo:** Usuario  
**Descripción:** Como **sistema** quiero **restringir el acceso según el rol del usuario** para **garantizar la seguridad y privacidad de la información**.  
**Prioridad:** Alta  
**Esfuerzo:** 8 horas

**Criterios de Aceptación:**
1. El sistema implementa control de acceso basado en roles (RBAC).
2. **Administrador (rol=1):** Acceso completo a todas las funcionalidades del sistema.
3. **Gerente (rol=2):** Acceso a gestión de usuarios (excepto administradores), visualización de todos los envíos, estadísticas generales, y reportes.
4. **Digitador (rol=3):** Acceso a visualización de compradores y otros digitadores, gestión completa de envíos y productos, y estadísticas de envíos.
5. **Comprador (rol=4):** Acceso limitado a gestión de su propio perfil, visualización de sus propios envíos, y gestión de productos en sus envíos.
6. El sistema valida permisos en cada endpoint antes de procesar la solicitud.
7. El sistema retorna mensajes de error apropiados (403 Forbidden) cuando un usuario intenta acceder a funcionalidades no permitidas.

---

#### US-16: Restablecer contraseña
**Tipo:** Usuario  
**Descripción:** Como **usuario** quiero **restablecer mi contraseña** para **poder acceder al sistema si la olvidé**.  
**Prioridad:** Media  
**Esfuerzo:** 8 horas

**Criterios de Aceptación:**
1. El sistema permite solicitar restablecimiento de contraseña mediante correo electrónico.
2. El sistema valida que el correo electrónico exista en el sistema antes de enviar el enlace.
3. El sistema genera enlaces de recuperación con tokens seguros y expiración temporal (24 horas).
4. El sistema envía correo electrónico con enlace de recuperación.
5. El sistema permite establecer nueva contraseña mediante el enlace de recuperación.
6. El sistema valida que la nueva contraseña cumpla con los requisitos de seguridad (mínimo 8 caracteres, mayúsculas, minúsculas, números y caracteres especiales).

---

#### US-17: Registro de logs
**Tipo:** Usuario  
**Descripción:** Como **administrador** quiero **tener registro de logs de todas las operaciones** para **auditar y rastrear actividades en el sistema**.  
**Prioridad:** Media  
**Esfuerzo:** 32 horas

**Criterios de Aceptación:**
1. El sistema registra logs de todas las operaciones importantes (creación, modificación, eliminación de entidades).
2. El sistema utiliza niveles de log apropiados (DEBUG, INFO, WARNING, ERROR, CRITICAL).
3. El sistema formatea logs de forma estructurada (JSON preferiblemente).
4. El sistema permite filtrar y buscar en logs.
5. El sistema rota logs para evitar llenar el disco.
6. El sistema registra: usuario, operación, entidad, fecha/hora, detalles adicionales.
7. El sistema registra intentos de inicio de sesión (exitosos y fallidos).
8. El sistema registra cambios de estado de envíos.
9. El sistema registra importaciones de archivos Excel.

---

### EPIC-02: Gestión de Envíos

#### US-03: Registrar envíos
**Tipo:** Usuario  
**Descripción:** Como **digitador o comprador** quiero **registrar un nuevo envío** para **documentar un envío con sus productos asociados**.  
**Prioridad:** Alta  
**Esfuerzo:** 16 horas

**Criterios de Aceptación:**
1. El sistema permite crear envíos con número único de guía aérea (HAWB).
2. El sistema valida que el HAWB sea único en el sistema.
3. El sistema asocia cada envío a un comprador específico.
4. El sistema permite registrar observaciones y fecha de emisión.
5. El sistema calcula automáticamente totales (peso, cantidad, valor) basándose en productos asociados.
6. El sistema calcula automáticamente el costo del servicio según tarifas aplicables.
7. El sistema valida que el comprador no exceda su cupo anual al crear un envío.
8. El sistema genera automáticamente un embedding para búsqueda semántica cuando se crea un envío.

---

#### US-04: Actualizar envíos
**Tipo:** Usuario  
**Descripción:** Como **digitador o comprador** quiero **actualizar un envío** para **modificar su información o productos asociados**.  
**Prioridad:** Alta  
**Esfuerzo:** 8 horas

**Criterios de Aceptación:**
1. El sistema permite actualizar información de envíos (parcial o completa).
2. El sistema valida permisos: compradores solo pueden modificar sus propios envíos.
3. El sistema recalcula automáticamente totales cuando se modifican productos asociados.
4. El sistema recalcula el costo del servicio cuando cambian productos o tarifas.
5. El sistema actualiza el embedding semántico cuando se modifica información relevante del envío.
6. El sistema registra la actualización en el log de auditoría.

---

#### US-05: Eliminar envíos
**Tipo:** Usuario  
**Descripción:** Como **digitador o administrador** quiero **eliminar un envío** para **remover envíos incorrectos o duplicados**.  
**Prioridad:** Media  
**Esfuerzo:** 8 horas

**Criterios de Aceptación:**
1. El sistema permite eliminar envíos (eliminación lógica o física según configuración).
2. El sistema valida permisos antes de permitir la eliminación.
3. El sistema muestra confirmación antes de eliminar.
4. El sistema elimina o desactiva los productos asociados al envío.
5. El sistema registra la eliminación en el log de auditoría.

---

#### US-06: Visualizar envíos
**Tipo:** Usuario  
**Descripción:** Como **usuario autenticado** quiero **visualizar envíos** para **ver los envíos disponibles según mis permisos**.  
**Prioridad:** Alta  
**Esfuerzo:** 32 horas

**Criterios de Aceptación:**
1. El sistema lista envíos con paginación (10 elementos por página por defecto).
2. El sistema aplica filtros automáticos según el rol: compradores solo ven sus envíos, otros roles ven todos los envíos.
3. El sistema permite ordenar por fecha, estado, valor, peso.
4. El sistema muestra información resumida: HAWB, comprador, estado, fecha, totales, cantidad de productos.
5. El sistema permite filtrar por estado (pendiente, en tránsito, entregado, cancelado, etc.).
6. El sistema permite filtrar por rango de fechas (fecha desde, fecha hasta).
7. El sistema permite filtrar por cliente/comprador (nombre, cédula, correo).
8. El sistema permite filtrar por ubicación (provincia, cantón, ciudad).
9. El sistema permite filtrar por número de guía (HAWB).
10. El sistema permite combinar múltiples filtros simultáneamente.
11. El sistema permite búsqueda por texto libre que busque en múltiples campos.

---

#### US-07: Historial de envíos
**Tipo:** Usuario  
**Descripción:** Como **usuario autenticado** quiero **consultar el historial de envíos** para **ver el registro de cambios y estados anteriores**.  
**Prioridad:** Media  
**Esfuerzo:** 16 horas

**Criterios de Aceptación:**
1. El sistema permite consultar el historial de cambios de un envío específico.
2. El sistema muestra historial de cambios de estado con fecha, hora y usuario que realizó el cambio.
3. El sistema muestra observaciones asociadas a cada cambio de estado.
4. El sistema permite filtrar el historial por tipo de cambio (estado, productos, información general).
5. El sistema muestra el historial ordenado cronológicamente (más reciente primero).

---

#### US-08: Carga de envíos por archivo Excel
**Tipo:** Usuario  
**Descripción:** Como **digitador o administrador** quiero **cargar un archivo Excel** para **importar múltiples envíos de forma masiva**.  
**Prioridad:** Alta  
**Esfuerzo:** 24 horas

**Criterios de Aceptación:**
1. El sistema permite cargar archivos en formato .xlsx y .xls.
2. El sistema valida el tamaño máximo del archivo (15 MB).
3. El sistema valida la estructura del archivo (columnas requeridas, formato de datos).
4. El sistema procesa el archivo y extrae información de envíos y productos.
5. El sistema muestra un resumen previo de los datos a importar antes de confirmar.
6. El sistema reporta errores de validación de forma clara y específica.
7. El sistema valida que el archivo tenga las columnas requeridas.
8. El sistema valida formatos de datos (fechas, números, texto).
9. El sistema valida que los datos cumplan con reglas de negocio (HAWB único, comprador existente, etc.).
10. El sistema muestra resumen: número de registros válidos, número de errores.
11. El sistema permite confirmar o cancelar la importación.
12. El sistema almacena el archivo original en Supabase Storage.
13. El sistema registra metadatos de la importación: fecha, usuario, número de registros, estado.

---

#### US-09: Descargar reportes de envíos
**Tipo:** Usuario  
**Descripción:** Como **usuario autenticado** quiero **descargar reportes de envíos** para **tener los datos en diferentes formatos (Excel, PDF, CSV)**.  
**Prioridad:** Media  
**Esfuerzo:** 8 horas

**Criterios de Aceptación:**
1. El sistema permite exportar listados de envíos en formato Excel (.xlsx).
2. El sistema permite exportar listados de envíos en formato PDF.
3. El sistema permite exportar listados de envíos en formato CSV.
4. El sistema aplica los mismos filtros de la vista actual al exportar.
5. El sistema incluye información completa: HAWB, comprador, productos, totales, estado, fechas.
6. Los reportes Excel tienen formato profesional con encabezados, estilos y filtros automáticos.
7. Los reportes PDF tienen formato profesional listo para impresión con resúmenes de totales.
8. Los archivos CSV tienen codificación UTF-8 y formato compatible con Excel.

---

#### US-12: Detalle de los envíos
**Tipo:** Usuario  
**Descripción:** Como **usuario autenticado** quiero **consultar detalles de un envío** para **ver toda su información y productos asociados**.  
**Prioridad:** Alta  
**Esfuerzo:** 8 horas

**Criterios de Aceptación:**
1. El sistema permite consultar detalles de un envío específico por ID.
2. El sistema valida permisos: compradores solo pueden ver sus propios envíos.
3. El sistema muestra información completa: HAWB, comprador, productos, totales, estado, observaciones, fechas.
4. El sistema muestra historial de cambios de estado si existe.
5. El sistema muestra información detallada de cada producto asociado al envío.

---

#### US-13: Actualizar el estado de los envíos
**Tipo:** Usuario  
**Descripción:** Como **digitador o gerente** quiero **cambiar el estado de un envío** para **actualizar su progreso en el proceso de envío**.  
**Prioridad:** Media  
**Esfuerzo:** 16 horas

**Criterios de Aceptación:**
1. El sistema permite cambiar el estado de un envío mediante endpoint específico.
2. El sistema define estados: Pendiente, En Tránsito, Entregado, Cancelado, Retenido, Devuelto.
3. El sistema valida transiciones de estado válidas (ej: no se puede cambiar de "Entregado" a "Pendiente").
4. El sistema registra cada cambio de estado con fecha, hora y usuario que realizó el cambio.
5. El sistema genera notificaciones automáticas cuando cambia el estado (especialmente para compradores).
6. El sistema permite agregar observaciones al cambiar el estado.
7. El sistema registra el cambio en el log de auditoría.

---

### EPIC-03: Búsqueda Semántica

#### US-10: Búsqueda semántica
**Tipo:** Usuario  
**Descripción:** Como **usuario autenticado** quiero **realizar búsquedas semánticas usando lenguaje natural** para **encontrar envíos relevantes aunque no use las palabras exactas**.  
**Prioridad:** Alta  
**Esfuerzo:** 80 horas

**Criterios de Aceptación:**
1. El sistema permite realizar búsquedas usando lenguaje natural (consultas en español).
2. El sistema genera un embedding de la consulta del usuario.
3. El sistema busca envíos similares usando búsqueda vectorial (similitud coseno).
4. El sistema retorna resultados ordenados por relevancia semántica.
5. El sistema muestra puntuaciones de similitud para cada resultado.
6. El sistema procesa y normaliza el texto de la consulta antes de generar el embedding.
7. El tiempo de respuesta de la búsqueda es menor a 1 minuto.
8. El sistema genera embeddings automáticamente cuando se crea un envío.
9. El sistema actualiza embeddings cuando se modifica información relevante de un envío.
10. El sistema almacena embeddings en la base de datos usando pgvector (VectorField).
11. El sistema indexa el texto completo del envío (HAWB, comprador, productos, observaciones) para generar el embedding.
12. El sistema utiliza el modelo text-embedding-3-small de OpenAI por defecto.
13. El sistema maneja errores si la generación de embedding falla (no bloquea la creación del envío).

---

#### US-11: Búsqueda semántica con parámetros
**Tipo:** Usuario  
**Descripción:** Como **usuario autenticado** quiero **aplicar filtros a mi búsqueda semántica** para **obtener resultados más precisos**.  
**Prioridad:** Alta  
**Esfuerzo:** 16 horas

**Criterios de Aceptación:**
1. El sistema permite aplicar filtros por fecha (desde, hasta).
2. El sistema permite filtrar por estado del envío.
3. El sistema permite filtrar por remitente/comprador.
4. El sistema permite filtrar por ubicación (ciudad destino).
5. El sistema combina la búsqueda semántica con los filtros aplicados.
6. El sistema respeta los límites de permisos según el rol del usuario.
7. El sistema permite configurar el número máximo de resultados a retornar.
8. El sistema permite seleccionar el modelo de embedding a utilizar.

---

### EPIC-04: Comunicación y Seguridad

#### US-14: Canal de comunicación segura
**Tipo:** Usuario  
**Descripción:** Como **sistema** quiero **proporcionar un canal de comunicación segura** para **proteger la información transmitida entre cliente y servidor**.  
**Prioridad:** Alta  
**Esfuerzo:** 8 horas

**Criterios de Aceptación:**
1. El sistema utiliza protocolo HTTPS para todas las comunicaciones en producción.
2. El sistema utiliza certificados SSL/TLS válidos.
3. El sistema redirige automáticamente conexiones HTTP a HTTPS en producción.
4. El sistema valida certificados en el cliente para prevenir ataques man-in-the-middle.
5. El sistema implementa protección CSRF (Cross-Site Request Forgery) en todos los formularios.
6. El sistema sanitiza todas las entradas del usuario para prevenir XSS (Cross-Site Scripting).
7. El sistema valida y sanitiza datos en el backend antes de procesarlos.

---

## 🔧 HISTORIAS TÉCNICAS

### Resumen de Historias Técnicas

| Identificador | Nombre de la historia | Prioridad | Esfuerzo (horas) |
|---|---|---|---|
| UT-01 | Requisitos del sistema | Alta | 8 |
| UT-02 | Arquitectura del sistema | Alta | 8 |
| UT-03 | Modelo de procesos | Media | 16 |
| UT-04 | Generar texto indexado de envíos | Alta | 24 |
| UT-05 | Generación de embeddings | Alta | 40 |
| UT-06 | Generar texto indexado de envíos manuales | Media | 32 |
| UT-07 | Reporte de pruebas | Media | 8 |
| UT-08 | Métricas de pruebas | Alta | 16 |
| UT-09 | Comportamiento temporal | Alta | 24 |
| UT-10 | Utilización de recursos | Alta | 24 |
| UT-11 | Verificación y pruebas de aceptación | Alta | 6 |
| UT-12 | Presentación de sistema | Alta | 6 |
| **Total** | **12 historias técnicas** | | **212 horas** |

---

### EPIC-05: Infraestructura y Arquitectura

#### UT-01: Requisitos del sistema
**Tipo:** Técnica  
**Descripción:** Como **desarrollador** quiero **documentar los requisitos del sistema** para **tener una especificación clara de funcionalidades y restricciones**.  
**Prioridad:** Alta  
**Esfuerzo:** 8 horas

**Criterios de Aceptación:**
1. El sistema tiene documentación completa de requisitos funcionales.
2. El sistema tiene documentación completa de requisitos no funcionales.
3. El sistema tiene documentación de restricciones técnicas y de negocio.
4. El sistema tiene documentación de casos de uso principales.
5. La documentación está actualizada y accesible para el equipo de desarrollo.

---

#### UT-02: Arquitectura del sistema
**Tipo:** Técnica  
**Descripción:** Como **desarrollador** quiero **definir la arquitectura del sistema** para **establecer la estructura y organización del código**.  
**Prioridad:** Alta  
**Esfuerzo:** 8 horas

**Criterios de Aceptación:**
1. El sistema implementa arquitectura en capas: Views (Presentación), Services (Lógica de Negocio), Repositories (Acceso a Datos), Models (Modelos).
2. Las capas superiores no acceden directamente a capas inferiores (ej: Views no acceden directamente a Models).
3. El sistema utiliza el patrón Repository para abstraer el acceso a datos.
4. El sistema utiliza el patrón Service para encapsular lógica de negocio.
5. Cada capa tiene responsabilidades claramente definidas.
6. El sistema tiene documentación de la arquitectura con diagramas.

---

#### UT-03: Modelo de procesos
**Tipo:** Técnica  
**Descripción:** Como **desarrollador** quiero **definir el modelo de procesos** para **documentar los flujos de trabajo del sistema**.  
**Prioridad:** Media  
**Esfuerzo:** 16 horas

**Criterios de Aceptación:**
1. El sistema tiene documentación de procesos principales (registro de envíos, búsqueda semántica, importación de Excel).
2. El sistema tiene diagramas de flujo de procesos críticos.
3. El sistema documenta las interacciones entre componentes.
4. El sistema documenta los puntos de integración con servicios externos.
5. La documentación está actualizada y refleja el estado actual del sistema.

---

### EPIC-06: Búsqueda Semántica - Infraestructura

#### UT-04: Generar texto indexado de envíos
**Tipo:** Técnica  
**Descripción:** Como **desarrollador** quiero **generar texto indexado de envíos** para **preparar la información antes de generar embeddings**.  
**Prioridad:** Alta  
**Esfuerzo:** 24 horas

**Criterios de Aceptación:**
1. El sistema genera texto indexado automáticamente cuando se crea un envío.
2. El sistema actualiza el texto indexado cuando se modifica información relevante de un envío.
3. El texto indexado incluye: HAWB, comprador (nombre, cédula, ubicación), productos (descripción, categoría), estado, observaciones, fechas.
4. El sistema normaliza y limpia el texto antes de indexarlo.
5. El sistema almacena el texto indexado en la base de datos para referencia.
6. El sistema permite regenerar texto indexado para envíos existentes mediante comando de gestión.

---

#### UT-05: Generación de embeddings
**Tipo:** Técnica  
**Descripción:** Como **desarrollador** quiero **implementar generación de embeddings** para **indexar envíos para búsqueda semántica**.  
**Prioridad:** Alta  
**Esfuerzo:** 40 horas

**Criterios de Aceptación:**
1. El sistema se integra con la API de OpenAI para generación de embeddings.
2. El sistema genera embeddings automáticamente cuando se crea un envío.
3. El sistema actualiza embeddings cuando se modifica información relevante de un envío.
4. El sistema almacena embeddings en la base de datos usando pgvector (VectorField).
5. El sistema utiliza el modelo text-embedding-3-small de OpenAI por defecto.
6. El sistema maneja errores y timeouts de la API de forma apropiada.
7. El sistema implementa retry logic para llamadas fallidas (máximo 3 intentos).
8. El sistema registra costos y uso de la API de OpenAI.
9. El sistema permite configurar endpoints y credenciales de la API mediante variables de entorno.
10. El sistema valida que la API esté configurada antes de intentar generar embeddings.
11. El sistema permite generar embeddings para envíos existentes mediante comando de gestión.
12. El sistema procesa embeddings en lotes para optimizar el rendimiento.

---

#### UT-06: Generar texto indexado de envíos manuales
**Tipo:** Técnica  
**Descripción:** Como **desarrollador** quiero **generar texto indexado de envíos manuales** para **permitir la regeneración de índices cuando sea necesario**.  
**Prioridad:** Media  
**Esfuerzo:** 32 horas

**Criterios de Aceptación:**
1. El sistema proporciona un comando de gestión para regenerar texto indexado de todos los envíos.
2. El sistema permite regenerar texto indexado de envíos específicos por ID.
3. El sistema permite regenerar texto indexado de envíos filtrados por criterios (fecha, estado, comprador).
4. El sistema muestra progreso durante la regeneración (número de envíos procesados).
5. El sistema maneja errores durante la regeneración sin detener el proceso completo.
6. El sistema registra en logs los envíos procesados y cualquier error encontrado.
7. El sistema permite ejecutar la regeneración en modo dry-run para validar sin modificar.

---

### EPIC-07: Pruebas y Calidad

#### UT-07: Reporte de pruebas
**Tipo:** Técnica  
**Descripción:** Como **desarrollador** quiero **generar reportes de pruebas** para **documentar los resultados de las pruebas realizadas**.  
**Prioridad:** Media  
**Esfuerzo:** 8 horas

**Criterios de Aceptación:**
1. El sistema genera reportes de pruebas unitarias.
2. El sistema genera reportes de pruebas de integración.
3. El sistema genera reportes de pruebas de aceptación.
4. Los reportes incluyen: número de pruebas ejecutadas, número de pruebas exitosas, número de pruebas fallidas, tiempo de ejecución.
5. Los reportes se generan en formato legible (HTML, JSON, XML).
6. El sistema permite exportar reportes para análisis posterior.

---

#### UT-08: Métricas de pruebas
**Tipo:** Técnica  
**Descripción:** Como **desarrollador** quiero **obtener métricas de pruebas** para **evaluar la cobertura y calidad del código**.  
**Prioridad:** Alta  
**Esfuerzo:** 16 horas

**Criterios de Aceptación:**
1. El sistema calcula cobertura de código de las pruebas unitarias.
2. El sistema calcula cobertura de código de las pruebas de integración.
3. El sistema muestra métricas de cobertura por módulo/componente.
4. El sistema genera reportes de cobertura en formato HTML.
5. El sistema establece un umbral mínimo de cobertura (ej: 80%).
6. El sistema alerta cuando la cobertura está por debajo del umbral.
7. El sistema rastrea métricas de pruebas a lo largo del tiempo.

---

#### UT-09: Comportamiento temporal
**Tipo:** Técnica  
**Descripción:** Como **desarrollador** quiero **evaluar el comportamiento temporal del sistema** para **garantizar que cumple con los requisitos de rendimiento**.  
**Prioridad:** Alta  
**Esfuerzo:** 24 horas

**Criterios de Aceptación:**
1. El sistema mide tiempos de respuesta de endpoints críticos.
2. El sistema mide tiempo de respuesta de búsqueda semántica (debe ser menor a 1 minuto).
3. El sistema mide tiempo de respuesta de importación de archivos Excel.
4. El sistema mide tiempo de generación de reportes (PDF, Excel, CSV).
5. El sistema documenta tiempos de respuesta esperados y reales.
6. El sistema identifica cuellos de botella en el rendimiento.
7. El sistema genera reportes de rendimiento con gráficos y estadísticas.

---

#### UT-10: Utilización de recursos
**Tipo:** Técnica  
**Descripción:** Como **desarrollador** quiero **monitorear la utilización de recursos** para **optimizar el uso de memoria, CPU y almacenamiento**.  
**Prioridad:** Alta  
**Esfuerzo:** 24 horas

**Criterios de Aceptación:**
1. El sistema monitorea uso de memoria (RAM) del servidor.
2. El sistema monitorea uso de CPU del servidor.
3. El sistema monitorea uso de almacenamiento en disco.
4. El sistema monitorea uso de recursos de base de datos (conexiones, consultas).
5. El sistema genera alertas cuando el uso de recursos excede umbrales definidos.
6. El sistema documenta métricas de recursos en reportes.
7. El sistema identifica operaciones que consumen más recursos.
8. El sistema proporciona recomendaciones para optimización de recursos.

---

#### UT-11: Verificación y pruebas de aceptación
**Tipo:** Técnica  
**Descripción:** Como **desarrollador** quiero **realizar verificación y pruebas de aceptación** para **validar que el sistema cumple con los requisitos**.  
**Prioridad:** Alta  
**Esfuerzo:** 6 horas

**Criterios de Aceptación:**
1. El sistema tiene pruebas de aceptación para todas las historias de usuario.
2. Las pruebas de aceptación validan todos los criterios de aceptación de cada historia.
3. Las pruebas de aceptación se ejecutan automáticamente en el pipeline de CI/CD.
4. El sistema genera reportes de pruebas de aceptación.
5. Las pruebas de aceptación están documentadas y son reproducibles.

---

#### UT-12: Presentación de sistema
**Tipo:** Técnica  
**Descripción:** Como **desarrollador** quiero **preparar la presentación del sistema** para **demostrar las funcionalidades implementadas**.  
**Prioridad:** Alta  
**Esfuerzo:** 6 horas

**Criterios de Aceptación:**
1. El sistema tiene documentación de usuario actualizada.
2. El sistema tiene guías de uso para funcionalidades principales.
3. El sistema tiene demostraciones grabadas o scripts de demostración.
4. El sistema está desplegado en ambiente de demostración.
5. El sistema tiene datos de prueba apropiados para la demostración.
6. La presentación cubre todas las funcionalidades principales del sistema.

---

## 📋 DEPENDENCIAS ENTRE HISTORIAS

### Dependencias de Historias de Usuario

- **US-01 (Inicio de sesión)** depende de **UT-02 (Arquitectura del sistema)** y configuración de autenticación JWT
- **US-02 (Asignar roles)** depende de **US-15 (Acceso por roles)**
- **US-03 (Registrar envíos)** depende de **UT-04 (Generar texto indexado de envíos)** y **UT-05 (Generación de embeddings)**
- **US-04 (Actualizar envíos)** depende de **UT-04 (Generar texto indexado de envíos)** y **UT-05 (Generación de embeddings)**
- **US-10 (Búsqueda semántica)** depende de **UT-04 (Generar texto indexado de envíos)** y **UT-05 (Generación de embeddings)**
- **US-11 (Búsqueda semántica con parámetros)** depende de **US-10 (Búsqueda semántica)**
- **US-08 (Carga de envíos por archivo Excel)** requiere procesamiento de archivos Excel
- **US-14 (Canal de comunicación segura)** es requisito previo para todas las historias que requieren comunicación segura

### Dependencias de Historias Técnicas

- **UT-02 (Arquitectura del sistema)** es requisito previo para todas las historias de implementación de funcionalidades
- **UT-04 (Generar texto indexado de envíos)** es requisito previo para **UT-05 (Generación de embeddings)**
- **UT-05 (Generación de embeddings)** es requisito previo para **US-10 (Búsqueda semántica)**
- **UT-06 (Generar texto indexado de envíos manuales)** depende de **UT-04 (Generar texto indexado de envíos)**
- **UT-11 (Verificación y pruebas de aceptación)** depende de la finalización de todas las historias de usuario
- **UT-12 (Presentación de sistema)** depende de la finalización de todas las historias principales

---

## 📊 RESUMEN TOTAL

**Total de Historias de Usuario:** 17  
**Total de Esfuerzo (HU):** 296 horas

**Total de Historias Técnicas:** 12  
**Total de Esfuerzo (HT):** 212 horas

**Total General:** 29 historias | 508 horas

---

**Documento generado:** Enero 2026  
**Última actualización:** Enero 2026  
**Versión:** 2.0

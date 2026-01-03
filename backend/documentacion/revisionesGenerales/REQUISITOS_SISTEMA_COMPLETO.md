# 📋 REQUISITOS DEL SISTEMA - DOCUMENTO COMPLETO

## 📌 INFORMACIÓN GENERAL

**Sistema:** Sistema de Gestión de Envíos con Búsqueda Semántica  
**Versión del Documento:** 2.0  
**Fecha:** 2024  
**Arquitectura:** Frontend (React) + Backend (Django REST Framework) + Base de Datos (Supabase/PostgreSQL)

---

## 🔵 REQUISITOS FUNCIONALES

### 🔐 1. GESTIÓN DE AUTENTICACIÓN Y USUARIOS

#### RF-01: Registro de Usuarios
**Descripción:** El sistema debe permitir el registro de nuevos usuarios en el sistema.  
**Detalles:**
- El sistema debe permitir el registro de compradores mediante un formulario público.
- El registro de otros roles (Administrador, Gerente, Digitador) solo puede ser realizado por usuarios con permisos administrativos.
- Durante el registro, el sistema debe validar que la cédula sea única y tenga formato ecuatoriano válido (10 dígitos).
- El sistema debe validar que el correo electrónico sea único y tenga formato válido.
- El sistema debe validar que la contraseña cumpla con los requisitos de seguridad establecidos (mínimo 8 caracteres, mayúsculas, minúsculas, números y caracteres especiales).
- El sistema debe almacenar información adicional del usuario: nombre completo, teléfono, fecha de nacimiento, dirección, y ubicación geográfica (provincia, cantón, ciudad).

#### RF-02: Inicio y Cierre de Sesión
**Descripción:** El sistema debe permitir a los usuarios autenticarse y cerrar sesión de forma segura.  
**Detalles:**
- El sistema debe implementar autenticación mediante tokens JWT (JSON Web Tokens).
- El sistema debe proporcionar tokens de acceso y tokens de actualización (refresh tokens).
- El sistema debe implementar límite de intentos de inicio de sesión fallidos (máximo 5 intentos).
- El sistema debe bloquear temporalmente el acceso después de superar el límite de intentos (15 minutos).
- El sistema debe registrar todos los intentos de inicio de sesión (exitosos y fallidos) para auditoría.
- El sistema debe permitir cerrar sesión invalidando el token de acceso actual.
- El sistema debe validar que el usuario esté activo antes de permitir el inicio de sesión.

#### RF-03: Recuperación y Actualización de Contraseñas
**Descripción:** El sistema debe permitir a los usuarios recuperar y actualizar sus contraseñas.  
**Detalles:**
- El sistema debe permitir solicitar restablecimiento de contraseña mediante correo electrónico.
- El sistema debe validar que el correo electrónico exista en el sistema antes de enviar el enlace de recuperación.
- El sistema debe generar enlaces de recuperación con tokens seguros y expiración temporal.
- El sistema debe permitir a los usuarios autenticados cambiar su contraseña actual.
- El sistema debe validar que la nueva contraseña cumpla con los requisitos de seguridad.
- El sistema debe requerir la contraseña actual para autorizar el cambio de contraseña.
- El sistema debe encriptar todas las contraseñas antes de almacenarlas en la base de datos.

#### RF-04: Gestión de Usuarios (CRUD)
**Descripción:** El sistema debe permitir la gestión completa de usuarios (crear, leer, actualizar, eliminar).  
**Detalles:**
- El sistema debe permitir crear nuevos usuarios con todos los campos requeridos.
- El sistema debe permitir listar usuarios con paginación y filtros por rol, estado activo, y ubicación.
- El sistema debe permitir consultar los detalles de un usuario específico.
- El sistema debe permitir actualizar información de usuarios (parcial o completa).
- El sistema debe permitir eliminar usuarios (eliminación lógica o física según configuración).
- El sistema debe validar permisos según el rol del usuario que realiza la operación.
- El sistema debe registrar todas las operaciones de gestión de usuarios en el log de auditoría.

#### RF-05: Asignación de Roles
**Descripción:** El sistema debe asignar y gestionar roles de usuario (Administrador, Gerente, Digitador y Comprador).  
**Detalles:**
- El sistema debe definir cuatro roles principales: Administrador (rol=1), Gerente (rol=2), Digitador (rol=3), y Comprador (rol=4).
- El sistema debe permitir asignar roles a usuarios durante la creación o actualización.
- El sistema debe validar que solo usuarios con rol de Administrador puedan asignar roles de Administrador.
- El sistema debe proporcionar métodos de consulta para verificar el rol de un usuario.
- El sistema debe permitir filtrar usuarios por rol mediante endpoints específicos.

#### RF-06: Control de Acceso Basado en Roles (RBAC)
**Descripción:** El sistema debe restringir el acceso a rutas y funcionalidades según el rol del usuario.  
**Detalles:**
- **Administrador (rol=1):** Acceso completo a todas las funcionalidades del sistema, incluyendo gestión de todos los usuarios.
- **Gerente (rol=2):** Acceso a gestión de usuarios (excepto administradores), visualización de todos los envíos, estadísticas generales, y reportes.
- **Digitador (rol=3):** Acceso a visualización de compradores y otros digitadores, gestión completa de envíos y productos, y estadísticas de envíos.
- **Comprador (rol=4):** Acceso limitado a gestión de su propio perfil, visualización de sus propios envíos, y gestión de productos en sus envíos.
- El sistema debe validar permisos en cada endpoint antes de procesar la solicitud.
- El sistema debe retornar mensajes de error apropiados cuando un usuario intenta acceder a funcionalidades no permitidas.

#### RF-07: Gestión de Perfil de Usuario
**Descripción:** El sistema debe permitir a los usuarios gestionar su propio perfil.  
**Detalles:**
- El sistema debe permitir a los usuarios autenticados consultar su perfil completo.
- El sistema debe permitir actualizar información personal (nombre, teléfono, dirección, ubicación geográfica).
- El sistema debe validar que el usuario solo pueda modificar su propio perfil (excepto administradores).
- El sistema debe permitir actualizar la ubicación geográfica seleccionando provincia, cantón y ciudad de Ecuador.
- El sistema debe mostrar estadísticas personales del usuario (envíos realizados, cupo utilizado, etc.).

---

### 📦 2. GESTIÓN DE ENVÍOS

#### RF-08: Registro de Envíos
**Descripción:** El sistema debe permitir registrar nuevos envíos con toda la información requerida.  
**Detalles:**
- El sistema debe permitir crear envíos con un número único de guía aérea (HAWB).
- El sistema debe validar que el HAWB sea único en el sistema.
- El sistema debe asociar cada envío a un comprador específico.
- El sistema debe permitir registrar información adicional: observaciones, fecha de emisión.
- El sistema debe calcular automáticamente los totales (peso, cantidad, valor) basándose en los productos asociados.
- El sistema debe calcular automáticamente el costo del servicio según las tarifas aplicables.
- El sistema debe validar que el comprador no exceda su cupo anual al crear un envío.
- El sistema debe generar automáticamente un embedding para búsqueda semántica cuando se crea un envío.

#### RF-09: Modificación de Envíos
**Descripción:** El sistema debe permitir modificar la información de envíos existentes.  
**Detalles:**
- El sistema debe permitir actualizar información de envíos (parcial o completa).
- El sistema debe recalcular automáticamente los totales cuando se modifican productos asociados.
- El sistema debe recalcular el costo del servicio cuando cambian productos o tarifas.
- El sistema debe validar permisos: los compradores solo pueden modificar sus propios envíos.
- El sistema debe actualizar el embedding semántico cuando se modifica información relevante del envío.
- El sistema debe registrar cambios de estado en el historial del envío.

#### RF-10: Eliminación de Envíos
**Descripción:** El sistema debe permitir eliminar envíos del sistema.  
**Detalles:**
- El sistema debe permitir eliminar envíos (eliminación lógica o física según configuración).
- El sistema debe validar permisos antes de permitir la eliminación.
- El sistema debe eliminar o desactivar los productos asociados al envío.
- El sistema debe registrar la eliminación en el log de auditoría.

#### RF-11: Listado de Envíos con Paginación
**Descripción:** El sistema debe mostrar la lista de envíos registrados con paginación.  
**Detalles:**
- El sistema debe listar envíos con paginación (10 elementos por página por defecto, configurable).
- El sistema debe aplicar filtros automáticos según el rol del usuario (compradores solo ven sus envíos).
- El sistema debe permitir ordenar envíos por fecha, estado, valor, peso, etc.
- El sistema debe mostrar información resumida: HAWB, comprador, estado, fecha, totales.
- El sistema debe incluir contadores de productos asociados a cada envío.

#### RF-12: Consulta de Historial de Envíos
**Descripción:** El sistema debe permitir consultar el historial completo de envíos.  
**Detalles:**
- El sistema debe mantener un historial completo de todos los envíos (incluyendo eliminados si es eliminación lógica).
- El sistema debe permitir filtrar el historial por fecha, estado, comprador, ubicación.
- El sistema debe mostrar cambios de estado en el historial de cada envío.
- El sistema debe permitir exportar el historial en diferentes formatos (Excel, CSV, PDF).

#### RF-13: Cambio de Estado de Envíos
**Descripción:** El sistema debe permitir cambiar el estado de un envío.  
**Detalles:**
- El sistema debe definir los siguientes estados: Pendiente, En Tránsito, Entregado, Cancelado, Retenido, Devuelto.
- El sistema debe permitir cambiar el estado de un envío mediante un endpoint específico.
- El sistema debe validar transiciones de estado válidas (ej: no se puede cambiar de "Entregado" a "Pendiente").
- El sistema debe registrar cada cambio de estado con fecha, hora y usuario que realizó el cambio.
- El sistema debe generar notificaciones automáticas cuando cambia el estado de un envío (especialmente para compradores).
- El sistema debe permitir agregar observaciones al cambiar el estado.

#### RF-14: Generación de Número de Seguimiento
**Descripción:** El sistema debe generar un número único de seguimiento (HAWB) por envío.  
**Detalles:**
- El sistema debe generar automáticamente un HAWB único si no se proporciona uno.
- El sistema debe validar la unicidad del HAWB antes de crear el envío.
- El sistema debe permitir búsqueda de envíos por número de HAWB.
- El sistema debe mostrar el HAWB de forma prominente en todas las vistas relacionadas con el envío.

#### RF-15: Filtrado de Envíos
**Descripción:** El sistema debe permitir filtrar envíos por múltiples criterios.  
**Detalles:**
- El sistema debe permitir filtrar por estado (pendiente, en tránsito, entregado, cancelado, etc.).
- El sistema debe permitir filtrar por rango de fechas (fecha desde, fecha hasta).
- El sistema debe permitir filtrar por cliente/comprador (nombre, cédula, correo).
- El sistema debe permitir filtrar por ubicación (provincia, cantón, ciudad).
- El sistema debe permitir filtrar por número de guía (HAWB).
- El sistema debe permitir combinar múltiples filtros simultáneamente.
- El sistema debe permitir búsqueda por texto libre que busque en múltiples campos.

#### RF-16: Comprobante de Envío
**Descripción:** El sistema debe generar comprobantes de envío en formato PDF.  
**Detalles:**
- El sistema debe generar un comprobante PDF con toda la información del envío.
- El comprobante debe incluir: HAWB, información del comprador, productos, totales, estado, fecha.
- El comprobante debe tener un formato profesional y listo para impresión.
- El sistema debe permitir descargar el comprobante desde la interfaz.

---

### 🛍️ 3. GESTIÓN DE PRODUCTOS

#### RF-17: Registro de Productos
**Descripción:** El sistema debe permitir registrar productos asociados a envíos.  
**Detalles:**
- El sistema debe permitir crear productos asociados a un envío específico.
- Cada producto debe tener: descripción, peso, cantidad, valor, categoría.
- El sistema debe definir categorías preestablecidas: Electrónica, Ropa, Hogar, Deportes, Otros.
- El sistema debe calcular automáticamente el costo de envío del producto según tarifas aplicables.
- El sistema debe recalcular los totales del envío cuando se agregan, modifican o eliminan productos.

#### RF-18: Modificación de Productos
**Descripción:** El sistema debe permitir modificar información de productos.  
**Detalles:**
- El sistema debe permitir actualizar cualquier campo de un producto.
- El sistema debe recalcular automáticamente el costo de envío cuando cambia el peso o la categoría.
- El sistema debe recalcular los totales del envío padre cuando se modifica un producto.

#### RF-19: Eliminación de Productos
**Descripción:** El sistema debe permitir eliminar productos de envíos.  
**Detalles:**
- El sistema debe permitir eliminar productos individuales.
- El sistema debe recalcular automáticamente los totales del envío después de eliminar un producto.
- El sistema debe validar que el envío tenga al menos un producto (o permitir envíos sin productos según reglas de negocio).

#### RF-20: Listado y Filtrado de Productos
**Descripción:** El sistema debe permitir listar y filtrar productos.  
**Detalles:**
- El sistema debe permitir listar todos los productos con paginación.
- El sistema debe permitir filtrar productos por categoría, envío, rango de peso, rango de valor.
- El sistema debe permitir buscar productos por descripción.
- El sistema debe mostrar estadísticas de productos por categoría.

---

### 📊 4. GESTIÓN DE ARCHIVOS EXCEL

#### RF-21: Carga de Archivos Excel
**Descripción:** El sistema debe permitir cargar archivos Excel para insertar automáticamente información en la base de datos.  
**Detalles:**
- El sistema debe permitir cargar archivos en formato .xlsx y .xls.
- El sistema debe validar el tamaño máximo del archivo (15 MB).
- El sistema debe validar la estructura del archivo (columnas requeridas, formato de datos).
- El sistema debe procesar el archivo y extraer información de envíos y productos.
- El sistema debe mostrar un resumen previo de los datos a importar antes de confirmar.

#### RF-22: Validación de Archivos Excel
**Descripción:** El sistema debe validar el formato y contenido de los archivos Excel cargados.  
**Detalles:**
- El sistema debe validar que el archivo tenga las columnas requeridas.
- El sistema debe validar formatos de datos (fechas, números, texto).
- El sistema debe validar que los datos cumplan con las reglas de negocio (HAWB único, comprador existente, etc.).
- El sistema debe reportar errores de validación de forma clara y específica.
- El sistema debe permitir corregir errores y reintentar la importación.

#### RF-23: Almacenamiento de Archivos
**Descripción:** El sistema debe almacenar los datos extraídos del Excel en la tabla de archivo alojada en Supabase.  
**Detalles:**
- El sistema debe almacenar el archivo original en Supabase Storage.
- El sistema debe registrar metadatos de la importación: fecha, usuario, número de registros, estado.
- El sistema debe mantener un historial de todas las importaciones realizadas.
- El sistema debe permitir descargar el archivo original después de la importación.

#### RF-24: Historial de Cargas de Archivos
**Descripción:** El sistema debe registrar un historial de cargas de archivos.  
**Detalles:**
- El sistema debe registrar cada carga de archivo con: fecha, usuario, nombre del archivo, número de registros procesados, número de registros exitosos, número de errores.
- El sistema debe permitir consultar el historial de importaciones.
- El sistema debe permitir filtrar el historial por fecha, usuario, estado (éxito/error).
- El sistema debe permitir descargar reportes de importaciones anteriores.

---

### 🔍 5. BÚSQUEDA TRADICIONAL

#### RF-25: Búsqueda Tradicional
**Descripción:** El sistema debe permitir realizar búsquedas tradicionales por texto en usuarios, envíos y productos.  
**Detalles:**
- El sistema debe permitir búsquedas generales que busquen en todos los tipos de entidades.
- El sistema debe permitir búsquedas específicas por tipo: usuarios, envíos, productos.
- El sistema debe aplicar filtros de permisos según el rol del usuario.
- El sistema debe mostrar resultados agrupados por tipo de entidad.
- El sistema debe mostrar el total de resultados encontrados.

#### RF-26: Historial de Búsquedas Tradicionales
**Descripción:** El sistema debe mantener un historial de búsquedas tradicionales realizadas.  
**Detalles:**
- El sistema debe registrar cada búsqueda tradicional: término, tipo, usuario, fecha, resultados encontrados.
- El sistema debe permitir consultar el historial de búsquedas del usuario actual.
- El sistema debe permitir limpiar el historial de búsquedas.
- El sistema debe proporcionar estadísticas de búsquedas (términos más buscados, tipos más usados).

---

### 🤖 6. BÚSQUEDA SEMÁNTICA

#### RF-27: Generación de Embeddings
**Descripción:** El sistema debe generar embeddings a partir de los envíos almacenados.  
**Detalles:**
- El sistema debe generar embeddings usando modelos de OpenAI (text-embedding-ada-002 u otros).
- El sistema debe generar embeddings automáticamente cuando se crea o modifica un envío.
- El sistema debe almacenar los embeddings en la base de datos usando pgvector.
- El sistema debe permitir regenerar embeddings masivamente mediante comandos de gestión.
- El sistema debe indexar el texto completo del envío (HAWB, comprador, productos, observaciones) para generar el embedding.

#### RF-28: Búsqueda Semántica
**Descripción:** El sistema debe permitir búsquedas semánticas mediante lenguaje natural.  
**Detalles:**
- El sistema debe permitir realizar búsquedas usando lenguaje natural (consultas en español).
- El sistema debe generar un embedding de la consulta del usuario.
- El sistema debe buscar envíos similares usando búsqueda vectorial (similitud coseno).
- El sistema debe retornar resultados ordenados por relevancia semántica.
- El sistema debe mostrar puntuaciones de similitud para cada resultado.
- El sistema debe procesar y normalizar el texto de la consulta antes de generar el embedding.

#### RF-29: Generación de Embeddings de Consultas
**Descripción:** El sistema debe generar embeddings a partir de las búsquedas realizadas.  
**Detalles:**
- El sistema debe generar un embedding para cada consulta de búsqueda semántica.
- El sistema debe almacenar el embedding de la consulta en el historial.
- El sistema debe permitir reutilizar embeddings de consultas similares para optimizar costos.

#### RF-30: Resultados Ordenados por Similitud
**Descripción:** El sistema debe mostrar resultados ordenados según la similitud semántica.  
**Detalles:**
- El sistema debe calcular múltiples métricas de similitud: coseno, producto punto, distancia euclidiana, distancia Manhattan.
- El sistema debe permitir seleccionar la métrica de ordenamiento (score combinado por defecto).
- El sistema debe aplicar umbrales de similitud para filtrar resultados poco relevantes.
- El sistema debe mostrar fragmentos relevantes del texto que coinciden con la consulta.
- El sistema debe proporcionar una razón de relevancia para cada resultado.

#### RF-31: Refinamiento de Búsqueda Semántica
**Descripción:** El sistema debe permitir refinar la búsqueda semántica con filtros adicionales.  
**Detalles:**
- El sistema debe permitir aplicar filtros por fecha (desde, hasta).
- El sistema debe permitir filtrar por estado del envío.
- El sistema debe permitir filtrar por remitente/comprador.
- El sistema debe permitir filtrar por ubicación (ciudad destino).
- El sistema debe combinar la búsqueda semántica con los filtros aplicados.
- El sistema debe respetar los límites de permisos según el rol del usuario.

#### RF-32: Historial de Búsquedas Semánticas
**Descripción:** El sistema debe mantener un historial completo de búsquedas semánticas.  
**Detalles:**
- El sistema debe registrar cada búsqueda semántica: consulta, usuario, fecha, resultados encontrados, tiempo de respuesta, modelo utilizado, costo, tokens utilizados.
- El sistema debe permitir consultar el historial de búsquedas del usuario.
- El sistema debe permitir limpiar el historial de búsquedas semánticas.
- El sistema debe proporcionar sugerencias basadas en búsquedas anteriores.

#### RF-33: Métricas de Búsqueda Semántica
**Descripción:** El sistema debe proporcionar métricas de rendimiento de búsquedas semánticas.  
**Detalles:**
- El sistema debe registrar el tiempo de respuesta de cada búsqueda.
- El sistema debe registrar el costo de cada búsqueda (costo de generación de embeddings).
- El sistema debe registrar el número de tokens utilizados.
- El sistema debe proporcionar estadísticas: tiempo promedio, costo total, número total de búsquedas.
- El sistema debe mostrar el número total de embeddings generados.

---

### 📈 7. REPORTES Y ESTADÍSTICAS

#### RF-34: Métricas Generales
**Descripción:** El sistema debe mostrar métricas generales del sistema.  
**Detalles:**
- El sistema debe mostrar el número total de envíos.
- El sistema debe mostrar la distribución de envíos por estado.
- El sistema debe mostrar métricas de rendimiento (envíos por mes, tendencias).
- El sistema debe mostrar volumen mensual de envíos.
- El sistema debe mostrar estadísticas de usuarios por rol.
- El sistema debe actualizar las métricas en tiempo real.

#### RF-35: Tarjetas Estadísticas
**Descripción:** El sistema debe permitir visualizar tarjetas estadísticas.  
**Detalles:**
- El sistema debe mostrar tarjetas con estadísticas por estado (pendientes, en tránsito, entregados, etc.).
- El sistema debe mostrar estadísticas por tipo de producto o categoría.
- El sistema debe mostrar estadísticas por cliente/comprador.
- El sistema debe mostrar estadísticas por fecha (diarias, semanales, mensuales).
- El sistema debe permitir filtrar las tarjetas según criterios seleccionados.

#### RF-36: Generación de Reportes Exportables
**Descripción:** El sistema debe generar reportes exportables en PDF o Excel.  
**Detalles:**
- El sistema debe permitir exportar listados de envíos en formato Excel (.xlsx).
- El sistema debe permitir exportar listados de envíos en formato CSV.
- El sistema debe permitir exportar listados de envíos en formato PDF.
- El sistema debe aplicar los mismos filtros de la vista actual al exportar.
- El sistema debe incluir información completa: HAWB, comprador, productos, totales, estado, fechas.
- El sistema debe formatear los reportes de forma profesional con encabezados, estilos y resúmenes.
- El sistema debe incluir resúmenes de totales (peso total, valor total, costo total) en los reportes PDF.

#### RF-37: Dashboard de Usuario
**Descripción:** El sistema debe proporcionar un dashboard personalizado para cada usuario.  
**Detalles:**
- El sistema debe mostrar un dashboard diferente según el rol del usuario.
- Para compradores: debe mostrar sus envíos, cupo utilizado, estadísticas personales.
- Para administradores y gerentes: debe mostrar métricas globales, estadísticas generales.
- El sistema debe permitir filtrar el dashboard por año.
- El sistema debe mostrar gráficos y visualizaciones de datos.

#### RF-38: Estadísticas de Cupo Anual
**Descripción:** El sistema debe mostrar estadísticas del cupo anual para compradores.  
**Detalles:**
- El sistema debe mostrar el cupo anual asignado al comprador.
- El sistema debe mostrar el peso total utilizado en el año actual.
- El sistema debe mostrar el porcentaje de cupo utilizado.
- El sistema debe mostrar el peso restante disponible.
- El sistema debe validar el cupo antes de permitir crear nuevos envíos.

---

### 🔔 8. SISTEMA DE NOTIFICACIONES

#### RF-39: Notificaciones de Envíos
**Descripción:** El sistema debe notificar a los compradores cuando se le haya agregado un envío o modificado su estado.  
**Detalles:**
- El sistema debe generar notificaciones automáticas cuando se crea un envío para un comprador.
- El sistema debe generar notificaciones cuando cambia el estado de un envío.
- El sistema debe generar notificaciones cuando se asigna un envío a un comprador.
- El sistema debe almacenar las notificaciones en la base de datos.
- El sistema debe permitir marcar notificaciones como leídas.
- El sistema debe permitir marcar todas las notificaciones como leídas.

#### RF-40: Gestión de Notificaciones
**Descripción:** El sistema debe permitir gestionar las notificaciones de usuarios.  
**Detalles:**
- El sistema debe permitir listar todas las notificaciones del usuario autenticado.
- El sistema debe permitir filtrar notificaciones por tipo (nuevo envío, estado cambiado, general).
- El sistema debe mostrar un contador de notificaciones no leídas.
- El sistema debe permitir eliminar notificaciones individuales.
- El sistema debe permitir consultar notificaciones recientes (últimas 10, 20, 50).
- El sistema debe actualizar las notificaciones en tiempo real mediante polling o WebSockets.

#### RF-41: Tipos de Notificaciones
**Descripción:** El sistema debe soportar diferentes tipos de notificaciones.  
**Detalles:**
- El sistema debe definir tipos: "nuevo_envio", "envio_asignado", "estado_cambiado", "general".
- Cada notificación debe incluir: título, mensaje, tipo, enlace opcional, metadata adicional.
- El sistema debe formatear los mensajes de forma clara y legible.
- El sistema debe incluir información contextual en la metadata (ID de envío, estado anterior, etc.).

---

### 🗺️ 9. GESTIÓN DE UBICACIONES GEOGRÁFICAS

#### RF-42: Sistema de Ubicaciones
**Descripción:** El sistema debe gestionar ubicaciones geográficas de Ecuador.  
**Detalles:**
- El sistema debe implementar una estructura jerárquica: Provincia → Cantón → Ciudad.
- El sistema debe proporcionar endpoints para obtener provincias, cantones y ciudades.
- El sistema debe almacenar coordenadas geográficas (latitud, longitud) para cada ciudad.
- El sistema debe permitir buscar ciudades por nombre.
- El sistema debe asociar usuarios y envíos con ubicaciones geográficas.

#### RF-43: Visualización en Mapa
**Descripción:** El sistema debe permitir visualizar compradores en un mapa.  
**Detalles:**
- El sistema debe proporcionar endpoints para obtener compradores con ubicación para mapa.
- El sistema debe retornar coordenadas geográficas junto con información del comprador.
- El sistema debe permitir filtrar compradores por ciudad para visualización en mapa.

---

### 💰 10. GESTIÓN DE TARIFAS

#### RF-44: Gestión de Tarifas
**Descripción:** El sistema debe gestionar tarifas para calcular costos de envío.  
**Detalles:**
- El sistema debe permitir crear, modificar y eliminar tarifas.
- Cada tarifa debe tener: categoría de producto, peso mínimo, peso máximo, cargo base, precio por kilogramo.
- El sistema debe calcular automáticamente el costo de envío de productos según las tarifas aplicables.
- El sistema debe validar que exista una tarifa activa para cada categoría y rango de peso.
- El sistema debe permitir activar/desactivar tarifas.

#### RF-45: Cálculo Automático de Costos
**Descripción:** El sistema debe calcular automáticamente los costos de envío.  
**Detalles:**
- El sistema debe calcular el costo de cada producto según su categoría y peso.
- El sistema debe calcular el costo total del servicio sumando los costos de todos los productos.
- El sistema debe recalcular costos automáticamente cuando cambian productos o tarifas.
- El sistema debe proporcionar un endpoint para calcular costos antes de crear el envío.

---

### 📝 11. AUDITORÍA Y LOGS

#### RF-46: Registro de Actividad del Sistema
**Descripción:** El sistema debe generar un registro de actividad del sistema para conocer acciones realizadas por los usuarios.  
**Detalles:**
- El sistema debe registrar todas las operaciones importantes: creación, modificación, eliminación de entidades.
- Cada registro debe incluir: usuario, operación, entidad, fecha/hora, detalles adicionales.
- El sistema debe permitir consultar el log de auditoría con filtros por usuario, fecha, tipo de operación.
- El sistema debe proteger el log de auditoría contra modificaciones o eliminaciones.
- El sistema debe exportar logs de auditoría para análisis externos.

#### RF-47: Métricas del Sistema
**Descripción:** El sistema debe registrar métricas de uso del sistema.  
**Detalles:**
- El sistema debe registrar métricas de búsquedas (tradicionales y semánticas).
- El sistema debe registrar métricas de importaciones y exportaciones.
- El sistema debe registrar métricas de uso por usuario y por rol.
- El sistema debe proporcionar endpoints para consultar métricas agregadas.

---

## 🟡 REQUISITOS NO FUNCIONALES

### 🔒 1. SEGURIDAD

#### RNF-01: Comunicación Cifrada
**Descripción:** La comunicación entre cliente y servidor debe estar cifrada mediante HTTPS.  
**Detalles:**
- El sistema debe utilizar protocolo HTTPS para todas las comunicaciones.
- El sistema debe utilizar certificados SSL/TLS válidos.
- El sistema debe redirigir automáticamente conexiones HTTP a HTTPS en producción.
- El sistema debe validar certificados en el cliente para prevenir ataques man-in-the-middle.

#### RNF-02: Seguridad de Contraseñas
**Descripción:** La contraseña debe tener controles de seguridad y encriptación en la base de datos.  
**Detalles:**
- El sistema debe encriptar todas las contraseñas usando algoritmos seguros (bcrypt, Argon2).
- El sistema debe requerir contraseñas con mínimo 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales.
- El sistema debe validar la fortaleza de contraseñas antes de almacenarlas.
- El sistema nunca debe almacenar contraseñas en texto plano.
- El sistema debe implementar políticas de expiración de contraseñas (opcional, según configuración).

#### RNF-03: Control de Acceso Basado en Roles
**Descripción:** El sistema debe contar con un control de acceso basado en roles (RBAC).  
**Detalles:**
- El sistema debe implementar RBAC de forma consistente en todas las capas (frontend, backend, base de datos).
- El sistema debe validar permisos en cada solicitud antes de procesarla.
- El sistema debe implementar principios de menor privilegio (cada usuario solo tiene los permisos necesarios).
- El sistema debe permitir auditoría de permisos y accesos.

#### RNF-04: Protección contra Ataques
**Descripción:** El sistema debe implementar protecciones contra ataques comunes.  
**Detalles:**
- El sistema debe implementar protección contra ataques de fuerza bruta (límite de intentos de login).
- El sistema debe implementar protección CSRF (Cross-Site Request Forgery).
- El sistema debe implementar protección XSS (Cross-Site Scripting).
- El sistema debe validar y sanitizar todas las entradas del usuario.
- El sistema debe implementar rate limiting para prevenir abuso de APIs.

#### RNF-05: Autenticación JWT
**Descripción:** El sistema debe utilizar autenticación mediante tokens JWT.  
**Detalles:**
- El sistema debe generar tokens JWT con tiempo de expiración apropiado.
- El sistema debe implementar refresh tokens para renovar tokens de acceso.
- El sistema debe invalidar tokens cuando el usuario cierra sesión.
- El sistema debe validar la firma y expiración de tokens en cada solicitud.

---

### ⚡ 2. RENDIMIENTO

#### RNF-06: Tiempo de Respuesta de Búsqueda Semántica
**Descripción:** La búsqueda semántica debe realizar una consulta en menos de 1 minuto.  
**Detalles:**
- El sistema debe optimizar la generación de embeddings para reducir tiempos.
- El sistema debe utilizar caché para embeddings de consultas similares.
- El sistema debe optimizar las consultas vectoriales en la base de datos.
- El sistema debe limitar el número de envíos procesados en cada búsqueda (máximo 300).
- El sistema debe proporcionar feedback al usuario durante búsquedas largas.

#### RNF-07: Tamaño Máximo de Archivos Excel
**Descripción:** La carga del archivo Excel no debe exceder a 15 MB.  
**Detalles:**
- El sistema debe validar el tamaño del archivo antes de procesarlo.
- El sistema debe rechazar archivos que excedan el límite con mensaje de error claro.
- El sistema debe optimizar el procesamiento de archivos grandes.
- El sistema debe proporcionar recomendaciones para reducir el tamaño del archivo.

#### RNF-08: Paginación y Optimización de Consultas
**Descripción:** El sistema debe implementar paginación eficiente y optimizar consultas.  
**Detalles:**
- El sistema debe paginar todos los listados para evitar cargar grandes volúmenes de datos.
- El sistema debe utilizar índices en la base de datos para optimizar consultas frecuentes.
- El sistema debe implementar lazy loading y select_related/prefetch_related donde sea apropiado.
- El sistema debe limitar el número de resultados retornados por defecto.

#### RNF-09: Caché de Datos
**Descripción:** El sistema debe implementar caché para mejorar el rendimiento.  
**Detalles:**
- El sistema debe cachear embeddings de consultas similares.
- El sistema debe cachear datos frecuentemente consultados (listas de ubicaciones, estadísticas).
- El sistema debe implementar invalidación de caché cuando los datos cambian.
- El sistema debe utilizar caché distribuido en producción (Redis, Memcached).

---

### 🛠️ 3. ARQUITECTURA Y TECNOLOGÍA

#### RNF-10: Framework Frontend
**Descripción:** La interfaz debe ser desarrollada con el Framework Frontend React.  
**Detalles:**
- El sistema debe utilizar React como framework principal del frontend.
- El sistema debe utilizar TypeScript para tipado estático.
- El sistema debe seguir mejores prácticas de React (componentes funcionales, hooks).
- El sistema debe implementar un sistema de enrutamiento (React Router).
- El sistema debe utilizar un sistema de gestión de estado (Redux, Context API, o similar).

#### RNF-11: Framework Backend
**Descripción:** El sistema debe ser desarrollado con el Framework Backend Django.  
**Detalles:**
- El sistema debe utilizar Django como framework principal del backend.
- El sistema debe utilizar Django REST Framework para la construcción de APIs REST.
- El sistema debe seguir la arquitectura en capas (Views, Services, Repositories, Models).
- El sistema debe utilizar migraciones de Django para gestión de esquema de base de datos.
- El sistema debe implementar serializers para validación y transformación de datos.

#### RNF-12: Arquitectura en Capas
**Descripción:** El sistema cumple una arquitectura del sistema por capas.  
**Detalles:**
- El sistema debe separar responsabilidades en capas: Presentación (Views), Lógica de Negocio (Services), Acceso a Datos (Repositories), Modelos (Models).
- Cada capa debe tener responsabilidades claramente definidas.
- Las capas superiores no deben acceder directamente a capas inferiores (ej: Views no deben acceder directamente a Models).
- El sistema debe utilizar el patrón Repository para abstraer el acceso a datos.
- El sistema debe utilizar el patrón Service para encapsular lógica de negocio.

#### RNF-13: Integración con Supabase
**Descripción:** El sistema debe integrarse nativamente con Supabase.  
**Detalles:**
- El sistema debe utilizar Supabase como base de datos principal (PostgreSQL).
- El sistema debe utilizar Supabase Storage para almacenamiento de archivos.
- El sistema debe utilizar pgvector (extensión de PostgreSQL) para búsqueda vectorial.
- El sistema debe configurar conexiones seguras a Supabase.
- El sistema debe utilizar las características nativas de Supabase cuando sea apropiado.

#### RNF-14: Consumo de APIs Externas
**Descripción:** El sistema debe permitir el consumo de APIs externas.  
**Detalles:**
- El sistema debe integrarse con APIs de OpenAI para generación de embeddings.
- El sistema debe manejar errores y timeouts de APIs externas de forma apropiada.
- El sistema debe implementar retry logic para llamadas fallidas.
- El sistema debe registrar costos y uso de APIs externas.
- El sistema debe permitir configurar endpoints y credenciales de APIs externas.

---

### 🌐 4. COMPATIBILIDAD Y ACCESIBILIDAD

#### RNF-15: Compatibilidad con Navegadores
**Descripción:** El sistema debe ser compatible con los principales navegadores modernos.  
**Detalles:**
- El sistema debe funcionar correctamente en Chrome, Firefox, Safari, Edge (últimas 2 versiones).
- El sistema debe utilizar características web estándar y evitar dependencias de navegadores específicos.
- El sistema debe probarse en diferentes navegadores antes de desplegar.
- El sistema debe proporcionar mensajes de error apropiados para navegadores no soportados.

#### RNF-16: Diseño Responsivo
**Descripción:** El sistema debe ser accesible desde dispositivos móviles y tablets.  
**Detalles:**
- El sistema debe adaptarse a diferentes tamaños de pantalla (responsive design).
- El sistema debe ser usable en dispositivos móviles (teléfonos y tablets).
- El sistema debe optimizar la experiencia de usuario para touch en dispositivos móviles.
- El sistema debe probarse en diferentes dispositivos y resoluciones.

#### RNF-17: Accesibilidad Web
**Descripción:** El sistema debe seguir estándares de accesibilidad web.  
**Detalles:**
- El sistema debe cumplir con estándares WCAG 2.1 nivel AA (mínimo).
- El sistema debe proporcionar alternativas de texto para imágenes.
- El sistema debe ser navegable mediante teclado.
- El sistema debe tener suficiente contraste de colores para legibilidad.

---

### 📦 5. GESTIÓN Y DEPLOYMENT

#### RNF-18: Repositorio en Línea
**Descripción:** El sistema debe alojarse en un repositorio en línea.  
**Detalles:**
- El sistema debe estar versionado usando Git.
- El sistema debe estar alojado en un repositorio remoto (GitHub, GitLab, Bitbucket).
- El sistema debe utilizar ramas para desarrollo, staging y producción.
- El sistema debe implementar pull requests y code reviews.
- El sistema debe mantener un historial de commits claro y descriptivo.

#### RNF-19: Documentación de API
**Descripción:** El sistema debe proporcionar documentación completa de la API.  
**Detalles:**
- El sistema debe generar documentación automática usando OpenAPI/Swagger.
- El sistema debe proporcionar ejemplos de uso para cada endpoint.
- El sistema debe documentar parámetros, respuestas y códigos de error.
- El sistema debe estar accesible en `/api/docs/` y `/api/redoc/`.

#### RNF-20: Logs en Tiempo Real
**Descripción:** El sistema debe tener registros de log en tiempo real.  
**Detalles:**
- El sistema debe registrar logs de todas las operaciones importantes.
- El sistema debe utilizar niveles de log apropiados (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- El sistema debe formatear logs de forma estructurada (JSON preferiblemente).
- El sistema debe permitir filtrar y buscar en logs.
- El sistema debe rotar logs para evitar llenar el disco.

#### RNF-21: Manejo de Errores
**Descripción:** El sistema debe manejar errores de forma apropiada.  
**Detalles:**
- El sistema debe capturar y manejar todos los errores sin exponer información sensible.
- El sistema debe retornar mensajes de error claros y útiles para el usuario.
- El sistema debe registrar errores en logs para debugging.
- El sistema debe implementar un manejador de excepciones centralizado.
- El sistema debe retornar códigos de estado HTTP apropiados.

#### RNF-22: Validación de Datos
**Descripción:** El sistema debe validar todos los datos de entrada.  
**Detalles:**
- El sistema debe validar datos en el frontend (validación del cliente).
- El sistema debe validar datos en el backend (validación del servidor, nunca confiar solo en el cliente).
- El sistema debe retornar mensajes de error de validación claros y específicos.
- El sistema debe validar tipos de datos, rangos, formatos y reglas de negocio.

#### RNF-23: Internacionalización
**Descripción:** El sistema debe soportar múltiples idiomas (opcional, preparado para futuro).  
**Detalles:**
- El sistema debe estar preparado para internacionalización (i18n).
- El sistema debe utilizar archivos de traducción para textos de la interfaz.
- El sistema debe detectar el idioma del navegador del usuario.
- El sistema debe permitir cambiar el idioma manualmente.

---

### 🔄 6. MANTENIBILIDAD Y ESCALABILIDAD

#### RNF-24: Código Mantenible
**Descripción:** El código debe ser mantenible y seguir mejores prácticas.  
**Detalles:**
- El código debe seguir convenciones de estilo (PEP 8 para Python, ESLint para JavaScript/TypeScript).
- El código debe estar documentado con comentarios y docstrings apropiados.
- El código debe ser modular y reutilizable.
- El código debe seguir principios SOLID y DRY (Don't Repeat Yourself).

#### RNF-25: Pruebas
**Descripción:** El sistema debe incluir pruebas automatizadas.  
**Detalles:**
- El sistema debe incluir pruebas unitarias para lógica de negocio crítica.
- El sistema debe incluir pruebas de integración para APIs.
- El sistema debe mantener una cobertura de pruebas razonable (mínimo 70%).
- El sistema debe ejecutar pruebas automáticamente en CI/CD.

#### RNF-26: Escalabilidad
**Descripción:** El sistema debe ser escalable para manejar crecimiento futuro.  
**Detalles:**
- El sistema debe estar diseñado para manejar aumento de usuarios y datos.
- El sistema debe utilizar bases de datos optimizadas para búsquedas vectoriales (pgvector).
- El sistema debe estar preparado para horizontal scaling si es necesario.
- El sistema debe monitorear rendimiento y optimizar cuellos de botella.

---

## 📊 RESUMEN DE REQUISITOS

### Requisitos Funcionales: 47
- Gestión de Autenticación y Usuarios: 7
- Gestión de Envíos: 9
- Gestión de Productos: 4
- Gestión de Archivos Excel: 4
- Búsqueda Tradicional: 2
- Búsqueda Semántica: 7
- Reportes y Estadísticas: 5
- Sistema de Notificaciones: 3
- Gestión de Ubicaciones Geográficas: 2
- Gestión de Tarifas: 2
- Auditoría y Logs: 2

### Requisitos No Funcionales: 26
- Seguridad: 5
- Rendimiento: 4
- Arquitectura y Tecnología: 5
- Compatibilidad y Accesibilidad: 3
- Gestión y Deployment: 4
- Mantenibilidad y Escalabilidad: 3

### **TOTAL: 73 REQUISITOS**

---

## 📝 NOTAS ADICIONALES

1. **Priorización:** Los requisitos están organizados por categoría, pero pueden priorizarse según necesidades del proyecto (MVP vs. funcionalidades completas).

2. **Evolución:** Este documento debe actualizarse conforme el sistema evoluciona y se agregan nuevas funcionalidades.

3. **Trazabilidad:** Cada requisito debe estar vinculado a casos de prueba y documentación técnica correspondiente.

4. **Validación:** Todos los requisitos deben ser validados con stakeholders antes de la implementación.

---

**Documento generado:** 2024  
**Última actualización:** 2024  
**Versión:** 2.0


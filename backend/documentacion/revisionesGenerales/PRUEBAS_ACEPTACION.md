# ✅ PRUEBAS DE ACEPTACIÓN

## 📌 INFORMACIÓN GENERAL

**Sistema:** Sistema de Gestión de Envíos con Búsqueda Semántica  
**Versión del Documento:** 1.0  
**Fecha:** Enero 2026  
**Alcance:** Pruebas de aceptación para todas las historias de usuario y técnicas

---

## 📋 PRUEBAS DE ACEPTACIÓN - HISTORIAS DE USUARIO

### US-01: Inicio de sesión

#### PA-US-01-01: Inicio de sesión exitoso
**Descripción:** Verificar que un usuario puede iniciar sesión con credenciales válidas.

**Pasos:**
1. Acceder al endpoint `/api/auth/login/`
2. Enviar credenciales válidas (username y contraseña)
3. Verificar respuesta exitosa

**Resultado Esperado:**
- Status code: 200 OK
- Response contiene `access` y `refresh` tokens
- Los tokens son válidos y pueden usarse para autenticación

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-01-02: Bloqueo después de intentos fallidos
**Descripción:** Verificar que el sistema bloquea el acceso después de 5 intentos fallidos.

**Pasos:**
1. Intentar iniciar sesión con credenciales incorrectas 5 veces consecutivas
2. Intentar iniciar sesión con credenciales correctas inmediatamente después
3. Esperar 15 minutos
4. Intentar iniciar sesión con credenciales correctas nuevamente

**Resultado Esperado:**
- Después de 5 intentos fallidos, el sistema retorna error 429 (Too Many Requests)
- El mensaje indica que la cuenta está bloqueada temporalmente
- Después de 15 minutos, el usuario puede iniciar sesión exitosamente

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-01-03: Usuario desactivado no puede iniciar sesión
**Descripción:** Verificar que usuarios desactivados no pueden iniciar sesión.

**Pasos:**
1. Desactivar un usuario en el sistema
2. Intentar iniciar sesión con las credenciales de ese usuario

**Resultado Esperado:**
- Status code: 403 Forbidden o 401 Unauthorized
- Mensaje de error indica que el usuario está desactivado

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-01-04: Registro de intentos de inicio de sesión
**Descripción:** Verificar que todos los intentos de inicio de sesión se registran en logs.

**Pasos:**
1. Realizar varios intentos de inicio de sesión (exitosos y fallidos)
2. Consultar los logs del sistema

**Resultado Esperado:**
- Todos los intentos aparecen en los logs con: usuario, fecha/hora, resultado (éxito/fallo), IP
- Los logs están en formato estructurado (JSON)

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-02: Asignar roles

#### PA-US-02-01: Administrador puede asignar cualquier rol
**Descripción:** Verificar que un administrador puede asignar cualquier rol a un usuario.

**Pasos:**
1. Autenticarse como administrador
2. Crear o actualizar un usuario asignando diferentes roles (Gerente, Digitador, Comprador)
3. Verificar que el rol se asigna correctamente

**Resultado Esperado:**
- El sistema permite asignar cualquier rol
- El rol se guarda correctamente en la base de datos
- El usuario tiene los permisos correspondientes a su rol

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-02-02: Solo administrador puede asignar rol de administrador
**Descripción:** Verificar que solo un administrador puede asignar el rol de administrador.

**Pasos:**
1. Autenticarse como gerente
2. Intentar asignar rol de administrador a un usuario
3. Autenticarse como administrador
4. Asignar rol de administrador a un usuario

**Resultado Esperado:**
- Gerente recibe error 403 Forbidden al intentar asignar rol de administrador
- Administrador puede asignar rol de administrador exitosamente

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-02-03: Registro de cambios de rol en auditoría
**Descripción:** Verificar que los cambios de rol se registran en el log de auditoría.

**Pasos:**
1. Autenticarse como administrador
2. Cambiar el rol de un usuario
3. Consultar el log de auditoría

**Resultado Esperado:**
- El cambio de rol aparece en el log con: usuario que realizó el cambio, usuario modificado, rol anterior, rol nuevo, fecha/hora

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-03: Registrar envíos

#### PA-US-03-01: Crear envío con datos válidos
**Descripción:** Verificar que se puede crear un envío con todos los datos requeridos.

**Pasos:**
1. Autenticarse como digitador o comprador
2. Crear un envío con: HAWB único, comprador válido, productos, observaciones
3. Verificar que el envío se crea correctamente

**Resultado Esperado:**
- Status code: 201 Created
- El envío se guarda en la base de datos con todos los datos
- Los totales (peso, cantidad, valor) se calculan automáticamente
- El costo del servicio se calcula según las tarifas aplicables
- Se genera un embedding automáticamente para búsqueda semántica

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-03-02: Validar HAWB único
**Descripción:** Verificar que no se pueden crear envíos con HAWB duplicado.

**Pasos:**
1. Crear un envío con HAWB "ABC123"
2. Intentar crear otro envío con el mismo HAWB "ABC123"

**Resultado Esperado:**
- El segundo intento retorna error 400 Bad Request
- Mensaje de error indica que el HAWB ya existe

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-03-03: Validar cupo anual del comprador
**Descripción:** Verificar que no se pueden crear envíos si el comprador excede su cupo anual.

**Pasos:**
1. Crear un comprador con cupo anual de 100 kg
2. Crear envíos que sumen 99 kg
3. Intentar crear un envío de 5 kg

**Resultado Esperado:**
- El sistema valida el cupo antes de crear el envío
- Si excede el cupo, retorna error 400 Bad Request
- Mensaje de error indica el cupo disponible y el cupo requerido

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-03-04: Generación automática de embedding
**Descripción:** Verificar que se genera un embedding automáticamente al crear un envío.

**Pasos:**
1. Crear un envío con información completa
2. Consultar la tabla de embeddings en la base de datos

**Resultado Esperado:**
- Existe un registro en la tabla de embeddings asociado al envío
- El embedding tiene las dimensiones correctas (1536 para text-embedding-3-small)
- El embedding se puede usar para búsqueda semántica

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-04: Actualizar envíos

#### PA-US-04-01: Actualizar información de envío
**Descripción:** Verificar que se puede actualizar la información de un envío.

**Pasos:**
1. Autenticarse como digitador o comprador
2. Obtener un envío existente
3. Actualizar campos como observaciones, fecha de emisión
4. Verificar que los cambios se guardan

**Resultado Esperado:**
- Status code: 200 OK
- Los cambios se guardan correctamente en la base de datos
- El embedding se actualiza automáticamente si cambia información relevante

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-04-02: Recalcular totales al modificar productos
**Descripción:** Verificar que los totales se recalculan automáticamente al modificar productos.

**Pasos:**
1. Obtener un envío con productos
2. Agregar un nuevo producto al envío
3. Verificar los totales del envío

**Resultado Esperado:**
- Los totales (peso, cantidad, valor) se recalculan automáticamente
- El costo del servicio se recalcula según las nuevas tarifas

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-04-03: Comprador solo puede modificar sus propios envíos
**Descripción:** Verificar que un comprador no puede modificar envíos de otros compradores.

**Pasos:**
1. Autenticarse como comprador A
2. Intentar actualizar un envío del comprador B

**Resultado Esperado:**
- Status code: 403 Forbidden o 404 Not Found
- Mensaje de error indica que no tiene permisos para modificar ese envío

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-05: Eliminar envíos

#### PA-US-05-01: Eliminar envío con confirmación
**Descripción:** Verificar que se puede eliminar un envío con confirmación previa.

**Pasos:**
1. Autenticarse como digitador o administrador
2. Obtener un envío existente
3. Eliminar el envío
4. Verificar que el envío se elimina (lógica o físicamente)

**Resultado Esperado:**
- Status code: 204 No Content o 200 OK
- El envío se elimina de la base de datos (o se marca como eliminado)
- Los productos asociados también se eliminan o desactivan
- La eliminación se registra en el log de auditoría

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-05-02: Validar permisos para eliminar
**Descripción:** Verificar que solo usuarios con permisos pueden eliminar envíos.

**Pasos:**
1. Autenticarse como comprador
2. Intentar eliminar un envío

**Resultado Esperado:**
- Status code: 403 Forbidden
- Mensaje de error indica que no tiene permisos para eliminar envíos

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-06: Visualizar envíos

#### PA-US-06-01: Listar envíos con paginación
**Descripción:** Verificar que se pueden listar envíos con paginación.

**Pasos:**
1. Autenticarse como usuario
2. Acceder al endpoint de listado de envíos
3. Verificar la respuesta paginada

**Resultado Esperado:**
- Status code: 200 OK
- Response contiene: `count`, `next`, `previous`, `results`
- Por defecto se muestran 10 elementos por página
- Se puede configurar el tamaño de página mediante parámetros

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-06-02: Filtros automáticos por rol
**Descripción:** Verificar que los filtros se aplican automáticamente según el rol.

**Pasos:**
1. Autenticarse como comprador
2. Listar envíos
3. Autenticarse como gerente
4. Listar envíos

**Resultado Esperado:**
- Comprador solo ve sus propios envíos
- Gerente ve todos los envíos del sistema

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-06-03: Filtrar por múltiples criterios
**Descripción:** Verificar que se pueden aplicar múltiples filtros simultáneamente.

**Pasos:**
1. Autenticarse como usuario
2. Listar envíos con filtros: estado="Entregado", fechaDesde="2025-01-01", fechaHasta="2025-01-31", ciudad="Quito"

**Resultado Esperado:**
- Status code: 200 OK
- Solo se retornan envíos que cumplen TODOS los filtros aplicados
- Los resultados están correctamente filtrados

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-06-04: Ordenar resultados
**Descripción:** Verificar que se pueden ordenar los resultados por diferentes campos.

**Pasos:**
1. Listar envíos ordenados por fecha (ascendente)
2. Listar envíos ordenados por valor (descendente)
3. Listar envíos ordenados por peso

**Resultado Esperado:**
- Los resultados se ordenan correctamente según el parámetro especificado
- Se puede ordenar por: fecha, estado, valor, peso

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-07: Historial de envíos

#### PA-US-07-01: Consultar historial de cambios de estado
**Descripción:** Verificar que se puede consultar el historial de cambios de estado de un envío.

**Pasos:**
1. Obtener un envío que haya tenido cambios de estado
2. Consultar el historial del envío
3. Verificar que se muestran todos los cambios

**Resultado Esperado:**
- Se muestran todos los cambios de estado con: fecha, hora, usuario que realizó el cambio, estado anterior, estado nuevo
- Los cambios están ordenados cronológicamente (más reciente primero)

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-07-02: Filtrar historial por tipo de cambio
**Descripción:** Verificar que se puede filtrar el historial por tipo de cambio.

**Pasos:**
1. Consultar historial de un envío
2. Filtrar solo cambios de estado
3. Filtrar solo cambios de productos

**Resultado Esperado:**
- Los filtros funcionan correctamente
- Solo se muestran los cambios del tipo especificado

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-08: Carga de envíos por archivo Excel

#### PA-US-08-01: Cargar archivo Excel válido
**Descripción:** Verificar que se puede cargar y procesar un archivo Excel válido.

**Pasos:**
1. Autenticarse como digitador o administrador
2. Cargar un archivo Excel (.xlsx) con formato correcto
3. Verificar que el sistema procesa el archivo

**Resultado Esperado:**
- Status code: 200 OK o 202 Accepted
- El sistema valida la estructura del archivo
- El sistema muestra un resumen de los datos a importar
- El archivo se almacena en Supabase Storage

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-08-02: Validar estructura del archivo
**Descripción:** Verificar que el sistema valida la estructura del archivo Excel.

**Pasos:**
1. Cargar un archivo Excel sin las columnas requeridas
2. Cargar un archivo Excel con formato incorrecto

**Resultado Esperado:**
- Status code: 400 Bad Request
- Mensaje de error indica qué columnas faltan o están incorrectas
- El sistema no procesa el archivo

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-08-03: Validar tamaño máximo del archivo
**Descripción:** Verificar que el sistema rechaza archivos que exceden el tamaño máximo.

**Pasos:**
1. Intentar cargar un archivo Excel de más de 15 MB

**Resultado Esperado:**
- Status code: 400 Bad Request
- Mensaje de error indica que el archivo excede el tamaño máximo permitido

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-08-04: Validar reglas de negocio en importación
**Descripción:** Verificar que el sistema valida reglas de negocio durante la importación.

**Pasos:**
1. Cargar un archivo Excel con HAWB duplicado
2. Cargar un archivo Excel con comprador inexistente
3. Verificar los errores reportados

**Resultado Esperado:**
- El sistema reporta errores específicos para cada registro inválido
- El sistema muestra resumen: número de registros válidos, número de errores
- Se puede confirmar o cancelar la importación

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-08-05: Confirmar importación
**Descripción:** Verificar que se pueden importar los datos después de la validación.

**Pasos:**
1. Cargar un archivo Excel válido
2. Revisar el resumen de datos
3. Confirmar la importación

**Resultado Esperado:**
- Los envíos se crean correctamente en la base de datos
- Se generan embeddings para los nuevos envíos
- Se registra la importación con metadatos: fecha, usuario, número de registros, estado

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-09: Descargar reportes de envíos

#### PA-US-09-01: Exportar a Excel
**Descripción:** Verificar que se puede exportar envíos a formato Excel.

**Pasos:**
1. Aplicar filtros a la lista de envíos
2. Exportar a Excel
3. Descargar el archivo

**Resultado Esperado:**
- Se genera un archivo .xlsx
- El archivo contiene todos los envíos que cumplen los filtros aplicados
- El archivo tiene formato profesional con encabezados, estilos y filtros automáticos

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-09-02: Exportar a PDF
**Descripción:** Verificar que se puede exportar envíos a formato PDF.

**Pasos:**
1. Aplicar filtros a la lista de envíos
2. Exportar a PDF
3. Descargar el archivo

**Resultado Esperado:**
- Se genera un archivo PDF
- El archivo contiene todos los envíos que cumplen los filtros aplicados
- El PDF tiene formato profesional listo para impresión
- El PDF incluye resúmenes de totales (peso total, valor total, costo total)

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-09-03: Exportar a CSV
**Descripción:** Verificar que se puede exportar envíos a formato CSV.

**Pasos:**
1. Aplicar filtros a la lista de envíos
2. Exportar a CSV
3. Descargar el archivo

**Resultado Esperado:**
- Se genera un archivo CSV
- El archivo tiene codificación UTF-8
- El archivo es compatible con Excel y otros programas de hojas de cálculo

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-10: Búsqueda semántica

#### PA-US-10-01: Búsqueda semántica básica
**Descripción:** Verificar que se puede realizar una búsqueda semántica usando lenguaje natural.

**Pasos:**
1. Autenticarse como usuario
2. Realizar búsqueda semántica con texto: "envíos entregados en Quito"
3. Verificar los resultados

**Resultado Esperado:**
- Status code: 200 OK
- Se retornan envíos relevantes ordenados por relevancia semántica
- Cada resultado tiene una puntuación de similitud
- El tiempo de respuesta es menor a 1 minuto

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-10-02: Generación de embedding de consulta
**Descripción:** Verificar que se genera un embedding para la consulta del usuario.

**Pasos:**
1. Realizar una búsqueda semántica
2. Verificar en los logs que se generó un embedding para la consulta

**Resultado Esperado:**
- Se genera un embedding de la consulta usando OpenAI
- El embedding tiene las dimensiones correctas (1536 para text-embedding-3-small)
- El costo y tokens utilizados se registran

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-10-03: Búsqueda por similitud coseno
**Descripción:** Verificar que la búsqueda utiliza similitud coseno para encontrar envíos relevantes.

**Pasos:**
1. Realizar búsqueda semántica con consulta específica
2. Verificar que los resultados están ordenados por score de similitud (mayor a menor)

**Resultado Esperado:**
- Los resultados están ordenados por relevancia semántica
- Los envíos más relevantes aparecen primero
- Se aplica un umbral mínimo de similitud (ej: 0.28) para filtrar resultados poco relevantes

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-10-04: Normalización de texto
**Descripción:** Verificar que el texto de la consulta se normaliza antes de generar el embedding.

**Pasos:**
1. Realizar búsquedas con diferentes formatos: "ENVÍOS QUITO", "envíos quito", "Envíos Quito"
2. Verificar que los resultados son consistentes

**Resultado Esperado:**
- El sistema normaliza el texto (minúsculas, limpieza de caracteres especiales)
- Los resultados son consistentes independientemente del formato de entrada

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-10-05: Tiempo de respuesta
**Descripción:** Verificar que el tiempo de respuesta de la búsqueda es menor a 1 minuto.

**Pasos:**
1. Realizar búsqueda semántica
2. Medir el tiempo de respuesta

**Resultado Esperado:**
- El tiempo de respuesta es menor a 60 segundos
- El sistema procesa eficientemente incluso con muchos envíos en la base de datos

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-11: Búsqueda semántica con parámetros

#### PA-US-11-01: Filtrar por fecha
**Descripción:** Verificar que se pueden aplicar filtros de fecha a la búsqueda semántica.

**Pasos:**
1. Realizar búsqueda semántica con filtros: fechaDesde="2025-01-01", fechaHasta="2025-01-31"
2. Verificar que solo se retornan envíos en ese rango de fechas

**Resultado Esperado:**
- Solo se retornan envíos que cumplen el filtro de fecha
- Los resultados mantienen el orden por relevancia semántica

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-11-02: Filtrar por estado
**Descripción:** Verificar que se pueden aplicar filtros de estado a la búsqueda semántica.

**Pasos:**
1. Realizar búsqueda semántica con filtro: estado="Entregado"
2. Verificar que solo se retornan envíos con ese estado

**Resultado Esperado:**
- Solo se retornan envíos con el estado especificado
- Los resultados mantienen el orden por relevancia semántica

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-11-03: Filtrar por comprador
**Descripción:** Verificar que se pueden aplicar filtros de comprador a la búsqueda semántica.

**Pasos:**
1. Realizar búsqueda semántica con filtro de comprador específico
2. Verificar que solo se retornan envíos de ese comprador

**Resultado Esperado:**
- Solo se retornan envíos del comprador especificado
- Los resultados mantienen el orden por relevancia semántica

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-11-04: Filtrar por ubicación
**Descripción:** Verificar que se pueden aplicar filtros de ubicación a la búsqueda semántica.

**Pasos:**
1. Realizar búsqueda semántica con filtro: ciudadDestino="Quito"
2. Verificar que solo se retornan envíos con esa ciudad destino

**Resultado Esperado:**
- Solo se retornan envíos con la ubicación especificada
- Los resultados mantienen el orden por relevancia semántica

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-11-05: Combinar múltiples filtros
**Descripción:** Verificar que se pueden combinar múltiples filtros simultáneamente.

**Pasos:**
1. Realizar búsqueda semántica con múltiples filtros: fechaDesde, fechaHasta, estado, ciudadDestino
2. Verificar que solo se retornan envíos que cumplen TODOS los filtros

**Resultado Esperado:**
- Solo se retornan envíos que cumplen todos los filtros aplicados
- Los resultados mantienen el orden por relevancia semántica

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-11-06: Configurar límite de resultados
**Descripción:** Verificar que se puede configurar el número máximo de resultados.

**Pasos:**
1. Realizar búsqueda semántica con limite=10
2. Realizar búsqueda semántica con limite=50

**Resultado Esperado:**
- Se retornan exactamente el número de resultados especificado (o menos si hay menos resultados disponibles)
- El límite funciona correctamente

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-11-07: Respetar permisos por rol
**Descripción:** Verificar que los filtros respetan los límites de permisos según el rol.

**Pasos:**
1. Autenticarse como comprador
2. Realizar búsqueda semántica
3. Verificar que solo ve sus propios envíos

**Resultado Esperado:**
- Comprador solo ve envíos que le pertenecen, independientemente de los filtros aplicados
- Gerente y administrador ven todos los envíos que cumplen los filtros

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-12: Detalle de los envíos

#### PA-US-12-01: Consultar detalle de envío
**Descripción:** Verificar que se puede consultar el detalle completo de un envío.

**Pasos:**
1. Autenticarse como usuario
2. Obtener el detalle de un envío por ID
3. Verificar la información mostrada

**Resultado Esperado:**
- Status code: 200 OK
- Se muestra información completa: HAWB, comprador, productos, totales, estado, observaciones, fechas
- Se muestra historial de cambios de estado si existe

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-12-02: Validar permisos para ver detalle
**Descripción:** Verificar que un comprador solo puede ver sus propios envíos.

**Pasos:**
1. Autenticarse como comprador A
2. Intentar obtener el detalle de un envío del comprador B

**Resultado Esperado:**
- Status code: 403 Forbidden o 404 Not Found
- Mensaje de error indica que no tiene permisos para ver ese envío

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-12-03: Mostrar productos asociados
**Descripción:** Verificar que se muestran todos los productos asociados al envío.

**Pasos:**
1. Obtener el detalle de un envío con múltiples productos
2. Verificar que se muestran todos los productos

**Resultado Esperado:**
- Se muestran todos los productos con: descripción, peso, cantidad, valor, categoría
- La información de productos es completa y precisa

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-13: Actualizar el estado de los envíos

#### PA-US-13-01: Cambiar estado de envío
**Descripción:** Verificar que se puede cambiar el estado de un envío.

**Pasos:**
1. Autenticarse como digitador o gerente
2. Cambiar el estado de un envío de "Pendiente" a "En Tránsito"
3. Verificar que el cambio se guarda

**Resultado Esperado:**
- Status code: 200 OK
- El estado se actualiza correctamente en la base de datos
- Se registra el cambio con fecha, hora y usuario que realizó el cambio

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-13-02: Validar transiciones de estado
**Descripción:** Verificar que solo se permiten transiciones de estado válidas.

**Pasos:**
1. Cambiar estado de un envío a "Entregado"
2. Intentar cambiar el estado de "Entregado" a "Pendiente"

**Resultado Esperado:**
- El segundo cambio retorna error 400 Bad Request
- Mensaje de error indica que la transición de estado no es válida

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-13-03: Generar notificaciones al cambiar estado
**Descripción:** Verificar que se generan notificaciones cuando cambia el estado de un envío.

**Pasos:**
1. Cambiar el estado de un envío de un comprador
2. Consultar las notificaciones del comprador

**Resultado Esperado:**
- Se crea una notificación para el comprador
- La notificación indica el cambio de estado
- La notificación incluye información del envío

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-13-04: Agregar observaciones al cambiar estado
**Descripción:** Verificar que se pueden agregar observaciones al cambiar el estado.

**Pasos:**
1. Cambiar el estado de un envío agregando observaciones
2. Verificar que las observaciones se guardan

**Resultado Esperado:**
- Las observaciones se guardan junto con el cambio de estado
- Las observaciones aparecen en el historial del envío

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-14: Canal de comunicación segura

#### PA-US-14-01: Comunicación HTTPS
**Descripción:** Verificar que todas las comunicaciones utilizan HTTPS en producción.

**Pasos:**
1. Acceder al sistema en producción
2. Verificar que la conexión es HTTPS
3. Intentar acceder mediante HTTP

**Resultado Esperado:**
- Todas las conexiones en producción son HTTPS
- Las conexiones HTTP se redirigen automáticamente a HTTPS
- Los certificados SSL/TLS son válidos

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-14-02: Protección CSRF
**Descripción:** Verificar que el sistema implementa protección CSRF.

**Pasos:**
1. Intentar realizar una solicitud POST sin token CSRF
2. Realizar una solicitud POST con token CSRF válido

**Resultado Esperado:**
- Solicitud sin token CSRF retorna error 403 Forbidden
- Solicitud con token CSRF válido se procesa correctamente

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-14-03: Protección XSS
**Descripción:** Verificar que el sistema sanitiza entradas para prevenir XSS.

**Pasos:**
1. Intentar ingresar código JavaScript en campos de texto
2. Verificar que el código no se ejecuta

**Resultado Esperado:**
- El código JavaScript se sanitiza y no se ejecuta
- Los caracteres especiales se escapan correctamente
- El sistema previene ataques XSS

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-15: Acceso por roles

#### PA-US-15-01: Permisos de administrador
**Descripción:** Verificar que un administrador tiene acceso completo a todas las funcionalidades.

**Pasos:**
1. Autenticarse como administrador
2. Acceder a diferentes endpoints del sistema
3. Verificar que tiene acceso a todo

**Resultado Esperado:**
- Administrador puede acceder a todos los endpoints
- Administrador puede gestionar usuarios, envíos, reportes, búsqueda semántica, etc.

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-15-02: Permisos de gerente
**Descripción:** Verificar que un gerente tiene acceso a funcionalidades de gestión pero no puede gestionar administradores.

**Pasos:**
1. Autenticarse como gerente
2. Intentar gestionar usuarios (crear, actualizar, eliminar)
3. Intentar gestionar administradores

**Resultado Esperado:**
- Gerente puede gestionar usuarios excepto administradores
- Gerente puede ver todos los envíos, estadísticas, reportes
- Gerente no puede crear o modificar administradores

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-15-03: Permisos de digitador
**Descripción:** Verificar que un digitador puede gestionar envíos pero tiene acceso limitado a usuarios.

**Pasos:**
1. Autenticarse como digitador
2. Intentar gestionar envíos
3. Intentar ver usuarios

**Resultado Esperado:**
- Digitador puede crear, actualizar, eliminar envíos
- Digitador puede ver compradores y otros digitadores
- Digitador no puede ver gerentes o administradores

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-15-04: Permisos de comprador
**Descripción:** Verificar que un comprador solo puede ver y gestionar sus propios envíos.

**Pasos:**
1. Autenticarse como comprador
2. Intentar ver envíos
3. Intentar ver envíos de otros compradores

**Resultado Esperado:**
- Comprador solo ve sus propios envíos
- Comprador puede gestionar productos en sus envíos
- Comprador no puede ver envíos de otros compradores
- Comprador no puede gestionar usuarios

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-15-05: Validación de permisos en endpoints
**Descripción:** Verificar que todos los endpoints validan permisos antes de procesar solicitudes.

**Pasos:**
1. Autenticarse como comprador
2. Intentar acceder a endpoints restringidos (gestión de usuarios, reportes administrativos)
3. Verificar las respuestas

**Resultado Esperado:**
- Endpoints restringidos retornan 403 Forbidden
- Mensajes de error son claros y apropiados
- El sistema valida permisos en cada solicitud

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-16: Restablecer contraseña

#### PA-US-16-01: Solicitar restablecimiento de contraseña
**Descripción:** Verificar que se puede solicitar restablecimiento de contraseña mediante correo.

**Pasos:**
1. Acceder al endpoint de restablecimiento de contraseña
2. Enviar correo electrónico válido
3. Verificar que se envía el correo

**Resultado Esperado:**
- Status code: 200 OK
- Se envía correo electrónico con enlace de recuperación
- El enlace contiene un token seguro con expiración de 24 horas

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-16-02: Validar correo electrónico
**Descripción:** Verificar que el sistema valida que el correo exista antes de enviar el enlace.

**Pasos:**
1. Solicitar restablecimiento con correo inexistente
2. Solicitar restablecimiento con correo existente

**Resultado Esperado:**
- Correo inexistente: se retorna mensaje genérico (por seguridad) pero no se envía correo
- Correo existente: se envía correo con enlace de recuperación

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-16-03: Establecer nueva contraseña
**Descripción:** Verificar que se puede establecer nueva contraseña mediante el enlace de recuperación.

**Pasos:**
1. Hacer clic en el enlace de recuperación del correo
2. Establecer nueva contraseña que cumpla los requisitos
3. Intentar iniciar sesión con la nueva contraseña

**Resultado Esperado:**
- Se puede establecer nueva contraseña mediante el enlace
- La nueva contraseña debe cumplir requisitos de seguridad
- Se puede iniciar sesión con la nueva contraseña
- El token de recuperación se invalida después de usarse

**Resultado Esperado:**
- Status code: 200 OK
- Se puede iniciar sesión con la nueva contraseña
- El token de recuperación se invalida después de usarse

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-16-04: Validar requisitos de contraseña
**Descripción:** Verificar que el sistema valida los requisitos de seguridad de la nueva contraseña.

**Pasos:**
1. Intentar establecer contraseña sin mayúsculas
2. Intentar establecer contraseña sin números
3. Intentar establecer contraseña con menos de 8 caracteres
4. Establecer contraseña que cumpla todos los requisitos

**Resultado Esperado:**
- Contraseñas que no cumplen requisitos retornan error 400 Bad Request
- Mensaje de error indica qué requisitos faltan
- Contraseña que cumple requisitos se acepta correctamente

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-16-05: Expiración del token
**Descripción:** Verificar que el token de recuperación expira después de 24 horas.

**Pasos:**
1. Solicitar restablecimiento de contraseña
2. Esperar más de 24 horas (o modificar fecha del token en BD)
3. Intentar usar el enlace de recuperación

**Resultado Esperado:**
- El enlace expirado retorna error 400 Bad Request
- Mensaje de error indica que el enlace ha expirado
- Se debe solicitar un nuevo enlace de recuperación

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### US-17: Registro de logs

#### PA-US-17-01: Registrar operaciones importantes
**Descripción:** Verificar que se registran todas las operaciones importantes en logs.

**Pasos:**
1. Realizar operaciones: crear envío, actualizar envío, eliminar envío, cambiar estado
2. Consultar los logs del sistema

**Resultado Esperado:**
- Todas las operaciones aparecen en los logs
- Los logs incluyen: usuario, operación, entidad, fecha/hora, detalles adicionales
- Los logs están en formato estructurado (JSON)

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-17-02: Niveles de log apropiados
**Descripción:** Verificar que se utilizan niveles de log apropiados.

**Pasos:**
1. Realizar diferentes tipos de operaciones
2. Verificar los niveles de log utilizados

**Resultado Esperado:**
- Operaciones normales: INFO
- Advertencias: WARNING
- Errores: ERROR
- Errores críticos: CRITICAL
- Información de debugging: DEBUG

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-17-03: Filtrar y buscar en logs
**Descripción:** Verificar que se pueden filtrar y buscar en logs.

**Pasos:**
1. Consultar logs filtrados por usuario
2. Consultar logs filtrados por tipo de operación
3. Consultar logs filtrados por fecha

**Resultado Esperado:**
- Los filtros funcionan correctamente
- Se pueden combinar múltiples filtros
- La búsqueda es eficiente incluso con muchos registros

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-17-04: Rotación de logs
**Descripción:** Verificar que los logs se rotan para evitar llenar el disco.

**Pasos:**
1. Generar muchos logs
2. Verificar que los logs antiguos se archivan o eliminan según configuración

**Resultado Esperado:**
- Los logs se rotan automáticamente cuando alcanzan un tamaño máximo
- Los logs antiguos se archivan o eliminan según configuración
- El sistema no se queda sin espacio en disco por logs

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-17-05: Registrar intentos de inicio de sesión
**Descripción:** Verificar que se registran todos los intentos de inicio de sesión.

**Pasos:**
1. Realizar varios intentos de inicio de sesión (exitosos y fallidos)
2. Consultar los logs

**Resultado Esperado:**
- Todos los intentos aparecen en los logs
- Los logs incluyen: usuario, IP, fecha/hora, resultado (éxito/fallo), motivo del fallo si aplica

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-17-06: Registrar cambios de estado de envíos
**Descripción:** Verificar que se registran todos los cambios de estado de envíos.

**Pasos:**
1. Cambiar el estado de varios envíos
2. Consultar los logs

**Resultado Esperado:**
- Todos los cambios de estado aparecen en los logs
- Los logs incluyen: envío (HAWB), estado anterior, estado nuevo, usuario que realizó el cambio, fecha/hora

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-US-17-07: Registrar importaciones de archivos Excel
**Descripción:** Verificar que se registran todas las importaciones de archivos Excel.

**Pasos:**
1. Importar varios archivos Excel
2. Consultar los logs

**Resultado Esperado:**
- Todas las importaciones aparecen en los logs
- Los logs incluyen: usuario, nombre del archivo, fecha, número de registros procesados, número de registros exitosos, número de errores, estado

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

## 📋 PRUEBAS DE ACEPTACIÓN - HISTORIAS TÉCNICAS

### UT-01: Requisitos del sistema

#### PA-UT-01-01: Documentación de requisitos funcionales
**Descripción:** Verificar que existe documentación completa de requisitos funcionales.

**Pasos:**
1. Consultar la documentación de requisitos funcionales
2. Verificar que cubre todas las funcionalidades principales

**Resultado Esperado:**
- Existe documentación completa de requisitos funcionales
- La documentación está actualizada y accesible
- La documentación cubre: autenticación, gestión de usuarios, gestión de envíos, búsqueda semántica, importación, reportes

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-01-02: Documentación de requisitos no funcionales
**Descripción:** Verificar que existe documentación completa de requisitos no funcionales.

**Pasos:**
1. Consultar la documentación de requisitos no funcionales
2. Verificar que cubre: rendimiento, seguridad, escalabilidad, usabilidad

**Resultado Esperado:**
- Existe documentación completa de requisitos no funcionales
- La documentación incluye: tiempos de respuesta esperados, requisitos de seguridad, requisitos de escalabilidad, requisitos de usabilidad

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### UT-02: Arquitectura del sistema

#### PA-UT-02-01: Implementación de arquitectura en capas
**Descripción:** Verificar que el sistema implementa arquitectura en capas correctamente.

**Pasos:**
1. Revisar la estructura del código
2. Verificar que las capas están separadas: Views, Services, Repositories, Models

**Resultado Esperado:**
- El código está organizado en capas claramente definidas
- Las capas superiores no acceden directamente a capas inferiores
- Views no acceden directamente a Models
- Se utiliza el patrón Repository para acceso a datos
- Se utiliza el patrón Service para lógica de negocio

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-02-02: Documentación de arquitectura
**Descripción:** Verificar que existe documentación de la arquitectura con diagramas.

**Pasos:**
1. Consultar la documentación de arquitectura
2. Verificar que incluye diagramas

**Resultado Esperado:**
- Existe documentación de arquitectura
- La documentación incluye diagramas de capas
- La documentación explica las responsabilidades de cada capa

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### UT-03: Modelo de procesos

#### PA-UT-03-01: Documentación de procesos principales
**Descripción:** Verificar que existe documentación de los procesos principales del sistema.

**Pasos:**
1. Consultar la documentación de procesos
2. Verificar que cubre: registro de envíos, búsqueda semántica, importación de Excel

**Resultado Esperado:**
- Existe documentación de procesos principales
- La documentación incluye diagramas de flujo
- La documentación explica cada paso del proceso

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-03-02: Documentación de interacciones entre componentes
**Descripción:** Verificar que se documentan las interacciones entre componentes.

**Pasos:**
1. Consultar la documentación de interacciones
2. Verificar que explica cómo interactúan los componentes

**Resultado Esperado:**
- Existe documentación de interacciones entre componentes
- La documentación incluye diagramas de secuencia o de componentes
- La documentación explica el flujo de datos entre componentes

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### UT-04: Generar texto indexado de envíos

#### PA-UT-04-01: Generación automática de texto indexado
**Descripción:** Verificar que se genera texto indexado automáticamente al crear un envío.

**Pasos:**
1. Crear un envío con información completa
2. Consultar el texto indexado en la base de datos

**Resultado Esperado:**
- Se genera texto indexado automáticamente
- El texto indexado incluye: HAWB, comprador (nombre, cédula, ubicación), productos (descripción, categoría), estado, observaciones, fechas
- El texto está normalizado y limpio

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-04-02: Actualización de texto indexado
**Descripción:** Verificar que se actualiza el texto indexado cuando se modifica un envío.

**Pasos:**
1. Crear un envío
2. Modificar información relevante del envío
3. Consultar el texto indexado actualizado

**Resultado Esperado:**
- El texto indexado se actualiza automáticamente
- El texto refleja los cambios realizados

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-04-03: Comando para regenerar texto indexado
**Descripción:** Verificar que existe un comando para regenerar texto indexado de envíos existentes.

**Pasos:**
1. Ejecutar comando de gestión para regenerar texto indexado
2. Verificar que se regenera para todos los envíos

**Resultado Esperado:**
- El comando regenera texto indexado para todos los envíos
- El comando muestra progreso durante la ejecución
- El comando maneja errores sin detener el proceso completo

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### UT-05: Generación de embeddings

#### PA-UT-05-01: Integración con API de OpenAI
**Descripción:** Verificar que el sistema se integra correctamente con la API de OpenAI.

**Pasos:**
1. Configurar credenciales de OpenAI
2. Generar un embedding de prueba
3. Verificar que se genera correctamente

**Resultado Esperado:**
- El sistema se conecta correctamente a la API de OpenAI
- Se genera embedding con las dimensiones correctas (1536 para text-embedding-3-small)
- El embedding se almacena en la base de datos

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-05-02: Generación automática de embeddings
**Descripción:** Verificar que se generan embeddings automáticamente al crear un envío.

**Pasos:**
1. Crear un envío
2. Verificar que se genera un embedding automáticamente

**Resultado Esperado:**
- Se genera embedding automáticamente
- El embedding se almacena en la base de datos usando pgvector
- El embedding tiene las dimensiones correctas

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-05-03: Manejo de errores y retry logic
**Descripción:** Verificar que el sistema maneja errores y implementa retry logic.

**Pasos:**
1. Simular error en la API de OpenAI (temporalmente desconectar)
2. Intentar generar embedding
3. Verificar que se reintenta (máximo 3 intentos)

**Resultado Esperado:**
- El sistema implementa retry logic (máximo 3 intentos)
- Los errores se manejan apropiadamente
- Los errores se registran en logs
- El sistema no bloquea la creación del envío si falla la generación de embedding

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-05-04: Registro de costos y uso de API
**Descripción:** Verificar que se registran costos y uso de la API de OpenAI.

**Pasos:**
1. Generar varios embeddings
2. Consultar los logs de uso de API

**Resultado Esperado:**
- Se registran: número de tokens utilizados, costo, modelo utilizado, fecha/hora
- Los registros están en formato estructurado
- Se pueden consultar estadísticas de uso y costo

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-05-05: Comando para generar embeddings de envíos existentes
**Descripción:** Verificar que existe un comando para generar embeddings de envíos existentes.

**Pasos:**
1. Ejecutar comando de gestión para generar embeddings
2. Verificar que se generan embeddings para todos los envíos sin embedding

**Resultado Esperado:**
- El comando genera embeddings para envíos existentes
- El comando procesa en lotes para optimizar rendimiento
- El comando muestra progreso durante la ejecución
- El comando maneja errores sin detener el proceso completo

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### UT-06: Generar texto indexado de envíos manuales

#### PA-UT-06-01: Comando para regenerar texto indexado
**Descripción:** Verificar que existe un comando para regenerar texto indexado de todos los envíos.

**Pasos:**
1. Ejecutar comando de gestión para regenerar texto indexado
2. Verificar que se regenera para todos los envíos

**Resultado Esperado:**
- El comando regenera texto indexado para todos los envíos
- El comando muestra progreso (número de envíos procesados)
- El comando maneja errores sin detener el proceso completo

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-06-02: Regenerar texto indexado de envíos específicos
**Descripción:** Verificar que se puede regenerar texto indexado de envíos específicos.

**Pasos:**
1. Ejecutar comando con filtro de ID de envío específico
2. Verificar que solo se regenera ese envío

**Resultado Esperado:**
- El comando permite especificar IDs de envíos
- Solo se regeneran los envíos especificados

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-06-03: Modo dry-run
**Descripción:** Verificar que el comando tiene modo dry-run para validar sin modificar.

**Pasos:**
1. Ejecutar comando en modo dry-run
2. Verificar que no se modifican datos pero se muestra qué se haría

**Resultado Esperado:**
- El modo dry-run muestra qué envíos se procesarían
- No se modifican datos en modo dry-run
- El modo dry-run es útil para validar antes de ejecutar

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### UT-07: Reporte de pruebas

#### PA-UT-07-01: Generar reportes de pruebas unitarias
**Descripción:** Verificar que se pueden generar reportes de pruebas unitarias.

**Pasos:**
1. Ejecutar pruebas unitarias
2. Generar reporte de pruebas

**Resultado Esperado:**
- Se genera reporte de pruebas unitarias
- El reporte incluye: número de pruebas ejecutadas, número de pruebas exitosas, número de pruebas fallidas, tiempo de ejecución
- El reporte está en formato legible (HTML, JSON, XML)

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-07-02: Generar reportes de pruebas de integración
**Descripción:** Verificar que se pueden generar reportes de pruebas de integración.

**Pasos:**
1. Ejecutar pruebas de integración
2. Generar reporte de pruebas

**Resultado Esperado:**
- Se genera reporte de pruebas de integración
- El reporte incluye información similar a pruebas unitarias
- El reporte está en formato legible

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### UT-08: Métricas de pruebas

#### PA-UT-08-01: Calcular cobertura de código
**Descripción:** Verificar que se calcula cobertura de código de las pruebas.

**Pasos:**
1. Ejecutar pruebas con herramienta de cobertura
2. Generar reporte de cobertura

**Resultado Esperado:**
- Se calcula cobertura de código
- El reporte muestra cobertura por módulo/componente
- El reporte está en formato HTML
- Se establece un umbral mínimo de cobertura (ej: 80%)

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-08-02: Alertar cuando cobertura está por debajo del umbral
**Descripción:** Verificar que el sistema alerta cuando la cobertura está por debajo del umbral.

**Pasos:**
1. Ejecutar pruebas con cobertura baja
2. Verificar que se genera alerta

**Resultado Esperado:**
- El sistema alerta cuando la cobertura está por debajo del umbral
- La alerta indica qué módulos tienen cobertura baja

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### UT-09: Comportamiento temporal

#### PA-UT-09-01: Medir tiempos de respuesta de endpoints
**Descripción:** Verificar que se miden tiempos de respuesta de endpoints críticos.

**Pasos:**
1. Realizar solicitudes a endpoints críticos
2. Medir tiempos de respuesta
3. Verificar que están dentro de los límites esperados

**Resultado Esperado:**
- Se miden tiempos de respuesta de endpoints críticos
- Los tiempos están documentados
- Los tiempos cumplen con los requisitos de rendimiento

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-09-02: Medir tiempo de respuesta de búsqueda semántica
**Descripción:** Verificar que el tiempo de respuesta de búsqueda semántica es menor a 1 minuto.

**Pasos:**
1. Realizar búsqueda semántica
2. Medir tiempo de respuesta
3. Verificar que es menor a 60 segundos

**Resultado Esperado:**
- El tiempo de respuesta de búsqueda semántica es menor a 60 segundos
- El tiempo se mide y documenta
- El sistema identifica cuellos de botella si el tiempo excede el límite

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-09-03: Generar reportes de rendimiento
**Descripción:** Verificar que se generan reportes de rendimiento con gráficos y estadísticas.

**Pasos:**
1. Ejecutar pruebas de rendimiento
2. Generar reporte de rendimiento

**Resultado Esperado:**
- Se genera reporte de rendimiento
- El reporte incluye gráficos y estadísticas
- El reporte identifica cuellos de botella

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### UT-10: Utilización de recursos

#### PA-UT-10-01: Monitorear uso de memoria
**Descripción:** Verificar que se monitorea el uso de memoria del servidor.

**Pasos:**
1. Ejecutar operaciones que consuman memoria
2. Consultar métricas de memoria

**Resultado Esperado:**
- Se monitorea uso de memoria (RAM)
- Las métricas se registran y documentan
- Se generan alertas cuando el uso excede umbrales

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-10-02: Monitorear uso de CPU
**Descripción:** Verificar que se monitorea el uso de CPU del servidor.

**Pasos:**
1. Ejecutar operaciones que consuman CPU
2. Consultar métricas de CPU

**Resultado Esperado:**
- Se monitorea uso de CPU
- Las métricas se registran y documentan
- Se generan alertas cuando el uso excede umbrales

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-10-03: Identificar operaciones que consumen más recursos
**Descripción:** Verificar que se identifican operaciones que consumen más recursos.

**Pasos:**
1. Ejecutar diferentes operaciones
2. Consultar métricas de recursos por operación

**Resultado Esperado:**
- Se identifican operaciones que consumen más recursos
- Las métricas se documentan
- Se proporcionan recomendaciones para optimización

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### UT-11: Verificación y pruebas de aceptación

#### PA-UT-11-01: Pruebas de aceptación para todas las historias de usuario
**Descripción:** Verificar que existen pruebas de aceptación para todas las historias de usuario.

**Pasos:**
1. Revisar la lista de historias de usuario
2. Verificar que cada historia tiene pruebas de aceptación

**Resultado Esperado:**
- Existen pruebas de aceptación para todas las historias de usuario
- Las pruebas validan todos los criterios de aceptación
- Las pruebas están documentadas

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-11-02: Ejecución automática de pruebas de aceptación
**Descripción:** Verificar que las pruebas de aceptación se ejecutan automáticamente en CI/CD.

**Pasos:**
1. Configurar pipeline de CI/CD
2. Verificar que las pruebas de aceptación se ejecutan automáticamente

**Resultado Esperado:**
- Las pruebas de aceptación se ejecutan automáticamente en el pipeline
- Los resultados se reportan en el pipeline
- El pipeline falla si las pruebas fallan

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

### UT-12: Presentación de sistema

#### PA-UT-12-01: Documentación de usuario actualizada
**Descripción:** Verificar que existe documentación de usuario actualizada.

**Pasos:**
1. Consultar la documentación de usuario
2. Verificar que está actualizada y cubre todas las funcionalidades

**Resultado Esperado:**
- Existe documentación de usuario
- La documentación está actualizada
- La documentación cubre todas las funcionalidades principales

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-12-02: Guías de uso para funcionalidades principales
**Descripción:** Verificar que existen guías de uso para funcionalidades principales.

**Pasos:**
1. Consultar las guías de uso
2. Verificar que cubren: inicio de sesión, gestión de envíos, búsqueda semántica, importación

**Resultado Esperado:**
- Existen guías de uso para funcionalidades principales
- Las guías son claras y fáciles de seguir
- Las guías incluyen capturas de pantalla o ejemplos

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

#### PA-UT-12-03: Sistema desplegado en ambiente de demostración
**Descripción:** Verificar que el sistema está desplegado en ambiente de demostración.

**Pasos:**
1. Acceder al ambiente de demostración
2. Verificar que todas las funcionalidades están disponibles

**Resultado Esperado:**
- El sistema está desplegado en ambiente de demostración
- Todas las funcionalidades están disponibles
- El ambiente tiene datos de prueba apropiados

**Estado:** ⬜ Pendiente | ✅ Aprobado | ❌ Rechazado

---

## 📊 RESUMEN DE PRUEBAS

**Total de Pruebas de Aceptación (HU):** 85 pruebas  
**Total de Pruebas de Aceptación (HT):** 35 pruebas  
**Total General:** 120 pruebas de aceptación

---

**Documento generado:** Enero 2026  
**Última actualización:** Enero 2026  
**Versión:** 1.0

# Descripción de Operaciones del Sistema

Este documento describe todas las operaciones disponibles en el sistema de gestión de envíos.

---

## Gestión de Usuarios

### Registrar usuarios
Permite crear nuevos usuarios en el sistema con información personal (nombre, correo, cédula, teléfono, dirección) y asignar un rol específico (Admin, Gerente, Digitador o Comprador). Incluye validación de datos únicos como cédula y correo electrónico, y establece un cupo anual por defecto para usuarios compradores.

### Modificar usuarios
Permite actualizar la información de usuarios existentes, incluyendo datos personales, rol asignado, estado de activación y cupo anual. Los cambios están sujetos a permisos según el rol del usuario que realiza la modificación.

### Listar usuarios
Muestra una lista paginada de todos los usuarios del sistema, filtrada según los permisos del usuario autenticado. Los administradores ven todos los usuarios, los gerentes ven todos excepto administradores, y los digitadores solo ven digitadores y compradores.

### Eliminar usuarios
Permite eliminar usuarios del sistema de forma permanente. Esta operación requiere permisos de administrador y puede incluir validaciones para prevenir la eliminación de usuarios con envíos asociados.

### Restablecer contraseña
Permite restablecer la contraseña de un usuario, ya sea por solicitud del propio usuario o por un administrador. Incluye validación de seguridad y puede enviar notificaciones por correo electrónico.

---

## Gestión de Envíos

### Ingresar envíos manuales
Permite crear envíos de forma manual ingresando toda la información requerida: número HAWB único, datos del comprador, productos asociados, peso, cantidad y valor total. El sistema calcula automáticamente el costo del servicio según las tarifas vigentes y valida el cupo anual del comprador.

### Importar envíos
Permite importar múltiples envíos desde un archivo Excel (.xlsx). El sistema procesa el archivo, valida los datos, detecta errores y permite revisar un preview antes de confirmar la importación. Genera un reporte detallado de envíos procesados correctamente y errores encontrados.

### Modificar envíos
Permite actualizar la información de envíos existentes, incluyendo datos del comprador, productos asociados, peso, valor y observaciones. Valida transiciones de estado y recalcula automáticamente los totales y costos cuando sea necesario.

### Eliminar envíos
Permite eliminar envíos del sistema de forma permanente. Esta operación requiere permisos adecuados y puede incluir validaciones para prevenir la eliminación de envíos en ciertos estados o con historial importante.

### Listar envíos
Muestra una lista paginada de envíos con filtros avanzados por estado, comprador, fecha de emisión, HAWB y otros criterios. Los compradores solo ven sus propios envíos, mientras que administradores, gerentes y digitadores pueden ver todos los envíos del sistema.

### Exportar envíos
Permite exportar los envíos filtrados a diferentes formatos: Excel (.xlsx), CSV o PDF. Incluye todos los datos del envío, productos asociados y puede generar comprobantes individuales o reportes masivos según las necesidades del usuario.

---

## Gestión de Tarifas y Productos

### Crear una nueva tarifa
Permite definir nuevas tarifas de envío con cargo base y precio por kilogramo. Las tarifas se utilizan para calcular automáticamente el costo del servicio al crear o modificar envíos.

### Modificar productos
Permite actualizar la información de productos asociados a envíos, incluyendo descripción, categoría, peso, cantidad y valor unitario. Los cambios se reflejan automáticamente en los totales del envío correspondiente.

### Eliminar productos
Permite eliminar productos de un envío específico. El sistema recalcula automáticamente los totales del envío (peso total, cantidad total y valor total) después de la eliminación.

---

## Búsqueda y Consultas

### Búsqueda tradicional
Permite buscar envíos, usuarios y productos usando coincidencias exactas o parciales de texto en campos específicos como HAWB, nombre del comprador, descripción de productos, etc. Retorna resultados paginados con información relevante.

### Búsqueda tradicional con filtros
Extiende la búsqueda tradicional permitiendo aplicar múltiples filtros simultáneos como fecha de emisión, estado del envío, ciudad de destino, rango de peso o valor, y otros criterios para refinar los resultados de búsqueda.

### Búsqueda semántica
Utiliza procesamiento de lenguaje natural e inteligencia artificial (embeddings de OpenAI) para encontrar envíos relevantes basándose en el significado de la consulta, no solo en coincidencias exactas de texto. Permite consultas en lenguaje natural como "envíos entregados en Quito la semana pasada".

### Búsqueda semántica con filtros
Combina la búsqueda semántica con filtros adicionales como fecha desde/hasta, estado, ciudad de destino y otros criterios para obtener resultados más precisos y relevantes según las necesidades específicas del usuario.

---

## Autenticación y Seguridad

### Autenticación de usuarios
Permite a los usuarios iniciar sesión en el sistema usando su correo electrónico y contraseña. El sistema valida las credenciales, genera un token JWT para mantener la sesión activa y retorna la información del usuario autenticado con sus permisos y roles.

### Cierre de sesión
Permite a los usuarios cerrar su sesión de forma segura, invalidando el token de autenticación y limpiando los datos de sesión almacenados en el cliente.

### Gestión de roles y permisos
Permite a los administradores gestionar los roles de los usuarios (Admin, Gerente, Digitador, Comprador) y definir qué operaciones puede realizar cada rol. El sistema valida los permisos en cada operación para garantizar la seguridad y el control de acceso.

---

## Auditoría y Reportes

### Auditoría de acciones (logs del sistema)
Registra automáticamente todas las acciones importantes realizadas en el sistema, incluyendo creación, modificación y eliminación de registros, cambios de estado, búsquedas realizadas y otras operaciones críticas. Los logs incluyen información del usuario, fecha, hora y detalles de la operación.

### Cambiar estado del envío
Permite cambiar el estado de un envío (Pendiente, En Tránsito, Entregado, Cancelado) validando que la transición sea válida según las reglas de negocio. Solo usuarios con permisos adecuados pueden realizar cambios de estado, y cada cambio se registra en el historial de auditoría.

### Seguimiento de envíos
Permite consultar el historial completo de un envío, incluyendo todos los cambios de estado, fechas importantes, productos asociados y observaciones. Proporciona una vista detallada del ciclo de vida del envío desde su creación hasta su entrega o cancelación.

### Validación de datos de envío
Valida automáticamente los datos ingresados al crear o modificar envíos, verificando que el HAWB sea único, que el comprador tenga cupo disponible, que los productos tengan información válida y que todos los campos requeridos estén completos antes de guardar.

### Generar reportes estadísticos
Permite generar reportes estadísticos sobre envíos, incluyendo totales por período, distribución por estado, análisis de compradores, tendencias de peso y valor, y otras métricas relevantes para la toma de decisiones gerenciales.

### Visualizar historial de búsquedas
Permite a los usuarios ver su historial de búsquedas realizadas (tanto tradicionales como semánticas), incluyendo los términos buscados, fecha y hora, cantidad de resultados encontrados y otros detalles relevantes para facilitar búsquedas futuras.

---

## Notas Adicionales

- Todas las operaciones requieren autenticación mediante token JWT.
- Los permisos varían según el rol del usuario autenticado.
- Las operaciones críticas se registran automáticamente en el sistema de auditoría.
- El sistema valida automáticamente los datos antes de procesar cualquier operación.
- Los compradores tienen acceso limitado a sus propios datos, mientras que otros roles tienen acceso más amplio según sus permisos.







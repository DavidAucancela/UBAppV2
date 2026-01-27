# 📊 Descripción de Tablas del Sistema

Este documento describe todas las tablas de la base de datos del sistema, incluyendo sus atributos, tipos de dato, restricciones NULL y descripción.

---

## 📋 Índice de Tablas

1. [usuarios](#1-tabla-usuarios)
2. [tarifa](#2-tabla-tarifa)
3. [envio](#3-tabla-envio)
4. [producto](#4-tabla-producto)
5. [archivo](#5-tabla-archivo)
6. [busqueda_tradicional](#6-tabla-busqueda_tradicional)
7. [embedding_envio](#7-tabla-embedding_envio)
8. [embedding_busqueda](#8-tabla-embedding_busqueda)
9. [historial_semantica](#9-tabla-historial_semantica)
10. [notificaciones](#10-tabla-notificaciones)
11. [prueba_controlada_semantica](#11-tabla-prueba_controlada_semantica)
12. [metrica_semantica](#12-tabla-metrica_semantica)
13. [registro_generacion_embedding](#13-tabla-registro_generacion_embedding)
14. [prueba_carga](#14-tabla-prueba_carga)
15. [metrica_rendimiento](#15-tabla-metrica_rendimiento)
16. [registro_manual_envio](#16-tabla-registro_manual_envio)
17. [prueba_rendimiento_completa](#17-tabla-prueba_rendimiento_completa)
18. [detalle_proceso_rendimiento](#18-tabla-detalle_proceso_rendimiento)

---

## 1. Tabla: usuarios

**Descripción**: Almacena la información de usuarios del sistema con roles, autenticación y datos personales.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único del usuario |
| password | Varchar(128) | NO | Hash de la contraseña del usuario |
| username | Varchar(150) | NO | Nombre de usuario único para login |
| nombre | Varchar(100) | SÍ | Nombre completo del usuario |
| correo | EmailField | SÍ | Correo electrónico único del usuario |
| cedula | Varchar(10) | NO | Cédula ecuatoriana única (10 dígitos) |
| rol | Integer | NO | Rol del usuario (1=Admin, 2=Gerente, 3=Digitador, 4=Comprador) |
| telefono | Varchar(15) | SÍ | Número de teléfono del usuario |
| fecha_nacimiento | Date | SÍ | Fecha de nacimiento del usuario |
| direccion | Text | SÍ | Dirección completa del usuario |
| cupo_anual | Decimal(10,2) | NO | Límite de peso anual en kg para compradores (default: 1000.00) |
| provincia | Varchar(100) | SÍ | Provincia de residencia |
| canton | Varchar(100) | SÍ | Cantón de residencia |
| ciudad | Varchar(100) | SÍ | Ciudad de residencia |
| is_active | Boolean | NO | Indica si el usuario está activo (heredado de AbstractUser) |
| is_staff | Boolean | NO | Indica si es personal administrativo |
| is_superuser | Boolean | NO | Indica si es superusuario |
| last_login | DateTime | SÍ | Última fecha de inicio de sesión |
| date_joined | DateTime | NO | Fecha de registro en el sistema |
| fecha_creacion | DateTime | NO | Fecha de creación del registro (auto_now_add) |
| fecha_actualizacion | DateTime | NO | Fecha de última actualización (auto_now) |

---

## 2. Tabla: tarifa

**Descripción**: Almacena las tarifas de envío configuradas por categoría y rango de peso.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único de la tarifa |
| categoria | Varchar(50) | NO | Categoría del producto (electronica, ropa, hogar, deportes, otros) |
| peso_minimo | Decimal(8,2) | NO | Peso mínimo en kilogramos para aplicar esta tarifa |
| peso_maximo | Decimal(8,2) | NO | Peso máximo en kilogramos para aplicar esta tarifa |
| precio_por_kg | Decimal(8,2) | NO | Precio en dólares por kilogramo |
| cargo_base | Decimal(8,2) | NO | Cargo fijo base para la categoría y rango (default: 0) |
| activa | Boolean | NO | Indica si la tarifa está activa (default: True) |
| fecha_creacion | DateTime | NO | Fecha de creación (auto_now_add) |
| fecha_actualizacion | DateTime | NO | Fecha de última actualización (auto_now) |

**Restricciones**: 
- Unique together: (categoria, peso_minimo, peso_maximo)

---

## 3. Tabla: envio

**Descripción**: Almacena la información de envíos realizados por compradores.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único del envío |
| hawb | Varchar(50) | NO | Número de HAWB (House Air Waybill) único |
| peso_total | Decimal(10,2) | NO | Peso total del envío en kilogramos (default: 0) |
| cantidad_total | Integer | NO | Cantidad total de productos en el envío (default: 0) |
| valor_total | Decimal(12,2) | NO | Valor total del envío en dólares (default: 0) |
| costo_servicio | Decimal(12,4) | NO | Costo calculado del servicio según tarifas (default: 0) |
| fecha_emision | DateTime | NO | Fecha de emisión del envío (default: now) |
| comprador_id | Integer (FK) | NO | Referencia al usuario comprador (rol=4) |
| estado | Varchar(20) | NO | Estado del envío (pendiente, en_transito, entregado, cancelado) (default: pendiente) |
| observaciones | Text | SÍ | Observaciones adicionales sobre el envío |
| fecha_creacion | DateTime | NO | Fecha de creación (auto_now_add) |
| fecha_actualizacion | DateTime | NO | Fecha de última actualización (auto_now) |

**Índices**: 
- hawb
- (comprador_id, fecha_emision)
- (estado, fecha_emision)
- fecha_emision (descendente)

---

## 4. Tabla: producto

**Descripción**: Almacena los productos asociados a cada envío.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único del producto |
| descripcion | Varchar(200) | NO | Descripción del producto |
| peso | Decimal(8,2) | NO | Peso del producto en kilogramos |
| cantidad | Integer | NO | Cantidad de unidades del producto |
| valor | Decimal(10,2) | NO | Valor unitario del producto en dólares |
| costo_envio | Decimal(10,2) | NO | Costo de envío calculado para este producto (default: 0) |
| envio_id | Integer (FK) | NO | Referencia al envío al que pertenece |
| categoria | Varchar(50) | NO | Categoría del producto (electronica, ropa, hogar, deportes, otros) (default: otros) |
| fecha_creacion | DateTime | NO | Fecha de creación (auto_now_add) |
| fecha_actualizacion | DateTime | NO | Fecha de última actualización (auto_now) |

**Índices**: 
- (envio_id, categoria)
- categoria

---

## 5. Tabla: archivo

**Descripción**: Almacena información sobre importaciones de archivos Excel realizadas por usuarios.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único de la importación |
| archivo | FileField | NO | Archivo Excel subido (upload_to='importaciones/%Y/%m/') |
| nombre_original | Varchar(255) | NO | Nombre original del archivo subido |
| estado | Varchar(20) | NO | Estado de la importación (pendiente, validando, validado, procesando, completado, error) (default: pendiente) |
| usuario_id | Integer (FK) | NO | Usuario que realizó la importación |
| total_registros | Integer | NO | Total de registros en el archivo (default: 0) |
| registros_validos | Integer | NO | Cantidad de registros válidos (default: 0) |
| registros_errores | Integer | NO | Cantidad de registros con errores (default: 0) |
| registros_duplicados | Integer | NO | Cantidad de registros duplicados (default: 0) |
| registros_procesados | Integer | NO | Cantidad de registros procesados (default: 0) |
| errores_validacion | JSON | NO | Detalles de errores encontrados durante validación (default: {}) |
| columnas_mapeadas | JSON | NO | Mapeo entre columnas del Excel y campos del modelo (default: {}) |
| registros_seleccionados | JSON | NO | Lista de índices de registros seleccionados para importar (default: []) |
| mensaje_resultado | Text | SÍ | Mensaje de resultado de la importación |
| fecha_creacion | DateTime | NO | Fecha de creación (auto_now_add) |
| fecha_actualizacion | DateTime | NO | Fecha de última actualización (auto_now) |
| fecha_completado | DateTime | SÍ | Fecha en que se completó la importación |

---

## 6. Tabla: busqueda_tradicional

**Descripción**: Almacena el historial de búsquedas tradicionales realizadas por usuarios.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único de la búsqueda |
| usuario_id | Integer (FK) | NO | Usuario que realizó la búsqueda |
| termino_busqueda | Varchar(255) | NO | Término de búsqueda utilizado |
| tipo_busqueda | Varchar(50) | NO | Tipo de búsqueda realizada (default: general) |
| fecha_busqueda | DateTime | NO | Fecha y hora de la búsqueda (auto_now_add) |
| resultados_encontrados | PositiveInteger | NO | Cantidad de resultados encontrados (default: 0) |
| resultados_json | JSON | SÍ | Resultados completos en formato JSON para generación de PDF |

---

## 7. Tabla: embedding_envio

**Descripción**: Almacena los vectores de embeddings generados para cada envío usando OpenAI.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único del embedding |
| envio_id | Integer (FK, OneToOne) | NO | Referencia única al envío |
| embedding_vector | Vector(1536) | SÍ | Vector de embedding de 1536 dimensiones (pgvector) |
| texto_indexado | Text | NO | Texto que fue usado para generar el embedding |
| fecha_generacion | DateTime | NO | Fecha de generación del embedding (auto_now) |
| modelo_usado | Varchar(100) | NO | Modelo de embedding utilizado (default: text-embedding-3-small) |
| cosine_similarity_avg | Float | NO | Similitud coseno promedio con otros embeddings (default: 0.0) |

**Índices**: 
- modelo_usado
- fecha_generacion

---

## 8. Tabla: embedding_busqueda

**Descripción**: Almacena el historial de búsquedas semánticas con sus embeddings de consulta.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único de la búsqueda |
| usuario_id | Integer (FK) | NO | Usuario que realizó la búsqueda |
| consulta | Text | NO | Texto de la consulta realizada |
| embedding_vector | Vector(1536) | SÍ | Vector embedding de la consulta para reutilización |
| resultados_encontrados | PositiveInteger | NO | Cantidad de resultados encontrados (default: 0) |
| tiempo_respuesta | Integer | NO | Tiempo de respuesta en milisegundos (default: 0) |
| fecha_busqueda | DateTime | NO | Fecha y hora de la búsqueda (auto_now_add) |
| filtros_aplicados | JSON | SÍ | Filtros aplicados durante la búsqueda |
| modelo_utilizado | Varchar(100) | NO | Modelo de embedding utilizado (default: text-embedding-3-small) |
| costo_consulta | Decimal(10,8) | NO | Costo en USD de la consulta según tokens (default: 0.0) |
| tokens_utilizados | PositiveInteger | NO | Tokens utilizados en la consulta (default: 0) |
| resultados_json | JSON | SÍ | Resultados completos con métricas para generación de PDF |

**Índices**: 
- (usuario_id, fecha_busqueda)
- modelo_utilizado

---

## 9. Tabla: historial_semantica

**Descripción**: Almacena sugerencias predefinidas y estadísticas de búsquedas semánticas populares.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único de la sugerencia |
| texto | Varchar(200) | NO | Texto de la sugerencia |
| categoria | Varchar(50) | NO | Categoría de la sugerencia (estado, ciudad, fecha, comprador, general) (default: general) |
| icono | Varchar(50) | NO | Clase de icono FontAwesome (default: fa-search) |
| orden | Integer | NO | Orden de visualización (default: 0) |
| activa | Boolean | NO | Indica si la sugerencia está activa (default: True) |
| fecha_creacion | DateTime | NO | Fecha de creación (auto_now_add) |
| veces_usada | PositiveInteger | NO | Contador de veces que se ha usado esta sugerencia (default: 0) |

---

## 10. Tabla: notificaciones

**Descripción**: Almacena las notificaciones del sistema para usuarios.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único de la notificación |
| usuario_id | Integer (FK) | NO | Usuario destinatario de la notificación |
| tipo | Varchar(20) | NO | Tipo de notificación (nuevo_envio, envio_asignado, estado_cambiado, general) (default: general) |
| titulo | Varchar(200) | NO | Título de la notificación |
| mensaje | Text | NO | Mensaje de la notificación |
| leida | Boolean | NO | Indica si la notificación ha sido leída (default: False) |
| fecha_lectura | DateTime | SÍ | Fecha en que se marcó como leída |
| enlace | Varchar(500) | SÍ | Enlace opcional (ej: a un envío específico) |
| metadata | JSON | NO | Información adicional en formato JSON (default: {}) |
| fecha_creacion | DateTime | NO | Fecha de creación (auto_now_add) |
| fecha_actualizacion | DateTime | NO | Fecha de última actualización (auto_now) |

**Índices**: 
- (usuario_id, leida)
- fecha_creacion

---

## 11. Tabla: prueba_controlada_semantica

**Descripción**: Almacena pruebas controladas de búsqueda semántica para evaluación offline con datos predefinidos.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único de la prueba |
| nombre | Varchar(200) | NO | Nombre descriptivo de la prueba controlada |
| descripcion | Text | SÍ | Descripción detallada de la prueba |
| consulta | Text | NO | Texto de la consulta a evaluar |
| resultados_relevantes | JSON | NO | Lista de IDs de envíos que son relevantes para esta consulta |
| fecha_creacion | DateTime | NO | Fecha de creación (auto_now_add) |
| fecha_ejecucion | DateTime | SÍ | Fecha en que se ejecutó la prueba |
| activa | Boolean | NO | Indica si la prueba está activa (default: True) |
| creado_por_id | Integer (FK) | SÍ | Usuario que creó la prueba |

---

## 12. Tabla: metrica_semantica

**Descripción**: Almacena métricas de evaluación de búsqueda semántica calculadas offline.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único de la métrica |
| busqueda_semantica_id | Integer (FK) | SÍ | Referencia opcional a búsqueda semántica real |
| prueba_controlada_id | Integer (FK) | SÍ | Referencia opcional a prueba controlada |
| consulta | Text | NO | Texto de la consulta evaluada |
| fecha_calculo | DateTime | NO | Fecha de cálculo de la métrica (auto_now_add) |
| resultados_rankeados | JSON | NO | Lista de resultados con scores y posiciones |
| mrr | Float | SÍ | MRR (Mean Reciprocal Rank) calculado (0.0-1.0) |
| ndcg_10 | Float | SÍ | Normalized Discounted Cumulative Gain@10 (0.0-1.0) |
| precision_5 | Float | SÍ | Precisión en los primeros 5 resultados (0.0-1.0) |
| total_resultados | PositiveInteger | NO | Total de resultados encontrados (default: 0) |
| total_relevantes_encontrados | PositiveInteger | NO | Total de resultados relevantes encontrados (default: 0) |
| tiempo_procesamiento_ms | Integer | NO | Tiempo de procesamiento en milisegundos (default: 0) |
| logs_pipeline | JSON | SÍ | Logs detallados de cada etapa del proceso semántico |
| modelo_embedding | Varchar(100) | NO | Modelo de embedding utilizado (default: text-embedding-3-small) |
| metrica_ordenamiento | Varchar(50) | NO | Métrica de ordenamiento utilizada (default: score_combinado) |

**Índices**: 
- fecha_calculo (descendente)
- mrr
- ndcg_10
- precision_5

---

## 13. Tabla: registro_generacion_embedding

**Descripción**: Registra cada generación de embedding de un envío (automática o manual).

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único del registro |
| envio_id | Integer (FK) | NO | Referencia al envío |
| estado | Varchar(20) | NO | Estado (generado, error, omitido) (default: generado) |
| dimension_embedding | PositiveInteger | NO | Dimensión del embedding (default: 1536) |
| fecha_generacion | DateTime | NO | Fecha de generación (auto_now_add) |
| tiempo_generacion_ms | Integer | NO | Tiempo de generación en milisegundos (default: 0) |
| modelo_usado | Varchar(100) | NO | Modelo utilizado (default: text-embedding-3-small) |
| mensaje_error | Text | SÍ | Mensaje de error si hubo fallo |
| tipo_proceso | Varchar(50) | NO | Tipo de proceso (automatico, manual, masivo) (default: automatico) |
| embedding_id | Integer (FK, OneToOne) | SÍ | Referencia al embedding generado (si fue exitoso) |

**Índices**: 
- fecha_generacion (descendente)
- estado
- tipo_proceso
- (envio_id, fecha_generacion)

---

## 14. Tabla: prueba_carga

**Descripción**: Almacena pruebas de carga del sistema con diferentes niveles de carga.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único de la prueba |
| nombre | Varchar(200) | NO | Nombre descriptivo de la prueba de carga |
| tipo_prueba | Varchar(50) | NO | Tipo de prueba (busqueda_semantica, registro_envio) |
| nivel_carga | PositiveInteger | NO | Cantidad de operaciones ejecutadas (1, 10, 30) |
| tipo_registro | Varchar(50) | SÍ | Tipo de registro (manual, automatico) - solo para pruebas de registro |
| fecha_ejecucion | DateTime | NO | Fecha de ejecución (auto_now_add) |
| ejecutado_por_id | Integer (FK) | SÍ | Usuario que ejecutó la prueba |
| tiempo_promedio_ms | Float | NO | Tiempo promedio de respuesta en ms (default: 0.0) |
| tiempo_minimo_ms | Integer | NO | Tiempo mínimo en ms (default: 0) |
| tiempo_maximo_ms | Integer | NO | Tiempo máximo en ms (default: 0) |
| cpu_promedio | Float | NO | CPU promedio en porcentaje (0.0-100.0) (default: 0.0) |
| cpu_maximo | Float | NO | CPU máximo en porcentaje (0.0-100.0) (default: 0.0) |
| ram_promedio_mb | Float | NO | RAM promedio en MB (default: 0.0) |
| ram_maximo_mb | Float | NO | RAM máximo en MB (default: 0.0) |
| total_exitosos | PositiveInteger | NO | Total de operaciones exitosas (default: 0) |
| total_errores | PositiveInteger | NO | Total de errores (default: 0) |
| datos_prueba | JSON | SÍ | Consultas o datos utilizados en la prueba |

**Índices**: 
- fecha_ejecucion (descendente)
- (tipo_prueba, nivel_carga)

---

## 15. Tabla: metrica_rendimiento

**Descripción**: Almacena métricas individuales de rendimiento para cada operación medida.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único de la métrica |
| prueba_carga_id | Integer (FK) | SÍ | Referencia opcional a prueba de carga |
| proceso | Varchar(50) | NO | Tipo de proceso (registro_envio_manual, registro_envio_automatico, busqueda_semantica) |
| tiempo_respuesta_ms | Integer | NO | Tiempo de respuesta en milisegundos (default: 0) |
| uso_cpu | Float | NO | Uso de CPU en porcentaje (0.0-100.0) (default: 0.0) |
| uso_ram_mb | Float | NO | Uso de RAM en MB (default: 0.0) |
| fecha_medicion | DateTime | NO | Fecha de medición (auto_now_add) |
| nivel_carga | PositiveInteger | SÍ | Cantidad de operaciones simultáneas (1, 10, 30) |
| exito | Boolean | NO | Indica si la operación fue exitosa (default: True) |
| detalles | JSON | SÍ | Información adicional sobre la operación |

**Índices**: 
- fecha_medicion (descendente)
- (proceso, nivel_carga)
- exito

---

## 16. Tabla: registro_manual_envio

**Descripción**: Simula y registra tiempos de registro manual de envíos para comparación con sistema automático.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único del registro |
| hawb | Varchar(50) | NO | Número de envío simulado |
| tiempo_registro_segundos | Float | NO | Tiempo medido con cronómetro para registro manual (default: 0.0) |
| fecha_registro | DateTime | NO | Fecha de registro (auto_now_add) |
| registrado_por_id | Integer (FK) | SÍ | Usuario que registró el tiempo manual |
| datos_envio | JSON | SÍ | Datos del envío que se registró manualmente |
| notas | Text | SÍ | Observaciones sobre el registro manual |

**Índices**: 
- fecha_registro (descendente)
- registrado_por_id

---

## 17. Tabla: prueba_rendimiento_completa

**Descripción**: Almacena resultados completos de pruebas de rendimiento del sistema ejecutadas desde comando.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único de la prueba |
| fecha_ejecucion | DateTime | NO | Fecha de ejecución (auto_now_add) |
| usuario_ejecutor_id | Integer (FK) | SÍ | Usuario que ejecutó la prueba |
| resultados_json | JSON | NO | Resultados completos de la prueba en formato JSON |
| tiempo_respuesta_manual_promedio | Float | SÍ | Tiempo manual promedio en segundos |
| tiempo_respuesta_web_promedio | Float | SÍ | Tiempo web promedio en segundos |
| mejora_factor | Float | SÍ | Factor de mejora (manual/web) |
| completada | Boolean | NO | Indica si la prueba se completó (default: True) |
| errores | Text | SÍ | Errores encontrados durante la ejecución |
| salida_completa | Text | SÍ | Salida completa del comando para referencia |

**Índices**: 
- fecha_ejecucion (descendente)
- usuario_ejecutor_id
- completada

---

## 18. Tabla: detalle_proceso_rendimiento

**Descripción**: Almacena detalles individuales de cada proceso (M1-M14) con estadísticas completas de rendimiento.

| Atributo | Tipo de dato | NULL | Descripción |
|----------|--------------|------|-------------|
| id | Integer (PK) | NO | Identificador único del detalle |
| prueba_id | Integer (FK) | NO | Referencia a la prueba de rendimiento completa |
| codigo_proceso | Varchar(10) | NO | Código del proceso (M1-M14) |
| nombre_proceso | Varchar(200) | NO | Nombre descriptivo del proceso |
| tiempo_media | Float | NO | Tiempo promedio en segundos |
| tiempo_minimo | Float | NO | Tiempo mínimo en segundos |
| tiempo_maximo | Float | NO | Tiempo máximo en segundos |
| tiempo_mediana | Float | NO | Tiempo mediana en segundos |
| tiempo_desviacion | Float | NO | Desviación estándar de tiempos |
| cpu_media | Float | NO | CPU promedio en porcentaje |
| cpu_minimo | Float | NO | CPU mínimo en porcentaje |
| cpu_maximo | Float | NO | CPU máximo en porcentaje |
| cpu_mediana | Float | NO | CPU mediana en porcentaje |
| cpu_desviacion | Float | NO | Desviación estándar de CPU |
| ram_media | Float | NO | RAM promedio en KB |
| ram_minimo | Float | NO | RAM mínimo en KB |
| ram_maximo | Float | NO | RAM máximo en KB |
| ram_mediana | Float | NO | RAM mediana en KB |
| ram_desviacion | Float | NO | Desviación estándar de RAM |
| categoria_tiempo | Varchar(20) | NO | Categoría según tiempo (Excelente, Aceptable, Deficiente, Inaceptable) |
| calificacion_tiempo | Integer | NO | Calificación de tiempo (0-100) |
| categoria_cpu | Varchar(20) | NO | Categoría según CPU (Excelente, Muy bueno, Bueno, Aceptable, Regular, Malo) |
| calificacion_cpu | Integer | NO | Calificación de CPU (0-100) |
| categoria_ram | Varchar(20) | NO | Categoría según RAM (Excelente, Muy bueno, Bueno, Aceptable, Regular, Malo) |
| calificacion_ram | Integer | NO | Calificación de RAM (0-100) |
| iteraciones_completadas | Integer | NO | Iteraciones completadas |
| iteraciones_totales | Integer | NO | Iteraciones totales |
| total_errores | Integer | NO | Total de errores (default: 0) |
| tiempos_raw | JSON | SÍ | Array con todos los tiempos medidos |
| cpus_raw | JSON | SÍ | Array con todos los valores de CPU medidos |
| rams_raw | JSON | SÍ | Array con todos los valores de RAM medidos |
| errores_detalle | JSON | SÍ | Lista de errores encontrados durante la ejecución |
| fecha_medicion | DateTime | NO | Fecha de medición (auto_now_add) |

**Índices**: 
- (prueba_id, codigo_proceso)
- (codigo_proceso, fecha_medicion)
- categoria_tiempo
- categoria_cpu
- categoria_ram

---

## 📝 Notas Adicionales

### Tipos de Datos Especiales

- **Vector(1536)**: Tipo especial de pgvector para almacenar vectores de 1536 dimensiones (embeddings)
- **JSON**: Campo JSON nativo de PostgreSQL para almacenar estructuras de datos complejas
- **Decimal(precision, scale)**: Tipo decimal con precisión exacta para cálculos financieros
- **FileField**: Campo de archivo de Django que almacena la ruta relativa del archivo

### Relaciones Importantes

- **Usuario ↔ Envío**: Un usuario comprador puede tener múltiples envíos
- **Envío ↔ Producto**: Un envío puede tener múltiples productos
- **Envío ↔ Embedding**: Relación uno a uno (OneToOne) para embeddings de envíos
- **Búsqueda Semántica ↔ Métricas**: Relación opcional para métricas de evaluación

### Índices de Rendimiento

Las tablas principales incluyen índices para optimizar consultas frecuentes:
- Búsquedas por HAWB, usuario, estado, fecha
- Filtros por categoría, modelo, tipo de proceso
- Ordenamiento por fechas descendentes

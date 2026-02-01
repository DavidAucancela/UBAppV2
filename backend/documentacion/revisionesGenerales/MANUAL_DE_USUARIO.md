# 📘 Manual de Usuario - Sistema UBApp

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Sistema:** Universal Box - Gestión de Envíos

---

## 📑 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Acceso al Sistema](#acceso-al-sistema)
3. [Roles y Permisos](#roles-y-permisos)
4. [Interfaz Principal](#interfaz-principal)
5. [Módulos del Sistema](#módulos-del-sistema)
   - [Dashboard Principal](#1-dashboard-principal)
   - [Gestión de Envíos](#2-gestión-de-envíos)
   - [Mis Envíos](#3-mis-envíos)
   - [Gestión de Productos](#4-gestión-de-productos)
   - [Gestión de Usuarios](#5-gestión-de-usuarios)
   - [Búsqueda de Envíos](#6-búsqueda-de-envíos)
   - [Búsqueda Semántica](#7-búsqueda-semántica)
   - [Búsqueda Unificada](#8-búsqueda-unificada)
   - [Importación desde Excel](#9-importación-desde-excel)
   - [Gestión de Tarifas](#10-gestión-de-tarifas)
   - [Mapa de Compradores](#11-mapa-de-compradores)
   - [Actividades del Sistema](#12-actividades-del-sistema)
   - [Notificaciones](#13-notificaciones)
   - [Mi Perfil](#14-mi-perfil)
6. [Preguntas Frecuentes](#preguntas-frecuentes)
7. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

### ¿Qué es UBApp?

UBApp (Universal Box Application) es un sistema integral de gestión de envíos diseñado para facilitar el registro, seguimiento y administración de envíos de productos. El sistema permite gestionar usuarios, productos, envíos, tarifas y generar reportes completos.

### Características Principales

- ✅ **Gestión completa de envíos** con seguimiento de estados
- ✅ **Sistema de roles y permisos** para control de acceso
- ✅ **Búsqueda avanzada** con búsqueda semántica e inteligente
- ✅ **Importación masiva** desde archivos Excel
- ✅ **Visualización geográfica** de compradores en mapa
- ✅ **Dashboard personalizado** según el rol del usuario
- ✅ **Gestión de tarifas** por categoría de producto
- ✅ **Generación de comprobantes** en PDF
- ✅ **Sistema de notificaciones** para compradores

---

## Acceso al Sistema

### Requisitos

- Navegador web moderno (Chrome, Firefox, Edge, Safari)
- Conexión a Internet
- Credenciales de acceso (usuario y contraseña)

### Inicio de Sesión

1. **Acceder a la página de inicio**
   - Abra su navegador y navegue a la URL del sistema
   - Será redirigido automáticamente a la página de información general

2. **Navegar al login**
   - Haga clic en el botón **"Iniciar Sesión"** en el menú superior
   - O acceda directamente a `/login`

3. **Ingresar credenciales**
   - **Usuario:** Ingrese su nombre de usuario o correo electrónico
   - **Contraseña:** Ingrese su contraseña
   - Haga clic en **"Iniciar Sesión"**

4. **Acceso exitoso**
   - Si las credenciales son correctas, será redirigido al dashboard correspondiente según su rol

### Registro de Nuevo Usuario

1. En la página de inicio, haga clic en **"Registrarse"**
2. Complete el formulario con:
   - Nombre completo
   - Correo electrónico
   - Cédula (10 dígitos)
   - Contraseña (debe cumplir requisitos de seguridad)
   - Confirmación de contraseña
3. Haga clic en **"Registrarse"**
4. Un administrador o gerente deberá activar su cuenta y asignar un rol

### Recuperación de Contraseña

Si olvidó su contraseña, contacte al administrador del sistema para restablecerla.

---

## Roles y Permisos

El sistema cuenta con cuatro roles principales, cada uno con permisos específicos:

### 👑 Administrador (Admin)

**Acceso completo a todas las funcionalidades:**
- ✅ Gestión completa de usuarios (crear, editar, eliminar, asignar roles)
- ✅ Gestión de todos los envíos del sistema
- ✅ Dashboard de gerente con estadísticas completas
- ✅ Búsqueda semántica e inteligente
- ✅ Gestión de tarifas
- ✅ Importación desde Excel
- ✅ Visualización de mapa de compradores
- ✅ Acceso a actividades del sistema
- ✅ Configuración del sistema

### 👔 Gerente

**Gestión y análisis:**
- ✅ Búsqueda semántica e inteligente
- ✅ Dashboard de gerente (vista de todos los envíos)
- ✅ Visualización de usuarios (excepto administradores)
- ✅ Gestión de envíos
- ✅ Mapa de compradores
- ✅ Gestión de tarifas
- ✅ Importación desde Excel
- ✅ Reportes y estadísticas

### ⌨️ Digitador

**Operación diaria:**
- ✅ Gestión de envíos (crear, editar, eliminar)
- ✅ Importación de archivos Excel
- ✅ Visualización de compradores
- ✅ Mapa de compradores
- ✅ Gestión de productos
- ✅ Búsqueda básica de envíos

### 🛒 Comprador

**Acceso personal:**
- ✅ Dashboard personal con cupo anual
- ✅ Visualización de sus propios envíos
- ✅ Estadísticas personales
- ✅ Seguimiento de cupo anual
- ✅ Notificaciones
- ✅ Gestión de su propio perfil

---

## Interfaz Principal

### Barra de Navegación

La barra de navegación superior contiene:

- **Logo/Inicio:** Regresa a la página principal
- **Menú de Navegación:** Acceso rápido a los módulos principales
- **Perfil de Usuario:** Menú desplegable con:
  - Mi Perfil
  - Actividades del Sistema
  - Cerrar Sesión

### Menú Lateral (si aplica)

Algunos módulos incluyen un menú lateral con opciones adicionales y filtros.

### Área de Contenido Principal

Muestra el contenido del módulo seleccionado, con:
- Encabezado con título y descripción
- Botones de acción (crear, editar, eliminar)
- Filtros y búsqueda
- Tabla o lista de elementos
- Paginación (si aplica)

---

## Módulos del Sistema

## 1. Dashboard Principal

**Ruta:** `/inicio`  
**Acceso:** Admin, Gerente, Digitador

### Descripción

El dashboard principal muestra un resumen completo de las estadísticas del sistema, incluyendo envíos, usuarios y productos.

### Funcionalidades

#### Tarjetas de Indicadores Principales (KPIs)

- **Total Envíos:** Cantidad total de envíos registrados
- **Envíos Pendientes:** Envíos que requieren atención
- **Total Productos:** Productos disponibles en el catálogo
- **Total Usuarios:** Usuarios activos (solo Admin/Gerente)

#### Estadísticas por Categoría

**Usuarios del Sistema** (Admin/Gerente):
- Distribución por roles (Admin, Gerente, Digitador, Comprador)
- Haga clic en una tarjeta para filtrar usuarios por rol

**Estado de Envíos:**
- Pendiente
- En Tránsito
- Entregado
- Cancelado
- Haga clic en una tarjeta para filtrar envíos por estado

### Cómo Usar

1. Al iniciar sesión, será redirigido automáticamente al dashboard
2. Revise las estadísticas principales en las tarjetas superiores
3. Explore las categorías haciendo clic en las tarjetas para filtrar
4. Use los enlaces para navegar directamente a módulos específicos

---

## 2. Gestión de Envíos

**Ruta:** `/envios`  
**Acceso:** Todos los usuarios autenticados (con restricciones según rol)

### Descripción

Módulo principal para crear, editar, listar y gestionar envíos del sistema. Los compradores solo ven sus propios envíos.

### Crear un Nuevo Envío

1. **Acceder al módulo**
   - Navegue a **"Envíos"** en el menú
   - Haga clic en el botón **"Nuevo Envío"** (si tiene permisos)

2. **Completar información básica**
   - **HAWB:** Se genera automáticamente (formato: HAW + número secuencial)
   - **Comprador:** Seleccione el comprador de la lista (obligatorio)
   - **Estado:** Seleccione el estado inicial (por defecto: Pendiente)
   - **Observaciones:** Agregue notas adicionales (opcional)

3. **Agregar productos**
   - Haga clic en **"Agregar Producto"**
   - Complete los campos:
     - **Descripción:** Descripción del producto
     - **Categoría:** Seleccione la categoría (Electrónica, Ropa, Hogar, Deportes, Otros)
     - **Peso (kg):** Peso del producto en kilogramos
     - **Cantidad:** Cantidad de unidades
     - **Valor Unitario:** Valor por unidad
   - Haga clic en **"Agregar"**
   - Repita para agregar más productos

4. **Revisar totales**
   - El sistema calcula automáticamente:
     - **Peso Total:** Suma de todos los productos
     - **Cantidad Total:** Suma de cantidades
     - **Valor Total:** Suma de valores
     - **Costo de Envío:** Calculado según tarifas por categoría

5. **Guardar envío**
   - Revise toda la información
   - Haga clic en **"Guardar Envío"**
   - Se mostrará un mensaje de confirmación

### Editar un Envío

1. En la lista de envíos, localice el envío deseado
2. Haga clic en el botón **"Editar"** (ícono de lápiz)
3. Modifique los campos necesarios
4. Haga clic en **"Guardar Cambios"**

### Cambiar Estado de un Envío

1. Localice el envío en la lista
2. Haga clic en el menú de acciones (tres puntos)
3. Seleccione **"Cambiar Estado"**
4. Elija el nuevo estado:
   - **Pendiente:** Envío registrado, pendiente de procesamiento
   - **En Tránsito:** Envío en camino al destino
   - **Entregado:** Envío completado
   - **Cancelado:** Envío cancelado
5. Confirme el cambio

### Filtrar Envíos

Use los filtros en la parte superior:

- **Buscar:** Ingrese HAWB, nombre de comprador o cédula
- **Estado:** Filtre por estado (Pendiente, En Tránsito, Entregado, Cancelado)
- **Comprador:** Filtre por comprador específico (solo Admin/Gerente/Digitador)

### Ver Detalles de un Envío

1. Haga clic en el envío en la lista o en el botón **"Ver Detalles"**
2. Se mostrará un modal con:
   - Información completa del envío
   - Lista de productos asociados
   - Historial de cambios de estado
   - Opción para descargar comprobante PDF

### Generar Comprobante PDF

1. Abra los detalles del envío
2. Haga clic en **"Descargar Comprobante"**
3. Se generará y descargará un PDF con toda la información del envío

### Eliminar un Envío

⚠️ **Advertencia:** Esta acción no se puede deshacer.

1. Localice el envío en la lista
2. Haga clic en el botón **"Eliminar"** (ícono de papelera)
3. Confirme la eliminación

---

## 3. Mis Envíos

**Ruta:** `/mis-envios`  
**Acceso:** Todos los usuarios autenticados

### Descripción

Vista personalizada donde los compradores pueden ver y gestionar únicamente sus propios envíos.

### Funcionalidades

- Ver lista de todos sus envíos
- Filtrar por estado
- Ver detalles completos
- Descargar comprobantes PDF
- Seguimiento del estado de cada envío

### Cómo Usar

1. Acceda a **"Mis Envíos"** desde el menú
2. Use los filtros para encontrar envíos específicos
3. Haga clic en un envío para ver detalles completos
4. Descargue comprobantes cuando sea necesario

---

## 4. Gestión de Productos

**Ruta:** `/productos`  
**Acceso:** Admin, Gerente, Digitador

### Descripción

Catálogo de productos que pueden ser reutilizados en múltiples envíos. Los productos se organizan por categorías.

### Crear un Producto

1. **Acceder al módulo**
   - Navegue a **"Productos"** en el menú
   - Haga clic en **"Nuevo Producto"**

2. **Completar información**
   - **Descripción:** Descripción detallada del producto (obligatorio)
   - **Categoría:** Seleccione la categoría:
     - Electrónica
     - Ropa
     - Hogar
     - Deportes
     - Otros
   - **Peso (kg):** Peso unitario en kilogramos (obligatorio, debe ser positivo)
   - **Valor Unitario:** Valor monetario por unidad (obligatorio, debe ser positivo)

3. **Guardar**
   - Haga clic en **"Guardar Producto"**

### Editar un Producto

1. Localice el producto en la lista
2. Haga clic en **"Editar"**
3. Modifique los campos necesarios
4. Guarde los cambios

### Eliminar un Producto

⚠️ **Nota:** Solo se puede eliminar si no está asociado a ningún envío.

1. Localice el producto
2. Haga clic en **"Eliminar"**
3. Confirme la eliminación

### Filtrar Productos

- **Buscar:** Busque por descripción
- **Categoría:** Filtre por categoría específica

### Reutilizar Productos en Envíos

Al crear un envío, puede:
- Seleccionar productos existentes del catálogo
- O crear nuevos productos directamente desde el formulario de envío

---

## 5. Gestión de Usuarios

**Ruta:** `/usuarios`  
**Acceso:** Admin, Gerente

### Descripción

Administración completa de usuarios del sistema, incluyendo creación, edición, asignación de roles y gestión de permisos.

### Crear un Usuario

1. **Acceder al módulo**
   - Navegue a **"Usuarios"** en el menú
   - Haga clic en **"Nuevo Usuario"**

2. **Información básica**
   - **Nombre de Usuario:** Nombre único para iniciar sesión (obligatorio)
   - **Nombre Completo:** Nombre completo del usuario (obligatorio, mínimo 2 caracteres)
   - **Correo Electrónico:** Correo válido y único (obligatorio)
   - **Cédula:** Cédula ecuatoriana de 10 dígitos, única (obligatorio)
   - **Contraseña:** Debe cumplir requisitos de seguridad (ver abajo)
   - **Confirmar Contraseña:** Repita la contraseña

3. **Asignar rol**
   - **Rol:** Seleccione el rol del usuario:
     - Admin (solo otros admins pueden crear admins)
     - Gerente
     - Digitador
     - Comprador

4. **Información adicional (opcional)**
   - **Teléfono:** Número de contacto
   - **Fecha de Nacimiento:** Fecha de nacimiento
   - **Dirección:** Dirección completa
   - **Provincia:** Seleccione la provincia
   - **Cantón:** Seleccione el cantón (se carga según provincia)
   - **Ciudad:** Seleccione la ciudad (se carga según cantón)
   - **Cupo Anual:** Para compradores, límite de peso anual (kg)

5. **Estado**
   - **Activo:** Marque para activar la cuenta inmediatamente

6. **Guardar**
   - Haga clic en **"Guardar Usuario"**

### Requisitos de Contraseña

La contraseña debe cumplir:
- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula
- Al menos un número
- Al menos un carácter especial (!@#$%^&*)

### Editar un Usuario

1. Localice el usuario en la lista
2. Haga clic en **"Editar"**
3. Modifique los campos necesarios
   - **Nota:** La contraseña solo se puede cambiar desde el perfil del usuario o usando la opción "Cambiar Contraseña"
4. Guarde los cambios

### Cambiar Contraseña de un Usuario

1. Localice el usuario
2. Haga clic en **"Cambiar Contraseña"**
3. Ingrese la nueva contraseña (debe cumplir requisitos)
4. Confirme la contraseña
5. Guarde

### Activar/Desactivar Usuario

1. Localice el usuario
2. Use el interruptor **"Activo/Inactivo"** o haga clic en **"Activar/Desactivar"**
3. Un usuario inactivo no puede iniciar sesión

### Eliminar un Usuario

⚠️ **Advertencia:** Esta acción no se puede deshacer.

1. Localice el usuario
2. Haga clic en **"Eliminar"**
3. Confirme la eliminación

### Filtrar Usuarios

- **Buscar:** Busque por nombre, correo o cédula
- **Rol:** Filtre por rol específico
- **Estado:** Filtre por usuarios activos/inactivos

---

## 6. Búsqueda de Envíos

**Ruta:** `/busqueda-envios`  
**Acceso:** Todos los usuarios autenticados

### Descripción

Búsqueda básica de envíos por HAWB, comprador, cédula u otros criterios.

### Cómo Usar

1. Acceda a **"Búsqueda de Envíos"** desde el menú
2. Ingrese el término de búsqueda en el campo de búsqueda
3. Haga clic en **"Buscar"** o presione Enter
4. Los resultados se mostrarán en una lista
5. Haga clic en un resultado para ver detalles

### Criterios de Búsqueda

- HAWB (número de guía)
- Nombre del comprador
- Cédula del comprador
- Descripción de productos

---

## 7. Búsqueda Semántica

**Ruta:** `/busqueda-semantica`  
**Acceso:** Admin, Gerente

### Descripción

Búsqueda avanzada que utiliza inteligencia artificial para encontrar envíos por similitud semántica, no solo por palabras clave exactas.

### Ventajas

- Encuentra resultados relacionados aunque no use las palabras exactas
- Comprende el contexto de la búsqueda
- Mejores resultados para búsquedas complejas

### Cómo Usar

1. Acceda a **"Búsqueda Semántica"** desde el menú
2. Ingrese su consulta en lenguaje natural
   - Ejemplo: "envíos de laptops a Quito"
   - Ejemplo: "productos electrónicos pendientes"
3. Haga clic en **"Buscar"**
4. Los resultados se ordenan por relevancia
5. Revise los resultados y haga clic para ver detalles

### Consejos

- Use frases completas en lugar de palabras sueltas
- Sea específico sobre lo que busca
- Los resultados más relevantes aparecen primero

---

## 8. Búsqueda Unificada

**Ruta:** `/busqueda`  
**Acceso:** Todos los usuarios autenticados

### Descripción

Búsqueda combinada que integra búsqueda básica y semántica en una sola interfaz.

### Cómo Usar

1. Acceda a **"Búsqueda"** desde el menú
2. Ingrese su término de búsqueda
3. Seleccione el tipo de búsqueda:
   - **Básica:** Búsqueda por palabras clave exactas
   - **Semántica:** Búsqueda inteligente (solo Admin/Gerente)
4. Haga clic en **"Buscar"**
5. Revise los resultados combinados

---

## 9. Importación desde Excel

**Ruta:** `/importacion-excel`  
**Acceso:** Admin, Gerente, Digitador

### Descripción

Importación masiva de envíos desde archivos Excel (.xlsx, .xls) con validación previa y vista previa de datos.

### Proceso de Importación

#### Paso 1: Cargar Archivo

1. Acceda a **"Importación Excel"** desde el menú
2. Haga clic en **"Seleccionar Archivo"** o arrastre el archivo
3. Seleccione un archivo Excel (.xlsx o .xls)
4. El sistema validará el formato del archivo
5. Haga clic en **"Continuar"**

#### Paso 2: Vista Previa

1. Revise los datos en la tabla de vista previa
2. Verifique que las columnas se hayan mapeado correctamente
3. Revise las primeras filas para asegurar que los datos sean correctos
4. Haga clic en **"Continuar"**

#### Paso 3: Mapear Columnas

1. Revise el mapeo automático de columnas
2. Ajuste manualmente si es necesario:
   - Seleccione la columna del Excel
   - Asigne el campo correspondiente del sistema
3. **Importante:** Asegúrese de mapear el campo **HAWB** (obligatorio)
4. Campos disponibles:
   - HAWB (obligatorio)
   - Peso Total
   - Cantidad Total
   - Valor Total
   - Estado
   - Descripción Producto
   - Peso Producto
   - Cantidad Producto
   - Valor Producto
   - Categoría
   - Observaciones
5. Haga clic en **"Validar Datos"**

#### Paso 4: Validar y Seleccionar

1. Revise las estadísticas de validación:
   - **Registros válidos:** Listos para importar
   - **Registros con errores:** Requieren corrección
   - **Duplicados:** HAWBs que ya existen
2. Revise los errores en la tabla (marcados en rojo)
3. Descargue el reporte de errores si es necesario
4. Seleccione los registros que desea importar:
   - Use **"Seleccionar Todos"** para seleccionar todos los válidos
   - O seleccione individualmente
5. **Asignar Comprador:**
   - Ingrese el ID del comprador al que se asignarán los envíos
   - O seleccione de la lista de compradores
6. Haga clic en **"Importar Datos"**

#### Paso 5: Confirmar Importación

1. Revise el resumen de la importación:
   - Total de registros procesados
   - Registros importados exitosamente
   - Registros con errores
   - Porcentaje de éxito
2. Descargue el reporte de errores si hubo problemas
3. Opciones:
   - **Importar Otro Archivo:** Iniciar nueva importación
   - **Volver al Dashboard:** Regresar al inicio

### Formato del Archivo Excel

#### Columnas Requeridas

| Columna | Tipo | Obligatorio | Descripción |
|---------|------|-------------|-------------|
| HAWB | Texto | ✅ Sí | Número único de guía de envío |
| Peso Total | Número | ❌ No | Peso total del envío en kg |
| Cantidad Total | Entero | ❌ No | Cantidad total de productos |
| Valor Total | Número | ❌ No | Valor total del envío |
| Estado | Texto | ❌ No | pendiente, en_transito, entregado, cancelado |
| Descripción Producto | Texto | ❌ No | Descripción del producto |
| Peso Producto | Número | ❌ No | Peso individual del producto |
| Cantidad Producto | Entero | ❌ No | Cantidad del producto |
| Valor Producto | Número | ❌ No | Valor del producto |
| Categoría | Texto | ❌ No | electronica, ropa, hogar, deportes, otros |
| Observaciones | Texto | ❌ No | Notas adicionales |

#### Ejemplo de Datos

```
HAWB    | Peso Total | Cantidad Total | Valor Total | Descripción Producto | Categoría
--------|------------|----------------|-------------|---------------------|------------
HAWB001 | 5.5        | 2              | 150.00      | Laptop Dell         | electronica
HAWB002 | 1.2        | 3              | 45.50       | Camiseta Nike       | ropa
HAWB003 | 3.0        | 1              | 80.00       | Cafetera            | hogar
```

### Validaciones

El sistema valida:
- ✅ Formato de archivo correcto
- ✅ Estructura de columnas válida
- ✅ HAWB único (no duplicados)
- ✅ Tipos de datos correctos
- ✅ Valores positivos para peso y valor
- ✅ Categorías válidas

### Errores Comunes

- **HAWB duplicado:** El HAWB ya existe en el sistema
- **Formato incorrecto:** El archivo no es Excel válido
- **Columnas faltantes:** Faltan columnas requeridas
- **Datos inválidos:** Valores negativos o tipos incorrectos

### Descargar Plantilla

Puede descargar una plantilla de ejemplo desde el módulo para ver el formato correcto.

---

## 10. Gestión de Tarifas

**Ruta:** `/tarifas`  
**Acceso:** Admin, Gerente

### Descripción

Configuración de tarifas de envío por categoría de producto. Las tarifas se usan para calcular automáticamente los costos de envío.

### Crear una Tarifa

1. **Acceder al módulo**
   - Navegue a **"Tarifas"** en el menú
   - Haga clic en **"Nueva Tarifa"**

2. **Completar información**
   - **Categoría:** Seleccione la categoría de producto:
     - Electrónica
     - Ropa
     - Hogar
     - Deportes
     - Otros
   - **Precio por kg:** Precio en USD por kilogramo (obligatorio, debe ser positivo)
   - **Precio Base:** Precio mínimo del envío (opcional)
   - **Fecha de Vigencia:** Fecha desde la cual es válida (opcional)

3. **Guardar**
   - Haga clic en **"Guardar Tarifa"**

### Editar una Tarifa

1. Localice la tarifa en la lista
2. Haga clic en **"Editar"**
3. Modifique los valores necesarios
4. Guarde los cambios

### Eliminar una Tarifa

1. Localice la tarifa
2. Haga clic en **"Eliminar"**
3. Confirme la eliminación

### Cómo se Calculan los Costos

Al crear un envío, el sistema:
1. Identifica la categoría de cada producto
2. Busca la tarifa correspondiente a esa categoría
3. Calcula: `Cantidad × Peso × Precio por kg`
4. Suma todos los costos de productos
5. Aplica el precio base si es necesario

### Filtrar Tarifas

- **Categoría:** Filtre por categoría específica
- **Buscar:** Busque por categoría o precio

---

## 11. Mapa de Compradores

**Ruta:** `/mapa-compradores`  
**Acceso:** Admin, Gerente, Digitador

### Descripción

Visualización geográfica interactiva de todos los compradores en un mapa, mostrando su distribución por ubicación.

### Cómo Usar

1. Acceda a **"Mapa de Compradores"** desde el menú
2. El mapa se cargará automáticamente con marcadores de compradores
3. **Interactuar con el mapa:**
   - Haga clic en un marcador para ver información del comprador
   - Use el zoom para acercar/alejar
   - Arrastre para mover el mapa
4. **Filtros:**
   - **Provincia:** Filtre compradores por provincia
   - **Cantón:** Filtre por cantón (se carga según provincia)
   - **Ciudad:** Filtre por ciudad (se carga según cantón)
   - **Buscar:** Busque por nombre o cédula
5. Revise la información del comprador en el popup:
   - Nombre
   - Cédula
   - Ubicación completa
   - Total de envíos

### Información Mostrada

- Marcadores en el mapa según ubicación
- Popup con información del comprador al hacer clic
- Contador de compradores visibles
- Filtros por ubicación geográfica

---

## 12. Actividades del Sistema

**Ruta:** `/actividades`  
**Acceso:** Todos los usuarios autenticados

### Descripción

Panel de control con métricas, reportes y visualizaciones del rendimiento del sistema.

### Funcionalidades

#### Métricas Semánticas (Admin/Gerente)

- **MRR (Mean Reciprocal Rank):** Métrica de relevancia de búsqueda
- **nDCG@10:** Normalized Discounted Cumulative Gain
- **Precision@5:** Precisión en los primeros 5 resultados
- Gráficos de evolución temporal

#### Métricas de Rendimiento

- Tiempo de respuesta del sistema
- Nivel de carga (1/10/30 consultas simultáneas)
- Estadísticas por fecha
- Gráficos de rendimiento

#### Registros de Embeddings

- Estadísticas de generación de embeddings
- Procesamiento de datos
- Calidad de embeddings

### Cómo Usar

1. Acceda a **"Actividades del Sistema"** desde el menú o desde el perfil
2. Revise las métricas disponibles según su rol
3. Use los filtros de fecha para ver períodos específicos
4. Explore los gráficos para análisis visual

---

## 13. Notificaciones

**Ruta:** `/notificaciones`  
**Acceso:** Compradores

### Descripción

Sistema de notificaciones para compradores sobre sus envíos y actualizaciones importantes.

### Funcionalidades

- Ver todas las notificaciones
- Marcar como leídas
- Filtrar por tipo de notificación
- Eliminar notificaciones

### Cómo Usar

1. Acceda a **"Notificaciones"** desde el menú
2. Revise la lista de notificaciones
3. Haga clic en una notificación para ver detalles
4. Marque como leída cuando corresponda
5. Elimine notificaciones antiguas si lo desea

---

## 14. Mi Perfil

**Ruta:** `/perfil`  
**Acceso:** Todos los usuarios autenticados

### Descripción

Gestión de información personal y configuración de cuenta.

### Funcionalidades

#### Información Personal

1. **Editar información:**
   - Nombre completo
   - Correo electrónico
   - Teléfono
   - Fecha de nacimiento
   - Dirección

2. **Ubicación:**
   - Provincia
   - Cantón (se carga según provincia)
   - Ciudad (se carga según cantón)

3. **Guardar cambios:**
   - Haga clic en **"Guardar Cambios"**

#### Cambiar Contraseña

1. Haga clic en **"Cambiar Contraseña"**
2. Ingrese su contraseña actual
3. Ingrese la nueva contraseña (debe cumplir requisitos)
4. Confirme la nueva contraseña
5. Haga clic en **"Cambiar Contraseña"**

#### Información de Cuenta

- Nombre de usuario (no editable)
- Rol asignado (no editable, contacte al administrador)
- Estado de cuenta (Activo/Inactivo)
- Fecha de registro

### Requisitos de Contraseña

- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos una minúscula
- Al menos un número
- Al menos un carácter especial

---

## Preguntas Frecuentes

### ¿Cómo puedo recuperar mi contraseña?

Contacte al administrador del sistema para restablecer su contraseña.

### ¿Puedo cambiar mi rol de usuario?

No, solo un administrador puede cambiar su rol. Contacte al administrador si necesita un cambio.

### ¿Qué pasa si olvido el HAWB de un envío?

Use la búsqueda de envíos ingresando el nombre del comprador o su cédula.

### ¿Puedo eliminar un envío que ya fue entregado?

Sí, pero se recomienda no eliminar envíos entregados para mantener el historial. Considere cancelarlo en lugar de eliminarlo.

### ¿Cómo se calcula el costo de envío?

El costo se calcula automáticamente usando las tarifas configuradas por categoría de producto: `Cantidad × Peso × Precio por kg`.

### ¿Puedo importar productos desde Excel?

Sí, puede importar envíos completos con productos desde Excel usando el módulo de Importación Excel.

### ¿Qué formato de Excel necesito para importar?

Descargue la plantilla desde el módulo de Importación Excel o consulte la sección [Importación desde Excel](#9-importación-desde-excel) en este manual.

### ¿Puedo ver envíos de otros compradores?

- **Compradores:** Solo pueden ver sus propios envíos
- **Digitadores, Gerentes, Admins:** Pueden ver todos los envíos

### ¿Cómo genero un comprobante PDF?

1. Abra los detalles del envío
2. Haga clic en **"Descargar Comprobante"**
3. El PDF se descargará automáticamente

### ¿Qué es el cupo anual?

El cupo anual es el límite de peso (en kilogramos) que un comprador puede enviar durante el año. Se muestra en el dashboard personal.

---

## Solución de Problemas

### No puedo iniciar sesión

**Posibles causas:**
- Credenciales incorrectas
- Cuenta inactiva
- Problemas de conexión

**Solución:**
1. Verifique que su nombre de usuario y contraseña sean correctos
2. Contacte al administrador si su cuenta está inactiva
3. Verifique su conexión a Internet

### No veo ciertos módulos en el menú

**Causa:** Su rol no tiene permisos para acceder a esos módulos.

**Solución:** Contacte al administrador si necesita acceso adicional.

### Error al crear un envío

**Posibles causas:**
- HAWB duplicado
- Campos obligatorios faltantes
- Valores inválidos

**Solución:**
1. Verifique que el HAWB no exista (se genera automáticamente)
2. Complete todos los campos obligatorios
3. Verifique que los valores numéricos sean positivos

### Error al importar desde Excel

**Posibles causas:**
- Formato de archivo incorrecto
- Columnas mal mapeadas
- HAWBs duplicados
- Datos inválidos

**Solución:**
1. Verifique que el archivo sea .xlsx o .xls
2. Revise el mapeo de columnas
3. Corrija los HAWBs duplicados
4. Revise el reporte de errores descargable

### El mapa de compradores no carga

**Posibles causas:**
- Problemas de conexión
- Ubicaciones no configuradas

**Solución:**
1. Verifique su conexión a Internet
2. Asegúrese de que los compradores tengan ubicación configurada

### No puedo cambiar mi contraseña

**Posibles causas:**
- Contraseña actual incorrecta
- Nueva contraseña no cumple requisitos

**Solución:**
1. Verifique que la contraseña actual sea correcta
2. Asegúrese de que la nueva contraseña cumpla todos los requisitos:
   - Mínimo 8 caracteres
   - Al menos una mayúscula, una minúscula, un número y un carácter especial

### Los totales del envío no se calculan

**Causa:** Faltan productos o información incompleta.

**Solución:**
1. Asegúrese de agregar al menos un producto
2. Complete peso, cantidad y valor de cada producto
3. Los totales se calculan automáticamente

### No puedo eliminar un producto

**Causa:** El producto está asociado a uno o más envíos.

**Solución:** No se pueden eliminar productos que están en uso. Considere desactivarlo o editarlo en su lugar.

---

## Contacto y Soporte

Para asistencia adicional:
- Contacte al administrador del sistema
- Revise la documentación técnica disponible
- Consulte los logs del sistema (si tiene acceso)

---

## Glosario de Términos

- **HAWB:** House Air Waybill - Número único de identificación de envío
- **Cupo Anual:** Límite de peso anual que un comprador puede enviar
- **Embedding:** Representación vectorial de datos para búsqueda semántica
- **MRR:** Mean Reciprocal Rank - Métrica de calidad de búsqueda
- **nDCG:** Normalized Discounted Cumulative Gain - Métrica de relevancia
- **RBAC:** Role-Based Access Control - Control de acceso basado en roles

---

**Última actualización:** Enero 2026  
**Versión del Manual:** 1.0

# Informe de mejoras: Módulo Mapa de Compradores

**Componente:** `frontend/src/app/components/mapa-compradores`  
**Ruta:** `/mapa-compradores`  
**Fecha de revisión:** Enero 2026

---

## 1. Resumen del estado actual

El módulo ofrece:
- **Layout:** Mapa a la derecha, gráfico de compradores por ciudad a la izquierda, listado de envíos por comprador abajo.
- **Funcionalidad:** Filtros por provincia/ciudad, búsqueda de comprador, interacción mapa ↔ gráfico ↔ listado.
- **Tecnologías:** Angular (standalone), Leaflet, Chart.js, API `getMapaCompradores()`.

Este documento propone mejoras de **diseño**, **funcionalidad** y **experiencia de uso** priorizadas y realizables.

---

## 2. Mejoras de diseño

### 2.1 Jerarquía visual y legibilidad

| Mejora | Descripción | Prioridad |
|--------|-------------|-----------|
| **Encabezados de panel** | Unificar estilo de los tres paneles (izquierdo, derecho, inferior): mismo tamaño de título, iconos y color de acento. | Alta |
| **Contraste y accesibilidad** | Revisar contraste de texto sobre fondos (especialmente badges y leyenda del mapa). Objetivo: WCAG AA. | Alta |
| **Espaciado** | Definir escala de espaciado (ej. 8, 12, 16, 24, 32px) y aplicarla de forma consistente en filtros, cards y listas. | Media |
| **Tipografía** | Reducir variación de tamaños; por ejemplo: título página, título panel, cuerpo, metadatos. | Media |

### 2.2 Panel de filtros

- **Colapsar/expandir** en móvil para ganar espacio para el mapa y el gráfico.
- **Indicador visual** cuando hay filtros activos (ej. badge con número o color distinto en “Limpiar”).
- **Placeholder y labels** más claros: “Buscar por nombre o usuario” en el input de comprador.

### 2.3 Gráfico (panel izquierdo)

- **Altura fija** del contenedor del gráfico (ej. 320px) para evitar saltos al cambiar datos.
- **Título del gráfico** visible: “Top 10 ciudades por número de compradores”.
- **Empty state** cuando no hay datos: mensaje + icono en lugar de gráfico vacío.
- **Colores** alineados con el resto de la app (por ejemplo, paleta del dashboard).

### 2.4 Mapa (panel derecho)

- **Controles de Leaflet** siempre visibles (zoom +/-) y con estilo coherente (tema claro/oscuro).
- **Leyenda** fija en una esquina (ej. inferior derecha) con mismo estilo que el resto del módulo.
- **Popup** de provincia/comprador: mismo tipo de letra y espaciado que el resto de la app; botones con estado hover.

### 2.5 Listado de envíos (panel inferior)

- **Cabecera de tabla** si se muestra en formato tabla: columnas ordenables (comprador, ciudad, envíos, estado reciente).
- **Paginación o “ver más”** cuando hay muchos compradores para no sobrecargar el DOM.
- **Estado vacío** mejorado: ilustración o icono grande + texto (“No hay envíos con los filtros actuales”) + sugerencia (“Prueba a quitar filtros”).

### 2.6 Responsive

- **Breakpoint único** (ej. 1024px) donde el layout pasa a una columna; definir orden: mapa arriba y gráfico + listado abajo (o al revés según prioridad).
- **Touch:** tamaño mínimo de botones y áreas clicables (44px) y distancia entre elementos para evitar clics erróneos.
- **Gráfico:** en móvil, altura reducida pero legible; considerar scroll horizontal si hay muchas barras.

---

## 3. Mejoras de funcionalidad

### 3.1 Navegación y sincronización

| Mejora | Descripción | Prioridad |
|--------|-------------|-----------|
| **Breadcrumb o contexto** | Mostrar “Ecuador > [Provincia] > [Ciudad]” cuando hay provincia/ciudad seleccionada para entender dónde se está. | Alta |
| **Resaltar en mapa** | Al elegir una ciudad en el gráfico o en la lista, centrar el mapa en esa provincia/ciudad y resaltar el marcador (animación o estilo distinto). | Alta |
| **Resaltar en listado** | Al hacer clic en un comprador en el mapa, hacer scroll hasta su tarjeta en el listado y resaltarla brevemente. | Media |
| **URL / estado** | Reflejar provincia y ciudad en query params (ej. `?provincia=Guayas&ciudad=Guayaquil`) para poder compartir y recargar la misma vista. | Media |

### 3.2 Filtros y búsqueda

- **Búsqueda por HAWB** en el listado de envíos (solo si el backend lo permite o hay datos en cliente).
- **Filtro por estado de envío** (pendiente, en tránsito, entregado, cancelado) en el panel inferior.
- **Orden del listado:** por nombre comprador, ciudad, o número de envíos (selector en cabecera del panel).
- **Debounce** en el input de búsqueda de comprador (ej. 300 ms) para no llamar a `actualizarVistaFiltrada()` en cada tecla.

### 3.3 Gráfico

- **Cambio de tipo** opcional: además de barras, ofrecer gráfico de pastel/dona para “compradores por provincia”.
- **Clic en barra:** además de filtrar por ciudad, opción de “solo esta ciudad” para que el listado muestre solo compradores de esa ciudad.
- **Tooltip** con más datos: ciudad, provincia, número de compradores, número total de envíos.

### 3.4 Mapa

- **Cluster de marcadores** cuando hay muchos compradores en una provincia (ej. Leaflet.markercluster) para no saturar el mapa.
- **Límite de zoom** máximo razonable (ej. 14–15) para no llegar a calles si no hay datos tan granulares.
- **Botón “Mi ubicación”** (opcional) para centrar el mapa en la ubicación del usuario si se usa geolocalización.

### 3.5 Listado de envíos

- **Expandir/colapsar** cada tarjeta de comprador para ver solo cabecera por defecto y detalles al clic.
- **Enlace al detalle del envío** desde cada fila (HAWB) si existe ruta de detalle en la app.
- **Exportar** listado visible (CSV/Excel) de compradores y envíos filtrados.

### 3.6 Datos y rendimiento

- **Caché** de la respuesta de `getMapaCompradores()` (por tiempo o hasta que el usuario pulse “Actualizar”).
- **Loading por zona:** spinner solo en el panel que está cargando (mapa, gráfico o listado) si en el futuro se cargaran por separado.
- **Manejo de errores:** mensaje por panel (ej. “No se pudo cargar el mapa”) con botón “Reintentar” sin recargar toda la página.

---

## 4. Mejoras de experiencia de uso (UX)

- **Onboarding breve:** tooltip o modal la primera vez que se entra: “Puedes filtrar por provincia y ciudad, hacer clic en el gráfico o en el mapa para explorar.”
- **Feedback inmediato:** al aplicar filtros, mensaje corto “Mostrando X compradores” o actualizar el subtítulo del listado.
- **Confirmación al limpiar filtros:** si hay varios filtros activos, opción “¿Limpiar todos los filtros?” para evitar pérdida accidental de contexto.
- **Atajos de teclado** (opcional): “Escape” para volver a vista general del mapa o limpiar selección.

---

## 5. Mejoras técnicas (código y mantenimiento)

- **Tipado:** sustituir `any` en `map`, `markers`, `L` por tipos de Leaflet (`Map`, `Marker`, etc.) para mejor autocompletado y menos errores.
- **Desuscripciones:** asegurar que todas las suscripciones (p. ej. a `getMapaCompradores()`) se cancelen en `ngOnDestroy` (por ejemplo con `takeUntilDestroyed()` o un `Subject`).
- **Reutilización:** extraer lógica de “compradores por ciudad” y “envíos por comprador” a un servicio o a funciones puras en un util, para facilitar tests y reutilización.
- **Tests:** al menos tests unitarios para `obtenerDatosFiltrados()`, `obtenerEnviosFiltrados()` y `getTotalEnviosSeleccionados()`.
- **Accesibilidad:** `aria-label` en botones solo con icono, `role` y `aria-live` en zona de resultados del listado, y orden de tabulación lógico en filtros y paneles.

---

## 6. Priorización sugerida

### Fase 1 (impacto rápido)
1. Indicador de filtros activos en el panel de filtros.  
2. Breadcrumb o texto de contexto (provincia/ciudad seleccionada).  
3. Resaltar en el mapa la provincia/ciudad seleccionada desde el gráfico.  
4. Debounce en búsqueda de comprador.  
5. Empty states claros en gráfico y listado.

### Fase 2 (valor para el usuario)
1. Query params en la URL para compartir vista.  
2. Paginación o “ver más” en el listado.  
3. Clusters en el mapa cuando hay muchos compradores.  
4. Mejorar responsive (orden y tamaño de paneles en móvil).  
5. Filtro por estado de envío en el listado.

### Fase 3 (pulido y robustez)
1. Refactor de tipos y servicios.  
2. Tests unitarios.  
3. Pequeño onboarding o tooltips.  
4. Exportar listado (CSV/Excel).  
5. Revisión de accesibilidad (contraste, teclado, lectores de pantalla).

---

## 7. Conclusión

El módulo ya ofrece un layout claro (mapa a la derecha, gráfico a la izquierda, listado abajo) y filtros útiles. Las mejoras propuestas se centran en:

- **Diseño:** consistencia visual, jerarquía, empty states y responsive.  
- **Funcionalidad:** sincronización entre mapa, gráfico y listado, filtros adicionales, clusters y (opcionalmente) estado en la URL.  
- **UX:** feedback claro, contexto (breadcrumb), y menor riesgo de clics accidentales al limpiar filtros.  
- **Código:** tipado, desuscripciones, servicios y tests para mantener y extender el módulo con seguridad.

Aplicando en primer lugar la Fase 1 se obtiene una mejora notable de usabilidad y claridad con esfuerzo acotado.

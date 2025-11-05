# 🚀 Guía de Inicio Rápido - Módulo de Búsqueda de Envíos

## ⚡ Acceso Inmediato

### Paso 1: Navegar al Módulo

Abra su navegador y vaya a:

```
http://localhost:4200/busqueda-envios
```

O agregue el enlace al menú de su aplicación.

---

## 📝 Uso Básico en 3 Pasos

### 1️⃣ Búsqueda Rápida

```
Escriba en la barra de búsqueda:
→ Número de guía (HAWB123)
→ Nombre del destinatario (Juan Pérez)
→ Cualquier término relacionado
```

**Resultado:** Lista de envíos que coinciden con su búsqueda

### 2️⃣ Usar Filtros Avanzados

```
Click en "Mostrar Filtros Avanzados"
→ Complete los campos deseados
→ Click en "Buscar"
```

**Filtros disponibles:**
- Número de Guía
- Nombre del Destinatario
- Ciudad de Destino
- Estado del Envío
- Rango de Fechas

### 3️⃣ Ver Detalles y Acciones

```
Para cada envío encontrado:
👁️  Ver detalles completos
📥 Descargar comprobante
🖨️  Imprimir comprobante
🗺️  Ver en mapa
```

---

## 🎯 Ejemplos de Búsqueda

### Ejemplo 1: Buscar por Número de Guía

```
1. En la barra principal, escriba: HAWB001
2. Espere 0.5 segundos
3. ✅ Resultado: Envío con guía HAWB001
```

### Ejemplo 2: Buscar Envíos En Tránsito

```
1. Click en "Mostrar Filtros Avanzados"
2. En "Estado del Envío", seleccione: En Tránsito
3. Click en "Buscar"
4. ✅ Resultado: Todos los envíos en tránsito
```

### Ejemplo 3: Buscar por Ciudad y Fecha

```
1. Click en "Mostrar Filtros Avanzados"
2. Ciudad de Destino: Quito
3. Fecha Desde: 2025-01-01
4. Fecha Hasta: 2025-01-31
5. Click en "Buscar"
6. ✅ Resultado: Envíos a Quito en enero 2025
```

### Ejemplo 4: Buscar por Destinatario

```
1. En "Filtros Avanzados"
2. Nombre del Destinatario: María García
3. Click en "Buscar"
4. ✅ Resultado: Todos los envíos para María García
```

---

## 🔧 Acciones Comunes

### Ver Detalles de un Envío

```
1. Localice el envío en la tabla
2. Click en el botón del ojo (👁️)
3. Se abre un modal con:
   - Información general
   - Datos del destinatario
   - Lista de productos
   - Observaciones
```

### Descargar Comprobante

```
1. Click en el botón de descarga (📥)
2. El PDF se descarga automáticamente
3. Nombre del archivo: comprobante-HAWB001.pdf
```

### Ver Ubicación en Mapa

```
1. Click en el botón del mapa (🗺️)
2. Redirige al módulo de mapas
3. Muestra la ubicación del destinatario
```

---

## 📊 Personalizar Vista

### Cambiar Ordenamiento

```
En el selector "Ordenar por":
→ Fecha más reciente (por defecto)
→ Fecha más antigua
→ Número de guía A-Z
→ Valor mayor/menor
→ Peso mayor/menor
```

### Cambiar Elementos por Página

```
En el selector "Mostrar":
→ 5 elementos
→ 10 elementos (por defecto)
→ 20 elementos
→ 50 elementos
```

### Navegar entre Páginas

```
Opciones de navegación:
← Anterior | 1 2 3 ... 10 | Siguiente →
```

---

## ❓ Preguntas Frecuentes

### ¿Cómo limpio los filtros?

**Respuesta:** Click en el botón "Limpiar Filtros" o en la (X) de la barra de búsqueda principal.

### ¿La búsqueda es en tiempo real?

**Respuesta:** Sí, en la barra principal. Hay un delay de 500ms para evitar búsquedas excesivas.

### ¿Puedo exportar los resultados?

**Respuesta:** Sí, si tiene permisos de Admin, Gerente o Digitador. Click en "Exportar" y seleccione el formato.

### ¿Qué significan los colores de estado?

**Respuesta:**
- 🔵 Azul = Pendiente
- 🟠 Naranja = En Tránsito
- 🟢 Verde = Entregado
- 🔴 Rojo = Cancelado

### ¿Por qué no veo todos los envíos?

**Respuesta:** Los Compradores solo ven sus propios envíos. Admin, Gerente y Digitador ven todos.

---

## 🎨 Atajos de Teclado (Futuro)

```
Ctrl + K    → Enfocar barra de búsqueda
Ctrl + F    → Abrir filtros avanzados
Ctrl + L    → Limpiar filtros
Esc         → Cerrar modal
```

---

## 🐛 ¿Problemas?

### No aparecen resultados

```
✓ Verifique que existan datos en la base de datos
✓ Limpie los filtros y busque de nuevo
✓ Revise los permisos de su usuario
```

### Error de conexión

```
✓ Verifique que el backend esté ejecutándose
✓ Confirme la URL del API en environment.ts
✓ Revise la consola del navegador (F12)
```

### La página está en blanco

```
✓ Recargue la página (F5)
✓ Limpie la caché del navegador
✓ Revise la consola para errores
```

---

## 📱 Uso en Móvil

El módulo es completamente responsive:

```
📱 Móvil:
→ Tabla se vuelve scrolleable horizontalmente
→ Filtros se apilan verticalmente
→ Botones de acción más grandes
→ Menú de navegación adaptado
```

---

## ✅ Checklist de Primera Vez

- [ ] Accedí al módulo en el navegador
- [ ] Probé la búsqueda general
- [ ] Abrí los filtros avanzados
- [ ] Filtré por estado
- [ ] Vi los detalles de un envío
- [ ] Probé la paginación
- [ ] Cambié el ordenamiento
- [ ] Ajusté elementos por página

---

## 🎓 Consejos Pro

### Tip 1: Búsqueda Combinada
```
Use búsqueda general + filtros avanzados para resultados precisos
Ejemplo: "Juan" en búsqueda + Estado: "En Tránsito"
```

### Tip 2: Ordenamiento Inteligente
```
Para auditorías: Ordene por "Fecha más reciente"
Para reportes: Ordene por "Valor mayor"
```

### Tip 3: Paginación Eficiente
```
Para búsquedas específicas: Use 5-10 elementos
Para navegación general: Use 20-50 elementos
```

### Tip 4: Filtros Guardados (Próximamente)
```
Guarde combinaciones de filtros frecuentes
Acceso rápido con un solo click
```

---

## 📞 Soporte Rápido

**¿Necesita ayuda inmediata?**

1. Consulte la documentación completa: `MODULO_BUSQUEDA_ENVIOS_README.md`
2. Revise ejemplos de código en la documentación
3. Contacte al equipo de desarrollo

---

## 🎉 ¡Listo para Empezar!

Ya tiene todo lo necesario para usar el módulo de búsqueda de envíos de manera eficiente.

**Recuerde:**
- La búsqueda es intuitiva y rápida
- Los filtros le dan control total
- Todos los datos están protegidos por permisos
- La interfaz se adapta a su dispositivo

**¡Feliz búsqueda! 🚀📦**


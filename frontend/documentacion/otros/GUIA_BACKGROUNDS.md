# Guía de Configuración de Backgrounds del Sistema

Este documento explica dónde y cómo modificar los backgrounds (fondos) de las distintas ventanas y componentes del sistema UBApp.

## 📍 Ubicaciones para Modificar Backgrounds

### 1. Background Global del Sistema
**Archivo:** `frontend/src/styles.css`

```css
body {
  background-color: #f8fafc;  /* Cambiar este valor */
  color: #1e293b;
}
```

**Uso:** Este es el fondo principal que se aplica a toda la aplicación cuando no hay un componente específico que lo sobrescriba.

---

### 2. Background del Contenedor Principal
**Archivo:** `frontend/src/app/app.component.css`

**Sección 1 - Body:**
```css
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f8fafc;  /* Cambiar aquí */
  color: #1e293b;
}
```

**Sección 2 - Main Content:**
```css
.main-content {
  flex: 1;
  padding: 0;
  width: 100%;
  /* Agregar background-color aquí si deseas un fondo específico para el contenido */
}
```

---

### 3. Background de la Navbar
**Archivo:** `frontend/src/app/components/navbar/navbar.component.css`

```css
.animated-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);  /* Cambiar aquí */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
```

**Para un fondo sólido en lugar de gradiente:**
```css
background: #667eea;  /* Color sólido */
```

**Para un fondo diferente:**
```css
background: linear-gradient(135deg, #tu-color-1 0%, #tu-color-2 100%);
```

---

### 4. Background del Footer
**Archivo:** `frontend/src/app/components/footer/footer.component.css`

```css
.app-footer {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);  /* Cambiar aquí */
  color: white;
  margin-top: auto;
}
```

---

### 5. Background de Cards (Tarjetas)
**Archivo:** `frontend/src/styles.css`

```css
.card {
  background: white;  /* Cambiar aquí */
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}
```

---

### 6. Background de Componentes Específicos

Cada componente puede tener su propio archivo CSS con backgrounds personalizados:

- **Dashboard:** `frontend/src/app/components/dashboard/dashboard/dashboard.component.css`
- **Búsqueda:** `frontend/src/app/components/busqueda-envios/busqueda-envios.component.css`
- **Envíos:** `frontend/src/app/components/envios/envios-list/envios-list.component.css`
- **Etc.**

Busca en cada archivo CSS del componente la propiedad `background` o `background-color`.

---

### 7. Modo Oscuro (Dark Mode)

**Para backgrounds en modo oscuro:**

**Archivo:** `frontend/src/app/app.component.css`

```css
body.dark-mode {
  background-color: #1e293b;  /* Cambiar fondo en modo oscuro */
  color: #e5e7eb;
}

body.dark-mode .card {
  background-color: #334155;  /* Cambiar fondo de cards en modo oscuro */
}
```

**Archivo:** `frontend/src/app/components/navbar/navbar.component.css`

```css
:host-context(.dark-mode) .animated-header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);  /* Cambiar aquí */
}
```

---

## 🎨 Ejemplos de Configuración

### Ejemplo 1: Cambiar el fondo principal a un color sólido
```css
/* En frontend/src/styles.css */
body {
  background-color: #ffffff;  /* Fondo blanco */
}
```

### Ejemplo 2: Cambiar el fondo principal a un gradiente personalizado
```css
/* En frontend/src/styles.css */
body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### Ejemplo 3: Cambiar el fondo principal a una imagen
```css
/* En frontend/src/styles.css */
body {
  background-image: url('/assets/images/fondo.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}
```

### Ejemplo 4: Background diferente por ruta
Puedes agregar clases específicas en los componentes según la ruta activa:

```typescript
// En el componente TypeScript
export class MyComponent {
  constructor(private router: Router) {}
  
  get isDashboard() {
    return this.router.url.includes('/dashboard');
  }
}
```

```html
<!-- En el template HTML -->
<div [class.dashboard-bg]="isDashboard" class="component-container">
  <!-- contenido -->
</div>
```

```css
/* En el CSS del componente */
.component-container {
  background-color: #f8fafc;  /* Fondo por defecto */
}

.component-container.dashboard-bg {
  background-color: #e0e7ff;  /* Fondo específico para dashboard */
}
```

---

## 📝 Notas Importantes

1. **Orden de Precedencia:** Los estilos más específicos sobrescriben los generales. Un estilo en un componente específico tiene prioridad sobre los estilos globales.

2. **Modo Oscuro:** Asegúrate de definir backgrounds para modo oscuro si planeas usarlo.

3. **Responsive:** Considera usar media queries para backgrounds diferentes en móviles:
   ```css
   @media (max-width: 768px) {
     body {
       background-color: #f5f5f5;
     }
   }
   ```

4. **Performance:** Las imágenes de fondo grandes pueden afectar el rendimiento. Usa imágenes optimizadas y considera usar `background-attachment: fixed` solo cuando sea necesario.

---

## 🔄 Próximos Pasos

1. Modifica los archivos mencionados según tus preferencias
2. Recarga la aplicación para ver los cambios
3. Ajusta los colores de texto si cambias a un fondo oscuro
4. Prueba en modo oscuro si aplica

---

**Última actualización:** Enero 2025


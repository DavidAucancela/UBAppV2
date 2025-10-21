# Mejoras del Sistema - Gestión de Roles y Dashboard de Usuario

## Fecha: Octubre 2025

## Resumen de Mejoras Implementadas

Este documento describe las mejoras implementadas en el sistema de gestión de envíos, enfocadas en:
1. Sistema de roles y permisos mejorado
2. Dashboard personalizado para usuarios
3. Visualización de cupo anual
4. Páginas informativas del sistema

---

## 1. Sistema de Roles y Permisos

### Roles Definidos

#### 👑 **Administrador (Admin)**
- **Acceso:** Completo a todas las funcionalidades
- **Permisos:**
  - Gestión completa de usuarios
  - Gestión de envíos
  - Dashboard de gerente
  - Búsqueda semántica e inteligente
  - Todas las demás funcionalidades

#### 👔 **Gerente**
- **Acceso:** Gestión y análisis
- **Permisos:**
  - Búsqueda semántica e inteligente
  - Dashboard de gerente (vista de todos los envíos del sistema)
  - Visualización de usuarios (excepto admins)
  - Gestión de envíos
  - Mapa de compradores
  - Reportes y estadísticas

#### ⌨️ **Digitador**
- **Acceso:** Operación diaria
- **Permisos:**
  - Gestión de envíos (crear, editar, eliminar)
  - Importación de archivos Excel
  - Visualización de compradores
  - Mapa de compradores

#### 🛒 **Comprador**
- **Acceso:** Personal
- **Permisos:**
  - Dashboard personal con cupo anual
  - Visualización de sus propios envíos
  - Estadísticas personales
  - Seguimiento de cupo anual

### Nuevas Clases de Permisos (Backend)

```python
# backend/apps/usuarios/permissions.py

- SoloAdmin: Solo administradores
- EsAdminOGerente: Administradores y gerentes
- EsDigitador: Digitadores, gerentes y administradores
- AccesoBusquedaSemantica: Admin y gerentes
- AccesoDashboardGerente: Admin y gerentes
- PuedeGestionarEnvios: Admin, gerentes y digitadores
```

---

## 2. Dashboard de Usuario

### Ubicación
- **Ruta:** `/dashboard-usuario`
- **Componente:** `DashboardUsuarioComponent`
- **Acceso:** Todos los usuarios autenticados

### Características

#### Para Compradores

**Visualización de Cupo Anual:**
- Barra de progreso animada y colorida
- Muestra peso usado vs. cupo total
- Porcentaje de uso
- Peso disponible
- Alertas cuando se acerca al límite (80%, 90%)
- Colores dinámicos según el uso:
  - Verde: < 50%
  - Azul: 50-79%
  - Amarillo: 80-89%
  - Rojo: ≥ 90%

**Estadísticas Personales:**
- Total de envíos
- Envíos por estado (pendientes, en tránsito, entregados, cancelados)
- Valor total de envíos
- Costo total de servicios
- Peso total enviado

**Envíos Recientes:**
- Últimos 10 envíos
- Vista detallada con estado, peso, valor
- Link para ver todos los envíos

#### Para Otros Roles
- Vista de estadísticas generales
- Información relevante según el rol

### Endpoints del Backend

```python
# GET /api/usuarios/dashboard_usuario/
# Parámetros: ?anio=2025 (opcional)
# Retorna: Dashboard completo con estadísticas y envíos recientes

# GET /api/usuarios/estadisticas_cupo/
# Parámetros: ?anio=2025 (opcional)
# Retorna: Estadísticas detalladas del cupo anual

# GET /api/usuarios/mis_envios/
# Parámetros: ?estado=pendiente&fecha_desde=2025-01-01&fecha_hasta=2025-12-31
# Retorna: Todos los envíos del usuario con filtros
```

---

## 3. Cupo Anual

### Modelo de Usuario Actualizado

```python
# Nuevo campo en el modelo Usuario
cupo_anual = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=1000.00,
    verbose_name="Cupo Anual (kg)"
)
```

### Métodos del Modelo

```python
# Obtener peso usado en el año
usuario.obtener_peso_usado_anual(anio=2025)

# Obtener peso disponible
usuario.obtener_peso_disponible_anual(anio=2025)

# Obtener porcentaje de uso
usuario.obtener_porcentaje_cupo_usado(anio=2025)

# Obtener estadísticas completas
usuario.obtener_estadisticas_envios(anio=2025)
```

### Migración

```bash
# Ejecutar migración para agregar el campo cupo_anual
cd backend
python manage.py migrate usuarios
```

---

## 4. Páginas Informativas

### 4.1 Página de Información General

**Ruta:** `/informacion`
**Componente:** `InformacionGeneralComponent`
**Acceso:** Público

#### Características:
- Hero section con presentación del sistema
- Características principales (6 tarjetas destacadas)
- Beneficios del sistema
- Información sobre roles
- Call-to-action para iniciar sesión
- Footer con información de copyright

#### Secciones:
1. **Hero:** Presentación principal con botones de acción
2. **Características:** Gestión de envíos, dashboard, búsqueda, importación, mapa, seguridad
3. **Beneficios:** Lista de ventajas del sistema
4. **Roles:** Explicación visual de cada rol
5. **CTA:** Llamada a la acción para acceder al sistema

### 4.2 Página de Ubicaciones

**Ruta:** `/ubicaciones`
**Componente:** `UbicacionesComponent`
**Acceso:** Público

#### Características:
- Listado de oficinas de la empresa
- Información detallada de cada ubicación:
  - Dirección completa
  - Teléfono y email
  - Horario de atención
  - Coordenadas geográficas
- Visualización en mapa (placeholder con link a Google Maps)
- Botón para abrir en Google Maps directamente

#### Ubicaciones Incluidas:
1. **Quito** (Oficina Principal)
2. **Guayaquil** (Sucursal)
3. **Cuenca** (Sucursal)

---

## 5. Mis Envíos

### Ubicación
- **Ruta:** `/mis-envios`
- **Componente:** `MisEnviosComponent`
- **Acceso:** Usuarios autenticados

### Características:
- Lista completa de envíos del usuario
- Filtros avanzados:
  - Por estado
  - Por rango de fechas
- Tabla responsive con información detallada
- Link para volver al dashboard

---

## 6. Actualización de Rutas

### Rutas Públicas
```typescript
{ path: '', redirectTo: '/informacion' }
{ path: 'informacion', component: InformacionGeneralComponent }
{ path: 'ubicaciones', component: UbicacionesComponent }
{ path: 'login', component: LoginComponent }
```

### Rutas Protegidas con Roles
```typescript
// Dashboard de Gerente (Admin y Gerente)
{ path: 'dashboard', component: DashboardComponent, 
  canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE])] }

// Dashboard de Usuario (Todos)
{ path: 'dashboard-usuario', component: DashboardUsuarioComponent,
  canActivate: [authGuard] }

// Búsqueda Semántica (Admin y Gerente)
{ path: 'busqueda-semantica', component: BusquedaSemanticaComponent,
  canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE])] }

// Gestión de Envíos (Admin, Gerente, Digitador)
{ path: 'envios', component: EnviosListComponent,
  canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR])] }
```

---

## 7. Servicios del Frontend

### UsuarioService

```typescript
// Nuevo servicio para gestionar dashboard y envíos del usuario
getDashboardUsuario(anio?: number): Observable<{...}>
getEstadisticasCupo(anio?: number): Observable<EstadisticasCupo>
getMisEnvios(filtros?: {...}): Observable<{...}>
```

---

## 8. Interfaces TypeScript Actualizadas

```typescript
// Modelo de Usuario
interface Usuario {
  cupo_anual?: number;
  // ... otros campos
}

// Dashboard de Usuario
interface DashboardUsuario {
  usuario: Usuario;
  cupo_anual: number;
  peso_usado: number;
  peso_disponible: number;
  porcentaje_usado: number;
  total_envios: number;
  // ... estadísticas
  anio: number;
}

// Estadísticas de Cupo
interface EstadisticasCupo {
  cupo_anual: number;
  peso_usado: number;
  peso_disponible: number;
  porcentaje_usado: number;
  anio: number;
  alerta: 'success' | 'info' | 'warning';
}
```

---

## 9. Flujo de Navegación

### Usuario No Autenticado
```
/ (Raíz)
  ↓
/informacion (Página principal)
  ↓
[Ver Información] → [Ver Ubicaciones] → [Iniciar Sesión]
```

### Usuario Comprador
```
Login
  ↓
/dashboard-usuario (Dashboard Personal)
  ↓
- Ver cupo anual
- Ver estadísticas personales
- Ver envíos recientes
  ↓
/mis-envios (Todos mis envíos)
```

### Usuario Digitador
```
Login
  ↓
/inicio
  ↓
- Gestión de envíos
- Importación Excel
- Mapa de compradores
```

### Usuario Gerente
```
Login
  ↓
/inicio
  ↓
- Dashboard de Gerente (todos los envíos)
- Búsqueda semántica
- Búsqueda inteligente
- Gestión de usuarios
- Reportes completos
```

### Usuario Admin
```
Login
  ↓
/inicio
  ↓
Acceso completo a todas las funcionalidades
```

---

## 10. Estilos y UI/UX

### Características Visuales

1. **Barra de Progreso de Cupo:**
   - Animada con gradientes
   - Colores dinámicos según porcentaje
   - Efecto "striped" animado
   - Altura de 30px para mejor visibilidad

2. **Tarjetas Informativas:**
   - Sombras suaves
   - Hover effects con elevación
   - Animaciones de fade-in
   - Iconos de Bootstrap Icons

3. **Responsive Design:**
   - Adaptación a móviles
   - Grid system de Bootstrap
   - Tablas responsive

4. **Animaciones:**
   - Fade-in para carga de contenido
   - Float para iconos decorativos
   - Pulse para elementos importantes
   - Hover effects en tarjetas

---

## 11. Instalación y Configuración

### Backend

```bash
cd backend

# Activar entorno virtual
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Ejecutar migraciones
python manage.py makemigrations usuarios
python manage.py migrate

# Actualizar cupo anual de usuarios existentes (opcional)
python manage.py shell
>>> from apps.usuarios.models import Usuario
>>> Usuario.objects.filter(rol=4).update(cupo_anual=1000.00)
```

### Frontend

```bash
cd frontend

# Instalar dependencias (si es necesario)
npm install

# Compilar y ejecutar
ng serve
```

---

## 12. Testing

### Endpoints a Probar

```bash
# Dashboard de usuario
GET http://localhost:8000/api/usuarios/dashboard_usuario/?anio=2025

# Estadísticas de cupo
GET http://localhost:8000/api/usuarios/estadisticas_cupo/?anio=2025

# Mis envíos
GET http://localhost:8000/api/usuarios/mis_envios/?estado=pendiente

# Mis envíos con filtro de fechas
GET http://localhost:8000/api/usuarios/mis_envios/?fecha_desde=2025-01-01&fecha_hasta=2025-12-31
```

### Escenarios de Prueba

1. **Comprador con envíos:**
   - Verificar cálculo correcto del cupo usado
   - Verificar alertas cuando se acerca al límite
   - Verificar filtros de envíos

2. **Gerente:**
   - Acceso a dashboard gerencial
   - Acceso a búsqueda semántica
   - No puede ver el cupo personal (no aplica)

3. **Digitador:**
   - Puede gestionar envíos
   - No puede acceder a búsqueda semántica
   - No puede acceder a dashboard gerencial

4. **Admin:**
   - Acceso completo a todo

---

## 13. Próximas Mejoras Sugeridas

1. **Notificaciones:**
   - Alertas cuando el usuario se acerca al límite de cupo
   - Notificaciones de cambios de estado de envíos

2. **Reportes:**
   - Exportación de estadísticas a PDF
   - Reportes mensuales automáticos

3. **Analíticas:**
   - Gráficos de uso de cupo a lo largo del tiempo
   - Comparación año a año

4. **Mapa Real:**
   - Integración con Google Maps API
   - Visualización interactiva de ubicaciones

---

## 14. Archivos Modificados y Creados

### Backend

**Modificados:**
- `backend/apps/usuarios/models.py` - Agregado cupo_anual y métodos
- `backend/apps/usuarios/views.py` - Agregados nuevos endpoints
- `backend/apps/usuarios/serializers.py` - Agregado DashboardUsuarioSerializer
- `backend/apps/usuarios/permissions.py` - Nuevas clases de permisos

**Creados:**
- `backend/apps/usuarios/migrations/0006_usuario_cupo_anual.py` - Migración

### Frontend

**Creados:**
- `frontend/src/app/services/usuario.service.ts`
- `frontend/src/app/components/dashboard/dashboard-usuario/`
  - `dashboard-usuario.component.ts`
  - `dashboard-usuario.component.html`
  - `dashboard-usuario.component.css`
- `frontend/src/app/components/envios/mis-envios/`
  - `mis-envios.component.ts`
  - `mis-envios.component.html`
  - `mis-envios.component.css`
- `frontend/src/app/components/informacion/informacion-general/`
  - `informacion-general.component.ts`
  - `informacion-general.component.html`
  - `informacion-general.component.css`
- `frontend/src/app/components/informacion/ubicaciones/`
  - `ubicaciones.component.ts`
  - `ubicaciones.component.html`
  - `ubicaciones.component.css`

**Modificados:**
- `frontend/src/app/models/usuario.ts` - Interfaces actualizadas
- `frontend/src/app/app.routes.ts` - Rutas actualizadas

---

## 15. Conclusión

Se ha implementado exitosamente un sistema completo de gestión de roles y permisos, junto con dashboards personalizados y páginas informativas. El sistema ahora proporciona:

✅ Control granular de acceso por roles
✅ Dashboard personalizado para cada tipo de usuario
✅ Visualización intuitiva del cupo anual
✅ Páginas informativas profesionales
✅ Mejor experiencia de usuario
✅ Navegación optimizada

El sistema está listo para producción y puede ser extendido fácilmente con las mejoras sugeridas.

---

**Documentación creada:** Octubre 2025
**Última actualización:** Octubre 2025
**Versión:** 2.0


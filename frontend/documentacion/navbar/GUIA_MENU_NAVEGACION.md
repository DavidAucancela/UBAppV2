# Guía de Modificación del Menú de Navegación

Esta guía explica cómo modificar los elementos y subcategorías del menú de navegación, así como controlar quién puede acceder y visualizar esas categorías.

## 📍 Ubicación del Archivo

**Archivo:** `frontend/src/app/components/navbar/navbar.component.ts`

El menú se define en la propiedad privada `allNavItems` (líneas 143-239).

---

## 🔧 Estructura de un Elemento del Menú

Cada elemento del menú (`NavItem`) tiene la siguiente estructura:

```typescript
interface NavItem {
  label: string;           // Texto que se muestra en el menú
  icon: string;            // Icono de Font Awesome (ej: 'fas fa-home')
  route: string;           // Ruta de Angular (ej: '/dashboard')
  roles: Roles[];          // Array de roles que pueden ver este elemento
  order: number;           // Orden de aparición en el menú (menor número = aparece primero)
  subItems?: NavSubItem[]; // Opcional: subcategorías
}

interface NavSubItem {
  label: string;           // Texto del submenú
  icon: string;            // Icono de Font Awesome
  route: string;           // Ruta de Angular
}
```

---

## 👥 Roles Disponibles

Los roles están definidos en `frontend/src/app/models/usuario.ts`:

```typescript
export enum Roles {
  ADMIN = 1,      // Administrador
  GERENTE = 2,    // Gerente
  DIGITADOR = 3,  // Digitador
  COMPRADOR = 4   // Comprador
}
```

---

## 📝 Ejemplos de Modificación

### Ejemplo 1: Agregar un Nuevo Elemento del Menú

```typescript
// En navbar.component.ts, dentro de allNavItems array
{
  label: 'Inventario',
  icon: 'fas fa-warehouse',
  route: '/inventario',
  roles: [Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR], // Solo estos roles pueden verlo
  order: 6
}
```

### Ejemplo 2: Agregar un Elemento con Subcategorías

```typescript
{
  label: 'Reportes',
  icon: 'fas fa-chart-bar',
  route: '/reportes',
  roles: [Roles.ADMIN, Roles.GERENTE],
  order: 8,
  subItems: [
    { 
      label: 'Reportes de Envíos', 
      icon: 'fas fa-truck', 
      route: '/reportes/envios' 
    },
    { 
      label: 'Reportes de Ventas', 
      icon: 'fas fa-dollar-sign', 
      route: '/reportes/ventas' 
    },
    { 
      label: 'Rendimiento', 
      icon: 'fas fa-tachometer-alt', 
      route: '/reportes/rendimiento' 
    }
  ]
}
```

### Ejemplo 3: Modificar Permisos de Acceso

Para cambiar quién puede ver un elemento del menú, modifica el array `roles`:

```typescript
// Solo Admin puede ver
roles: [Roles.ADMIN]

// Admin y Gerente pueden ver
roles: [Roles.ADMIN, Roles.GERENTE]

// Todos los roles pueden ver
roles: [Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR, Roles.COMPRADOR]

// Solo Compradores pueden ver
roles: [Roles.COMPRADOR]
```

### Ejemplo 4: Cambiar el Orden de los Elementos

Modifica la propiedad `order`. Los elementos se ordenan de menor a mayor:

```typescript
{
  label: 'Dashboard',
  order: 1  // Aparece primero
},
{
  label: 'Envíos',
  order: 3  // Aparece después del Dashboard
},
{
  label: 'Reportes',
  order: 8  // Aparece al final
}
```

### Ejemplo 5: Eliminar un Elemento del Menú

Simplemente elimina el objeto del array `allNavItems`:

```typescript
// ANTES
{
  label: 'Productos',
  icon: 'fas fa-box',
  route: '/productos',
  roles: [Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR],
  order: 6
},

// DESPUÉS - Eliminado completamente
```

### Ejemplo 6: Modificar un Elemento Existente

Busca el elemento en `allNavItems` y modifica sus propiedades:

```typescript
// ANTES
{
  label: 'Dashboard',
  icon: 'fas fa-home',
  route: '/dashboard',
  roles: [Roles.ADMIN, Roles.GERENTE],
  order: 1
}

// DESPUÉS - Permitir que Digitador también lo vea
{
  label: 'Dashboard',
  icon: 'fas fa-home',
  route: '/dashboard',
  roles: [Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR], // Agregado ROLES.DIGITADOR
  order: 1
}
```

---

## 🔒 Control de Acceso por Ruta

Además de controlar la visibilidad en el menú, también debes proteger las rutas en el backend y en los guards de Angular.

### En Angular (Guards)

**Archivo:** `frontend/src/app/guards/role.guard.ts`

```typescript
import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { Roles } from '../models/usuario';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(route: any): boolean {
    const allowedRoles = route.data['roles'] as Roles[];
    const user = this.authService.getCurrentUser();
    
    if (!user) {
      this.router.navigate(['/login']);
      return false;
    }
    
    if (!allowedRoles.includes(user.rol)) {
      this.router.navigate(['/unauthorized']);
      return false;
    }
    
    return true;
  }
}
```

### En las Rutas

**Archivo:** `frontend/src/app/app.routes.ts`

```typescript
{
  path: 'dashboard',
  component: DashboardComponent,
  canActivate: [AuthGuard, RoleGuard],
  data: { roles: [Roles.ADMIN, Roles.GERENTE] } // Solo Admin y Gerente pueden acceder
}
```

---

## 📋 Menú Actual (Referencia)

El menú actual está estructurado así:

1. **Dashboard** (Admin, Gerente) - Orden: 1
2. **Dashboard Usuario** (Comprador) - Orden: 1
3. **Mis Envíos** (Comprador) - Orden: 2
4. **Usuarios** (Admin, Gerente) - Orden: 2
5. **Envíos** (Admin, Gerente, Digitador) - Orden: 3
   - Envíos Activos
   - Envíos Pendientes
   - Envíos Completados
   - Historial
6. **Búsqueda** (Todos) - Orden: 4
   - Búsqueda Semántica
   - Búsqueda Tradicional
   - Búsqueda Avanzada
7. **Mapa** (Admin, Gerente) - Orden: 5
   - Rutas de Entrega
   - Áreas de Cobertura
   - Tiempos de Entrega
8. **Productos** (Admin, Gerente, Digitador) - Orden: 6
   - Inventario
   - Categorías
   - Almacenes
9. **Importar Excel** (Admin, Gerente, Digitador) - Orden: 7
10. **Reportes** (Admin, Gerente) - Orden: 8
    - Reportes de Envíos
    - Reportes de Ventas
    - Rendimiento

---

## ⚠️ Notas Importantes

1. **Sincronización con Backend:** El control de acceso en el menú es solo visual. Asegúrate de que el backend también valide los permisos.

2. **Iconos:** Usa iconos de Font Awesome. Formato: `'fas fa-icon-name'`. Consulta: https://fontawesome.com/icons

3. **Rutas:** Las rutas deben existir en `app.routes.ts` para que funcionen correctamente.

4. **Orden:** Si dos elementos tienen el mismo `order`, pueden aparecer en orden aleatorio.

5. **Subcategorías:** Los `subItems` no tienen control de acceso individual. Si el elemento padre es visible, todos sus subitems también lo serán.

---

## 🔄 Proceso de Modificación

1. **Editar** `navbar.component.ts`
2. **Modificar** el array `allNavItems`
3. **Guardar** el archivo
4. **Recargar** la aplicación
5. **Verificar** que los cambios se reflejen correctamente
6. **Probar** con diferentes roles de usuario

---

## 📝 Ejemplo Completo de Modificación

Supongamos que quieres agregar un nuevo elemento "Analytics" solo para Admin y Gerente:

```typescript
// En navbar.component.ts, dentro de allNavItems array

// ... elementos existentes ...

{
  label: 'Analytics',
  icon: 'fas fa-chart-line',
  route: '/analytics',
  roles: [Roles.ADMIN, Roles.GERENTE],
  order: 9,
  subItems: [
    { 
      label: 'Métricas Generales', 
      icon: 'fas fa-chart-bar', 
      route: '/analytics/metricas' 
    },
    { 
      label: 'Análisis de Tendencias', 
      icon: 'fas fa-chart-area', 
      route: '/analytics/tendencias' 
    }
  ]
}
```

Luego, agrega la ruta en `app.routes.ts`:

```typescript
{
  path: 'analytics',
  component: AnalyticsComponent,
  canActivate: [AuthGuard, RoleGuard],
  data: { roles: [Roles.ADMIN, Roles.GERENTE] }
}
```

---

**Última actualización:** Enero 2025




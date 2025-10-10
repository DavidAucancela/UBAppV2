# 🛠️ SOLUCIONES PROPUESTAS - IMPLEMENTACIÓN

Este documento contiene código listo para implementar las soluciones más críticas.

---

## 1. AUTHGUARD - Protección de Rutas

### Archivo: `src/app/guards/auth.guard.ts`

```typescript
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  // Redirigir al login si no está autenticado
  router.navigate(['/login']);
  return false;
};
```

### Archivo: `src/app/guards/role.guard.ts`

```typescript
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { Roles } from '../models/usuario';

export const roleGuard = (allowedRoles: Roles[]) => {
  return () => {
    const authService = inject(AuthService);
    const router = inject(Router);
    const currentUser = authService.getCurrentUser();

    if (!currentUser) {
      router.navigate(['/login']);
      return false;
    }

    if (allowedRoles.includes(currentUser.rol as Roles)) {
      return true;
    }

    // Usuario no tiene permiso, redirigir al dashboard
    router.navigate(['/dashboard']);
    return false;
  };
};
```

### Actualizar `src/app/app.routes.ts`

```typescript
import { Routes } from '@angular/router';
import { LoginComponent } from './components/auth/login/login.component';
import { DashboardComponent } from './components/dashboard/dashboard/dashboard.component';
import { UsuariosListComponent } from './components/usuarios/usuarios-list/usuarios-list.component';
import { EnviosListComponent } from './components/envios/envios-list/envios-list.component';
import { ProductosListComponent } from './components/productos/productos-list/productos-list.component';
import { authGuard } from './guards/auth.guard';
import { roleGuard } from './guards/role.guard';
import { Roles } from './models/usuario';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { 
    path: 'dashboard', 
    component: DashboardComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'usuarios', 
    component: UsuariosListComponent,
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE])]
  },
  { 
    path: 'envios', 
    component: EnviosListComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'productos', 
    component: ProductosListComponent,
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR])]
  },
  { path: '**', redirectTo: '/login' }
];
```

---

## 2. SISTEMA DE ENVIRONMENTS

### Archivo: `src/environments/environment.ts`

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api',
  appName: 'UBApp',
  version: '1.0.0',
  enableDebug: true,
  sessionTimeout: 30 * 60 * 1000, // 30 minutos
};
```

### Archivo: `src/environments/environment.prod.ts`

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://api.ubapp.com/api',
  appName: 'UBApp',
  version: '1.0.0',
  enableDebug: false,
  sessionTimeout: 30 * 60 * 1000, // 30 minutos
};
```

### Actualizar `angular.json`

```json
{
  "projects": {
    "ANGULAR_FRONTEND": {
      "architect": {
        "build": {
          "configurations": {
            "production": {
              "fileReplacements": [
                {
                  "replace": "src/environments/environment.ts",
                  "with": "src/environments/environment.prod.ts"
                }
              ]
            }
          }
        }
      }
    }
  }
}
```

### Actualizar Servicios

**Archivo: `src/app/services/auth.service.ts`**

```typescript
import { environment } from '../../environments/environment';

export class AuthService {
  private apiUrl = environment.apiUrl; // ← Cambiar esto
  // ... resto del código
}
```

**Archivo: `src/app/services/api.service.ts`**

```typescript
import { environment } from '../../environments/environment';

export class ApiService {
  private apiUrl = environment.apiUrl; // ← Cambiar esto
  // ... resto del código
}
```

---

## 3. HTTP INTERCEPTOR

### Archivo: `src/app/interceptors/auth.interceptor.ts`

```typescript
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { Router } from '@angular/router';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  // Agregar withCredentials para enviar cookies
  const modifiedReq = req.clone({
    withCredentials: true,
    setHeaders: {
      'Content-Type': 'application/json',
    }
  });

  return next(modifiedReq).pipe(
    catchError((error: HttpErrorResponse) => {
      // Manejar errores de autenticación
      if (error.status === 401) {
        console.error('Error de autenticación: Sesión expirada');
        localStorage.removeItem('currentUser');
        router.navigate(['/login']);
      } 
      
      // Manejar errores de permisos
      else if (error.status === 403) {
        console.error('Error de permisos: No tienes acceso');
        router.navigate(['/dashboard']);
      }
      
      // Manejar errores de servidor
      else if (error.status >= 500) {
        console.error('Error del servidor:', error.message);
        // Aquí podrías mostrar un toast/notification
      }

      return throwError(() => error);
    })
  );
};
```

### Archivo: `src/app/interceptors/error.interceptor.ts`

```typescript
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
// import { NotificationService } from '../services/notification.service'; // ← Crear este servicio

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  // const notificationService = inject(NotificationService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'Ha ocurrido un error';

      if (error.error instanceof ErrorEvent) {
        // Error del lado del cliente
        errorMessage = `Error: ${error.error.message}`;
      } else {
        // Error del lado del servidor
        errorMessage = `Código de error: ${error.status}\nMensaje: ${error.message}`;
      }

      console.error(errorMessage);
      
      // Mostrar notificación al usuario
      // notificationService.showError(errorMessage);

      return throwError(() => error);
    })
  );
};
```

### Actualizar `src/app/app.config.ts`

```typescript
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';

import { routes } from './app.routes';
import { authInterceptor } from './interceptors/auth.interceptor';
import { errorInterceptor } from './interceptors/error.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor, errorInterceptor])),
    provideAnimations()
  ]
};
```

---

## 4. SERVICIO DE NOTIFICACIONES

### Archivo: `src/app/services/notification.service.ts`

```typescript
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface Notification {
  id: number;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private notifications$ = new BehaviorSubject<Notification[]>([]);
  private idCounter = 0;

  getNotifications(): Observable<Notification[]> {
    return this.notifications$.asObservable();
  }

  showSuccess(message: string, duration: number = 3000): void {
    this.show('success', message, duration);
  }

  showError(message: string, duration: number = 5000): void {
    this.show('error', message, duration);
  }

  showWarning(message: string, duration: number = 4000): void {
    this.show('warning', message, duration);
  }

  showInfo(message: string, duration: number = 3000): void {
    this.show('info', message, duration);
  }

  private show(type: 'success' | 'error' | 'warning' | 'info', message: string, duration: number): void {
    const notification: Notification = {
      id: this.idCounter++,
      type,
      message,
      duration
    };

    const current = this.notifications$.value;
    this.notifications$.next([...current, notification]);

    // Auto-remover después del duration
    if (duration > 0) {
      setTimeout(() => {
        this.remove(notification.id);
      }, duration);
    }
  }

  remove(id: number): void {
    const current = this.notifications$.value;
    this.notifications$.next(current.filter(n => n.id !== id));
  }

  clear(): void {
    this.notifications$.next([]);
  }
}
```

### Componente de Notificaciones

**Archivo: `src/app/components/shared/notification/notification.component.ts`**

```typescript
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificationService, Notification } from '../../../services/notification.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-notification',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="notification-container">
      <div 
        *ngFor="let notification of notifications$ | async"
        class="notification"
        [class.success]="notification.type === 'success'"
        [class.error]="notification.type === 'error'"
        [class.warning]="notification.type === 'warning'"
        [class.info]="notification.type === 'info'"
      >
        <i class="fas" 
           [class.fa-check-circle]="notification.type === 'success'"
           [class.fa-exclamation-circle]="notification.type === 'error'"
           [class.fa-exclamation-triangle]="notification.type === 'warning'"
           [class.fa-info-circle]="notification.type === 'info'"
        ></i>
        <span>{{ notification.message }}</span>
        <button class="close-btn" (click)="close(notification.id)">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  `,
  styles: [`
    .notification-container {
      position: fixed;
      top: 90px;
      right: 20px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .notification {
      min-width: 300px;
      padding: 15px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
      display: flex;
      align-items: center;
      gap: 12px;
      animation: slideIn 0.3s ease-out;
      background: white;
    }

    @keyframes slideIn {
      from {
        transform: translateX(400px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }

    .notification i {
      font-size: 1.2rem;
    }

    .notification.success {
      border-left: 4px solid #10b981;
      color: #065f46;
    }

    .notification.success i {
      color: #10b981;
    }

    .notification.error {
      border-left: 4px solid #ef4444;
      color: #991b1b;
    }

    .notification.error i {
      color: #ef4444;
    }

    .notification.warning {
      border-left: 4px solid #f59e0b;
      color: #92400e;
    }

    .notification.warning i {
      color: #f59e0b;
    }

    .notification.info {
      border-left: 4px solid #3b82f6;
      color: #1e40af;
    }

    .notification.info i {
      color: #3b82f6;
    }

    .notification span {
      flex: 1;
      font-weight: 500;
    }

    .close-btn {
      background: none;
      border: none;
      cursor: pointer;
      color: #6b7280;
      padding: 4px;
      transition: color 0.2s;
    }

    .close-btn:hover {
      color: #111827;
    }
  `]
})
export class NotificationComponent implements OnInit {
  notifications$!: Observable<Notification[]>;

  constructor(private notificationService: NotificationService) {}

  ngOnInit(): void {
    this.notifications$ = this.notificationService.getNotifications();
  }

  close(id: number): void {
    this.notificationService.remove(id);
  }
}
```

### Agregar al AppComponent

**Archivo: `src/app/app.component.html`**

Agregar antes del cierre de `</body>`:

```html
<app-notification></app-notification>
```

**Archivo: `src/app/app.component.ts`**

```typescript
import { NotificationComponent } from './components/shared/notification/notification.component';

@Component({
  // ...
  imports: [
    CommonModule, 
    RouterOutlet, 
    RouterLink, 
    RouterLinkActive,
    NotificationComponent  // ← Agregar
  ],
  // ...
})
```

---

## 5. ACTUALIZAR TSCONFIG.JSON

```json
{
  "compileOnSave": false,
  "compilerOptions": {
    "outDir": "./dist/out-tsc",
    "strict": true,  // ← Cambiar a true
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": false,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "skipLibCheck": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "experimentalDecorators": true,
    "moduleResolution": "bundler",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022"
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true  // ← Cambiar a true
  }
}
```

---

## 6. USO DE LAS SOLUCIONES

### Ejemplo: Usar NotificationService

```typescript
// En cualquier componente
constructor(private notificationService: NotificationService) {}

onSave() {
  this.apiService.createUsuario(data).subscribe({
    next: () => {
      this.notificationService.showSuccess('Usuario creado exitosamente');
    },
    error: () => {
      this.notificationService.showError('Error al crear usuario');
    }
  });
}
```

### Ejemplo: Reemplazar confirm() nativo

**Antes:**
```typescript
if (confirm('¿Estás seguro?')) {
  this.delete();
}
```

**Después:** Crear un servicio de confirmación o usar el NotificationService

---

## 7. CHECKLIST DE IMPLEMENTACIÓN

- [ ] Crear carpeta `src/app/guards/`
- [ ] Crear `auth.guard.ts`
- [ ] Crear `role.guard.ts`
- [ ] Actualizar `app.routes.ts`
- [ ] Crear carpeta `src/environments/`
- [ ] Crear `environment.ts`
- [ ] Crear `environment.prod.ts`
- [ ] Actualizar `angular.json`
- [ ] Actualizar servicios para usar environment
- [ ] Crear carpeta `src/app/interceptors/`
- [ ] Crear `auth.interceptor.ts`
- [ ] Crear `error.interceptor.ts`
- [ ] Actualizar `app.config.ts`
- [ ] Crear `notification.service.ts`
- [ ] Crear componente de notificaciones
- [ ] Agregar componente al AppComponent
- [ ] Actualizar `tsconfig.json`
- [ ] Probar todas las rutas protegidas
- [ ] Probar manejo de errores
- [ ] Probar notificaciones

---

## 8. TESTING

```typescript
// Probar guards
ng test

// Probar en navegador
npm start

// Intentar acceder a /dashboard sin login → Debe redirigir a /login
// Login y acceder a /usuarios → Debe funcionar si eres Admin/Gerente
// Login como Comprador y acceder a /usuarios → Debe redirigir a /dashboard
```

---

**Próximo paso:** Implementar componentes de Envíos y Productos (ver próximo documento)




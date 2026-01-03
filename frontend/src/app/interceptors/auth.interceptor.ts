import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { Router } from '@angular/router';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  // Obtener el token de autenticación
  let authToken: string | null = null;
  if (typeof window !== 'undefined' && window.localStorage) {
    authToken = localStorage.getItem('authToken');
  }

  // Clonar la solicitud con el token de autenticación si existe
  let modifiedReq = req.clone({
    withCredentials: true
  });

  if (authToken) {
    modifiedReq = modifiedReq.clone({
      setHeaders: {
        'Authorization': `Bearer ${authToken}`
      }
    });
  }

  return next(modifiedReq).pipe(
    catchError((error) => {
      if (error.status === 401) {
        // No autorizado: limpiar sesión y redirigir a login
        if (typeof window !== 'undefined' && window.localStorage) {
          localStorage.removeItem('currentUser');
          localStorage.removeItem('authToken');
        }
        router.navigate(['/login']);
      } else if (error.status === 403) {
        // Prohibido: redirigir al dashboard
        router.navigate(['/inicio']);
      } else if (error.status === 0) {
        // Error de conexión
        console.error('Error de conexión con el servidor');
      }
      return throwError(() => error);
    })
  );
};

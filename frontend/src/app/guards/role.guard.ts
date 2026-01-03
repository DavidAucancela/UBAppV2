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
    router.navigate(['/inicio']);
    return false;
  };
};
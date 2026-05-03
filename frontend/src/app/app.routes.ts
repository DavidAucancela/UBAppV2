import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { roleGuard } from './guards/role.guard';
import { Roles } from './models/usuario';

export const routes: Routes = [
  // Páginas públicas
  { path: '', redirectTo: '/informacion', pathMatch: 'full' },
  {
    path: 'informacion',
    loadComponent: () => import('./components/informacion/informacion-general/informacion-general.component').then(m => m.InformacionGeneralComponent)
  },
  {
    path: 'ubicaciones',
    loadComponent: () => import('./components/informacion/ubicaciones/ubicaciones.component').then(m => m.UbicacionesComponent)
  },
  {
    path: 'login',
    loadComponent: () => import('./components/auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./components/auth/register/register.component').then(m => m.RegisterComponent)
  },

  // Dashboard — roles internos
  {
    path: 'inicio',
    loadComponent: () => import('./components/dashboard/inicio/inicio.component').then(m => m.InicioComponent),
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR])]
  },
  {
    path: 'actividades',
    loadComponent: () => import('./components/dashboard/actividades-sistema/actividades-sistema.component').then(m => m.ActividadesSistemaComponent),
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE])]
  },
  {
    path: 'dashboard-usuario',
    loadComponent: () => import('./components/dashboard/dashboard-usuario/dashboard-usuario.component').then(m => m.DashboardUsuarioComponent),
    canActivate: [authGuard, roleGuard([Roles.COMPRADOR])]
  },

  // Perfil — cualquier rol autenticado
  {
    path: 'perfil',
    loadComponent: () => import('./components/perfil/perfil.component').then(m => m.PerfilComponent),
    canActivate: [authGuard]
  },

  // Envíos
  {
    path: 'envios',
    loadComponent: () => import('./components/envios/envios-list/envios-list.component').then(m => m.EnviosListComponent),
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR])]
  },
  {
    path: 'mis-envios',
    loadComponent: () => import('./components/envios/mis-envios/mis-envios.component').then(m => m.MisEnviosComponent),
    canActivate: [authGuard, roleGuard([Roles.COMPRADOR])]
  },

  // Búsqueda
  {
    path: 'busqueda',
    loadComponent: () => import('./components/busqueda-unificada/busqueda-unificada.component').then(m => m.BusquedaUnificadaComponent),
    canActivate: [authGuard]
  },
  {
    path: 'busqueda-envios',
    loadComponent: () => import('./components/busqueda-envios/busqueda-envios.component').then(m => m.BusquedaEnviosComponent),
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR])]
  },
  {
    path: 'busqueda-semantica',
    loadComponent: () => import('./components/busqueda-semantica/busqueda-semantica.component').then(m => m.BusquedaSemanticaComponent),
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE])]
  },

  // Gestión — roles internos
  {
    path: 'usuarios',
    loadComponent: () => import('./components/usuarios/usuarios-list/usuarios-list.component').then(m => m.UsuariosListComponent),
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE])]
  },
  {
    path: 'productos',
    loadComponent: () => import('./components/productos/productos-list/productos-list.component').then(m => m.ProductosListComponent),
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR])]
  },
  {
    path: 'tarifas',
    loadComponent: () => import('./components/tarifas/tarifas-list.component').then(m => m.TarifasListComponent),
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE])]
  },
  {
    path: 'importacion-excel',
    loadComponent: () => import('./components/importacion-excel/importacion-excel.component').then(m => m.ImportacionExcelComponent),
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR])]
  },
  {
    path: 'mapa-compradores',
    loadComponent: () => import('./components/mapa-compradores/mapa-compradores.component').then(m => m.MapaCompradoresComponent),
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR])]
  },

  // Notificaciones — todos los roles autenticados
  {
    path: 'notificaciones',
    loadComponent: () => import('./components/notificaciones/notificaciones-list/notificaciones-list.component').then(m => m.NotificacionesListComponent),
    canActivate: [authGuard]
  },

  { path: '**', loadComponent: () => import('./components/not-found/not-found.component').then(m => m.NotFoundComponent) }
];

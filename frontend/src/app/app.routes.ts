import { Routes } from '@angular/router';
import { LoginComponent } from './components/auth/login/login.component';
import { DashboardComponent } from './components/dashboard/dashboard/dashboard.component';
import { InicioComponent } from './components/dashboard/inicio/inicio.component';
import { UsuariosListComponent } from './components/usuarios/usuarios-list/usuarios-list.component';
import { EnviosListComponent } from './components/envios/envios-list/envios-list.component';
import { ProductosListComponent } from './components/productos/productos-list/productos-list.component';
import { MapaCompradoresComponent } from './components/mapa-compradores/mapa-compradores.component';
import { BusquedaEnviosComponent } from './components/busqueda-envios/busqueda-envios.component';
import { BusquedaSemanticaComponent } from './components/busqueda-semantica/busqueda-semantica.component';
import { BusquedaUnificadaComponent } from './components/busqueda-unificada/busqueda-unificada.component';
import { authGuard } from './guards/auth.guard';
import { roleGuard } from './guards/role.guard';
import { Roles } from './models/usuario';


export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { 
    path: 'inicio', 
    component: InicioComponent,
    canActivate: [authGuard]
  },
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
    path: 'busqueda-envios', 
    component: BusquedaEnviosComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'busqueda-semantica', 
    component: BusquedaSemanticaComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'busqueda', 
    component: BusquedaUnificadaComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'productos', 
    component: ProductosListComponent,
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR])]
  },
  { 
    path: 'mapa-compradores', 
    component: MapaCompradoresComponent,
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR])]
  },
  { path: '**', redirectTo: '/login' }
];
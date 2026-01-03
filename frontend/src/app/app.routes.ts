import { Routes } from '@angular/router';
import { LoginComponent } from './components/auth/login/login.component';
import { InicioComponent } from './components/dashboard/inicio/inicio.component';
import { DashboardUsuarioComponent } from './components/dashboard/dashboard-usuario/dashboard-usuario.component';
import { UsuariosListComponent } from './components/usuarios/usuarios-list/usuarios-list.component';
import { EnviosListComponent } from './components/envios/envios-list/envios-list.component';
import { MisEnviosComponent } from './components/envios/mis-envios/mis-envios.component';
import { ProductosListComponent } from './components/productos/productos-list/productos-list.component';
import { MapaCompradoresComponent } from './components/mapa-compradores/mapa-compradores.component';
import { BusquedaEnviosComponent } from './components/busqueda-envios/busqueda-envios.component';
import { BusquedaSemanticaComponent } from './components/busqueda-semantica/busqueda-semantica.component';
import { BusquedaUnificadaComponent } from './components/busqueda-unificada/busqueda-unificada.component';
import { ImportacionExcelComponent } from './components/importacion-excel/importacion-excel.component';
import { InformacionGeneralComponent } from './components/informacion/informacion-general/informacion-general.component';
import { UbicacionesComponent } from './components/informacion/ubicaciones/ubicaciones.component';
import { RegisterComponent } from './components/auth/register/register.component';
import { PerfilComponent } from './components/perfil/perfil.component';
import { ActividadesSistemaComponent } from './components/dashboard/actividades-sistema/actividades-sistema.component';
import { TarifasListComponent } from './components/tarifas/tarifas-list.component';
import { authGuard } from './guards/auth.guard';
import { roleGuard } from './guards/role.guard';
import { Roles } from './models/usuario';


export const routes: Routes = [
  // Páginas públicas
  { path: '', redirectTo: '/informacion', pathMatch: 'full' },
  { path: 'informacion', component: InformacionGeneralComponent },
  { path: 'ubicaciones', component: UbicacionesComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  
  // Páginas protegidas
  { 
    path: 'inicio', 
    component: InicioComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'actividades', 
    component: ActividadesSistemaComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'perfil', 
    component: PerfilComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'dashboard-usuario', 
    component: DashboardUsuarioComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'mis-envios', 
    component: MisEnviosComponent,
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
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE])]
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
  { 
    path: 'importacion-excel', 
    component: ImportacionExcelComponent,
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR])]
  },
  { 
    path: 'tarifas', 
    component: TarifasListComponent,
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE])]
  },
  { path: '**', redirectTo: '/informacion' }
];
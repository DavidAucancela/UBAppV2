import { Routes } from '@angular/router';
import { LoginComponent } from './components/auth/login/login.component';
import { VerifyEmailComponent } from './components/auth/verify-email/verify-email.component';
import { ResetPasswordComponent } from './components/auth/reset-password/reset-password.component';
import { ChangePasswordComponent } from './components/auth/change-password/change-password.component';
import { DashboardComponent } from './components/dashboard/dashboard/dashboard.component';
import { UsuariosListComponent } from './components/usuarios/usuarios-list/usuarios-list.component';
import { EnviosListComponent } from './components/envios/envios-list/envios-list.component';
import { ProductosListComponent } from './components/productos/productos-list/productos-list.component';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'verify-email', component: VerifyEmailComponent },
  { path: 'reset-password', component: ResetPasswordComponent },
  { path: 'change-password', component: ChangePasswordComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'usuarios', component: UsuariosListComponent },
  { path: 'envios', component: EnviosListComponent },
  { path: 'productos', component: ProductosListComponent },
  { path: '**', redirectTo: '/login' }
];

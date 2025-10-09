import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, BehaviorSubject, timer, Subscription } from 'rxjs';
import { tap, map } from 'rxjs/operators';
import { Usuario } from '../models/usuario';

export interface PasswordChangeRequest {
  password_actual: string;
  password_nuevo: string;
  password_confirm: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  user_id: number;
  new_password: string;
  confirm_password: string;
}

export interface EmailVerification {
  token: string;
  user_id: number;
}

export interface UsuarioEstadisticas {
  por_rol: { [key: string]: number };
  total_usuarios: number;
  usuarios_activos: number;
  usuarios_verificados: number;
  usuarios_bloqueados: number;
  activos_ultimas_24h: number;
}

@Injectable({
  providedIn: 'root'
})
export class UsuarioService {
  private apiUrl = 'http://localhost:8000/api/usuarios';
  private inactivityTimer?: Subscription;
  private sessionCheckTimer?: Subscription;
  
  // Subject para notificar cambios en usuarios
  private usuariosActualizados = new BehaviorSubject<boolean>(false);
  public usuariosActualizados$ = this.usuariosActualizados.asObservable();

  constructor(private http: HttpClient) {
    this.iniciarMonitoreoSesion();
  }

  // ===== CRUD de Usuarios =====
  getUsuarios(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(`${this.apiUrl}/`);
  }

  getUsuario(id: number): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}/${id}/`);
  }

  createUsuario(usuario: Usuario): Observable<Usuario> {
    return this.http.post<Usuario>(`${this.apiUrl}/`, usuario).pipe(
      tap(() => this.usuariosActualizados.next(true))
    );
  }

  updateUsuario(id: number, usuario: Partial<Usuario>): Observable<Usuario> {
    return this.http.patch<Usuario>(`${this.apiUrl}/${id}/`, usuario).pipe(
      tap(() => this.usuariosActualizados.next(true))
    );
  }

  deleteUsuario(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`).pipe(
      tap(() => this.usuariosActualizados.next(true))
    );
  }

  // ===== Autenticación y Registro =====
  register(usuario: Usuario): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/register/`, usuario);
  }

  // ===== Verificación de Email =====
  verifyEmail(verification: EmailVerification): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/verify-email/`, verification);
  }

  resendVerification(email: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/resend-verification/`, { email });
  }

  // ===== Recuperación de Contraseña =====
  requestPasswordReset(request: PasswordResetRequest): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/password-reset/`, request);
  }

  confirmPasswordReset(data: PasswordResetConfirm): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/password-reset-confirm/`, data);
  }

  // ===== Gestión de Perfil =====
  getPerfil(): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}/perfil/`);
  }

  updatePerfil(usuario: Partial<Usuario>): Observable<Usuario> {
    return this.http.patch<Usuario>(`${this.apiUrl}/actualizar_perfil/`, usuario);
  }

  cambiarPassword(passwords: PasswordChangeRequest): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/cambiar_password/`, passwords);
  }

  // ===== Acciones de Administración =====
  activarDesactivarUsuario(id: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${id}/activar_desactivar/`, {}).pipe(
      tap(() => this.usuariosActualizados.next(true))
    );
  }

  forzarCambioPassword(id: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${id}/forzar_cambio_password/`, {});
  }

  desbloquearUsuario(id: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${id}/desbloquear/`, {}).pipe(
      tap(() => this.usuariosActualizados.next(true))
    );
  }

  // ===== Consultas Especiales =====
  getCompradores(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(`${this.apiUrl}/compradores/`);
  }

  getUsuariosPorRol(rol: number): Observable<Usuario[]> {
    const params = new HttpParams().set('rol', rol.toString());
    return this.http.get<Usuario[]>(`${this.apiUrl}/por_rol/`, { params });
  }

  getEstadisticas(): Observable<UsuarioEstadisticas> {
    return this.http.get<UsuarioEstadisticas>(`${this.apiUrl}/estadisticas/`);
  }

  // ===== Búsqueda y Filtrado =====
  buscarUsuarios(termino: string): Observable<Usuario[]> {
    const params = new HttpParams().set('search', termino);
    return this.http.get<Usuario[]>(`${this.apiUrl}/`, { params });
  }

  // ===== Monitoreo de Sesión =====
  private iniciarMonitoreoSesion(): void {
    // Reiniciar el timer de inactividad en cada actividad del usuario
    if (typeof window !== 'undefined') {
      ['mousedown', 'keypress', 'scroll', 'touchstart'].forEach(event => {
        document.addEventListener(event, () => this.resetInactivityTimer());
      });
    }

    // Verificar el estado de la sesión cada 5 minutos
    this.sessionCheckTimer = timer(0, 5 * 60 * 1000).subscribe(() => {
      this.checkSession();
    });
  }

  private resetInactivityTimer(): void {
    // Cancelar el timer anterior si existe
    if (this.inactivityTimer) {
      this.inactivityTimer.unsubscribe();
    }

    // Iniciar un nuevo timer de 30 minutos
    this.inactivityTimer = timer(30 * 60 * 1000).subscribe(() => {
      this.handleInactivity();
    });
  }

  private checkSession(): void {
    this.http.get<any>(`${this.apiUrl}/check_session/`).subscribe({
      next: (response) => {
        if (!response.active) {
          this.handleSessionExpired(response.message);
        }
        if (response.must_change_password) {
          this.handleMustChangePassword();
        }
      },
      error: (error) => {
        if (error.status === 401) {
          this.handleSessionExpired('Sesión expirada');
        }
      }
    });
  }

  private handleInactivity(): void {
    // Mostrar advertencia antes de cerrar sesión
    if (confirm('Tu sesión está a punto de expirar por inactividad. ¿Deseas continuar?')) {
      this.checkSession();
      this.resetInactivityTimer();
    } else {
      this.handleSessionExpired('Sesión cerrada por inactividad');
    }
  }

  private handleSessionExpired(message: string): void {
    // Limpiar localStorage
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('currentUser');
    }

    // Redirigir al login
    alert(message);
    window.location.href = '/login';
  }

  private handleMustChangePassword(): void {
    // Redirigir a cambio de contraseña
    if (window.location.pathname !== '/change-password') {
      alert('Debes cambiar tu contraseña');
      window.location.href = '/change-password';
    }
  }

  // ===== Validaciones =====
  validarPasswordSeguro(password: string): { valido: boolean; mensaje?: string } {
    if (password.length < 8) {
      return { valido: false, mensaje: 'La contraseña debe tener al menos 8 caracteres' };
    }
    if (!/[A-Z]/.test(password)) {
      return { valido: false, mensaje: 'La contraseña debe contener al menos una letra mayúscula' };
    }
    if (!/[a-z]/.test(password)) {
      return { valido: false, mensaje: 'La contraseña debe contener al menos una letra minúscula' };
    }
    if (!/\d/.test(password)) {
      return { valido: false, mensaje: 'La contraseña debe contener al menos un número' };
    }
    if (!/[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]/.test(password)) {
      return { valido: false, mensaje: 'La contraseña debe contener al menos un carácter especial' };
    }
    if (password.includes(' ')) {
      return { valido: false, mensaje: 'La contraseña no puede contener espacios' };
    }
    return { valido: true };
  }

  validarEmail(email: string): boolean {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  }

  validarCedula(cedula: string): boolean {
    const cedulaLimpia = cedula.replace(/-/g, '').replace(/ /g, '');
    return /^\d{8,}$/.test(cedulaLimpia);
  }

  validarTelefono(telefono: string): boolean {
    const telefonoLimpio = telefono.replace(/-/g, '').replace(/ /g, '').replace(/\+/g, '');
    return /^\d+$/.test(telefonoLimpio);
  }

  // Cleanup
  ngOnDestroy(): void {
    if (this.inactivityTimer) {
      this.inactivityTimer.unsubscribe();
    }
    if (this.sessionCheckTimer) {
      this.sessionCheckTimer.unsubscribe();
    }
  }
}


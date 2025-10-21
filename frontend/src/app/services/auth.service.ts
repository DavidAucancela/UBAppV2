import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { Usuario, LoginRequest, LoginResponse, Roles } from '../models/usuario';
import { environment } from '../environments/environment';


@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl; 
  private currentUserSubject = new BehaviorSubject<Usuario | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadCurrentUser();
  }

  private loadCurrentUser(): void {
    if (typeof window !== 'undefined' && window.localStorage) {
      const user = localStorage.getItem('currentUser');
      if (user) {
        this.currentUserSubject.next(JSON.parse(user));
      }
    }
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/usuarios/auth/login/`, credentials)
      .pipe(
        tap(response => {
          if (response.user && response.token) {
            if (typeof window !== 'undefined' && window.localStorage) {
              localStorage.setItem('currentUser', JSON.stringify(response.user));
              localStorage.setItem('authToken', response.token);
              // Guardar refresh token si está presente
              if ((response as any).refresh) {
                localStorage.setItem('refreshToken', (response as any).refresh);
              }
            }
            this.currentUserSubject.next(response.user);
          }
        })
      );
  }

  logout(): void {
    // Obtener refresh token para enviarlo al backend
    const refreshToken = this.getRefreshToken();
    
    // Llamar al endpoint de logout
    this.http.post(`${this.apiUrl}/usuarios/auth/logout/`, { refresh: refreshToken }).subscribe({
      next: () => {
        console.log('Logout exitoso');
      },
      error: (error) => {
        console.error('Error en logout:', error);
      }
    });
    
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('currentUser');
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
    }
    this.currentUserSubject.next(null);
  }

  getCurrentUser(): Usuario | null {
    return this.currentUserSubject.value;
  }

  isAuthenticated(): boolean {
    return this.getCurrentUser() !== null;
  }

  hasRole(role: Roles): boolean {
    const user = this.getCurrentUser();
    return user ? user.rol === role : false;
  }

  isAdmin(): boolean {
    return this.hasRole(Roles.ADMIN);
  }

  isGerente(): boolean {
    return this.hasRole(Roles.GERENTE);
  }

  isDigitador(): boolean {
    return this.hasRole(Roles.DIGITADOR);
  }

  isComprador(): boolean {
    return this.hasRole(Roles.COMPRADOR);
  }

  canManageUsers(): boolean {
    return this.isAdmin() || this.isGerente();
  }

  canManageEnvios(): boolean {
    return this.isAdmin() || this.isGerente() || this.isDigitador();
  }

  canViewAllEnvios(): boolean {
    return this.isAdmin() || this.isGerente() || this.isDigitador();
  }

  canViewOwnEnvios(): boolean {
    return this.isComprador();
  }

  getToken(): string | null {
    if (typeof window !== 'undefined' && window.localStorage) {
      return localStorage.getItem('authToken');
    }
    return null;
  }

  getRefreshToken(): string | null {
    if (typeof window !== 'undefined' && window.localStorage) {
      return localStorage.getItem('refreshToken');
    }
    return null;
  }

  getAuthHeaders(): { [key: string]: string } {
    return {
      'Content-Type': 'application/json',
      'X-CSRFToken': this.getCSRFToken()
    };
  }

  private getCSRFToken(): string {
    if (typeof window !== 'undefined' && window.document) {
      return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1] || '';
    }
    return '';
  }
}

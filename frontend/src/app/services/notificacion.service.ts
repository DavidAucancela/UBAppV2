import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, interval, Subscription } from 'rxjs';
import { switchMap, catchError, tap } from 'rxjs/operators';
import { of } from 'rxjs';
import { Notificacion, NotificacionResponse, NotificacionCount } from '../models/notificacion';
import { AuthService } from './auth.service';
import { Roles } from '../models/usuario';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class NotificacionService {
  private apiUrl = environment.apiUrl;
  private notificacionesSubject = new BehaviorSubject<Notificacion[]>([]);
  private countSubject = new BehaviorSubject<NotificacionCount>({ total: 0, no_leidas: 0 });
  private pollSubscription?: Subscription;
  private readonly POLL_INTERVAL = 30000; // 30 segundos

  public notificaciones$ = this.notificacionesSubject.asObservable();
  public count$ = this.countSubject.asObservable();

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {
    // Suscribirse a cambios de usuario para iniciar/detener polling
    this.authService.currentUser$.subscribe(user => {
      if (user && user.rol === Roles.COMPRADOR) {
        this.startPolling();
      } else {
        this.stopPolling();
        this.clearNotificaciones();
      }
    });
  }

  /**
   * Obtener notificaciones del backend
   */
  obtenerNotificaciones(): Observable<NotificacionResponse> {
    return this.http.get<NotificacionResponse>(`${this.apiUrl}/notificaciones/`).pipe(
      tap(response => {
        this.notificacionesSubject.next(response.results);
        this.actualizarContador(response.results);
      }),
      catchError(error => {
        console.error('Error al obtener notificaciones:', error);
        return of({ count: 0, next: null, previous: null, results: [] });
      })
    );
  }

  /**
   * Obtener contador de notificaciones no leídas
   */
  obtenerContador(): Observable<NotificacionCount> {
    return this.http.get<NotificacionCount>(`${this.apiUrl}/notificaciones/contador/`).pipe(
      tap(count => this.countSubject.next(count)),
      catchError(error => {
        console.error('Error al obtener contador de notificaciones:', error);
        return of({ total: 0, no_leidas: 0 });
      })
    );
  }

  /**
   * Marcar notificación como leída
   */
  marcarComoLeida(id: number): Observable<Notificacion> {
    return this.http.patch<Notificacion>(`${this.apiUrl}/notificaciones/${id}/marcar-leida/`, {}).pipe(
      tap(() => {
        const notificaciones = this.notificacionesSubject.value;
        const index = notificaciones.findIndex(n => n.id === id);
        if (index !== -1) {
          notificaciones[index].leida = true;
          notificaciones[index].fecha_lectura = new Date().toISOString();
          this.notificacionesSubject.next([...notificaciones]);
          this.actualizarContador(notificaciones);
        }
      }),
      catchError(error => {
        console.error('Error al marcar notificación como leída:', error);
        throw error;
      })
    );
  }

  /**
   * Marcar todas las notificaciones como leídas
   */
  marcarTodasComoLeidas(): Observable<void> {
    return this.http.post<void>(`${this.apiUrl}/notificaciones/marcar-todas-leidas/`, {}).pipe(
      tap(() => {
        const notificaciones = this.notificacionesSubject.value.map(n => ({
          ...n,
          leida: true,
          fecha_lectura: new Date().toISOString()
        }));
        this.notificacionesSubject.next(notificaciones);
        this.actualizarContador(notificaciones);
      }),
      catchError(error => {
        console.error('Error al marcar todas las notificaciones como leídas:', error);
        throw error;
      })
    );
  }

  /**
   * Eliminar notificación
   */
  eliminarNotificacion(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/notificaciones/${id}/`).pipe(
      tap(() => {
        const notificaciones = this.notificacionesSubject.value.filter(n => n.id !== id);
        this.notificacionesSubject.next(notificaciones);
        this.actualizarContador(notificaciones);
      }),
      catchError(error => {
        console.error('Error al eliminar notificación:', error);
        throw error;
      })
    );
  }

  /**
   * Obtener notificaciones no leídas (para el contador)
   */
  obtenerNoLeidas(): Notificacion[] {
    return this.notificacionesSubject.value.filter(n => !n.leida);
  }

  /**
   * Obtener contador actual
   */
  obtenerContadorActual(): NotificacionCount {
    const notificaciones = this.notificacionesSubject.value;
    return {
      total: notificaciones.length,
      no_leidas: notificaciones.filter(n => !n.leida).length
    };
  }

  /**
   * Iniciar polling automático de notificaciones
   */
  private startPolling(): void {
    this.stopPolling(); // Asegurar que no hay múltiples suscripciones

    // Cargar inmediatamente
    this.obtenerNotificaciones().subscribe();

    // Polling cada 30 segundos
    this.pollSubscription = interval(this.POLL_INTERVAL).pipe(
      switchMap(() => this.obtenerNotificaciones())
    ).subscribe();
  }

  /**
   * Detener polling automático
   */
  private stopPolling(): void {
    if (this.pollSubscription) {
      this.pollSubscription.unsubscribe();
      this.pollSubscription = undefined;
    }
  }

  /**
   * Limpiar notificaciones
   */
  private clearNotificaciones(): void {
    this.notificacionesSubject.next([]);
    this.countSubject.next({ total: 0, no_leidas: 0 });
  }

  /**
   * Actualizar contador basado en notificaciones actuales
   */
  private actualizarContador(notificaciones: Notificacion[]): void {
    const noLeidas = notificaciones.filter(n => !n.leida).length;
    this.countSubject.next({
      total: notificaciones.length,
      no_leidas: noLeidas
    });
  }

  /**
   * Limpiar recursos al destruir el servicio
   */
  ngOnDestroy(): void {
    this.stopPolling();
  }
}








import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificacionService } from '../../../services/notificacion.service';
import { AuthService } from '../../../services/auth.service';
import { Notificacion, NotificacionResponse } from '../../../models/notificacion';
import { EnvioDetailModalComponent } from '../../shared/envio-detail-modal/envio-detail-modal.component';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-notificaciones-list',
  standalone: true,
  imports: [CommonModule, EnvioDetailModalComponent],
  templateUrl: './notificaciones-list.component.html',
  styleUrl: './notificaciones-list.component.css'
})
export class NotificacionesListComponent implements OnInit, OnDestroy {
  notificaciones: Notificacion[] = [];
  loading = false;
  error: string | null = null;
  
  // Paginación
  paginaActual = 1;
  itemsPerPage = 20;
  totalPaginas = 1;
  totalResultados = 0;
  
  // Filtros
  filtroLeidas: 'todas' | 'leidas' | 'no_leidas' = 'todas';
  
  // Modal de detalles de envío
  showEnvioDetailModal = false;
  selectedEnvioId: number | null = null;
  
  private subscription: Subscription | null = null;

  constructor(
    private notificacionService: NotificacionService,
    public authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadNotificaciones();
    
    // Suscribirse a cambios en las notificaciones
    this.subscription = this.notificacionService.notificaciones$.subscribe(
      (notificaciones) => {
        this.notificaciones = notificaciones;
        this.applyFilters();
      }
    );
  }

  ngOnDestroy(): void {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  loadNotificaciones(): void {
    this.loading = true;
    this.error = null;

    this.notificacionService.obtenerNotificaciones().subscribe({
      next: (response: NotificacionResponse) => {
        this.notificaciones = response.results || [];
        this.totalResultados = response.count || 0;
        this.totalPaginas = Math.ceil(this.totalResultados / this.itemsPerPage);
        this.applyFilters();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando notificaciones:', error);
        this.error = 'Error al cargar las notificaciones';
        this.loading = false;
      }
    });
  }

  applyFilters(): void {
    // Los filtros se aplican en el template con *ngIf
    // Aquí solo calculamos la paginación
    this.totalPaginas = Math.ceil(this.getFilteredNotificaciones().length / this.itemsPerPage);
  }

  getFilteredNotificaciones(): Notificacion[] {
    let filtered = [...this.notificaciones];
    
    if (this.filtroLeidas === 'leidas') {
      filtered = filtered.filter(n => n.leida);
    } else if (this.filtroLeidas === 'no_leidas') {
      filtered = filtered.filter(n => !n.leida);
    }
    
    return filtered;
  }

  get paginatedNotificaciones(): Notificacion[] {
    const filtered = this.getFilteredNotificaciones();
    const startIndex = (this.paginaActual - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    return filtered.slice(startIndex, endIndex);
  }

  cambiarFiltro(filtro: 'todas' | 'leidas' | 'no_leidas'): void {
    this.filtroLeidas = filtro;
    this.paginaActual = 1;
    this.applyFilters();
  }

  marcarComoLeida(notificacion: Notificacion, event: Event): void {
    event.stopPropagation();
    
    if (!notificacion.leida) {
      this.notificacionService.marcarComoLeida(notificacion.id).subscribe({
        next: () => {
          // El servicio actualiza automáticamente la lista
        },
        error: (error) => {
          console.error('Error marcando notificación como leída:', error);
        }
      });
    }
    
    // Abrir modal de detalles si tiene envio_id
    if (notificacion.metadata?.envio_id) {
      this.selectedEnvioId = notificacion.metadata.envio_id;
      this.showEnvioDetailModal = true;
    }
  }

  marcarTodasComoLeidas(): void {
    this.notificacionService.marcarTodasComoLeidas().subscribe({
      next: () => {
        // El servicio actualiza automáticamente la lista
      },
      error: (error) => {
        console.error('Error marcando todas como leídas:', error);
      }
    });
  }

  eliminarNotificacion(notificacion: Notificacion, event: Event): void {
    event.stopPropagation();
    
    if (confirm('¿Estás seguro de que quieres eliminar esta notificación?')) {
      this.notificacionService.eliminarNotificacion(notificacion.id).subscribe({
        next: () => {
          // El servicio actualiza automáticamente la lista
        },
        error: (error) => {
          console.error('Error eliminando notificación:', error);
        }
      });
    }
  }

  closeEnvioDetailModal(): void {
    this.showEnvioDetailModal = false;
    this.selectedEnvioId = null;
  }

  getNotificacionIcon(tipo: string): string {
    const iconos: { [key: string]: string } = {
      'nuevo_envio': 'fa-truck',
      'envio_asignado': 'fa-user-check',
      'estado_cambiado': 'fa-exchange-alt',
      'general': 'fa-bell'
    };
    return iconos[tipo] || 'fa-bell';
  }

  getTimeAgo(fecha: string): string {
    const ahora = new Date();
    const fechaNotificacion = new Date(fecha);
    const diferencia = ahora.getTime() - fechaNotificacion.getTime();
    const segundos = Math.floor(diferencia / 1000);
    const minutos = Math.floor(segundos / 60);
    const horas = Math.floor(minutos / 60);
    const dias = Math.floor(horas / 24);

    if (segundos < 60) return 'Hace unos segundos';
    if (minutos < 60) return `Hace ${minutos} minuto${minutos > 1 ? 's' : ''}`;
    if (horas < 24) return `Hace ${horas} hora${horas > 1 ? 's' : ''}`;
    if (dias < 7) return `Hace ${dias} día${dias > 1 ? 's' : ''}`;
    
    return fechaNotificacion.toLocaleDateString('es-ES', { 
      day: 'numeric', 
      month: 'short', 
      year: 'numeric' 
    });
  }

  cambiarPagina(pagina: number): void {
    if (pagina >= 1 && pagina <= this.totalPaginas) {
      this.paginaActual = pagina;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  get estadisticas() {
    const todas = this.notificaciones.length;
    const leidas = this.notificaciones.filter(n => n.leida).length;
    const noLeidas = todas - leidas;
    
    return { todas, leidas, noLeidas };
  }
}

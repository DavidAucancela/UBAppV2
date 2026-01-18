import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../services/api.service';
import { AuthService } from '../../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-inicio',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './inicio.component.html',
  styleUrl: './inicio.component.css'
})
export class InicioComponent implements OnInit {
  loading = true;
  error: string | null = null;
  
  stats: any = {
    envios: {
      total_envios: 0,
      envios_pendientes: 0,
      por_estado: {}
    },
    usuarios: {},
    productos: {
      total_productos: 0
    }
  };

  constructor(
    private apiService: ApiService,
    public authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.cargarEstadisticas();
  }

  cargarEstadisticas(): void {
    this.loading = true;
    this.error = null;

    // Cargar estadísticas de envíos
    this.apiService.getEstadisticasEnvios().subscribe({
      next: (data) => {
        this.stats.envios = data || { total_envios: 0, envios_pendientes: 0, por_estado: {} };
        this.loading = false;
      },
      error: (err) => {
        console.error('Error cargando estadísticas de envíos:', err);
        this.stats.envios = { total_envios: 0, envios_pendientes: 0, por_estado: {} };
        this.loading = false;
      }
    });

    // Cargar estadísticas de usuarios (solo para Admin y Gerente)
    if (this.isAdmin() || this.isGerente()) {
      this.apiService.getEstadisticasUsuarios().subscribe({
        next: (data) => {
          this.stats.usuarios = data || {};
        },
        error: (err) => {
          console.error('Error cargando estadísticas de usuarios:', err);
          this.stats.usuarios = {};
        }
      });
    }

    // Cargar estadísticas de productos (solo para quienes pueden gestionar envíos)
    if (this.canManageEnvios()) {
      this.apiService.getEstadisticasProductos().subscribe({
        next: (data) => {
          this.stats.productos = data || { total_productos: 0 };
        },
        error: (err) => {
          console.error('Error cargando estadísticas de productos:', err);
          this.stats.productos = { total_productos: 0 };
        }
      });
    }
  }

  isAdmin(): boolean {
    return this.authService.getCurrentUser()?.rol === 1;
  }

  isGerente(): boolean {
    return this.authService.getCurrentUser()?.rol === 2;
  }

  canManageEnvios(): boolean {
    const rol = this.authService.getCurrentUser()?.rol;
    return rol === 1 || rol === 2 || rol === 3; // Admin, Gerente, Digitador
  }

  getTotalUsuarios(): number {
    if (!this.stats.usuarios || typeof this.stats.usuarios !== 'object') {
      return 0;
    }
    return Object.values(this.stats.usuarios as { [key: string]: number }).reduce((sum: number, val: number) => {
      return sum + (typeof val === 'number' ? val : 0);
    }, 0);
  }

  getRoleClass(rol: string): string {
    const roleMap: { [key: string]: string } = {
      'Admin': 'admin',
      'Gerente': 'gerente',
      'Digitador': 'digitador',
      'Comprador': 'comprador'
    };
    return roleMap[rol] || 'default';
  }

  getStatusClass(estado: string): string {
    const statusMap: { [key: string]: string } = {
      'Entregado': 'delivered',
      'En tránsito': 'transit',
      'Pendiente': 'pending',
      'Cancelado': 'cancelled'
    };
    return statusMap[estado] || 'default';
  }

  getPercentage(value: number, total: number): number {
    if (!total || total === 0) return 0;
    return Math.round((value / total) * 100);
  }

  goToUsuariosWithRole(rol: string): void {
    // Navegar a usuarios con filtro por rol si es necesario
    this.router.navigate(['/usuarios']);
  }

  goToEnviosWithEstadoLabel(estado: string): void {
    // Mapear etiquetas a estados del backend
    const estadoMap: { [key: string]: string } = {
      'Entregado': 'entregado',
      'En tránsito': 'en_transito',
      'Pendiente': 'pendiente',
      'Cancelado': 'cancelado'
    };
    const estadoBackend = estadoMap[estado] || estado.toLowerCase();
    this.router.navigate(['/envios'], { queryParams: { estado: estadoBackend } });
  }
}

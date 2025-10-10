import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { ApiService } from '../../../services/api.service';
import { Usuario, Roles } from '../../../models/usuario';

interface Activity {
  type: string;
  description: string;
  time: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  currentUser: Usuario | null = null;
  stats: any = {};
  loading = true;
  recentActivity: Activity[] = [];

  constructor(
    private authService: AuthService,
    private apiService: ApiService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.loadStats();
    this.loadRecentActivity();
  }

  loadStats(): void {
    this.loading = true;
    
    // Cargar estadísticas según el rol del usuario
    if (this.authService.isAdmin() || this.authService.isGerente()) {
      this.loadAdminStats();
    } else if (this.authService.isDigitador()) {
      this.loadDigitadorStats();
    } else if (this.authService.isComprador()) {
      this.loadCompradorStats();
    }
  }

  private loadAdminStats(): void {
    // Cargar estadísticas de usuarios
    this.apiService.getEstadisticasUsuarios().subscribe({
      next: (userStats) => {
        this.stats.usuarios = userStats;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando estadísticas de usuarios:', error);
        this.loading = false;
      }
    });

    // Cargar estadísticas de envíos
    this.apiService.getEstadisticasEnvios().subscribe({
      next: (envioStats) => {
        this.stats.envios = envioStats;
      },
      error: (error) => {
        console.error('Error cargando estadísticas de envíos:', error);
      }
    });

    // Cargar estadísticas de productos
    this.apiService.getEstadisticasProductos().subscribe({
      next: (productoStats) => {
        this.stats.productos = productoStats;
      },
      error: (error) => {
        console.error('Error cargando estadísticas de productos:', error);
      }
    });
  }

  private loadDigitadorStats(): void {
    // Cargar estadísticas de envíos y productos
    this.apiService.getEstadisticasEnvios().subscribe({
      next: (envioStats) => {
        this.stats.envios = envioStats;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando estadísticas de envíos:', error);
        this.loading = false;
      }
    });

    // Cargar estadísticas de productos
    this.apiService.getEstadisticasProductos().subscribe({
      next: (productoStats) => {
        this.stats.productos = productoStats;
      },
      error: (error) => {
        console.error('Error cargando estadísticas de productos:', error);
      }
    });
  }

  private loadCompradorStats(): void {
    // Cargar estadísticas de envíos propios
    this.apiService.getMisEnvios().subscribe({
      next: (envios) => {
        this.stats.misEnvios = {
          total: envios.length,
          pendientes: envios.filter(e => e.estado === 'pendiente').length,
          en_transito: envios.filter(e => e.estado === 'en_transito').length,
          entregados: envios.filter(e => e.estado === 'entregado').length
        };
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando envíos:', error);
        this.loading = false;
      }
    });
  }

  private loadRecentActivity(): void {
    // Simular actividad reciente (en un caso real, esto vendría del backend)
    this.recentActivity = [
      {
        type: 'envio',
        description: 'Nuevo envío creado #1234',
        time: 'Hace 5 minutos'
      },
      {
        type: 'usuario',
        description: 'Usuario "Juan Pérez" registrado',
        time: 'Hace 15 minutos'
      },
      {
        type: 'producto',
        description: 'Producto "Laptop HP" agregado al catálogo',
        time: 'Hace 1 hora'
      },
      {
        type: 'envio',
        description: 'Envío #1230 entregado exitosamente',
        time: 'Hace 2 horas'
      }
    ];
  }

  // Métodos de verificación de roles
  isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  isGerente(): boolean {
    return this.authService.isGerente();
  }

  isDigitador(): boolean {
    return this.authService.isDigitador();
  }

  isComprador(): boolean {
    return this.authService.isComprador();
  }

  canManageUsers(): boolean {
    return this.authService.canManageUsers();
  }

  canManageEnvios(): boolean {
    return this.authService.canManageEnvios();
  }

  canViewAllEnvios(): boolean {
    return this.authService.canViewAllEnvios();
  }

  canViewOwnEnvios(): boolean {
    return this.authService.canViewOwnEnvios();
  }

  // Métodos para el template
  getStatusClass(status: any): string {
    const statusStr = String(status);
    switch (statusStr) {
      case 'Entregado':
        return 'success';
      case 'En Tránsito':
        return 'warning';
      case 'Pendiente':
        return 'warning';
      case 'Cancelado':
        return 'danger';
      default:
        return '';
    }
  }

  getActivityIcon(type: string): string {
    switch (type) {
      case 'envio':
        return 'fa-truck';
      case 'usuario':
        return 'fa-user-plus';
      case 'producto':
        return 'fa-box';
      case 'busqueda':
        return 'fa-search';
      default:
        return 'fa-info-circle';
    }
  }
}

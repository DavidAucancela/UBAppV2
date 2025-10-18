import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { ApiService } from '../../../services/api.service';
import { Usuario, Roles } from '../../../models/usuario';
import { ESTADOS_LABELS, EstadosEnvio } from '../../../models/envio';

interface Activity {
  type: string;
  description: string;
  time: string;
}

@Component({
  selector: 'app-inicio',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './inicio.component.html',
  styleUrl: './inicio.component.css'
})
export class InicioComponent implements OnInit {
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
        this.stats.envios = this.normalizeEnviosStats(envioStats);
        this.refreshEnviosPorEstadoFromList();
      },
      error: (error) => {
        console.error('Error cargando estadísticas de envíos:', error);
        this.refreshEnviosPorEstadoFromList();
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
        this.stats.envios = this.normalizeEnviosStats(envioStats);
        this.loading = false;
        this.refreshEnviosPorEstadoFromList();
      },
      error: (error) => {
        console.error('Error cargando estadísticas de envíos:', error);
        this.loading = false;
        this.refreshEnviosPorEstadoFromList();
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
    // Intentar cargar actividad real básica desde endpoints existentes como fallback
    const actividades: Activity[] = [];
    // Usuarios recientes
    this.apiService.getUsuarios().subscribe({
      next: (usuarios) => {
        const lista = Array.isArray(usuarios) ? usuarios : (usuarios as any).results || [];
        lista.slice(0, 3).forEach((u: any) => {
          actividades.push({
            type: 'usuario',
            description: `Nuevo usuario: ${u.nombre || u.username}`,
            time: u.fecha_creacion ? new Date(u.fecha_creacion).toLocaleString() : 'Reciente'
          });
        });
        this.recentActivity = [...actividades, ...this.recentActivity];
      },
      error: () => {}
    });
    // Envíos recientes
    this.apiService.getEnvios().subscribe({
      next: (envios) => {
        const lista = Array.isArray(envios) ? envios : (envios as any).results || [];
        lista.slice(0, 3).forEach((e: any) => {
          actividades.push({
            type: 'envio',
            description: `Envío ${e.hawb} (${e.estado_nombre || e.estado})`,
            time: e.fecha_creacion ? new Date(e.fecha_creacion).toLocaleString() : 'Reciente'
          });
        });
        this.recentActivity = actividades;
      },
      error: () => {
        // Si falla, mantener vacío
      }
    });
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
  private normalizeEnviosStats(envioStats: any): any {
    // Asegurar estructura y rellenar por_estado si falta o está vacío
    const result = { ...envioStats };
    const porEstado: Record<string, number> = {};
    const labels = ESTADOS_LABELS;
    const estados = [
      EstadosEnvio.ENTREGADO,
      EstadosEnvio.EN_TRANSITO,
      EstadosEnvio.PENDIENTE,
      EstadosEnvio.CANCELADO
    ];
    // Si viene por_estado, copiarlo; si no, iniciar en 0
    estados.forEach((estado) => {
      const label = labels[estado as keyof typeof labels];
      const fuente = envioStats?.por_estado || {};
      // Aceptar tanto claves en label como en valor canonico
      const valor =
        fuente[label] ??
        fuente[estado] ??
        0;
      porEstado[label] = Number(valor) || 0;
    });
    result.por_estado = porEstado;
    // Totales de respaldo
    if (typeof result.total_envios !== 'number') {
      result.total_envios = Object.values(porEstado).reduce((a, b) => a + (Number(b) || 0), 0);
    }
    if (typeof result.envios_pendientes !== 'number') {
      result.envios_pendientes = porEstado[ESTADOS_LABELS[EstadosEnvio.PENDIENTE as keyof typeof ESTADOS_LABELS]] || 0;
    }
    return result;
  }

  private normalizeText(value: string): string {
    // Convertir guiones bajos y espacios a un formato común
    return String(value || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/_/g, ' ')
      .trim();
  }

  private estadoMatches(keyNormalized: string, estado: EstadosEnvio): boolean {
    const canonical = this.normalizeText(estado);
    const label = this.normalizeText(ESTADOS_LABELS[estado as keyof typeof ESTADOS_LABELS]);
    return keyNormalized === canonical || keyNormalized === label;
  }

  private refreshEnviosPorEstadoFromList(): void {
    const compute = (lista: any[]) => {
      const counts: Record<string, number> = {
        'Entregado': 0,
        'En tránsito': 0,
        'Pendiente': 0,
        'Cancelado': 0
      };
      
      lista.forEach((e: any) => {
        const key = this.normalizeText(e.estado);
        
        if (this.estadoMatches(key, EstadosEnvio.ENTREGADO)) {
          counts['Entregado'] += 1;
        }
        else if (this.estadoMatches(key, EstadosEnvio.EN_TRANSITO)) {
          counts['En tránsito'] += 1;
        }
        else if (this.estadoMatches(key, EstadosEnvio.PENDIENTE)) {
          counts['Pendiente'] += 1;
        }
        else if (this.estadoMatches(key, EstadosEnvio.CANCELADO)) {
          counts['Cancelado'] += 1;
        }
      });
      
      if (!this.stats.envios) this.stats.envios = {};
      this.stats.envios.por_estado = counts;
      this.stats.envios.total_envios = lista.length;
      this.stats.envios.envios_pendientes = counts['Pendiente'];
    };

    if (this.isComprador()) {
      this.apiService.getMisEnvios().subscribe({
        next: (resp) => {
          const lista = Array.isArray(resp) ? resp : (resp as any).results || [];
          compute(lista);
        },
        error: () => {}
      });
    } else {
      this.apiService.getEnvios().subscribe({
        next: (resp) => {
          const lista = Array.isArray(resp) ? resp : (resp as any).results || [];
          compute(lista);
        },
        error: () => {}
      });
    }
  }

  getStatusClass(status: any): string {
    const s = this.normalizeText(String(status));
    if (this.estadoMatches(s, EstadosEnvio.ENTREGADO)) return 'success';
    if (this.estadoMatches(s, EstadosEnvio.EN_TRANSITO)) return 'warning';
    if (this.estadoMatches(s, EstadosEnvio.PENDIENTE)) return 'warning';
    if (this.estadoMatches(s, EstadosEnvio.CANCELADO)) return 'danger';
    return '';
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

  // Navegación desde tarjetas
  goToUsuariosWithRole(roleLabel: string): void {
    // Mapear label a enum
    const map: Record<string, number> = {
      'Admin': Roles.ADMIN,
      'Gerente': Roles.GERENTE,
      'Digitador': Roles.DIGITADOR,
      'Comprador': Roles.COMPRADOR
    };
    const rol = map[roleLabel];
    if (rol) {
      this.router.navigate(['/usuarios'], { queryParams: { rol } });
    } else {
      this.router.navigate(['/usuarios']);
    }
  }

  goToEnviosWithEstadoLabel(label: string): void {
    const normalized = this.normalizeText(label);
    let estado = '';
    if (this.estadoMatches(normalized, EstadosEnvio.PENDIENTE)) estado = EstadosEnvio.PENDIENTE;
    else if (this.estadoMatches(normalized, EstadosEnvio.EN_TRANSITO)) estado = EstadosEnvio.EN_TRANSITO;
    else if (this.estadoMatches(normalized, EstadosEnvio.ENTREGADO)) estado = EstadosEnvio.ENTREGADO;
    else if (this.estadoMatches(normalized, EstadosEnvio.CANCELADO)) estado = EstadosEnvio.CANCELADO;
    this.router.navigate(['/envios'], { queryParams: estado ? { estado } : undefined });
  }

  goToMapa(): void {
    this.router.navigate(['/mapa-compradores']);
  }
}


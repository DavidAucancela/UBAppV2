import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Subject, interval } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { AuthService } from '../../../services/auth.service';
import { ApiService } from '../../../services/api.service';
import { DashboardService, DashboardStats, MetricsSummary, UserActivity } from '../../../services/dashboard.service';
import { Usuario, Roles } from '../../../models/usuario';

interface StatCard {
  title: string;
  value: string;
  change: number;
  changeLabel: string;
  icon: string;
  color: string;
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
export class DashboardComponent implements OnInit, OnDestroy {
  currentUser: Usuario | null = null;
  dashboardStats: DashboardStats | null = null;
  metricsSummary: MetricsSummary | null = null;
  recentActivity: UserActivity[] = [];
  loading = true;
  error: string | null = null;
  
  // Chart configurations
  chartOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  pieChartOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'right'
      }
    }
  };

  // Stat cards for display
  statCards: StatCard[] = [];

  // Chart data
  enviosChartData: any = null;
  productosChartData: any = null;
  usuariosChartData: any = null;
  financialChartData: any = null;
  estadosChartData: any = null;
  categoriasChartData: any = null;

  // Selected period for metrics
  selectedPeriod = 'monthly';
  availablePeriods = [
    { value: 'daily', label: 'Últimos 30 días' },
    { value: 'weekly', label: 'Últimas 12 semanas' },
    { value: 'monthly', label: 'Últimos 12 meses' },
    { value: 'yearly', label: 'Últimos 2 años' }
  ];

  private destroy$ = new Subject<void>();

  constructor(
    private authService: AuthService,
    private apiService: ApiService,
    private dashboardService: DashboardService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.loadDashboardData();
    
    // Auto-refresh every 5 minutes
    interval(300000)
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => this.loadDashboardData());
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadDashboardData(): void {
    this.loading = true;
    this.error = null;

    // Load dashboard stats
    this.dashboardService.getDashboardStats()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (stats) => {
          this.dashboardStats = stats;
          this.createStatCards();
          this.createPieCharts();
          this.recentActivity = stats.actividad_reciente || [];
          this.loading = false;
        },
        error: (error) => {
          console.error('Error loading dashboard stats:', error);
          this.error = 'Error cargando estadísticas del dashboard';
          this.loading = false;
        }
      });

    // Load metrics summary
    this.loadMetricsSummary();
  }

  loadMetricsSummary(): void {
    this.dashboardService.getMetricsSummary(this.selectedPeriod)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (summary) => {
          this.metricsSummary = summary;
          this.createLineCharts();
        },
        error: (error) => {
          console.error('Error loading metrics summary:', error);
        }
      });
  }

  onPeriodChange(period: string): void {
    this.selectedPeriod = period;
    this.loadMetricsSummary();
  }

  private createStatCards(): void {
    if (!this.dashboardStats) return;

    const stats = this.dashboardStats;
    
    this.statCards = [
      {
        title: 'Total Envíos',
        value: this.dashboardService.formatNumber(stats.total_envios),
        change: stats.cambio_envios_mes,
        changeLabel: 'vs mes anterior',
        icon: 'fas fa-truck',
        color: 'primary'
      },
      {
        title: 'Total Productos',
        value: this.dashboardService.formatNumber(stats.total_productos),
        change: stats.cambio_productos_mes,
        changeLabel: 'vs mes anterior',
        icon: 'fas fa-box',
        color: 'success'
      },
      {
        title: 'Valor Total',
        value: this.dashboardService.formatCurrency(stats.valor_total_envios),
        change: stats.cambio_valor_mes,
        changeLabel: 'vs mes anterior',
        icon: 'fas fa-dollar-sign',
        color: 'warning'
      },
      {
        title: 'Usuarios Activos',
        value: this.dashboardService.formatNumber(stats.total_usuarios),
        change: 0, // No change data available for users
        changeLabel: 'total usuarios',
        icon: 'fas fa-users',
        color: 'info'
      }
    ];

    // Add role-specific cards
    if (this.isAdmin() || this.isGerente()) {
      this.statCards.push({
        title: 'Compradores',
        value: this.dashboardService.formatNumber(stats.total_compradores),
        change: 0,
        changeLabel: 'total compradores',
        icon: 'fas fa-user-tie',
        color: 'secondary'
      });
    }
  }

  private createLineCharts(): void {
    if (!this.metricsSummary) return;

    const summary = this.metricsSummary;

    // Envíos chart
    this.enviosChartData = {
      labels: summary.envios_data.labels,
      datasets: summary.envios_data.datasets.map(dataset => ({
        ...dataset,
        tension: 0.4,
        fill: false
      }))
    };

    // Productos chart
    this.productosChartData = {
      labels: summary.productos_data.labels,
      datasets: summary.productos_data.datasets.map(dataset => ({
        ...dataset,
        tension: 0.4,
        fill: false
      }))
    };

    // Usuarios activity chart
    this.usuariosChartData = {
      labels: summary.usuarios_data.labels,
      datasets: summary.usuarios_data.datasets.map(dataset => ({
        ...dataset,
        tension: 0.4,
        fill: false
      }))
    };

    // Financial chart
    this.financialChartData = {
      labels: summary.financial_data.labels,
      datasets: summary.financial_data.datasets.map(dataset => ({
        ...dataset,
        tension: 0.4,
        fill: false
      }))
    };
  }

  private createPieCharts(): void {
    if (!this.dashboardStats) return;

    const stats = this.dashboardStats;

    // Estados chart
    if (stats.envios_por_estado) {
      const estadosLabels = Object.keys(stats.envios_por_estado);
      const estadosData = Object.values(stats.envios_por_estado);
      
      this.estadosChartData = {
        labels: estadosLabels,
        datasets: [{
          data: estadosData,
          backgroundColor: this.dashboardService.getChartColors(estadosLabels.length),
          borderColor: this.dashboardService.getBorderColors(estadosLabels.length),
          borderWidth: 1
        }]
      };
    }

    // Categorías chart
    if (stats.productos_por_categoria) {
      const categoriasLabels = Object.keys(stats.productos_por_categoria);
      const categoriasData = Object.values(stats.productos_por_categoria);
      
      this.categoriasChartData = {
        labels: categoriasLabels,
        datasets: [{
          data: categoriasData,
          backgroundColor: this.dashboardService.getChartColors(categoriasLabels.length),
          borderColor: this.dashboardService.getBorderColors(categoriasLabels.length),
          borderWidth: 1
        }]
      };
    }
  }

  // Navigation methods
  navigateToEnvios(): void {
    this.router.navigate(['/envios']);
  }

  navigateToProductos(): void {
    this.router.navigate(['/productos']);
  }

  navigateToUsuarios(): void {
    if (this.canManageUsers()) {
      this.router.navigate(['/usuarios']);
    }
  }

  navigateToReports(): void {
    this.router.navigate(['/reports']);
  }

  // Role checking methods
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

  // Utility methods
  getChangeClass(change: number): string {
    if (change > 0) return 'text-success';
    if (change < 0) return 'text-danger';
    return 'text-muted';
  }

  getChangeIcon(change: number): string {
    if (change > 0) return 'fas fa-arrow-up';
    if (change < 0) return 'fas fa-arrow-down';
    return 'fas fa-minus';
  }

  getActivityIcon(action: string): string {
    switch (action) {
      case 'Crear Envío':
      case 'Actualizar Envío':
        return 'fas fa-truck';
      case 'Crear Producto':
      case 'Actualizar Producto':
        return 'fas fa-box';
      case 'Inicio de Sesión':
        return 'fas fa-sign-in-alt';
      case 'Búsqueda':
        return 'fas fa-search';
      case 'Exportar Datos':
        return 'fas fa-download';
      case 'Importar Datos':
        return 'fas fa-upload';
      default:
        return 'fas fa-info-circle';
    }
  }

  getActivityClass(action: string): string {
    switch (action) {
      case 'Crear Envío':
      case 'Crear Producto':
        return 'text-success';
      case 'Actualizar Envío':
      case 'Actualizar Producto':
        return 'text-warning';
      case 'Eliminar Envío':
      case 'Eliminar Producto':
        return 'text-danger';
      default:
        return 'text-primary';
    }
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Hace un momento';
    if (diffMins < 60) return `Hace ${diffMins} minutos`;
    if (diffHours < 24) return `Hace ${diffHours} horas`;
    if (diffDays < 7) return `Hace ${diffDays} días`;
    
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  refresh(): void {
    this.loadDashboardData();
  }
}

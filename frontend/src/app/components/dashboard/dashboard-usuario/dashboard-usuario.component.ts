import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { UsuarioService } from '../../../services/usuario.service';
import { AuthService } from '../../../services/auth.service';
import { DashboardUsuario } from '../../../models/usuario';
import { Envio } from '../../../models/envio';
import { Chart, ChartConfiguration, registerables } from 'chart.js';
import { Subscription } from 'rxjs';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard-usuario',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard-usuario.component.html',
  styleUrls: ['./dashboard-usuario.component.css']
})
export class DashboardUsuarioComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('estadosChart') estadosChartRef!: ElementRef<HTMLCanvasElement>;

  estadosChart: Chart | null = null;

  dashboard: DashboardUsuario | null = null;
  enviosRecientes: Envio[] = [];
  loading = true;
  error: string | null = null;
  anioActual = new Date().getFullYear();
  envioSeleccionado: Envio | null = null;

  private subscription: Subscription | null = null;
  private isLoading = false;

  constructor(
    private usuarioService: UsuarioService,
    public authService: AuthService
  ) {}

  ngOnInit(): void {
    this.cargarDashboard();
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      if (!this.loading && this.dashboard) {
        this.crearGraficos();
      }
    }, 300);
  }

  ngOnDestroy(): void {
    if (this.subscription) {
      this.subscription.unsubscribe();
      this.subscription = null;
    }
    this.destroyAllCharts();
  }

  cargarDashboard(): void {
    if (this.isLoading) return;
    this.isLoading = true;
    this.loading = true;
    this.error = null;

    if (this.subscription) {
      this.subscription.unsubscribe();
    }

    this.subscription = this.usuarioService.getDashboardUsuario(this.anioActual).subscribe({
      next: (data) => {
        try {
          if (!data || !data.dashboard) throw new Error('Datos inválidos recibidos del servidor');

          this.dashboard = data.dashboard;
          this.enviosRecientes = Array.isArray(data.envios_recientes) ? data.envios_recientes : [];
          this.asegurarValoresPorDefecto();

          this.loading = false;
          this.isLoading = false;

          setTimeout(() => {
            if (this.dashboard) this.crearGraficos();
          }, 300);
        } catch (err: any) {
          this.error = 'Error al procesar las estadísticas';
          this.loading = false;
          this.isLoading = false;
        }
      },
      error: (err) => {
        this.error = err?.error?.message || err?.error?.detail || err?.message || 'Error al cargar las estadísticas.';
        this.loading = false;
        this.isLoading = false;
      }
    });
  }

  private asegurarValoresPorDefecto(): void {
    if (!this.dashboard) return;
    this.dashboard.peso_usado        = this.dashboard.peso_usado        ?? 0;
    this.dashboard.peso_disponible   = this.dashboard.peso_disponible   ?? 0;
    this.dashboard.porcentaje_usado  = this.dashboard.porcentaje_usado  ?? 0;
    this.dashboard.total_envios      = this.dashboard.total_envios      ?? 0;
    this.dashboard.envios_pendientes = this.dashboard.envios_pendientes ?? 0;
    this.dashboard.envios_en_transito= this.dashboard.envios_en_transito?? 0;
    this.dashboard.envios_entregados = this.dashboard.envios_entregados ?? 0;
    this.dashboard.envios_cancelados = this.dashboard.envios_cancelados ?? 0;
    this.dashboard.valor_total       = this.dashboard.valor_total       ?? 0;
    this.dashboard.cupo_anual        = this.dashboard.cupo_anual        ?? 0;
  }

  private destroyAllCharts(): void {
    if (this.estadosChart) {
      this.estadosChart.destroy();
      this.estadosChart = null;
    }
  }

  private crearGraficos(): void {
    if (!this.dashboard) return;
    try {
      if (this.estadosChartRef?.nativeElement) this.crearGraficoEstados();
    } catch (error) {
      console.error('Error creando gráficos:', error);
    }
  }

  private crearGraficoEstados(): void {
    if (!this.estadosChartRef?.nativeElement || !this.dashboard) return;
    if (this.estadosChart) this.estadosChart.destroy();

    const pendientes  = this.dashboard.envios_pendientes  || 0;
    const enTransito  = this.dashboard.envios_en_transito || 0;
    const entregados  = this.dashboard.envios_entregados  || 0;
    const cancelados  = this.dashboard.envios_cancelados  || 0;
    const total       = pendientes + enTransito + entregados + cancelados;

    const config: ChartConfiguration<'doughnut'> = {
      type: 'doughnut',
      data: {
        labels: ['Pendientes', 'En Tránsito', 'Entregados', 'Cancelados'],
        datasets: [{
          data: [pendientes, enTransito, entregados, cancelados],
          backgroundColor: ['#f59e0b', '#3b82f6', '#10b981', '#94a3b8'],
          borderWidth: 0,
          hoverOffset: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: { display: false },
          tooltip: {
            padding: 12,
            titleFont: { size: 13, weight: 'bold' },
            bodyFont: { size: 12 },
            callbacks: {
              label: (ctx) => {
                const val = ctx.raw as number;
                const pct = total > 0 ? ((val / total) * 100).toFixed(1) : '0';
                return `  ${val} envíos (${pct}%)`;
              }
            }
          }
        }
      }
    };

    this.estadosChart = new Chart(this.estadosChartRef.nativeElement, config);
  }

  // ── Cupo gauge (CSS conic-gradient) ─────────────────────────────────────
  get cupoGaugeCss(): string {
    const p = this.dashboard?.porcentaje_usado || 0;
    const color = p >= 90 ? '#ef4444' : p >= 80 ? '#f59e0b' : p >= 50 ? '#3b82f6' : '#10b981';
    const trackColor = 'var(--color-border, #e2e8f0)';
    return `conic-gradient(${color} 0% ${p}%, ${trackColor} ${p}% 100%)`;
  }

  get cupoColor(): string {
    const p = this.dashboard?.porcentaje_usado || 0;
    if (p >= 90) return '#ef4444';
    if (p >= 80) return '#f59e0b';
    if (p >= 50) return '#3b82f6';
    return '#10b981';
  }

  get fechaHoy(): string {
    return new Date().toLocaleDateString('es-ES', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
  }

  // ── Helpers ──────────────────────────────────────────────────────────────
  abrirDetalle(envio: Envio): void {
    this.envioSeleccionado = envio;
  }

  cerrarDetalle(): void {
    this.envioSeleccionado = null;
  }

  formatearFecha(fecha: string | null | undefined): string {
    if (!fecha) return '-';
    return new Date(fecha).toLocaleString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  }

  obtenerEstadoEnvio(estado: string): string {
    const map: Record<string, string> = {
      pendiente: 'Pendiente', en_transito: 'En Tránsito',
      entregado: 'Entregado', cancelado: 'Cancelado'
    };
    return map[estado] || estado;
  }

  obtenerClaseEstado(estado: string): string {
    const map: Record<string, string> = {
      pendiente: 'warning', en_transito: 'info',
      entregado: 'success', cancelado: 'secondary'
    };
    return map[estado] || 'secondary';
  }
}

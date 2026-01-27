import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { UsuarioService } from '../../../services/usuario.service';
import { AuthService } from '../../../services/auth.service';
import { DashboardUsuario } from '../../../models/usuario';
import { Envio } from '../../../models/envio';
import { Chart, ChartConfiguration, registerables } from 'chart.js';
import { Subscription } from 'rxjs';

// Registrar todos los componentes de Chart.js
Chart.register(...registerables);

@Component({
  selector: 'app-dashboard-usuario',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard-usuario.component.html',
  styleUrls: ['./dashboard-usuario.component.css']
})
export class DashboardUsuarioComponent implements OnInit, OnDestroy, AfterViewInit {
  // Referencias a los canvas de gráficos
  @ViewChild('estadosChart') estadosChartRef!: ElementRef<HTMLCanvasElement>;

  // Instancias de gráficos
  estadosChart: Chart | null = null;

  dashboard: DashboardUsuario | null = null;
  enviosRecientes: Envio[] = [];
  loading = true;
  error: string | null = null;
  anioActual = new Date().getFullYear();
  private subscription: Subscription | null = null;
  private isLoading = false;

  constructor(
    private usuarioService: UsuarioService,
    public authService: AuthService
  ) { }

  ngOnInit(): void {
    this.cargarDashboard();
  }

  ngAfterViewInit(): void {
    // Esperar a que los datos estén cargados antes de crear los gráficos
    // Usar un timeout más largo para asegurar que los elementos canvas estén disponibles
    setTimeout(() => {
      if (!this.loading && this.dashboard) {
        this.crearGraficos();
      }
    }, 300);
  }

  ngOnDestroy(): void {
    // Limpiar suscripciones para evitar memory leaks
    if (this.subscription) {
      this.subscription.unsubscribe();
      this.subscription = null;
    }
    // Destruir todos los gráficos
    this.destroyAllCharts();
  }

  cargarDashboard(): void {
    // Prevenir múltiples llamadas simultáneas
    if (this.isLoading) {
      return;
    }

    this.isLoading = true;
    this.loading = true;
    this.error = null;

    // Cancelar suscripción anterior si existe
    if (this.subscription) {
      this.subscription.unsubscribe();
    }

    this.subscription = this.usuarioService.getDashboardUsuario(this.anioActual).subscribe({
      next: (data) => {
        try {
          // Validar datos recibidos
          if (!data || !data.dashboard) {
            throw new Error('Datos inválidos recibidos del servidor');
          }

          console.log('📊 Datos del dashboard recibidos:', data);
          console.log('👤 Usuario del dashboard:', data.dashboard?.usuario);
          console.log('📦 Estadísticas de envíos:', {
            total: data.dashboard?.total_envios,
            pendientes: data.dashboard?.envios_pendientes,
            en_transito: data.dashboard?.envios_en_transito,
            entregados: data.dashboard?.envios_entregados,
            cancelados: data.dashboard?.envios_cancelados
          });
          console.log('💰 Cupo:', {
            cupo_anual: data.dashboard?.cupo_anual,
            peso_usado: data.dashboard?.peso_usado,
            peso_disponible: data.dashboard?.peso_disponible,
            porcentaje_usado: data.dashboard?.porcentaje_usado
          });

          this.dashboard = data.dashboard;
          this.enviosRecientes = Array.isArray(data.envios_recientes) ? data.envios_recientes : [];
          
          console.log('📋 Envíos recientes:', this.enviosRecientes.length);
          
          // Asegurar valores por defecto para evitar errores
          this.asegurarValoresPorDefecto();
          
          this.loading = false;
          this.isLoading = false;

          // Crear gráficos después de que la vista esté lista
          // Usar un timeout para asegurar que los elementos canvas estén disponibles
          setTimeout(() => {
            if (this.dashboard) {
              this.crearGraficos();
            }
          }, 300);
        } catch (err: any) {
          console.error('❌ Error procesando datos del dashboard:', err);
          this.error = 'Error al procesar las estadísticas';
          this.loading = false;
          this.isLoading = false;
        }
      },
      error: (err) => {
        console.error('❌ Error al cargar dashboard:', err);
        console.error('📋 Detalles del error:', {
          status: err?.status,
          statusText: err?.statusText,
          error: err?.error,
          message: err?.message,
          url: err?.url
        });
        this.error = err?.error?.message || err?.error?.detail || err?.message || 'Error al cargar las estadísticas. Por favor, intenta nuevamente.';
        this.loading = false;
        this.isLoading = false;
      }
    });
  }

  private asegurarValoresPorDefecto(): void {
    if (!this.dashboard) return;

    // Asegurar que todos los valores numéricos tengan valores por defecto
    this.dashboard.peso_usado = this.dashboard.peso_usado ?? 0;
    this.dashboard.peso_disponible = this.dashboard.peso_disponible ?? 0;
    this.dashboard.porcentaje_usado = this.dashboard.porcentaje_usado ?? 0;
    this.dashboard.total_envios = this.dashboard.total_envios ?? 0;
    this.dashboard.envios_pendientes = this.dashboard.envios_pendientes ?? 0;
    this.dashboard.envios_en_transito = this.dashboard.envios_en_transito ?? 0;
    this.dashboard.envios_entregados = this.dashboard.envios_entregados ?? 0;
    this.dashboard.envios_cancelados = this.dashboard.envios_cancelados ?? 0;
    this.dashboard.valor_total = this.dashboard.valor_total ?? 0;
    this.dashboard.cupo_anual = this.dashboard.cupo_anual ?? 0;
  }

  cambiarAnio(anio: number): void {
    if (this.anioActual === anio) return;
    
    this.anioActual = anio;
    // Destruir gráficos antes de recargar
    this.destroyAllCharts();
    this.cargarDashboard();
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
      // Verificar que los elementos canvas estén disponibles
      if (this.estadosChartRef?.nativeElement) {
        this.crearGraficoEstados();
      }
    } catch (error) {
      console.error('Error creando gráficos:', error);
    }
  }

  private crearGraficoEstados(): void {
    if (!this.estadosChartRef?.nativeElement || !this.dashboard) return;

    // Destruir gráfico anterior si existe
    if (this.estadosChart) {
      this.estadosChart.destroy();
    }

    const config: ChartConfiguration = {
      type: 'bar',
      data: {
        labels: ['Pendientes', 'En Tránsito', 'Entregados', 'Cancelados'],
        datasets: [{
          label: 'Envíos',
          data: [
            this.dashboard.envios_pendientes || 0,
            this.dashboard.envios_en_transito || 0,
            this.dashboard.envios_entregados || 0,
            this.dashboard.envios_cancelados || 0
          ],
          backgroundColor: [
            '#f59e0b',
            '#3b82f6',
            '#10b981',
            '#64748b'
          ],
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            padding: 12,
            titleFont: { size: 13, weight: '600' },
            bodyFont: { size: 12 }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1 },
            grid: { color: '#f3f4f6' }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    };

    this.estadosChart = new Chart(this.estadosChartRef.nativeElement, config);
  }


  obtenerColorAlerta(): string {
    if (!this.dashboard) return 'success';
    
    const porcentaje = this.dashboard.porcentaje_usado || 0;
    if (porcentaje >= 90) return 'danger';
    if (porcentaje >= 80) return 'warning';
    if (porcentaje >= 50) return 'info';
    return 'success';
  }

  obtenerEstadoEnvio(estado: string): string {
    const estados: { [key: string]: string } = {
      'pendiente': 'Pendiente',
      'en_transito': 'En Tránsito',
      'entregado': 'Entregado',
      'cancelado': 'Cancelado'
    };
    return estados[estado] || estado;
  }

  obtenerClaseEstado(estado: string): string {
    const clases: { [key: string]: string } = {
      'pendiente': 'warning',
      'en_transito': 'info',
      'entregado': 'success',
      'cancelado': 'secondary'
    };
    return clases[estado] || 'secondary';
  }
}

















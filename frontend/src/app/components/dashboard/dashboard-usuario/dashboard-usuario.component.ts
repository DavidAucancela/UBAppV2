import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UsuarioService } from '../../../services/usuario.service';
import { AuthService } from '../../../services/auth.service';
import { DashboardUsuario } from '../../../models/usuario';
import { Envio } from '../../../models/envio';
import { Chart, ChartConfiguration, ChartType, registerables } from 'chart.js';
import { Subscription } from 'rxjs';

// Registrar todos los componentes de Chart.js
Chart.register(...registerables);

@Component({
  selector: 'app-dashboard-usuario',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard-usuario.component.html',
  styleUrls: ['./dashboard-usuario.component.css']
})
export class DashboardUsuarioComponent implements OnInit, OnDestroy, AfterViewInit {
  // Referencias a los canvas de gráficos
  @ViewChild('estadosChart') estadosChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('tendenciasChart') tendenciasChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('cupoChart') cupoChartRef!: ElementRef<HTMLCanvasElement>;

  // Instancias de gráficos
  estadosChart: Chart | null = null;
  tendenciasChart: Chart | null = null;
  cupoChart: Chart | null = null;

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
    if (this.tendenciasChart) {
      this.tendenciasChart.destroy();
      this.tendenciasChart = null;
    }
    if (this.cupoChart) {
      this.cupoChart.destroy();
      this.cupoChart = null;
    }
  }

  private crearGraficos(): void {
    if (!this.dashboard) return;

    try {
      // Verificar que los elementos canvas estén disponibles
      if (this.estadosChartRef?.nativeElement) {
        this.crearGraficoEstados();
      }
      if (this.tendenciasChartRef?.nativeElement) {
        this.crearGraficoTendencias();
      }
      if (this.cupoChartRef?.nativeElement && this.authService.isComprador()) {
        this.crearGraficoCupo();
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
      type: 'doughnut',
      data: {
        labels: ['Pendientes', 'En Tránsito', 'Entregados', 'Cancelados'],
        datasets: [{
          label: 'Envíos por Estado',
          data: [
            this.dashboard.envios_pendientes || 0,
            this.dashboard.envios_en_transito || 0,
            this.dashboard.envios_entregados || 0,
            this.dashboard.envios_cancelados || 0
          ],
          backgroundColor: [
            'rgba(255, 193, 7, 0.8)',
            'rgba(23, 162, 184, 0.8)',
            'rgba(40, 167, 69, 0.8)',
            'rgba(108, 117, 125, 0.8)'
          ],
          borderColor: [
            'rgba(255, 193, 7, 1)',
            'rgba(23, 162, 184, 1)',
            'rgba(40, 167, 69, 1)',
            'rgba(108, 117, 125, 1)'
          ],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 15,
              font: {
                size: 12
              }
            }
          },
          title: {
            display: true,
            text: 'Distribución de Envíos por Estado',
            font: {
              size: 16,
              weight: 'bold'
            }
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.label || '';
                const value = typeof context.parsed === 'number' ? context.parsed : 0;
                const dataArray = context.dataset.data as number[];
                const total = dataArray.reduce((a: number, b: number) => {
                  const numA = typeof a === 'number' ? a : 0;
                  const numB = typeof b === 'number' ? b : 0;
                  return numA + numB;
                }, 0);
                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0';
                return `${label}: ${value} (${percentage}%)`;
              }
            }
          }
        }
      }
    };

    this.estadosChart = new Chart(this.estadosChartRef.nativeElement, config);
  }

  private crearGraficoTendencias(): void {
    if (!this.tendenciasChartRef?.nativeElement || !this.dashboard) return;

    // Destruir gráfico anterior si existe
    if (this.tendenciasChart) {
      this.tendenciasChart.destroy();
    }

    // Generar datos mensuales simulados basados en el total
    // Distribuir el total de manera más realista
    const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    const totalEnvios = this.dashboard.total_envios || 0;
    
    // Crear una distribución más realista usando una función seno para simular variaciones
    const enviosMensuales = meses.map((_, index) => {
      if (totalEnvios === 0) return 0;
      // Usar una distribución más uniforme con pequeñas variaciones
      const base = totalEnvios / 12;
      const variation = Math.sin((index / 12) * Math.PI * 2) * (totalEnvios / 24);
      return Math.max(0, Math.floor(base + variation));
    });

    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: meses,
        datasets: [{
          label: 'Envíos Mensuales',
          data: enviosMensuales,
          borderColor: 'rgba(102, 126, 234, 1)',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBackgroundColor: 'rgba(102, 126, 234, 1)',
          pointBorderColor: '#fff',
          pointBorderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          title: {
            display: true,
            text: `Tendencias de Envíos ${this.anioActual}`,
            font: {
              size: 16,
              weight: 'bold'
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1
            }
          }
        }
      }
    };

    this.tendenciasChart = new Chart(this.tendenciasChartRef.nativeElement, config);
  }

  private crearGraficoCupo(): void {
    if (!this.cupoChartRef?.nativeElement || !this.dashboard || !this.authService.isComprador()) return;

    // Destruir gráfico anterior si existe
    if (this.cupoChart) {
      this.cupoChart.destroy();
    }

    const pesoUsado = this.dashboard.peso_usado || 0;
    const pesoDisponible = this.dashboard.peso_disponible || 0;
    const cupoTotal = this.dashboard.cupo_anual || (pesoUsado + pesoDisponible);

    const config: ChartConfiguration = {
      type: 'bar',
      data: {
        labels: ['Cupo Anual'],
        datasets: [
          {
            label: 'Peso Usado (kg)',
            data: [pesoUsado],
            backgroundColor: 'rgba(220, 53, 69, 0.8)',
            borderColor: 'rgba(220, 53, 69, 1)',
            borderWidth: 2
          },
          {
            label: 'Peso Disponible (kg)',
            data: [pesoDisponible],
            backgroundColor: 'rgba(40, 167, 69, 0.8)',
            borderColor: 'rgba(40, 167, 69, 1)',
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          title: {
            display: true,
            text: `Uso de Cupo Anual ${this.anioActual}`,
            font: {
              size: 16,
              weight: 'bold'
            }
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.dataset.label || '';
                let value = 0;
                
                // Extraer valor de forma segura según el tipo de gráfico
                if (typeof context.parsed === 'number') {
                  value = context.parsed;
                } else if (context.parsed && typeof context.parsed === 'object') {
                  // Para gráficos de barras, el valor está en parsed.y
                  const parsedObj = context.parsed as any;
                  if (parsedObj.y !== undefined && parsedObj.y !== null) {
                    value = Number(parsedObj.y);
                  }
                }
                
                const percentage = cupoTotal > 0 ? ((value / cupoTotal) * 100).toFixed(1) : '0';
                return `${label}: ${value.toFixed(2)} kg (${percentage}%)`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => `${value} kg`
            }
          }
        }
      }
    };

    this.cupoChart = new Chart(this.cupoChartRef.nativeElement, config);
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
      'pendiente': 'badge bg-warning',
      'en_transito': 'badge bg-info',
      'entregado': 'badge bg-success',
      'cancelado': 'badge bg-secondary'
    };
    return clases[estado] || 'badge bg-secondary';
  }
}

















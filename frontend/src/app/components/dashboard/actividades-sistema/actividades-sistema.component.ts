import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Chart, ChartConfiguration, registerables } from 'chart.js';
import { MetricasService } from '../../../services/metricas.service';

Chart.register(...registerables);

@Component({
  selector: 'app-actividades-sistema',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './actividades-sistema.component.html',
  styleUrl: './actividades-sistema.component.css'
})
export class ActividadesSistemaComponent implements OnInit, AfterViewInit, OnDestroy {
  // Estados de carga
  loading = true;
  loadingMetricasSemanticas = false;
  loadingMetricasRendimiento = false;
  ejecutandoPrueba = false;

  // Sección activa
  seccionActiva: 'semanticas' | 'rendimiento' = 'semanticas';

  // Datos de métricas semánticas
  metricasSemanticas: any[] = [];
  estadisticasSemanticas: any = {};
  pruebasControladas: any[] = [];
  
  // Datos de métricas de rendimiento
  metricasRendimiento: any[] = [];
  estadisticasRendimiento: any = {};
  pruebasCarga: any[] = [];
  registrosEmbedding: any[] = [];
  estadisticasEmbedding: any = {};
  registrosManuales: any[] = [];
  estadisticasRegistrosManuales: any = {};

  // Filtros
  filtroFechaDesde: string = '';
  filtroFechaHasta: string = '';
  filtroNivelCarga: number | null = null;

  // Gráficos
  @ViewChild('chartMetricasSemanticas') chartMetricasSemanticas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('chartTiemposRendimiento') chartTiemposRendimiento!: ElementRef<HTMLCanvasElement>;
  @ViewChild('chartRecursos') chartRecursos!: ElementRef<HTMLCanvasElement>;
  
  chartMetricasSemanticasInstance: Chart | null = null;
  chartTiemposRendimientoInstance: Chart | null = null;
  chartRecursosInstance: Chart | null = null;

  // Formularios
  nuevaPruebaControlada = {
    nombre: '',
    descripcion: '',
    consulta: '',
    resultados_relevantes: [] as number[]
  };

  nuevaPruebaCarga = {
    nivel_carga: 1,
    consultas: [''] as string[],
    nombre_prueba: ''
  };

  nuevoRegistroManual = {
    hawb: '',
    tiempo_registro_segundos: 0,
    datos_envio: null as any,
    notas: ''
  };

  constructor(
    private metricasService: MetricasService
  ) {}

  ngOnInit(): void {
    this.cargarDatos();
  }

  ngAfterViewInit(): void {
    // Los gráficos se crearán después de cargar los datos
  }

  ngOnDestroy(): void {
    this.destruirGraficos();
  }

  // ==================== CARGA DE DATOS ====================

  cargarDatos(): void {
    this.loading = true;
    
    // Cargar datos de ambas secciones
    Promise.all([
      this.cargarMetricasSemanticas(),
      this.cargarMetricasRendimiento(),
      this.cargarPruebasControladas(),
      this.cargarPruebasCarga(),
      this.cargarRegistrosEmbedding(),
      this.cargarRegistrosManuales()
    ]).finally(() => {
      this.loading = false;
      setTimeout(() => {
        this.crearGraficos();
      }, 100);
    });
  }

  cargarMetricasSemanticas(): Promise<void> {
    return new Promise((resolve) => {
      this.metricasService.getMetricasSemanticas(
        this.filtroFechaDesde || undefined,
        this.filtroFechaHasta || undefined
      ).subscribe({
        next: (data) => {
          this.metricasSemanticas = data;
          this.metricasService.getEstadisticasSemanticas(
            this.filtroFechaDesde || undefined,
            this.filtroFechaHasta || undefined
          ).subscribe({
            next: (stats) => {
              this.estadisticasSemanticas = stats;
              resolve();
            },
            error: () => resolve()
          });
        },
        error: () => resolve()
      });
    });
  }

  cargarMetricasRendimiento(): Promise<void> {
    return new Promise((resolve) => {
      this.metricasService.getMetricasRendimiento(
        undefined,
        this.filtroNivelCarga || undefined,
        this.filtroFechaDesde || undefined,
        this.filtroFechaHasta || undefined
      ).subscribe({
        next: (data) => {
          this.metricasRendimiento = data;
          this.metricasService.getEstadisticasRendimiento(
            undefined,
            this.filtroNivelCarga || undefined
          ).subscribe({
            next: (stats) => {
              this.estadisticasRendimiento = stats;
              resolve();
            },
            error: () => resolve()
          });
        },
        error: () => resolve()
      });
    });
  }

  cargarPruebasControladas(): Promise<void> {
    return new Promise((resolve) => {
      this.metricasService.getPruebasControladas(true).subscribe({
        next: (data) => {
          this.pruebasControladas = data;
          resolve();
        },
        error: () => resolve()
      });
    });
  }

  cargarPruebasCarga(): Promise<void> {
    return new Promise((resolve) => {
      this.metricasService.getPruebasCarga().subscribe({
        next: (data) => {
          this.pruebasCarga = data;
          resolve();
        },
        error: () => resolve()
      });
    });
  }

  cargarRegistrosEmbedding(): Promise<void> {
    return new Promise((resolve) => {
      this.metricasService.getRegistrosEmbedding().subscribe({
        next: (data) => {
          this.registrosEmbedding = data;
          this.metricasService.getEstadisticasEmbedding().subscribe({
            next: (stats) => {
              this.estadisticasEmbedding = stats;
              resolve();
            },
            error: () => resolve()
          });
        },
        error: () => resolve()
      });
    });
  }

  cargarRegistrosManuales(): Promise<void> {
    return new Promise((resolve) => {
      this.metricasService.getRegistrosManuales().subscribe({
        next: (data) => {
          this.registrosManuales = data;
          this.metricasService.getEstadisticasRegistrosManuales().subscribe({
            next: (stats) => {
              this.estadisticasRegistrosManuales = stats;
              resolve();
            },
            error: () => resolve()
          });
        },
        error: () => resolve()
      });
    });
  }

  // ==================== GRÁFICOS ====================

  crearGraficos(): void {
    this.crearGraficoMetricasSemanticas();
    this.crearGraficoTiemposRendimiento();
    this.crearGraficoRecursos();
  }

  crearGraficoMetricasSemanticas(): void {
    if (!this.chartMetricasSemanticas?.nativeElement) return;

    const datos = this.metricasSemanticas.slice(-20); // Últimas 20 métricas
    
    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: datos.map((m, i) => `Métrica ${m.id}`),
        datasets: [
          {
            label: 'MRR',
            data: datos.map(m => m.mrr || 0),
            borderColor: 'rgb(99, 102, 241)',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            tension: 0.4
          },
          {
            label: 'nDCG@10',
            data: datos.map(m => m.ndcg_10 || 0),
            borderColor: 'rgb(236, 72, 153)',
            backgroundColor: 'rgba(236, 72, 153, 0.1)',
            tension: 0.4
          },
          {
            label: 'Precision@5',
            data: datos.map(m => m.precision_5 || 0),
            borderColor: 'rgb(34, 197, 94)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top'
          },
          title: {
            display: true,
            text: 'Evolución de Métricas Semánticas'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 1.0
          }
        }
      }
    };

    this.destruirGrafico('metricasSemanticas');
    this.chartMetricasSemanticasInstance = new Chart(this.chartMetricasSemanticas.nativeElement, config);
  }

  crearGraficoTiemposRendimiento(): void {
    if (!this.chartTiemposRendimiento?.nativeElement) return;

    const datos = this.metricasRendimiento.slice(-30); // Últimas 30 métricas
    
    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: datos.map((m, i) => {
          const fecha = new Date(m.fecha_medicion);
          return fecha.toLocaleDateString() + ' ' + fecha.toLocaleTimeString();
        }),
        datasets: [
          {
            label: 'Tiempo de Respuesta (ms)',
            data: datos.map(m => m.tiempo_respuesta_ms),
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top'
          },
          title: {
            display: true,
            text: 'Tiempos de Respuesta del Sistema'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    };

    this.destruirGrafico('tiemposRendimiento');
    this.chartTiemposRendimientoInstance = new Chart(this.chartTiemposRendimiento.nativeElement, config);
  }

  crearGraficoRecursos(): void {
    if (!this.chartRecursos?.nativeElement) return;

    const datos = this.metricasRendimiento.slice(-30); // Últimas 30 métricas
    
    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: datos.map((m, i) => {
          const fecha = new Date(m.fecha_medicion);
          return fecha.toLocaleDateString() + ' ' + fecha.toLocaleTimeString();
        }),
        datasets: [
          {
            label: 'CPU (%)',
            data: datos.map(m => m.uso_cpu),
            borderColor: 'rgb(239, 68, 68)',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            tension: 0.4,
            yAxisID: 'y'
          },
          {
            label: 'RAM (MB)',
            data: datos.map(m => m.uso_ram_mb),
            borderColor: 'rgb(34, 197, 94)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            tension: 0.4,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top'
          },
          title: {
            display: true,
            text: 'Utilización de Recursos del Sistema'
          }
        },
        scales: {
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            beginAtZero: true,
            max: 100
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            beginAtZero: true,
            grid: {
              drawOnChartArea: false
            }
          }
        }
      }
    };

    this.destruirGrafico('recursos');
    this.chartRecursosInstance = new Chart(this.chartRecursos.nativeElement, config);
  }

  destruirGrafico(tipo: string): void {
    switch (tipo) {
      case 'metricasSemanticas':
        if (this.chartMetricasSemanticasInstance) {
          this.chartMetricasSemanticasInstance.destroy();
          this.chartMetricasSemanticasInstance = null;
        }
        break;
      case 'tiemposRendimiento':
        if (this.chartTiemposRendimientoInstance) {
          this.chartTiemposRendimientoInstance.destroy();
          this.chartTiemposRendimientoInstance = null;
        }
        break;
      case 'recursos':
        if (this.chartRecursosInstance) {
          this.chartRecursosInstance.destroy();
          this.chartRecursosInstance = null;
        }
        break;
    }
  }

  destruirGraficos(): void {
    this.destruirGrafico('metricasSemanticas');
    this.destruirGrafico('tiemposRendimiento');
    this.destruirGrafico('recursos');
  }

  // ==================== ACCIONES ====================

  cambiarSeccion(seccion: 'semanticas' | 'rendimiento'): void {
    this.seccionActiva = seccion;
    setTimeout(() => {
      this.crearGraficos();
    }, 100);
  }

  aplicarFiltros(): void {
    this.cargarDatos();
  }

  ejecutarPruebaControlada(pruebaId: number): void {
    this.ejecutandoPrueba = true;
    this.metricasService.ejecutarPruebaControlada(pruebaId).subscribe({
      next: (resultado) => {
        alert('Prueba ejecutada exitosamente');
        this.cargarMetricasSemanticas();
        this.ejecutandoPrueba = false;
      },
      error: (error) => {
        alert('Error ejecutando prueba: ' + (error.error?.error || error.message));
        this.ejecutandoPrueba = false;
      }
    });
  }

  ejecutarPruebaCarga(): void {
    if (this.nuevaPruebaCarga.consultas.length === 0 || !this.nuevaPruebaCarga.consultas[0]) {
      alert('Debe proporcionar al menos una consulta');
      return;
    }

    this.ejecutandoPrueba = true;
    this.metricasService.ejecutarPruebaCargaBusqueda(
      this.nuevaPruebaCarga.nivel_carga,
      this.nuevaPruebaCarga.consultas.filter(c => c.trim() !== ''),
      this.nuevaPruebaCarga.nombre_prueba || undefined
    ).subscribe({
      next: (resultado) => {
        alert('Prueba de carga ejecutada exitosamente');
        this.nuevaPruebaCarga = { nivel_carga: 1, consultas: [''], nombre_prueba: '' };
        this.cargarMetricasRendimiento();
        this.cargarPruebasCarga();
        this.ejecutandoPrueba = false;
      },
      error: (error) => {
        alert('Error ejecutando prueba: ' + (error.error?.error || error.message));
        this.ejecutandoPrueba = false;
      }
    });
  }

  agregarConsulta(): void {
    this.nuevaPruebaCarga.consultas.push('');
  }

  eliminarConsulta(index: number): void {
    this.nuevaPruebaCarga.consultas.splice(index, 1);
  }

  registrarEnvioManual(): void {
    if (!this.nuevoRegistroManual.hawb || this.nuevoRegistroManual.tiempo_registro_segundos <= 0) {
      alert('Debe completar todos los campos requeridos');
      return;
    }

    this.metricasService.registrarEnvioManual(
      this.nuevoRegistroManual.hawb,
      this.nuevoRegistroManual.tiempo_registro_segundos,
      this.nuevoRegistroManual.datos_envio,
      this.nuevoRegistroManual.notas
    ).subscribe({
      next: () => {
        alert('Registro manual guardado exitosamente');
        this.nuevoRegistroManual = { hawb: '', tiempo_registro_segundos: 0, datos_envio: null, notas: '' };
        this.cargarRegistrosManuales();
      },
      error: (error) => {
        alert('Error guardando registro: ' + (error.error?.error || error.message));
      }
    });
  }

  exportarCSV(tipo: 'semanticas' | 'rendimiento'): void {
    const fechaDesde = this.filtroFechaDesde || undefined;
    const fechaHasta = this.filtroFechaHasta || undefined;

    if (tipo === 'semanticas') {
      this.metricasService.exportarMetricasSemanticasCSV(fechaDesde, fechaHasta).subscribe({
        next: (blob) => {
          this.metricasService.descargarArchivo(blob, `metricas_semanticas_${new Date().toISOString().split('T')[0]}.csv`);
        },
        error: () => alert('Error exportando métricas semánticas')
      });
    } else {
      this.metricasService.exportarMetricasRendimientoCSV(fechaDesde, fechaHasta).subscribe({
        next: (blob) => {
          this.metricasService.descargarArchivo(blob, `metricas_rendimiento_${new Date().toISOString().split('T')[0]}.csv`);
        },
        error: () => alert('Error exportando métricas de rendimiento')
      });
    }
  }

  formatearFecha(fecha: string): string {
    return new Date(fecha).toLocaleString('es-ES');
  }

  formatearTiempo(ms: number): string {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  }
}

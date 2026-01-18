import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewInit, HostListener } from '@angular/core';
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
  @HostListener('click', ['$event'])
  onComponentClick(event: MouseEvent): void {
    // Permitir que los eventos del navbar se propaguen
    const target = event.target as HTMLElement;
    if (target.closest('.nav-menu, .nav-item, .dropdown-menu')) {
      // No hacer nada, dejar que el navbar maneje el evento
      return;
    }
  }
  // Estados de carga
  loading = true;
  loadingMetricasSemanticas = false;
  loadingMetricasRendimiento = false;
  ejecutandoPrueba = false;

  // Sección activa
  seccionActiva: 'semanticas' | 'rendimiento' | 'pruebas' = 'semanticas';
  
  // Pruebas de rendimiento completas
  ejecutandoPruebaCompleta = false;
  resultadosPruebaCompleta: any = null;
  iteracionesPrueba = 24;

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
  detallesProcesos: any[] = [];
  pruebasRendimientoCompletas: any[] = [];
  
  // Modal de detalle
  embeddingSeleccionado: any = null;
  pruebaSeleccionada: any = null;

  // Filtros
  filtroFechaDesde: string = '';
  filtroFechaHasta: string = '';
  filtroNivelCarga: number | null = null;

  // Gráficos
  @ViewChild('chartTiemposRendimiento') chartTiemposRendimiento!: ElementRef<HTMLCanvasElement>;
  @ViewChild('chartRecursos') chartRecursos!: ElementRef<HTMLCanvasElement>;
  @ViewChild('chartComparativoProcesos') chartComparativoProcesos!: ElementRef<HTMLCanvasElement>;
  
  chartTiemposRendimientoInstance: Chart | null = null;
  chartRecursosInstance: Chart | null = null;
  chartComparativoInstance: Chart | null = null;

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
      this.cargarDetallesProcesos(),
      this.cargarPruebasRendimientoCompletas()
    ]).finally(() => {
      this.loading = false;
      setTimeout(() => {
        this.crearGraficos();
      }, 200);
    });
  }
  
  cargarDetallesProcesos(): Promise<void> {
    return new Promise((resolve) => {
      this.metricasService.getDetallesProcesos().subscribe({
        next: (data) => {
          this.detallesProcesos = Array.isArray(data) ? data : [];
          console.log('Detalles de procesos cargados:', this.detallesProcesos.length);
          resolve();
        },
        error: (error) => {
          console.error('Error cargando detalles de procesos:', error);
          this.detallesProcesos = [];
          resolve();
        }
      });
    });
  }
  
  cargarPruebasRendimientoCompletas(): Promise<void> {
    return new Promise((resolve) => {
      this.metricasService.getPruebasRendimientoGuardadas().subscribe({
        next: (data) => {
          this.pruebasRendimientoCompletas = Array.isArray(data) ? data : [];
          console.log('Pruebas de rendimiento completas cargadas:', this.pruebasRendimientoCompletas.length);
          resolve();
        },
        error: (error) => {
          console.error('Error cargando pruebas de rendimiento completas:', error);
          this.pruebasRendimientoCompletas = [];
          resolve();
        }
      });
    });
  }

  cargarMetricasSemanticas(): Promise<void> {
    return new Promise((resolve) => {
      this.loadingMetricasSemanticas = true;
      this.metricasService.getMetricasSemanticas(
        this.filtroFechaDesde || undefined,
        this.filtroFechaHasta || undefined
      ).subscribe({
        next: (data) => {
          // Manejar datos paginados o array directo
          if (data && typeof data === 'object' && 'results' in data) {
            this.metricasSemanticas = Array.isArray(data.results) ? data.results : [];
          } else {
            this.metricasSemanticas = Array.isArray(data) ? data : [];
          }
          console.log('Métricas semánticas cargadas:', this.metricasSemanticas.length);
          this.metricasService.getEstadisticasSemanticas(
            this.filtroFechaDesde || undefined,
            this.filtroFechaHasta || undefined
          ).subscribe({
            next: (stats) => {
              this.estadisticasSemanticas = stats || {};
              this.loadingMetricasSemanticas = false;
              resolve();
            },
            error: (error) => {
              console.error('Error cargando estadísticas semánticas:', error);
              this.estadisticasSemanticas = {};
              this.loadingMetricasSemanticas = false;
              resolve();
            }
          });
        },
        error: (error) => {
          console.error('Error cargando métricas semánticas:', error);
          this.metricasSemanticas = [];
          this.estadisticasSemanticas = {};
          this.loadingMetricasSemanticas = false;
          resolve();
        }
      });
    });
  }

  cargarMetricasRendimiento(): Promise<void> {
    return new Promise((resolve) => {
      this.loadingMetricasRendimiento = true;
      this.metricasService.getMetricasRendimiento(
        undefined,
        this.filtroNivelCarga || undefined,
        this.filtroFechaDesde || undefined,
        this.filtroFechaHasta || undefined
      ).subscribe({
        next: (data) => {
          // Manejar datos paginados o array directo
          if (data && typeof data === 'object' && 'results' in data) {
            this.metricasRendimiento = Array.isArray(data.results) ? data.results : [];
          } else {
            this.metricasRendimiento = Array.isArray(data) ? data : [];
          }
          console.log('Métricas de rendimiento cargadas:', this.metricasRendimiento.length);
          this.metricasService.getEstadisticasRendimiento(
            undefined,
            this.filtroNivelCarga || undefined
          ).subscribe({
            next: (stats) => {
              this.estadisticasRendimiento = stats || {};
              this.loadingMetricasRendimiento = false;
              resolve();
            },
            error: (error) => {
              console.error('Error cargando estadísticas de rendimiento:', error);
              this.estadisticasRendimiento = {};
              this.loadingMetricasRendimiento = false;
              resolve();
            }
          });
        },
        error: (error) => {
          console.error('Error cargando métricas de rendimiento:', error);
          this.metricasRendimiento = [];
          this.estadisticasRendimiento = {};
          this.loadingMetricasRendimiento = false;
          resolve();
        }
      });
    });
  }

  cargarPruebasControladas(): Promise<void> {
    return new Promise((resolve) => {
      this.metricasService.getPruebasControladas(true).subscribe({
        next: (data) => {
          this.pruebasControladas = Array.isArray(data) ? data : [];
          resolve();
        },
        error: (error) => {
          console.error('Error cargando pruebas controladas:', error);
          this.pruebasControladas = [];
          resolve();
        }
      });
    });
  }

  cargarPruebasCarga(): Promise<void> {
    return new Promise((resolve) => {
      // Aplicar filtros si están configurados
      const tipoPrueba = undefined; // Puedes añadir filtro por tipo si es necesario
      const nivelCarga = this.filtroNivelCarga || undefined;
      const fechaDesde = this.filtroFechaDesde || undefined;
      const fechaHasta = this.filtroFechaHasta || undefined;
      
      this.metricasService.getPruebasCarga(tipoPrueba, nivelCarga, fechaDesde, fechaHasta).subscribe({
        next: (data) => {
          // Manejar datos paginados o array directo
          if (data && typeof data === 'object' && 'results' in data) {
            this.pruebasCarga = Array.isArray(data.results) ? data.results : [];
          } else {
            this.pruebasCarga = Array.isArray(data) ? data : [];
          }
          console.log('Pruebas de carga cargadas:', this.pruebasCarga.length);
          resolve();
        },
        error: (error) => {
          console.error('Error cargando pruebas de carga:', error);
          this.pruebasCarga = [];
          resolve();
        }
      });
    });
  }

  cargarRegistrosEmbedding(): Promise<void> {
    return new Promise((resolve) => {
      this.metricasService.getRegistrosEmbedding().subscribe({
        next: (data) => {
          // Manejar datos paginados o array directo
          if (data && typeof data === 'object' && 'results' in data) {
            this.registrosEmbedding = Array.isArray(data.results) ? data.results : [];
          } else {
            this.registrosEmbedding = Array.isArray(data) ? data : [];
          }
          console.log('Registros de embedding cargados:', this.registrosEmbedding.length);
          this.metricasService.getEstadisticasEmbedding().subscribe({
            next: (stats) => {
              this.estadisticasEmbedding = stats || {};
              resolve();
            },
            error: (error) => {
              console.error('Error cargando estadísticas de embedding:', error);
              this.estadisticasEmbedding = {};
              resolve();
            }
          });
        },
        error: (error) => {
          console.error('Error cargando registros de embedding:', error);
          this.registrosEmbedding = [];
          this.estadisticasEmbedding = {};
          resolve();
        }
          });
        });
  }

  

  // ==================== GRÁFICOS ====================

  crearGraficos(): void {
    // Solo crear gráficos de rendimiento
    if (this.seccionActiva === 'rendimiento') {
      this.crearGraficoTiemposRendimiento();
      this.crearGraficoRecursos();
      this.crearGraficoComparativoProcesos();
    }
  }
  
  crearGraficoComparativoProcesos(): void {
    if (!this.chartComparativoProcesos?.nativeElement) {
      console.log('Canvas de comparativo de procesos no disponible');
      return;
    }

    // Agrupar detalles por código de proceso
    const procesosPorCodigo: { [key: string]: any[] } = {};
    
    this.detallesProcesos.forEach(detalle => {
      if (!procesosPorCodigo[detalle.codigo_proceso]) {
        procesosPorCodigo[detalle.codigo_proceso] = [];
      }
      procesosPorCodigo[detalle.codigo_proceso].push(detalle);
    });

    // Calcular promedios por proceso
    const procesosOrdenados = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12', 'M13', 'M14'];
    const labels: string[] = [];
    const tiemposPromedio: number[] = [];
    const cpusPromedio: number[] = [];
    const ramsPromedio: number[] = [];
    const coloresTiempo: string[] = [];

    procesosOrdenados.forEach(codigo => {
      if (procesosPorCodigo[codigo] && procesosPorCodigo[codigo].length > 0) {
        const detalles = procesosPorCodigo[codigo];
        const ultimoDetalle = detalles[0]; // El más reciente
        
        labels.push(ultimoDetalle.nombre_proceso);
        tiemposPromedio.push(ultimoDetalle.tiempo_media);
        cpusPromedio.push(ultimoDetalle.cpu_media);
        ramsPromedio.push(ultimoDetalle.ram_media);
        
        // Color según categoría de tiempo
        const color = this.obtenerColorEstado(ultimoDetalle.categoria_tiempo);
        coloresTiempo.push(color);
      }
    });

    if (labels.length === 0) {
      console.log('No hay datos de procesos para el gráfico comparativo');
      return;
    }

    const config: ChartConfiguration = {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Tiempo Promedio (s)',
            data: tiemposPromedio,
            backgroundColor: coloresTiempo,
            borderColor: coloresTiempo,
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
            text: 'Comparativa de Tiempos por Proceso (M1-M14)'
          },
          tooltip: {
            callbacks: {
              afterLabel: (context) => {
                const index = context.dataIndex;
                return `CPU: ${cpusPromedio[index]?.toFixed(2)}%\nRAM: ${ramsPromedio[index]?.toFixed(2)} KB`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Tiempo (segundos)'
            }
          },
          x: {
            ticks: {
              autoSkip: false,
              maxRotation: 45,
              minRotation: 45
            }
          }
        }
      }
    };

    this.destruirGrafico('comparativo');
    this.chartComparativoInstance = new Chart(this.chartComparativoProcesos.nativeElement, config);
  }

  crearGraficoTiemposRendimiento(): void {
    if (!this.chartTiemposRendimiento?.nativeElement) {
      console.log('Canvas de tiempos de rendimiento no disponible');
      return;
    }

    const datos = (this.metricasRendimiento || []).slice(-30); // Últimas 30 métricas
    console.log('Creando gráfico de tiempos con', datos.length, 'métricas');
    
    if (datos.length === 0) {
      console.log('No hay datos para el gráfico de tiempos');
      const config: ChartConfiguration = {
        type: 'line',
        data: {
          labels: ['Sin datos'],
          datasets: []
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
              text: 'Tiempos de Respuesta del Sistema (Sin datos)'
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
      return;
    }
    
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
    if (!this.chartRecursos?.nativeElement) {
      console.log('Canvas de recursos no disponible');
      return;
    }

    const datos = (this.metricasRendimiento || []).slice(-30); // Últimas 30 métricas
    console.log('Creando gráfico de recursos con', datos.length, 'métricas');
    
    if (datos.length === 0) {
      console.log('No hay datos para el gráfico de recursos');
      const config: ChartConfiguration = {
        type: 'line',
        data: {
          labels: ['Sin datos'],
          datasets: []
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
              text: 'Utilización de Recursos del Sistema (Sin datos)'
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
      return;
    }
    
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
      case 'comparativo':
        if (this.chartComparativoInstance) {
          this.chartComparativoInstance.destroy();
          this.chartComparativoInstance = null;
        }
        break;
    }
  }

  destruirGraficos(): void {
    this.destruirGrafico('tiemposRendimiento');
    this.destruirGrafico('recursos');
    this.destruirGrafico('comparativo');
  }
  
  verDetallePrueba(prueba: any): void {
    this.pruebaSeleccionada = prueba;
  }
  
  cerrarDetallePrueba(): void {
    this.pruebaSeleccionada = null;
  }

  // ==================== ACCIONES ====================

  cambiarSeccion(seccion: 'semanticas' | 'rendimiento'): void {
    this.seccionActiva = seccion;
    setTimeout(() => {
      this.crearGraficos();
    }, 200);
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
    // Filtrar consultas vacías y verificar que haya al menos una
    const consultasValidas = this.nuevaPruebaCarga.consultas.filter(c => c && c.trim() !== '');
    
    if (consultasValidas.length === 0) {
      alert('Debe proporcionar al menos una consulta válida');
      return;
    }

    this.ejecutandoPrueba = true;
    console.log('Ejecutando prueba de carga:', {
      nivel_carga: this.nuevaPruebaCarga.nivel_carga,
      consultas: consultasValidas,
      nombre: this.nuevaPruebaCarga.nombre_prueba
    });

    this.metricasService.ejecutarPruebaCargaBusqueda(
      this.nuevaPruebaCarga.nivel_carga,
      consultasValidas,
      this.nuevaPruebaCarga.nombre_prueba || undefined
    ).subscribe({
      next: (resultado) => {
        console.log('Prueba de carga ejecutada exitosamente:', resultado);
        alert('Prueba de carga ejecutada exitosamente');
        this.nuevaPruebaCarga = { nivel_carga: 1, consultas: [''], nombre_prueba: '' };
        // Recargar datos después de un breve delay para asegurar que se guardaron
        setTimeout(() => {
          this.cargarMetricasRendimiento();
          this.cargarPruebasCarga();
          this.ejecutandoPrueba = false;
        }, 1500);
      },
      error: (error) => {
        console.error('Error ejecutando prueba de carga:', error);
        const mensajeError = error.error?.error || error.error?.mensaje || error.message || 'Error desconocido';
        alert('Error ejecutando prueba: ' + mensajeError);
        this.ejecutandoPrueba = false;
      }
    });
  }

  agregarConsulta(): void {
    if (!this.nuevaPruebaCarga.consultas) {
      this.nuevaPruebaCarga.consultas = [''];
    } else {
      this.nuevaPruebaCarga.consultas.push('');
    }
  }

  eliminarConsulta(index: number): void {
    this.nuevaPruebaCarga.consultas.splice(index, 1);
  }


  exportarCSV(tipo: 'semanticas' | 'rendimiento' | 'pruebas-carga'): void {
    const fechaDesde = this.filtroFechaDesde || undefined;
    const fechaHasta = this.filtroFechaHasta || undefined;

    if (tipo === 'semanticas') {
      this.metricasService.exportarMetricasSemanticasCSV(fechaDesde, fechaHasta).subscribe({
        next: (blob) => {
          this.metricasService.descargarArchivo(blob, `metricas_semanticas_${new Date().toISOString().split('T')[0]}.csv`);
        },
        error: () => alert('Error exportando métricas semánticas')
      });
    } else if (tipo === 'pruebas-carga') {
      this.metricasService.exportarPruebasCargaCSV().subscribe({
        next: (blob) => {
          this.metricasService.descargarArchivo(blob, `pruebas_carga_${new Date().toISOString().split('T')[0]}.csv`);
        },
        error: () => alert('Error exportando pruebas de carga')
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

  exportarCSVGraficoRecursos(): void {
    const datos = (this.metricasRendimiento || []).slice(-30);
    
    if (datos.length === 0) {
      alert('No hay datos para exportar');
      return;
    }

    // Crear contenido CSV
    let csvContent = 'Fecha,CPU (%),RAM (MB)\n';
    
    datos.forEach((m: any) => {
      const fecha = new Date(m.fecha_medicion);
      const fechaStr = fecha.toLocaleDateString() + ' ' + fecha.toLocaleTimeString();
      const cpu = m.uso_cpu?.toFixed(2) || '0.00';
      const ram = m.uso_ram_mb?.toFixed(2) || '0.00';
      csvContent += `${fechaStr},${cpu},${ram}\n`;
    });

    // Crear blob y descargar
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    this.metricasService.descargarArchivo(blob, `recursos_sistema_${new Date().toISOString().split('T')[0]}.csv`);
  }

  exportarCSVGraficoTiempos(): void {
    const datos = (this.metricasRendimiento || []).slice(-30);
    
    if (datos.length === 0) {
      alert('No hay datos para exportar');
      return;
    }

    // Crear contenido CSV
    let csvContent = 'Fecha,Tiempo Respuesta (ms),Proceso,Nivel Carga\n';
    
    datos.forEach((m: any) => {
      const fecha = new Date(m.fecha_medicion);
      const fechaStr = fecha.toLocaleDateString() + ' ' + fecha.toLocaleTimeString();
      const tiempo = m.tiempo_respuesta_ms || 0;
      const proceso = m.proceso || '-';
      const nivelCarga = m.nivel_carga || '-';
      csvContent += `${fechaStr},${tiempo},${proceso},${nivelCarga}\n`;
    });

    // Crear blob y descargar
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    this.metricasService.descargarArchivo(blob, `tiempos_respuesta_${new Date().toISOString().split('T')[0]}.csv`);
  }

  formatearFecha(fecha: string): string {
    return new Date(fecha).toLocaleString('es-ES');
  }

  formatearTiempo(ms: number): string {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  }

  ejecutarPruebaRendimientoCompleta(): void {
    if (this.ejecutandoPruebaCompleta) {
      return;
    }

    if (!confirm(`¿Desea ejecutar las pruebas de rendimiento completas con ${this.iteracionesPrueba} iteraciones?\n\nEsto puede tardar varios minutos.`)) {
      return;
    }

    this.ejecutandoPruebaCompleta = true;
    this.resultadosPruebaCompleta = null;

    console.log('Iniciando pruebas de rendimiento completas...');

    // Llamar al endpoint del backend para ejecutar pruebas de rendimiento
    this.metricasService.ejecutarPruebaRendimientoCompleta(this.iteracionesPrueba).subscribe({
      next: (resultado) => {
        console.log('Pruebas completadas:', resultado);
        this.resultadosPruebaCompleta = resultado;
        this.ejecutandoPruebaCompleta = false;
        
        // Mostrar notificación de éxito
        alert('✓ Pruebas de rendimiento completadas exitosamente');
        
        // Recargar métricas después de la prueba
        this.cargarMetricasRendimiento();
      },
      error: (error) => {
        console.error('Error ejecutando prueba completa:', error);
        const errorMsg = error.error?.error || error.error?.mensaje || error.message || 'Error desconocido';
        alert('Error ejecutando pruebas:\n\n' + errorMsg + '\n\nRevise la consola para más detalles.');
        this.ejecutandoPruebaCompleta = false;
      }
    });
  }
  
  cerrarResultadosPrueba(): void {
    this.resultadosPruebaCompleta = null;
  }

  obtenerEstadoISO25010(tiempo: number): string {
    if (tiempo <= 1.0) return 'Excelente';
    if (tiempo <= 3.0) return 'Aceptable';
    if (tiempo <= 10.0) return 'Deficiente';
    return 'Inaceptable';
  }

  obtenerColorEstado(estado: string): string {
    switch (estado) {
      case 'Excelente': return '#22c55e';
      case 'Aceptable': return '#3b82f6';
      case 'Deficiente': return '#f59e0b';
      case 'Inaceptable': return '#ef4444';
      default: return '#6b7280';
    }
  }

  verDetalleEmbedding(registro: any): void {
    this.embeddingSeleccionado = registro;
  }

  cerrarDetalleEmbedding(): void {
    this.embeddingSeleccionado = null;
  }
  
  obtenerProcesosOrdenados(resultadosJson: any): any[] {
    if (!resultadosJson) return [];
    
    const procesosOrdenados = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12', 'M13', 'M14'];
    const procesos: any[] = [];
    
    procesosOrdenados.forEach(codigo => {
      if (resultadosJson[codigo]) {
        const resultado = resultadosJson[codigo];
        const estadisticas = resultado.estadisticas || {};
        const evaluaciones = resultado.evaluaciones || {};
        
        procesos.push({
          codigo: codigo,
          tiempo_media: estadisticas.tiempo?.media,
          cpu_media: estadisticas.cpu?.media,
          ram_media: estadisticas.ram?.media,
          categoria_tiempo: evaluaciones.tiempo?.categoria || 'N/A',
          iteraciones_completadas: resultado.tiempos?.length || 0,
          total_errores: resultado.errores?.length || 0,
          error: resultado.error
        });
      }
    });
    
    return procesos;
  }

}

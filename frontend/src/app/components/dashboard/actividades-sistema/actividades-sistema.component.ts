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
  reporteComparativo: { filas: any[]; resumen: any } | null = null;
  loadingReporteComparativo = false;
  pruebasControladas: any[] = [];
  
  // Paginación para métricas semánticas
  paginaMetricasSemanticas = 1;
  totalPaginasMetricasSemanticas = 1;
  totalMetricasSemanticas = 0;
  elementosPorPaginaMetricasSemanticas = 10;
  
  // Datos de métricas de rendimiento (14 operaciones M1-M14)
  registrosEmbedding: any[] = [];
  estadisticasEmbedding: any = {};
  detallesProcesos: any[] = [];
  pruebasRendimientoCompletas: any[] = [];
  
  // Paginación para registros de embedding
  paginaRegistrosEmbedding = 1;
  totalPaginasRegistrosEmbedding = 1;
  totalRegistrosEmbedding = 0;
  elementosPorPaginaRegistrosEmbedding = 10;
  
  // Modal de detalle
  embeddingSeleccionado: any = null;
  pruebaSeleccionada: any = null;

  // Filtros
  filtroFechaDesde: string = '';
  filtroFechaHasta: string = '';

  // Gráficos (14 operaciones: tiempo, CPU, RAM)
  @ViewChild('chartComparativoProcesos') chartComparativoProcesos!: ElementRef<HTMLCanvasElement>;
  @ViewChild('chartCPUProcesos') chartCPUProcesos!: ElementRef<HTMLCanvasElement>;
  @ViewChild('chartRAMProcesos') chartRAMProcesos!: ElementRef<HTMLCanvasElement>;
  
  chartComparativoInstance: Chart | null = null;
  chartCPUProcesosInstance: Chart | null = null;
  chartRAMProcesosInstance: Chart | null = null;

  // Formularios
  nuevaPruebaControlada = {
    nombre: '',
    descripcion: '',
    consulta: '',
    resultados_relevantes: [] as number[]
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
    
    // Cargar datos de ambas secciones (sin pruebas de carga ni métricas de rendimiento antiguas)
    Promise.all([
      this.cargarMetricasSemanticas(),
      this.cargarReporteComparativo(),
      this.cargarPruebasControladas(),
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
        this.filtroFechaHasta || undefined,
        this.paginaMetricasSemanticas,
        this.elementosPorPaginaMetricasSemanticas
      ).subscribe({
        next: (data) => {
          // Manejar datos paginados
          if (data && typeof data === 'object' && 'results' in data) {
            this.metricasSemanticas = Array.isArray(data.results) ? data.results : [];
            this.totalMetricasSemanticas = data.count || 0;
            this.totalPaginasMetricasSemanticas = Math.ceil(this.totalMetricasSemanticas / this.elementosPorPaginaMetricasSemanticas);
          } else {
            this.metricasSemanticas = Array.isArray(data) ? data : [];
            this.totalMetricasSemanticas = this.metricasSemanticas.length;
            this.totalPaginasMetricasSemanticas = 1;
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

  cargarReporteComparativo(): Promise<void> {
    return new Promise((resolve) => {
      this.loadingReporteComparativo = true;
      this.metricasService.getReporteComparativo(
        this.filtroFechaDesde || undefined,
        this.filtroFechaHasta || undefined
      ).subscribe({
        next: (data) => {
          this.reporteComparativo = data || { filas: [], resumen: {} };
          this.loadingReporteComparativo = false;
          resolve();
        },
        error: (error) => {
          console.error('Error cargando reporte comparativo:', error);
          this.reporteComparativo = { filas: [], resumen: {} };
          this.loadingReporteComparativo = false;
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

  cargarRegistrosEmbedding(): Promise<void> {
    return new Promise((resolve) => {
      this.metricasService.getRegistrosEmbedding(
        undefined,
        undefined,
        this.paginaRegistrosEmbedding,
        this.elementosPorPaginaRegistrosEmbedding
      ).subscribe({
        next: (data) => {
          // Manejar datos paginados
          if (data && typeof data === 'object' && 'results' in data) {
            this.registrosEmbedding = Array.isArray(data.results) ? data.results : [];
            this.totalRegistrosEmbedding = data.count || 0;
            this.totalPaginasRegistrosEmbedding = Math.ceil(this.totalRegistrosEmbedding / this.elementosPorPaginaRegistrosEmbedding);
          } else {
            this.registrosEmbedding = Array.isArray(data) ? data : [];
            this.totalRegistrosEmbedding = this.registrosEmbedding.length;
            this.totalPaginasRegistrosEmbedding = 1;
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
  
  cambiarPaginaMetricasSemanticas(pagina: number): void {
    if (pagina >= 1 && pagina <= this.totalPaginasMetricasSemanticas) {
      this.paginaMetricasSemanticas = pagina;
      this.cargarMetricasSemanticas();
    }
  }
  
  cambiarPaginaRegistrosEmbedding(pagina: number): void {
    if (pagina >= 1 && pagina <= this.totalPaginasRegistrosEmbedding) {
      this.paginaRegistrosEmbedding = pagina;
      this.cargarRegistrosEmbedding();
    }
  }
  
  cambiarElementosPorPaginaMetricasSemanticas(elementos: number): void {
    this.elementosPorPaginaMetricasSemanticas = elementos;
    this.paginaMetricasSemanticas = 1;
    this.cargarMetricasSemanticas();
  }
  
  cambiarElementosPorPaginaRegistrosEmbedding(elementos: number): void {
    this.elementosPorPaginaRegistrosEmbedding = elementos;
    this.paginaRegistrosEmbedding = 1;
    this.cargarRegistrosEmbedding();
  }

  

  // ==================== GRÁFICOS ====================

  crearGraficos(): void {
    if (this.seccionActiva === 'rendimiento') {
      // Dar un pequeño delay para asegurar que el DOM esté listo
      setTimeout(() => {
        this.crearGraficoComparativoProcesos();
        this.crearGraficoCPUProcesos();
        this.crearGraficoRAMProcesos();
      }, 100);
    }
  }

  /** Estadísticas de rendimiento calculadas desde detalles de las 14 operaciones (M1-M14). */
  get estadisticasRendimientoDesdeProcesos(): {
    tiempo_promedio_ms: number;
    cpu_promedio: number;
    ram_promedio_mb: number;
    total_exitosos: number;
  } {
    const procesosOrdenados = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12', 'M13', 'M14'];
    const porCodigo: { [key: string]: any[] } = {};
    this.detallesProcesos.forEach(d => {
      if (!porCodigo[d.codigo_proceso]) porCodigo[d.codigo_proceso] = [];
      porCodigo[d.codigo_proceso].push(d);
    });
    let sumaTiempo = 0, sumaCpu = 0, sumaRam = 0, count = 0;
    procesosOrdenados.forEach(codigo => {
      const arr = porCodigo[codigo];
      if (arr?.length) {
        const ultimo = arr[0];
        sumaTiempo += (ultimo.tiempo_media || 0) * 1000;
        sumaCpu += ultimo.cpu_media || 0;
        sumaRam += (ultimo.ram_media || 0) / 1024;
        count++;
      }
    });
    return {
      tiempo_promedio_ms: count ? sumaTiempo / count : 0,
      cpu_promedio: count ? sumaCpu / count : 0,
      ram_promedio_mb: count ? sumaRam / count : 0,
      total_exitosos: count
    };
  }
  
  crearGraficoComparativoProcesos(): void {
    if (!this.chartComparativoProcesos?.nativeElement) return;
    const { labels, tiempos, cpus, rams, coloresTiempo } = this.obtenerDatosGraficoProcesos();

    const config: ChartConfiguration = {
      type: 'bar',
      data: {
        labels: labels.length ? labels : ['Sin datos'],
        datasets: [{
          label: 'Tiempo (s)',
          data: labels.length ? tiempos : [],
          backgroundColor: labels.length ? coloresTiempo : '#94a3b8',
          borderColor: labels.length ? coloresTiempo : '#64748b',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true, position: 'top' },
          title: { display: true, text: labels.length ? 'Tiempo de respuesta por proceso (M1-M14)' : 'Sin datos — ejecute una prueba' },
          tooltip: {
            callbacks: labels.length ? {
              afterLabel: (ctx: any) => {
                const i = ctx.dataIndex;
                return `CPU: ${cpus[i]?.toFixed(2)}%\nRAM: ${rams[i]?.toFixed(2)} KB`;
              }
            } : undefined
          }
        },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Tiempo (s)' } },
          x: { ticks: { autoSkip: false, maxRotation: 45, minRotation: 45 } }
        }
      }
    };
    this.destruirGrafico('comparativo');
    this.chartComparativoInstance = new Chart(this.chartComparativoProcesos.nativeElement, config);
  }

  /** Construye labels y datos por proceso (M1-M14) desde detallesProcesos. */
  private obtenerDatosGraficoProcesos(): { labels: string[]; tiempos: number[]; cpus: number[]; rams: number[]; coloresTiempo: string[] } {
    const procesosPorCodigo: { [key: string]: any[] } = {};
    this.detallesProcesos.forEach(d => {
      if (!procesosPorCodigo[d.codigo_proceso]) procesosPorCodigo[d.codigo_proceso] = [];
      procesosPorCodigo[d.codigo_proceso].push(d);
    });
    const procesosOrdenados = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12', 'M13', 'M14'];
    const labels: string[] = [];
    const tiempos: number[] = [];
    const cpus: number[] = [];
    const rams: number[] = [];
    const coloresTiempo: string[] = [];
    procesosOrdenados.forEach(codigo => {
      const arr = procesosPorCodigo[codigo];
      if (arr?.length) {
        // Ordenar por fecha de medición descendente y tomar el más reciente
        arr.sort((a, b) => {
          const fechaA = new Date(a.fecha_medicion || 0).getTime();
          const fechaB = new Date(b.fecha_medicion || 0).getTime();
          return fechaB - fechaA;
        });
        const ultimo = arr[0];
        labels.push(ultimo.nombre_proceso || codigo);
        tiempos.push(ultimo.tiempo_media || 0);
        cpus.push(ultimo.cpu_media || 0);
        rams.push(ultimo.ram_media || 0);
        coloresTiempo.push(this.obtenerColorEstado(ultimo.categoria_tiempo || 'N/A'));
      }
    });
    return { labels, tiempos, cpus, rams, coloresTiempo };
  }

  crearGraficoCPUProcesos(): void {
    if (!this.chartCPUProcesos?.nativeElement) return;
    const { labels, cpus } = this.obtenerDatosGraficoProcesos();
    const config: ChartConfiguration = {
      type: 'bar',
      data: {
        labels: labels.length ? labels : ['Sin datos'],
        datasets: [{
          label: 'CPU (%)',
          data: labels.length ? cpus : [],
          backgroundColor: '#ef4444',
          borderColor: '#dc2626',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true, position: 'top' },
          title: { display: true, text: 'Uso de CPU por proceso (M1-M14)' }
        },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'CPU (%)' } },
          x: { ticks: { autoSkip: false, maxRotation: 45, minRotation: 45 } }
        }
      }
    };
    this.destruirGrafico('cpuProcesos');
    this.chartCPUProcesosInstance = new Chart(this.chartCPUProcesos.nativeElement, config);
  }

  crearGraficoRAMProcesos(): void {
    if (!this.chartRAMProcesos?.nativeElement) return;
    const { labels, rams } = this.obtenerDatosGraficoProcesos();
    const config: ChartConfiguration = {
      type: 'bar',
      data: {
        labels: labels.length ? labels : ['Sin datos'],
        datasets: [{
          label: 'RAM (KB)',
          data: labels.length ? rams : [],
          backgroundColor: '#22c55e',
          borderColor: '#16a34a',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true, position: 'top' },
          title: { display: true, text: 'Uso de RAM por proceso (M1-M14)' }
        },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'RAM (KB)' } },
          x: { ticks: { autoSkip: false, maxRotation: 45, minRotation: 45 } }
        }
      }
    };
    this.destruirGrafico('ramProcesos');
    this.chartRAMProcesosInstance = new Chart(this.chartRAMProcesos.nativeElement, config);
  }

  destruirGrafico(tipo: string): void {
    switch (tipo) {
      case 'comparativo':
        if (this.chartComparativoInstance) {
          this.chartComparativoInstance.destroy();
          this.chartComparativoInstance = null;
        }
        break;
      case 'cpuProcesos':
        if (this.chartCPUProcesosInstance) {
          this.chartCPUProcesosInstance.destroy();
          this.chartCPUProcesosInstance = null;
        }
        break;
      case 'ramProcesos':
        if (this.chartRAMProcesosInstance) {
          this.chartRAMProcesosInstance.destroy();
          this.chartRAMProcesosInstance = null;
        }
        break;
    }
  }

  destruirGraficos(): void {
    this.destruirGrafico('comparativo');
    this.destruirGrafico('cpuProcesos');
    this.destruirGrafico('ramProcesos');
  }
  
  verDetallePrueba(prueba: any): void {
    // Cargar el detalle completo de la prueba desde el backend para evitar problemas con datos grandes
    if (prueba && prueba.id) {
      this.metricasService.getDetallePruebaRendimiento(prueba.id).subscribe({
        next: (detalle) => {
          this.pruebaSeleccionada = detalle;
        },
        error: (error) => {
          console.error('Error cargando detalle de prueba:', error);
          // Si falla, usar los datos básicos disponibles
          this.pruebaSeleccionada = prueba;
          alert('Error cargando detalles completos de la prueba. Se mostrarán datos básicos.');
        }
      });
    } else {
      this.pruebaSeleccionada = prueba;
    }
  }
  
  cerrarDetallePrueba(): void {
    this.pruebaSeleccionada = null;
  }

  // ==================== ACCIONES ====================

  cambiarSeccion(seccion: 'semanticas' | 'rendimiento'): void {
    this.seccionActiva = seccion;
    // Dar tiempo a que el DOM de la pestaña se renderice antes de crear los gráficos
    setTimeout(() => {
      this.crearGraficos();
    }, 400);
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
        this.cargarReporteComparativo();
        this.ejecutandoPrueba = false;
      },
      error: (error) => {
        alert('Error ejecutando prueba: ' + (error.error?.error || error.message));
        this.ejecutandoPrueba = false;
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

  /** Exporta los datos de las 14 operaciones (M1-M14) a CSV. */
  exportarCSVProcesos14(): void {
    const { labels, tiempos, cpus, rams } = this.obtenerDatosGraficoProcesos();
    if (!labels.length) {
      alert('No hay datos de procesos. Ejecute una prueba de rendimiento completa primero.');
      return;
    }
    let csvContent = 'Proceso,Tiempo (s),CPU (%),RAM (KB)\n';
    labels.forEach((nombre, i) => {
      csvContent += `"${nombre}",${(tiempos[i] ?? 0).toFixed(4)},${(cpus[i] ?? 0).toFixed(2)},${(rams[i] ?? 0).toFixed(2)}\n`;
    });
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    this.metricasService.descargarArchivo(blob, `procesos_14_operaciones_${new Date().toISOString().split('T')[0]}.csv`);
  }

  formatearFecha(fecha: string): string {
    return new Date(fecha).toLocaleString('es-ES');
  }

  /** Fecha actual formateada para usar en el template (evita new Date() en la plantilla). */
  get fechaActualFormateada(): string {
    return new Date().toLocaleString('es-ES');
  }

  /** Fin del rango mostrado en paginación de registros de embedding (evita Math en template). */
  get finRangoRegistrosEmbedding(): number {
    return Math.min(
      this.paginaRegistrosEmbedding * this.elementosPorPaginaRegistrosEmbedding,
      this.totalRegistrosEmbedding
    );
  }

  /** Inicio del rango mostrado en paginación de registros de embedding. */
  get inicioRangoRegistrosEmbedding(): number {
    if (this.totalRegistrosEmbedding === 0) return 0;
    return (this.paginaRegistrosEmbedding - 1) * this.elementosPorPaginaRegistrosEmbedding + 1;
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
        
        // Formatear resultados con fecha de ejecución correcta
        const fechaEjecucion = resultado.resultados?.fecha_ejecucion || resultado.fecha_ejecucion || new Date().toISOString();
        
        this.resultadosPruebaCompleta = {
          ...resultado,
          fecha_ejecucion: fechaEjecucion,
          mensaje: resultado.mensaje || 'Pruebas de rendimiento completas ejecutadas exitosamente',
          iteraciones: this.iteracionesPrueba
        };
        
        this.ejecutandoPruebaCompleta = false;
        
        // Refrescar historial y métricas de forma explícita (varias veces por si el backend tarda en guardar)
        this.cargarPruebasRendimientoCompletas();
        this.cargarDetallesProcesos();
        setTimeout(() => {
          this.cargarPruebasRendimientoCompletas();
          this.cargarDetallesProcesos().then(() => {
            this.destruirGraficos();
            setTimeout(() => this.crearGraficos(), 300);
          });
        }, 1500);
        setTimeout(() => this.cargarPruebasRendimientoCompletas(), 3000);
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

  /** Porcentaje para la barra de rendimiento (0–100): 3000 ms = 100%. */
  getGaugeWidth(ms: number): number {
    if (ms == null || ms <= 0) return 0;
    return Math.min(100, (ms / 3000) * 100);
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

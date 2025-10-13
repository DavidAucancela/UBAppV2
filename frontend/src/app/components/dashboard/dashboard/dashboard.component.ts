import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { ApiService } from '../../../services/api.service';
import { Usuario, Roles } from '../../../models/usuario';
import { ESTADOS_LABELS, EstadosEnvio } from '../../../models/envio';
import { Chart, ChartConfiguration, ChartType, registerables } from 'chart.js';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import * as XLSX from 'xlsx';

// Registrar todos los componentes de Chart.js
Chart.register(...registerables);

interface FilterOptions {
  periodo: 'dia' | 'semana' | 'mes' | 'año' | 'todo';
  tipoGrafico: 'linea' | 'barras' | 'dona' | 'radar' | 'area';
  metrica: 'envios' | 'productos' | 'usuarios' | 'ingresos';
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit, OnDestroy, AfterViewInit {
  // Referencias a los canvas de gráficos
  @ViewChild('enviosChart') enviosChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('productosChart') productosChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('estadosChart') estadosChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('tendenciasChart') tendenciasChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('categoriasChart') categoriasChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('kpiChart') kpiChartRef!: ElementRef<HTMLCanvasElement>;

  // Instancias de gráficos
  enviosChart: Chart | null = null;
  productosChart: Chart | null = null;
  estadosChart: Chart | null = null;
  tendenciasChart: Chart | null = null;
  categoriasChart: Chart | null = null;
  kpiChart: Chart | null = null;

  // Estado
  currentUser: Usuario | null = null;
  stats: any = {};
  loading = true;
  exportingData = false;

  // Exponer Math y Date para usar en el template
  Math = Math;
  Date = Date;

  // Control de pantalla completa
  fullscreenChart: string | null = null;

  // Datos para gráficos
  enviosData: any[] = [];
  productosData: any[] = [];
  usuariosData: any[] = [];
  
  // Control de carga de datos
  private datosEnviosCargados = false;
  private datosProductosCargados = false;
  private datosUsuariosCargados = false;

  // Filtros
  filters: FilterOptions = {
    periodo: 'mes',
    tipoGrafico: 'barras',
    metrica: 'envios'
  };

  // KPIs
  kpis = {
    totalEnvios: 0,
    totalProductos: 0,
    enviosPendientes: 0,
    tasaCrecimiento: 0,
    valorPromedio: 0,
    satisfaccionCliente: 0
  };

  // Opciones de filtros
  periodos = [
    { value: 'dia', label: 'Último día' },
    { value: 'semana', label: 'Última semana' },
    { value: 'mes', label: 'Último mes' },
    { value: 'año', label: 'Último año' },
    { value: 'todo', label: 'Todo el tiempo' }
  ];

  tiposGrafico = [
    { value: 'linea', label: 'Línea', icon: 'fa-chart-line' },
    { value: 'barras', label: 'Barras', icon: 'fa-chart-bar' },
    { value: 'dona', label: 'Dona', icon: 'fa-chart-pie' },
    { value: 'radar', label: 'Radar', icon: 'fa-chart-area' },
    { value: 'area', label: 'Área', icon: 'fa-chart-area' }
  ];

  metricas = [
    { value: 'envios', label: 'Envíos', icon: 'fa-truck' },
    { value: 'productos', label: 'Productos', icon: 'fa-box' },
    { value: 'usuarios', label: 'Usuarios', icon: 'fa-users' },
    { value: 'ingresos', label: 'Ingresos', icon: 'fa-dollar-sign' }
  ];

  constructor(
    private authService: AuthService,
    private apiService: ApiService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.loadStats();
    this.loadAllData();
  }

  ngAfterViewInit(): void {
    // Los gráficos se actualizarán automáticamente cuando los datos estén cargados
    // mediante el método checkAndUpdateCharts()
  }

  ngOnDestroy(): void {
    this.destroyAllCharts();
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

  loadAllData(): void {
    // Cargar envíos
    this.apiService.getEnvios().subscribe({
      next: (envios) => {
        this.enviosData = Array.isArray(envios) ? envios : (envios as any).results || [];
        this.datosEnviosCargados = true;
        this.calculateKPIs();
        this.checkAndUpdateCharts();
      },
      error: (error) => {
        console.error('Error cargando envíos:', error);
        this.datosEnviosCargados = true;
        this.checkAndUpdateCharts();
      }
    });

    // Cargar productos
    this.apiService.getProductos().subscribe({
      next: (productos) => {
        this.productosData = Array.isArray(productos) ? productos : (productos as any).results || [];
        this.datosProductosCargados = true;
        this.calculateKPIs();
        this.checkAndUpdateCharts();
      },
      error: (error) => {
        console.error('Error cargando productos:', error);
        this.datosProductosCargados = true;
        this.checkAndUpdateCharts();
      }
    });

    // Cargar usuarios (si tiene permisos)
    if (this.authService.canManageUsers()) {
      this.apiService.getUsuarios().subscribe({
        next: (usuarios) => {
          this.usuariosData = Array.isArray(usuarios) ? usuarios : (usuarios as any).results || [];
          this.datosUsuariosCargados = true;
          this.calculateKPIs();
          this.checkAndUpdateCharts();
        },
        error: (error) => {
          console.error('Error cargando usuarios:', error);
          this.datosUsuariosCargados = true;
          this.checkAndUpdateCharts();
        }
      });
    } else {
      // Si no tiene permisos, marcar como cargado
      this.datosUsuariosCargados = true;
    }
  }

  private checkAndUpdateCharts(): void {
    // Verificar si todos los datos necesarios están cargados
    if (this.datosEnviosCargados && this.datosProductosCargados && this.datosUsuariosCargados) {
      console.log('All data loaded, preparing to update charts...');
      // Esperar a que los ViewChild estén listos
      setTimeout(() => {
        this.updateCharts();
      }, 300);
    }
  }

  calculateKPIs(): void {
    // Total de envíos
    this.kpis.totalEnvios = this.enviosData.length;

    // Total de productos
    this.kpis.totalProductos = this.productosData.length;

    // Envíos pendientes
    this.kpis.enviosPendientes = this.enviosData.filter(e => 
      e.estado === 'pendiente' || e.estado === 'Pendiente'
    ).length;

    // Tasa de crecimiento (simulada basada en fechas)
    const enviosRecientes = this.filterByPeriod(this.enviosData, 'mes');
    const enviosAnteriores = this.enviosData.length - enviosRecientes.length;
    this.kpis.tasaCrecimiento = enviosAnteriores > 0 
      ? ((enviosRecientes.length - enviosAnteriores) / enviosAnteriores) * 100 
      : 0;

    // Valor promedio (simulado)
    this.kpis.valorPromedio = this.enviosData.length > 0 
      ? Math.round((Math.random() * 500 + 100) * 100) / 100 
      : 0;

    // Satisfacción del cliente (simulado)
    this.kpis.satisfaccionCliente = Math.round((Math.random() * 20 + 80) * 10) / 10;
  }

  filterByPeriod(data: any[], periodo: string): any[] {
    const now = new Date();
    let startDate = new Date();

    switch (periodo) {
      case 'dia':
        startDate.setDate(now.getDate() - 1);
        break;
      case 'semana':
        startDate.setDate(now.getDate() - 7);
        break;
      case 'mes':
        startDate.setMonth(now.getMonth() - 1);
        break;
      case 'año':
        startDate.setFullYear(now.getFullYear() - 1);
        break;
      case 'todo':
        return data;
    }

    return data.filter(item => {
      const itemDate = new Date(item.fecha_creacion || item.created_at || now);
      return itemDate >= startDate;
    });
  }

  onFilterChange(): void {
    this.updateCharts();
  }

  updateCharts(): void {
    // Verificar que todos los canvas estén disponibles
    if (!this.enviosChartRef?.nativeElement || 
        !this.productosChartRef?.nativeElement ||
        !this.estadosChartRef?.nativeElement ||
        !this.tendenciasChartRef?.nativeElement ||
        !this.categoriasChartRef?.nativeElement ||
        !this.kpiChartRef?.nativeElement) {
      console.log('Charts canvas not ready yet');
      return;
    }

    this.destroyAllCharts();

    setTimeout(() => {
      try {
        this.createEnviosChart();
        this.createProductosChart();
        this.createEstadosChart();
        this.createTendenciasChart();
        this.createCategoriasChart();
        this.createKPIChart();
        console.log('Charts created successfully');
      } catch (error) {
        console.error('Error creating charts:', error);
      }
    }, 100);
  }

  destroyAllCharts(): void {
    if (this.enviosChart) {
      this.enviosChart.destroy();
      this.enviosChart = null;
    }
    if (this.productosChart) {
      this.productosChart.destroy();
      this.productosChart = null;
    }
    if (this.estadosChart) {
      this.estadosChart.destroy();
      this.estadosChart = null;
    }
    if (this.tendenciasChart) {
      this.tendenciasChart.destroy();
      this.tendenciasChart = null;
    }
    if (this.categoriasChart) {
      this.categoriasChart.destroy();
      this.categoriasChart = null;
    }
    if (this.kpiChart) {
      this.kpiChart.destroy();
      this.kpiChart = null;
    }
  }

  createEnviosChart(): void {
    if (!this.enviosChartRef?.nativeElement) return;

    const filteredData = this.filterByPeriod(this.enviosData, this.filters.periodo);
    const groupedData = this.groupByDate(filteredData);

    const config: ChartConfiguration = {
      type: this.getChartType(this.filters.tipoGrafico) as ChartType,
      data: {
        labels: groupedData.labels,
        datasets: [{
          label: 'Envíos',
          data: groupedData.values,
          backgroundColor: this.filters.tipoGrafico === 'area' || this.filters.tipoGrafico === 'linea'
            ? 'rgba(102, 126, 234, 0.2)'
            : 'rgba(102, 126, 234, 0.8)',
          borderColor: 'rgba(102, 126, 234, 1)',
          borderWidth: 2,
          fill: this.filters.tipoGrafico === 'area',
          tension: 0.4
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
            text: 'Evolución de Envíos'
          }
        },
        scales: this.filters.tipoGrafico !== 'dona' && this.filters.tipoGrafico !== 'radar' ? {
          y: {
            beginAtZero: true
          }
        } : undefined
      }
    };

    this.enviosChart = new Chart(this.enviosChartRef.nativeElement, config);
  }

  createProductosChart(): void {
    if (!this.productosChartRef?.nativeElement) return;

    const categorias = this.groupByCategory(this.productosData);

    const config: ChartConfiguration = {
      type: 'bar',
      data: {
        labels: categorias.labels,
        datasets: [{
          label: 'Productos por categoría',
          data: categorias.values,
          backgroundColor: [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(237, 100, 166, 0.8)',
            'rgba(255, 154, 158, 0.8)',
            'rgba(250, 208, 196, 0.8)'
          ],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          title: {
            display: true,
            text: 'Distribución de Productos por Categoría'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    };

    this.productosChart = new Chart(this.productosChartRef.nativeElement, config);
  }

  createEstadosChart(): void {
    if (!this.estadosChartRef?.nativeElement) return;

    const estados = this.groupByEstado(this.enviosData);

    const config: ChartConfiguration = {
      type: 'doughnut',
      data: {
        labels: estados.labels,
        datasets: [{
          data: estados.values,
          backgroundColor: [
            'rgba(16, 185, 129, 0.8)',  // Verde - Entregado
            'rgba(245, 158, 11, 0.8)',   // Naranja - En tránsito
            'rgba(239, 68, 68, 0.8)',    // Rojo - Pendiente
            'rgba(156, 163, 175, 0.8)'   // Gris - Cancelado
          ],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'bottom'
          },
          title: {
            display: true,
            text: 'Distribución por Estado'
          }
        }
      }
    };

    this.estadosChart = new Chart(this.estadosChartRef.nativeElement, config);
  }

  createTendenciasChart(): void {
    if (!this.tendenciasChartRef?.nativeElement) return;

    const tendencias = this.calculateTrends();

    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: tendencias.labels,
        datasets: [
          {
            label: 'Envíos reales',
            data: tendencias.real,
            borderColor: 'rgba(102, 126, 234, 1)',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          },
          {
            label: 'Tendencia proyectada',
            data: tendencias.proyectada,
            borderColor: 'rgba(239, 68, 68, 1)',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            borderWidth: 2,
            borderDash: [5, 5],
            fill: false,
            tension: 0.4
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
            text: 'Análisis de Tendencias y Proyección'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    };

    this.tendenciasChart = new Chart(this.tendenciasChartRef.nativeElement, config);
  }

  createCategoriasChart(): void {
    if (!this.categoriasChartRef?.nativeElement) return;

    const metricas = this.calculateMetricsRadar();

    const config: ChartConfiguration = {
      type: 'radar',
      data: {
        labels: metricas.labels,
        datasets: [{
          label: 'Rendimiento',
          data: metricas.values,
          backgroundColor: 'rgba(102, 126, 234, 0.2)',
          borderColor: 'rgba(102, 126, 234, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(102, 126, 234, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(102, 126, 234, 1)'
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
            text: 'Análisis Multidimensional de Rendimiento'
          }
        },
        scales: {
          r: {
            beginAtZero: true,
            max: 100
          }
        }
      }
    };

    this.categoriasChart = new Chart(this.categoriasChartRef.nativeElement, config);
  }

  createKPIChart(): void {
    if (!this.kpiChartRef?.nativeElement) return;

    const kpiData = [
      this.kpis.tasaCrecimiento > 0 ? this.kpis.tasaCrecimiento : 0,
      this.kpis.satisfaccionCliente,
      (this.kpis.totalEnvios / Math.max(this.kpis.totalEnvios + this.kpis.enviosPendientes, 1)) * 100,
      Math.min((this.kpis.valorPromedio / 10), 100)
    ];

    const config: ChartConfiguration = {
      type: 'bar',
      data: {
        labels: ['Crecimiento', 'Satisfacción', 'Eficiencia', 'Valor'],
        datasets: [{
          label: 'KPIs (%)',
          data: kpiData,
          backgroundColor: [
            'rgba(16, 185, 129, 0.8)',
            'rgba(102, 126, 234, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(118, 75, 162, 0.8)'
          ],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: {
            display: false
          },
          title: {
            display: true,
            text: 'Indicadores Clave de Rendimiento'
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            max: 100
          }
        }
      }
    };

    this.kpiChart = new Chart(this.kpiChartRef.nativeElement, config);
  }

  // Funciones auxiliares de gráficos
  getChartType(tipo: string): string {
    const map: Record<string, string> = {
      'linea': 'line',
      'barras': 'bar',
      'dona': 'doughnut',
      'radar': 'radar',
      'area': 'line'
    };
    return map[tipo] || 'bar';
  }

  groupByDate(data: any[]): { labels: string[], values: number[] } {
    const grouped: Record<string, number> = {};

    data.forEach(item => {
      const date = new Date(item.fecha_creacion || item.created_at || new Date());
      let key: string;

      switch (this.filters.periodo) {
        case 'dia':
          key = date.toLocaleTimeString('es-ES', { hour: '2-digit' });
          break;
        case 'semana':
          key = date.toLocaleDateString('es-ES', { weekday: 'short' });
          break;
        case 'mes':
        case 'año':
          key = date.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' });
          break;
        default:
          key = date.toLocaleDateString('es-ES', { month: 'short', year: '2-digit' });
      }

      grouped[key] = (grouped[key] || 0) + 1;
    });

    // Si no hay datos, devolver datos de ejemplo para evitar gráficos vacíos
    if (Object.keys(grouped).length === 0) {
      return {
        labels: ['Sin datos'],
        values: [0]
      };
    }

    return {
      labels: Object.keys(grouped),
      values: Object.values(grouped)
    };
  }

  groupByCategory(data: any[]): { labels: string[], values: number[] } {
    const grouped: Record<string, number> = {};

    data.forEach(item => {
      const categoria = item.categoria || item.category || 'Sin categoría';
      grouped[categoria] = (grouped[categoria] || 0) + 1;
    });

    // Si no hay datos, devolver datos de ejemplo
    if (Object.keys(grouped).length === 0) {
      return {
        labels: ['Sin categoría'],
        values: [0]
      };
    }

    return {
      labels: Object.keys(grouped),
      values: Object.values(grouped)
    };
  }

  groupByEstado(data: any[]): { labels: string[], values: number[] } {
    const grouped: Record<string, number> = {
      'Entregado': 0,
      'En tránsito': 0,
      'Pendiente': 0,
      'Cancelado': 0
    };

    data.forEach(item => {
      const estado = item.estado || 'Pendiente';
      const normalized = estado.toLowerCase().replace(/_/g, ' ');

      if (normalized.includes('entregado')) {
        grouped['Entregado']++;
      } else if (normalized.includes('transito')) {
        grouped['En tránsito']++;
      } else if (normalized.includes('cancelado')) {
        grouped['Cancelado']++;
      } else {
        grouped['Pendiente']++;
      }
    });

    return {
      labels: Object.keys(grouped),
      values: Object.values(grouped)
    };
  }

  calculateTrends(): { labels: string[], real: number[], proyectada: number[] } {
    const filteredData = this.filterByPeriod(this.enviosData, this.filters.periodo);
    const grouped = this.groupByDate(filteredData);

    // Calcular proyección simple usando regresión lineal básica
    const n = grouped.values.length;
    const proyectada = [...grouped.values];

    if (n > 2) {
      const sumX = (n * (n - 1)) / 2;
      const sumY = grouped.values.reduce((a, b) => a + b, 0);
      const sumXY = grouped.values.reduce((sum, y, i) => sum + i * y, 0);
      const sumX2 = (n * (n - 1) * (2 * n - 1)) / 6;

      const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
      const intercept = (sumY - slope * sumX) / n;

      // Agregar 3 puntos de proyección
      for (let i = n; i < n + 3; i++) {
        proyectada.push(Math.max(0, Math.round(slope * i + intercept)));
      }
    }

    const labels = [...grouped.labels, 'Proyección +1', 'Proyección +2', 'Proyección +3'];

    return {
      labels,
      real: [...grouped.values, ...Array(3).fill(null)],
      proyectada: proyectada
    };
  }

  calculateMetricsRadar(): { labels: string[], values: number[] } {
    const entregados = this.enviosData.filter(e => 
      (e.estado || '').toLowerCase().includes('entregado')
    ).length;
    const total = this.enviosData.length || 1;

    return {
      labels: ['Puntualidad', 'Calidad', 'Eficiencia', 'Volumen', 'Satisfacción', 'Rentabilidad'],
      values: [
        Math.round((entregados / total) * 100),
        Math.round(Math.random() * 30 + 70),
        Math.round(((total - this.kpis.enviosPendientes) / total) * 100),
        Math.min((total / 50) * 100, 100),
        this.kpis.satisfaccionCliente,
        Math.round(Math.random() * 20 + 70)
      ]
    };
  }

  async exportData(formato: string): Promise<void> {
    this.exportingData = true;
    
    try {
      if (formato === 'pdf') {
        await this.exportToPDF();
      } else if (formato === 'excel') {
        await this.exportToExcel();
      }
    } catch (error) {
      console.error('Error exportando datos:', error);
      alert('Error al exportar los datos. Por favor, intenta de nuevo.');
    } finally {
      this.exportingData = false;
    }
  }

  private async exportToPDF(): Promise<void> {
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    let yPosition = 20;

    // Título
    pdf.setFontSize(20);
    pdf.text('Dashboard Analytics - UBApp', pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 10;

    // Fecha
    pdf.setFontSize(10);
    pdf.text(`Generado: ${new Date().toLocaleDateString('es-ES')}`, pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 15;

    // KPIs
    pdf.setFontSize(14);
    pdf.text('Indicadores Clave (KPIs)', 15, yPosition);
    yPosition += 8;

    pdf.setFontSize(10);
    const kpiTexts = [
      `Total Envíos: ${this.kpis.totalEnvios}`,
      `Envíos Pendientes: ${this.kpis.enviosPendientes}`,
      `Total Productos: ${this.kpis.totalProductos}`,
      `Valor Promedio: $${this.kpis.valorPromedio.toFixed(2)}`,
      `Tasa Crecimiento: ${this.kpis.tasaCrecimiento.toFixed(1)}%`,
      `Satisfacción Cliente: ${this.kpis.satisfaccionCliente.toFixed(1)}%`
    ];

    kpiTexts.forEach(text => {
      pdf.text(text, 20, yPosition);
      yPosition += 6;
    });

    yPosition += 10;

    // Capturar gráficos
    const charts = [
      { ref: this.enviosChartRef, title: 'Evolución de Envíos' },
      { ref: this.estadosChartRef, title: 'Estados de Envíos' },
      { ref: this.productosChartRef, title: 'Productos por Categoría' }
    ];

    for (const chart of charts) {
      if (chart.ref?.nativeElement) {
        // Verificar si hay espacio suficiente en la página
        if (yPosition + 80 > pageHeight - 20) {
          pdf.addPage();
          yPosition = 20;
        }

        pdf.setFontSize(12);
        pdf.text(chart.title, 15, yPosition);
        yPosition += 5;

        try {
          const canvas = await html2canvas(chart.ref.nativeElement, {
            scale: 2,
            backgroundColor: '#ffffff'
          });
          const imgData = canvas.toDataURL('image/png');
          const imgWidth = pageWidth - 30;
          const imgHeight = (canvas.height * imgWidth) / canvas.width;
          
          pdf.addImage(imgData, 'PNG', 15, yPosition, imgWidth, Math.min(imgHeight, 70));
          yPosition += Math.min(imgHeight, 70) + 10;
        } catch (error) {
          console.error(`Error capturando gráfico ${chart.title}:`, error);
        }
      }
    }

    // Guardar PDF
    pdf.save(`dashboard_analytics_${new Date().getTime()}.pdf`);
  }

  private async exportToExcel(): Promise<void> {
    const workbook = XLSX.utils.book_new();

    // Hoja 1: KPIs
    const kpisData = [
      ['Indicador', 'Valor'],
      ['Total Envíos', this.kpis.totalEnvios],
      ['Envíos Pendientes', this.kpis.enviosPendientes],
      ['Total Productos', this.kpis.totalProductos],
      ['Valor Promedio', this.kpis.valorPromedio],
      ['Tasa Crecimiento (%)', this.kpis.tasaCrecimiento],
      ['Satisfacción Cliente (%)', this.kpis.satisfaccionCliente]
    ];
    const kpisSheet = XLSX.utils.aoa_to_sheet(kpisData);
    XLSX.utils.book_append_sheet(workbook, kpisSheet, 'KPIs');

    // Hoja 2: Envíos
    if (this.enviosData.length > 0) {
      const enviosSheet = XLSX.utils.json_to_sheet(this.enviosData.map(e => ({
        'ID': e.id,
        'Estado': e.estado,
        'Fecha Creación': e.fecha_creacion ? new Date(e.fecha_creacion).toLocaleDateString('es-ES') : '',
        'Destino': e.destino || '',
        'Usuario': e.usuario_nombre || e.usuario || ''
      })));
      XLSX.utils.book_append_sheet(workbook, enviosSheet, 'Envíos');
    }

    // Hoja 3: Productos
    if (this.productosData.length > 0) {
      const productosSheet = XLSX.utils.json_to_sheet(this.productosData.map(p => ({
        'ID': p.id,
        'Nombre': p.nombre,
        'Categoría': p.categoria || p.category || '',
        'Cantidad': p.cantidad || 0,
        'Precio': p.precio || 0
      })));
      XLSX.utils.book_append_sheet(workbook, productosSheet, 'Productos');
    }

    // Hoja 4: Distribución por Estados
    const estadosData = this.groupByEstado(this.enviosData);
    const estadosExcel = [
      ['Estado', 'Cantidad'],
      ...estadosData.labels.map((label, index) => [label, estadosData.values[index]])
    ];
    const estadosSheet = XLSX.utils.aoa_to_sheet(estadosExcel);
    XLSX.utils.book_append_sheet(workbook, estadosSheet, 'Estados');

    // Guardar archivo
    XLSX.writeFile(workbook, `dashboard_analytics_${new Date().getTime()}.xlsx`);
  }

  async downloadChart(chartName: string): Promise<void> {
    let canvasRef: ElementRef<HTMLCanvasElement> | undefined;
    let filename = 'chart';

    switch (chartName) {
      case 'envios':
        canvasRef = this.enviosChartRef;
        filename = 'envios';
        break;
      case 'productos':
        canvasRef = this.productosChartRef;
        filename = 'productos';
        break;
      case 'estados':
        canvasRef = this.estadosChartRef;
        filename = 'estados';
        break;
      case 'tendencias':
        canvasRef = this.tendenciasChartRef;
        filename = 'tendencias';
        break;
      case 'categorias':
        canvasRef = this.categoriasChartRef;
        filename = 'categorias';
        break;
      case 'kpi':
        canvasRef = this.kpiChartRef;
        filename = 'kpi';
        break;
    }

    if (canvasRef?.nativeElement) {
      try {
        const canvas = await html2canvas(canvasRef.nativeElement, {
          scale: 2,
          backgroundColor: '#ffffff'
        });
        
        const link = document.createElement('a');
        link.download = `${filename}_${new Date().getTime()}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
      } catch (error) {
        console.error('Error descargando gráfico:', error);
        alert('Error al descargar el gráfico. Por favor, intenta de nuevo.');
      }
    }
  }

  toggleFullscreen(chartName: string): void {
    if (this.fullscreenChart === chartName) {
      this.fullscreenChart = null;
    } else {
      this.fullscreenChart = chartName;
    }
  }

  isFullscreen(chartName: string): boolean {
    return this.fullscreenChart === chartName;
  }

  @HostListener('document:keydown.escape', ['$event'])
  handleEscape(event: KeyboardEvent): void {
    if (this.fullscreenChart) {
      this.fullscreenChart = null;
    }
  }

  resetFilters(): void {
    this.filters = {
      periodo: 'mes',
      tipoGrafico: 'barras',
      metrica: 'envios'
    };
    this.updateCharts();
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
}

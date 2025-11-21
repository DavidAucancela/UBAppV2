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
  ultimaActualizacion: Date = new Date();

  // Exponer Math para usar en el template
  Math = Math;

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
  private chartsUpdateScheduled = false;
  private chartsUpdateTimeout: any = null;
  private chartsInitialized = false;
  private initializationAttempts = 0;
  private readonly MAX_INIT_ATTEMPTS = 10;
  private updateChartsRetryCount = 0;
  private readonly MAX_UPDATE_RETRIES = 5;
  private isInitializing = false;

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

  // Estadísticas de notificaciones
  notificacionesStats = {
    total: 0,
    noLeidas: 0,
    porTipo: {} as Record<string, number>
  };

  // Estadísticas de consultas semánticas
  semanticasStats = {
    totalConsultas: 0,
    totalEmbeddings: 0,
    totalTokens: 0,
    datosVectorizados: 0,
    promedioTiempoRespuesta: 0
  };

  // Estadísticas geográficas
  geograficasStats = {
    usuariosPorProvincia: {} as Record<string, number>,
    usuariosPorCanton: {} as Record<string, number>,
    usuariosPorCiudad: {} as Record<string, number>,
    totalConUbicacion: 0
  };

  // Control de visualización de tarjetas
  mostrarTodasLasTarjetas = true;
  categoriaSeleccionada: string | null = null;

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
    this.loadNotificacionesStats();
    this.loadSemanticasStats();
    this.loadGeograficasStats();
  }

  ngAfterViewInit(): void {
    // Esperar a que el DOM esté completamente renderizado
    setTimeout(() => {
      this.initializeCharts();
    }, 200);
  }

  ngOnDestroy(): void {
    if (this.chartsUpdateTimeout) {
      clearTimeout(this.chartsUpdateTimeout);
    }
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
        this.ultimaActualizacion = new Date();
      },
      error: (error) => {
        console.error('Error cargando estadísticas de usuarios:', error);
        this.loading = false;
        this.ultimaActualizacion = new Date();
      }
    });

    // Cargar estadísticas de envíos
    this.apiService.getEstadisticasEnvios().subscribe({
      next: (envioStats) => {
        this.stats.envios = this.normalizeEnviosStats(envioStats);
        // Actualizar KPIs con los datos reales del backend
        this.updateKPIsFromStats();
        // refreshEnviosPorEstadoFromListData() se llamará desde loadAllData() cuando los datos estén disponibles
        this.ultimaActualizacion = new Date();
      },
      error: (error) => {
        console.error('Error cargando estadísticas de envíos:', error);
        // refreshEnviosPorEstadoFromListData() se llamará desde loadAllData() cuando los datos estén disponibles
        this.ultimaActualizacion = new Date();
      }
    });

    // Cargar estadísticas de productos
    this.apiService.getEstadisticasProductos().subscribe({
      next: (productoStats) => {
        this.stats.productos = productoStats;
        // Actualizar KPIs con los datos reales del backend
        this.updateKPIsFromStats();
        this.ultimaActualizacion = new Date();
      },
      error: (error) => {
        console.error('Error cargando estadísticas de productos:', error);
        this.ultimaActualizacion = new Date();
      }
    });
  }

  private loadDigitadorStats(): void {
    // Cargar estadísticas de envíos y productos
    this.apiService.getEstadisticasEnvios().subscribe({
      next: (envioStats) => {
        this.stats.envios = this.normalizeEnviosStats(envioStats);
        // Actualizar KPIs con los datos reales del backend
        this.updateKPIsFromStats();
        this.loading = false;
        // refreshEnviosPorEstadoFromListData() se llamará desde loadAllData() cuando los datos estén disponibles
        this.ultimaActualizacion = new Date();
      },
      error: (error) => {
        console.error('Error cargando estadísticas de envíos:', error);
        this.loading = false;
        // refreshEnviosPorEstadoFromListData() se llamará desde loadAllData() cuando los datos estén disponibles
        this.ultimaActualizacion = new Date();
      }
    });

    // Cargar estadísticas de productos
    this.apiService.getEstadisticasProductos().subscribe({
      next: (productoStats) => {
        this.stats.productos = productoStats;
        // Actualizar KPIs con los datos reales del backend
        this.updateKPIsFromStats();
        this.ultimaActualizacion = new Date();
      },
      error: (error) => {
        console.error('Error cargando estadísticas de productos:', error);
        this.ultimaActualizacion = new Date();
      }
    });
  }

  private loadCompradorStats(): void {
    // Cargar estadísticas de envíos propios
    this.apiService.getMisEnvios().subscribe({
      next: (envios) => {
        const listaEnvios = Array.isArray(envios) ? envios : (envios as any).results || [];
        this.stats.misEnvios = {
          total: listaEnvios.length,
          pendientes: listaEnvios.filter((e: any) => e.estado === 'pendiente').length,
          en_transito: listaEnvios.filter((e: any) => e.estado === 'en_transito').length,
          entregados: listaEnvios.filter((e: any) => e.estado === 'entregado').length
        };
        // Actualizar KPIs con los datos del comprador
        this.kpis.totalEnvios = this.stats.misEnvios.total;
        this.kpis.enviosPendientes = this.stats.misEnvios.pendientes;
        this.loading = false;
        this.ultimaActualizacion = new Date();
      },
      error: (error) => {
        console.error('Error cargando envíos:', error);
        this.loading = false;
        this.ultimaActualizacion = new Date();
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
        // Actualizar estadísticas de estado usando los datos cargados
        this.refreshEnviosPorEstadoFromListData();
        this.checkAndUpdateCharts();
        this.ultimaActualizacion = new Date();
      },
      error: (error) => {
        console.error('Error cargando envíos:', error);
        this.datosEnviosCargados = true;
        this.checkAndUpdateCharts();
        this.ultimaActualizacion = new Date();
      }
    });

    // Cargar productos
    this.apiService.getProductos().subscribe({
      next: (productos) => {
        this.productosData = Array.isArray(productos) ? productos : (productos as any).results || [];
        this.datosProductosCargados = true;
        this.calculateKPIs();
        this.checkAndUpdateCharts();
        this.ultimaActualizacion = new Date();
      },
      error: (error) => {
        console.error('Error cargando productos:', error);
        this.datosProductosCargados = true;
        this.checkAndUpdateCharts();
        this.ultimaActualizacion = new Date();
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
          this.ultimaActualizacion = new Date();
        },
        error: (error) => {
          console.error('Error cargando usuarios:', error);
          this.datosUsuariosCargados = true;
          this.checkAndUpdateCharts();
          this.ultimaActualizacion = new Date();
        }
      });
    } else {
      // Si no tiene permisos, marcar como cargado
      this.datosUsuariosCargados = true;
    }
  }

  private initializeCharts(): void {
    // Evitar múltiples inicializaciones simultáneas
    if (this.isInitializing) {
      return;
    }

    // Si ya están inicializados, solo actualizar
    if (this.chartsInitialized && this.areChartsReady()) {
      this.updateCharts();
      return;
    }

    // Verificar si los canvas están disponibles
    if (this.areChartsReady()) {
      this.isInitializing = true;
      try {
        this.updateCharts();
        this.chartsInitialized = true;
        this.initializationAttempts = 0;
      } finally {
        this.isInitializing = false;
      }
    } else {
      // Reintentar si no se han excedido los intentos máximos
      if (this.initializationAttempts < this.MAX_INIT_ATTEMPTS) {
        this.initializationAttempts++;
        setTimeout(() => this.initializeCharts(), 200);
      } else {
        console.warn('No se pudieron inicializar los gráficos después de múltiples intentos');
        this.isInitializing = false;
      }
    }
  }

  private areChartsReady(): boolean {
    // Verificar que los canvas estén disponibles en el DOM
    // Solo verificamos los que están visibles según mostrarCategoria
    const needsGraficos = this.mostrarCategoria('graficos');
    
    if (!needsGraficos) {
      return false; // Los gráficos no están visibles aún
    }

    // Verificar que los ViewChild estén disponibles y que los elementos estén en el DOM
    // Usar querySelector como respaldo si ViewChild no está disponible aún
    const checkElement = (ref: ElementRef<HTMLCanvasElement> | undefined): boolean => {
      if (!ref?.nativeElement) {
        return false;
      }
      // Verificar que el elemento esté realmente en el DOM
      return document.contains(ref.nativeElement);
    };

    return (
      checkElement(this.enviosChartRef) &&
      checkElement(this.productosChartRef) &&
      checkElement(this.estadosChartRef) &&
      checkElement(this.tendenciasChartRef) &&
      checkElement(this.categoriasChartRef) &&
      checkElement(this.kpiChartRef)
    );
  }

  private checkAndUpdateCharts(): void {
    // Verificar si todos los datos necesarios están cargados
    if (this.datosEnviosCargados && this.datosProductosCargados && this.datosUsuariosCargados) {
      // Evitar múltiples llamadas simultáneas
      if (this.chartsUpdateScheduled) {
        return;
      }
      
      this.chartsUpdateScheduled = true;
      
      // Limpiar timeout anterior si existe
      if (this.chartsUpdateTimeout) {
        clearTimeout(this.chartsUpdateTimeout);
      }
      
      // Esperar a que los ViewChild estén listos
      this.chartsUpdateTimeout = setTimeout(() => {
        this.chartsUpdateScheduled = false;
        
        // Verificar si los gráficos están listos para ser creados/actualizados
        if (this.areChartsReady()) {
          if (this.chartsInitialized) {
            // Actualizar gráficos existentes
            this.updateCharts();
          } else {
            // Inicializar gráficos por primera vez
            this.initializeCharts();
          }
        } else if (!this.chartsInitialized) {
          // Si aún no están listos pero no se han inicializado, intentar inicializar
          // Esto maneja el caso donde los datos están listos pero el DOM aún no
          this.initializeCharts();
        }
      }, 300);
    }
  }

  calculateKPIs(): void {
    // Este método se mantiene para compatibilidad, pero ahora usamos updateKPIsFromStats()
    // que obtiene los datos reales del backend
    this.updateKPIsFromStats();
  }

  updateKPIsFromStats(): void {
    // Usar estadísticas del backend si están disponibles (datos reales)
    if (this.stats.envios && this.stats.envios.total_envios !== undefined) {
      this.kpis.totalEnvios = this.stats.envios.total_envios || 0;
      this.kpis.enviosPendientes = this.stats.envios.envios_pendientes || 0;
    } else {
      // Fallback: usar datos cargados (puede estar paginado)
      this.kpis.totalEnvios = this.enviosData.length;
      this.kpis.enviosPendientes = this.enviosData.filter(e => 
        e.estado === 'pendiente' || e.estado === 'Pendiente'
      ).length;
    }

    // Total de productos desde estadísticas del backend si está disponible
    if (this.stats.productos && this.stats.productos.total !== undefined) {
      this.kpis.totalProductos = this.stats.productos.total || 0;
    } else {
      // Fallback: usar datos cargados
      this.kpis.totalProductos = this.productosData.length;
    }

    // Tasa de crecimiento (simulada basada en fechas)
    const enviosRecientes = this.filterByPeriod(this.enviosData, 'mes');
    const enviosAnteriores = this.kpis.totalEnvios - enviosRecientes.length;
    this.kpis.tasaCrecimiento = enviosAnteriores > 0 
      ? ((enviosRecientes.length - enviosAnteriores) / enviosAnteriores) * 100 
      : 0;

    // Valor promedio (simulado)
    this.kpis.valorPromedio = this.kpis.totalEnvios > 0 
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
    // Cuando se aplica un filtro, ocultar todas las tarjetas y mostrar solo el gráfico seleccionado
    this.mostrarTodasLasTarjetas = false;
    // Esperar a que el DOM se actualice antes de actualizar los gráficos
    setTimeout(() => {
      if (this.areChartsReady()) {
        this.updateCharts();
      }
    }, 100);
  }

  resetFilters(): void {
    this.filters = {
      periodo: 'mes',
      tipoGrafico: 'barras',
      metrica: 'envios'
    };
    // Restaurar visualización de todas las tarjetas
    this.mostrarTodasLasTarjetas = true;
    this.categoriaSeleccionada = null;
    // Esperar a que el DOM se actualice antes de actualizar los gráficos
    setTimeout(() => {
      if (this.areChartsReady()) {
        this.updateCharts();
      }
    }, 100);
  }

  seleccionarCategoria(categoria: string): void {
    if (this.categoriaSeleccionada === categoria) {
      // Si ya está seleccionada, restaurar vista completa
      this.categoriaSeleccionada = null;
      this.mostrarTodasLasTarjetas = true;
    } else {
      // Ocultar todas y mostrar solo la categoría seleccionada
      this.categoriaSeleccionada = categoria;
      this.mostrarTodasLasTarjetas = false;
    }
    // Si se selecciona la categoría de gráficos, asegurar que estén inicializados
    if (categoria === 'graficos') {
      setTimeout(() => {
        if (!this.chartsInitialized && this.areChartsReady()) {
          this.initializeCharts();
        } else if (this.chartsInitialized && this.areChartsReady()) {
          this.updateCharts();
        }
      }, 100);
    }
  }

  mostrarCategoria(categoria: string): boolean {
    if (this.mostrarTodasLasTarjetas) return true;
    return this.categoriaSeleccionada === categoria;
  }

  updateCharts(): void {
    // Verificar que los canvas estén disponibles antes de continuar
    if (!this.areChartsReady()) {
      // Evitar bucles infinitos
      if (this.updateChartsRetryCount >= this.MAX_UPDATE_RETRIES) {
        console.warn('Max retries reached for updateCharts, aborting');
        this.updateChartsRetryCount = 0;
        return;
      }
      
      console.log('Charts canvas not ready yet, will retry...');
      this.updateChartsRetryCount++;
      
      // Reintentar después de un breve delay
      setTimeout(() => {
        if (this.areChartsReady()) {
          this.updateChartsRetryCount = 0; // Reset counter on success
          this.updateCharts();
        } else {
          this.updateChartsRetryCount = 0; // Reset counter if still not ready
        }
      }, 200);
      return;
    }

    // Reset retry counter when charts are ready
    this.updateChartsRetryCount = 0;

    // Destruir gráficos existentes de forma segura
    this.destroyAllCharts();

    // Usar requestAnimationFrame para asegurar que el DOM esté listo
    requestAnimationFrame(() => {
      try {
        // Crear gráficos uno por uno con manejo de errores individual
        if (this.enviosChartRef?.nativeElement) {
          this.createEnviosChart();
        }
        if (this.productosChartRef?.nativeElement) {
          this.createProductosChart();
        }
        if (this.estadosChartRef?.nativeElement) {
          this.createEstadosChart();
        }
        if (this.tendenciasChartRef?.nativeElement) {
          this.createTendenciasChart();
        }
        if (this.categoriasChartRef?.nativeElement) {
          this.createCategoriasChart();
        }
        if (this.kpiChartRef?.nativeElement) {
          this.createKPIChart();
        }
        console.log('Charts created successfully');
      } catch (error) {
        console.error('Error creating charts:', error);
        // No propagar el error para evitar cuelgues
      }
    });
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
    if (!this.enviosChartRef?.nativeElement) {
      console.warn('enviosChart canvas not available');
      return;
    }
    
    // Destruir gráfico existente si existe
    if (this.enviosChart) {
      this.enviosChart.destroy();
      this.enviosChart = null;
    }

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
    if (!this.productosChartRef?.nativeElement) {
      console.warn('productosChart canvas not available');
      return;
    }
    
    // Destruir gráfico existente si existe
    if (this.productosChart) {
      this.productosChart.destroy();
      this.productosChart = null;
    }

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
    if (!this.estadosChartRef?.nativeElement) {
      console.warn('estadosChart canvas not available');
      return;
    }
    
    // Destruir gráfico existente si existe
    if (this.estadosChart) {
      this.estadosChart.destroy();
      this.estadosChart = null;
    }

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
    if (!this.tendenciasChartRef?.nativeElement) {
      console.warn('tendenciasChart canvas not available');
      return;
    }
    
    // Destruir gráfico existente si existe
    if (this.tendenciasChart) {
      this.tendenciasChart.destroy();
      this.tendenciasChart = null;
    }

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
    if (!this.categoriasChartRef?.nativeElement) {
      console.warn('categoriasChart canvas not available');
      return;
    }
    
    // Destruir gráfico existente si existe
    if (this.categoriasChart) {
      this.categoriasChart.destroy();
      this.categoriasChart = null;
    }

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
    if (!this.kpiChartRef?.nativeElement) {
      console.warn('kpiChart canvas not available');
      return;
    }
    
    // Destruir gráfico existente si existe
    if (this.kpiChart) {
      this.kpiChart.destroy();
      this.kpiChart = null;
    }

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

  loadNotificacionesStats(): void {
    // Cargar estadísticas de notificaciones
    this.apiService.getNotificaciones().subscribe({
      next: (response: any) => {
        const notificaciones = Array.isArray(response) ? response : (response.results || []);
        this.notificacionesStats.total = notificaciones.length;
        this.notificacionesStats.noLeidas = notificaciones.filter((n: any) => !n.leida).length;
        
        // Contar por tipo
        const porTipo: Record<string, number> = {};
        notificaciones.forEach((n: any) => {
          porTipo[n.tipo] = (porTipo[n.tipo] || 0) + 1;
        });
        this.notificacionesStats.porTipo = porTipo;
      },
      error: (error) => {
        console.error('Error cargando estadísticas de notificaciones:', error);
      }
    });
  }

  loadSemanticasStats(): void {
    // Cargar estadísticas de consultas semánticas usando el endpoint de métricas
    this.apiService.obtenerMetricasSemanticas().subscribe({
      next: (stats: any) => {
        this.semanticasStats.totalConsultas = stats.total_consultas || 0;
        this.semanticasStats.totalEmbeddings = stats.total_embeddings || 0;
        this.semanticasStats.totalTokens = stats.total_tokens || 0;
        this.semanticasStats.datosVectorizados = stats.datos_vectorizados || 0;
        this.semanticasStats.promedioTiempoRespuesta = stats.promedio_tiempo_respuesta || 0;
      },
      error: (error) => {
        console.error('Error cargando estadísticas semánticas:', error);
        // Si el endpoint no existe o falla, calcular desde los datos disponibles
        this.calcularStatsSemanticasDesdeDatos();
      }
    });
  }

  calcularStatsSemanticasDesdeDatos(): void {
    // Calcular estadísticas básicas desde los modelos disponibles
    // Esto es un fallback si el endpoint no está disponible
    this.apiService.obtenerHistorialSemantico().subscribe({
      next: (historial: any) => {
        const lista = Array.isArray(historial) ? historial : [];
        this.semanticasStats.totalConsultas = lista.length;
        
        // Calcular tiempo promedio
        if (lista.length > 0) {
          const tiempos = lista.map((h: any) => h.tiempo_respuesta || 0).filter((t: number) => t > 0);
          this.semanticasStats.promedioTiempoRespuesta = tiempos.length > 0
            ? tiempos.reduce((a: number, b: number) => a + b, 0) / tiempos.length
            : 0;
        }
      },
      error: () => {
        // Si también falla, dejar valores en 0
      }
    });
  }

  loadGeograficasStats(): void {
    // Cargar estadísticas geográficas de usuarios
    this.apiService.getUsuarios().subscribe({
      next: (usuarios: any) => {
        const listaUsuarios = Array.isArray(usuarios) ? usuarios : (usuarios.results || []);
        
        const porProvincia: Record<string, number> = {};
        const porCanton: Record<string, number> = {};
        const porCiudad: Record<string, number> = {};
        let conUbicacion = 0;

        listaUsuarios.forEach((usuario: any) => {
          if (usuario.provincia) {
            porProvincia[usuario.provincia] = (porProvincia[usuario.provincia] || 0) + 1;
            conUbicacion++;
          }
          if (usuario.canton) {
            porCanton[usuario.canton] = (porCanton[usuario.canton] || 0) + 1;
          }
          if (usuario.ciudad) {
            porCiudad[usuario.ciudad] = (porCiudad[usuario.ciudad] || 0) + 1;
          }
        });

        this.geograficasStats.usuariosPorProvincia = porProvincia;
        this.geograficasStats.usuariosPorCanton = porCanton;
        this.geograficasStats.usuariosPorCiudad = porCiudad;
        this.geograficasStats.totalConUbicacion = conUbicacion;
      },
      error: (error) => {
        console.error('Error cargando estadísticas geográficas:', error);
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

  // Método que usa los datos ya cargados (sin hacer llamada HTTP adicional)
  private refreshEnviosPorEstadoFromListData(): void {
    if (!this.enviosData || this.enviosData.length === 0) {
      return; // Esperar a que loadAllData() cargue los datos
    }
    
    const counts: Record<string, number> = {
      'Entregado': 0,
      'En tránsito': 0,
      'Pendiente': 0,
      'Cancelado': 0
    };
    
    this.enviosData.forEach((e: any) => {
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
    this.stats.envios.total_envios = this.enviosData.length;
    this.stats.envios.envios_pendientes = counts['Pendiente'];
  }

  // Método original mantenido por compatibilidad (pero no se usa en el flujo normal)
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

  // Métodos auxiliares para notificaciones
  getNotificacionesTipos(): string[] {
    return Object.keys(this.notificacionesStats.porTipo);
  }

  getNotificacionIcon(tipo: string): string {
    const iconMap: Record<string, string> = {
      'nuevo_envio': 'fa-truck',
      'envio_asignado': 'fa-user-check',
      'estado_cambiado': 'fa-exchange-alt',
      'general': 'fa-info-circle'
    };
    return iconMap[tipo] || 'fa-bell';
  }

  getNotificacionLabel(tipo: string): string {
    const labelMap: Record<string, string> = {
      'nuevo_envio': 'Nuevo Envío',
      'envio_asignado': 'Envío Asignado',
      'estado_cambiado': 'Estado Cambiado',
      'general': 'General'
    };
    return labelMap[tipo] || tipo;
  }

  // Métodos auxiliares para estadísticas geográficas
  getTotalProvincias(): number {
    return Object.keys(this.geograficasStats.usuariosPorProvincia).length;
  }

  getTotalCantones(): number {
    return Object.keys(this.geograficasStats.usuariosPorCanton).length;
  }

  getTotalCiudades(): number {
    return Object.keys(this.geograficasStats.usuariosPorCiudad).length;
  }

  getTopProvincias(): Array<{nombre: string, cantidad: number}> {
    const provincias = Object.entries(this.geograficasStats.usuariosPorProvincia)
      .map(([nombre, cantidad]) => ({ nombre, cantidad: cantidad as number }))
      .sort((a, b) => b.cantidad - a.cantidad)
      .slice(0, 5);
    return provincias;
  }
}

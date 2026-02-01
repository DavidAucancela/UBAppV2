import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../../services/api.service';
import { AuthService } from '../../../services/auth.service';
import { UsuarioService } from '../../../services/usuario.service';
import { MetricasService } from '../../../services/metricas.service';
import { forkJoin, of, Subscription, timer } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { Chart, ChartConfiguration, registerables } from 'chart.js';

Chart.register(...registerables);

/** Plugin que dibuja el valor numérico sobre cada barra para que se vean los meses con pocos registros */
const barDataLabelsPlugin = {
  id: 'barDataLabels',
  afterDatasetsDraw(chart: Chart) {
    const opts = (chart.options?.plugins as any)?.barDataLabels;
    if (!opts || (chart as any).config?.type !== 'bar') return;
    const ctx = chart.ctx;
    const meta = chart.getDatasetMeta(0);
    if (!meta?.data?.length) return;
    const dataset = chart.data.datasets[0];
    const values = dataset.data as number[];
    ctx.save();
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.fillStyle = opts.color ?? '#374151';
    ctx.font = `${opts.fontWeight ?? '600'} ${opts.fontSize ?? '12'}px ${opts.fontFamily ?? 'sans-serif'}`;
    meta.data.forEach((bar: any, i: number) => {
      const v = values[i];
      if (v == null) return;
      const x = bar.x;
      const y = bar.y - 4;
      ctx.fillText(String(v), x, y);
    });
    ctx.restore();
  }
};
Chart.register(barDataLabelsPlugin);

export type TipoGraficoPastel =
  | 'estado_envios'
  | 'compradores_ciudad'
  | 'productos_categoria'
  | 'envios_mes';

interface PieOption {
  id: TipoGraficoPastel;
  label: string;
  icon: string;
}

export type TipoActividad = 'envio' | 'usuario';
export interface ActividadItem {
  _tipo: TipoActividad;
  _fecha: number;
  _titulo: string;
  _subtitulo: string;
  _icono: string;
  _statusClass?: string;
  envio?: any;
  usuario?: any;
}

@Component({
  selector: 'app-inicio',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './inicio.component.html',
  styleUrl: './inicio.component.css'
})
export class InicioComponent implements OnInit, OnDestroy {
  @ViewChild('chartPastel') chartPastelRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('chartBar') chartBarRef!: ElementRef<HTMLCanvasElement>;
  chartPastelInstance: Chart<'doughnut' | 'bar'> | null = null;
  chartBarInstance: Chart<'bar'> | null = null;

  loading = true;
  error: string | null = null;
  private refreshSub: Subscription | null = null;
  private readonly INTERVALO_REFRESH_MS = 60_000;

  isComprador = false;
  dashboardUsuario: any = null;

  stats = {
    envios: {
      total_envios: 0,
      envios_pendientes: 0,
      envios_en_transito: 0,
      envios_entregados: 0,
      envios_cancelados: 0,
      por_estado: {} as Record<string, number>
    },
    tarifas_totales: 0,
    busquedas_semanticas: 0,
    productos: [] as any[],
    productosPorCategoria: {} as Record<string, number>,
    tarifas: [] as any[],
    mapaCompradores: { provincias: [] as any[], total_compradores: 0 },
    enviosTodos: [] as any[],
    enviosRecientes: [] as any[],
    actividadReciente: [] as ActividadItem[]
  };

  actividadSeleccionada: ActividadItem | null = null;

  opcionesPastel: PieOption[] = [
    { id: 'estado_envios', label: 'Estado de los envíos', icon: 'fa-truck' },
    { id: 'compradores_ciudad', label: 'Compradores por ciudad', icon: 'fa-map-marker-alt' },
    { id: 'productos_categoria', label: 'Productos por categoría', icon: 'fa-box' },
    { id: 'envios_mes', label: 'Envíos por mes', icon: 'fa-calendar-alt' }
  ];

  tipoGraficoSeleccionado: TipoGraficoPastel = 'estado_envios';
  aniosDisponibles = [2025, 2026];
  anioGraficoEnviosMes = new Date().getFullYear();
  coloresPastel = [
    '#667eea', '#764ba2', '#10b981', '#f59e0b', '#3b82f6',
    '#8b5cf6', '#ec4899', '#14b8a6', '#64748b'
  ];

  constructor(
    private apiService: ApiService,
    public authService: AuthService,
    private usuarioService: UsuarioService,
    private metricasService: MetricasService
  ) {
    this.isComprador = this.authService.isComprador();
  }

  ngOnInit(): void {
    this.cargarEstadisticas();
    this.iniciarAutoRefresh();
  }

  ngOnDestroy(): void {
    this.detenerAutoRefresh();
    this.destruirGraficoPastel();
    this.destruirGraficoBarra();
  }

  private iniciarAutoRefresh(): void {
    this.detenerAutoRefresh();
    this.refreshSub = timer(this.INTERVALO_REFRESH_MS, this.INTERVALO_REFRESH_MS)
      .pipe(switchMap(() => this.cargarDatos()))
      .subscribe({
        next: (r) => {
          this.aplicarResultados(r);
          setTimeout(() => {
            if (this.isComprador) {
              this.actualizarGraficoBarra();
            } else {
              this.actualizarGraficoPastel();
            }
          }, 50);
        },
        error: () => {}
      });
  }

  private detenerAutoRefresh(): void {
    if (this.refreshSub) {
      this.refreshSub.unsubscribe();
      this.refreshSub = null;
    }
  }

  private cargarDatos() {
    const requests: any = {
      envios: this.apiService.getEstadisticasEnvios().pipe(
        catchError(() => of({ total_envios: 0, envios_pendientes: 0, por_estado: {} }))
      ),
      tarifas: this.apiService.getTarifas().pipe(
        catchError(() => of([] as any[]))
      ),
      metricas: this.metricasService.getEstadisticasSemanticas().pipe(
        catchError(() => of({ total_metricas: 0 }))
      ),
      busquedaMetricas: this.apiService.obtenerMetricasSemanticas().pipe(
        catchError(() => of({ totalBusquedas: 0, busquedasTotales: 0 }))
      ),
      productos: this.apiService.getProductos().pipe(
        catchError(() => of([] as any[]))
      ),
      estadisticasProductos: this.apiService.getEstadisticasProductos().pipe(
        catchError(() => of({ por_categoria: {} as Record<string, number> }))
      ),
      mapa: this.apiService.getMapaCompradores().pipe(
        catchError(() => of({ provincias: [], total_compradores: 0 }))
      ),
      usuarios: this.apiService.getUsuarios().pipe(
        catchError(() => of([] as any[]))
      )
    };

    // Si es comprador, cargar datos específicos
    if (this.isComprador) {
      requests.dashboardUsuario = this.usuarioService.getDashboardUsuario().pipe(
        catchError(() => of({ dashboard: null, envios_recientes: [] }))
      );
      requests.misEnvios = this.usuarioService.getMisEnvios().pipe(
        catchError(() => of({ envios: [], total_envios: 0 }))
      );
    } else {
      requests.enviosList = this.apiService.getEnvios().pipe(
        catchError(() => of([] as any[]))
      );
    }

    return forkJoin(requests);
  }

  private aplicarResultados(r: any): void {
    // Si es comprador, usar datos del dashboard del usuario
    if (this.isComprador && r.dashboardUsuario?.dashboard) {
      this.dashboardUsuario = r.dashboardUsuario.dashboard;
      const dash = r.dashboardUsuario.dashboard;
      this.stats.envios = {
        total_envios: dash.total_envios ?? 0,
        envios_pendientes: dash.envios_pendientes ?? 0,
        envios_en_transito: dash.envios_en_transito ?? 0,
        envios_entregados: dash.envios_entregados ?? 0,
        envios_cancelados: dash.envios_cancelados ?? 0,
        por_estado: {
          pendiente: dash.envios_pendientes ?? 0,
          en_transito: dash.envios_en_transito ?? 0,
          entregado: dash.envios_entregados ?? 0,
          cancelado: dash.envios_cancelados ?? 0
        }
      };
      this.stats.enviosRecientes = Array.isArray(r.dashboardUsuario.envios_recientes) 
        ? r.dashboardUsuario.envios_recientes.slice(0, 5) 
        : [];
      
      // Crear actividad desde envíos recientes
      const actividades: ActividadItem[] = [];
      this.stats.enviosRecientes.forEach((e: any) => {
        const ts = new Date((e.fecha_actualizacion || e.fecha_emision || e.fecha_creacion || 0)).getTime();
        actividades.push({
          _tipo: 'envio',
          _fecha: ts,
          _titulo: `Envío ${e.hawb || '#' + e.id}`,
          _subtitulo: `${this.estadoEtiqueta(e.estado)} · ${this.formatearFecha(e.fecha_actualizacion || e.fecha_emision || e.fecha_creacion)}`,
          _icono: 'fa-truck',
          _statusClass: this.getStatusClass(e.estado),
          envio: e
        });
      });
      actividades.sort((a, b) => b._fecha - a._fecha);
      this.stats.actividadReciente = this.filtrarActividadSinFechasFuturas(actividades);
    } else {
      // Para admin/gerente/digitador
      this.stats.envios = {
        total_envios: r.envios?.total_envios ?? 0,
        envios_pendientes: r.envios?.envios_pendientes ?? 0,
        envios_en_transito: r.envios?.por_estado?.en_transito ?? 0,
        envios_entregados: r.envios?.por_estado?.entregado ?? 0,
        envios_cancelados: r.envios?.por_estado?.cancelado ?? 0,
        por_estado: r.envios?.por_estado ?? {}
      };
      this.stats.tarifas = Array.isArray(r.tarifas) ? r.tarifas : [];
      this.stats.tarifas_totales = this.stats.tarifas.length;
      const busqueda = r.busquedaMetricas ?? {};
      const metricas = r.metricas ?? {};
      this.stats.busquedas_semanticas =
        (busqueda.totalBusquedas ?? busqueda.busquedasTotales ?? 0) ||
        (metricas.total_metricas ?? 0);
      this.stats.productos = Array.isArray(r.productos) ? r.productos : [];
      this.stats.productosPorCategoria = r.estadisticasProductos?.por_categoria ?? {};
      this.stats.mapaCompradores = {
        provincias: r.mapa?.provincias ?? [],
        total_compradores: r.mapa?.total_compradores ?? 0
      };
      const list = Array.isArray(r.enviosList) ? r.enviosList : [];
      this.stats.enviosTodos = list;
      const usuarios = Array.isArray(r.usuarios) ? r.usuarios : [];
      const actividades: ActividadItem[] = [];
      list.forEach((e: any) => {
        const ts = new Date((e.fecha_actualizacion || e.fecha_emision || e.fecha_creacion || 0)).getTime();
        actividades.push({
          _tipo: 'envio',
          _fecha: ts,
          _titulo: `Envío ${e.hawb || '#' + e.id}`,
          _subtitulo: `${this.estadoEtiqueta(e.estado)} · ${this.formatearFecha(e.fecha_actualizacion || e.fecha_emision || e.fecha_creacion)}`,
          _icono: 'fa-truck',
          _statusClass: this.getStatusClass(e.estado),
          envio: e
        });
      });
      usuarios.forEach((u: any) => {
        const ts = new Date((u.fecha_actualizacion || u.fecha_creacion || 0)).getTime();
        actividades.push({
          _tipo: 'usuario',
          _fecha: ts,
          _titulo: u.nombre || u.username || 'Usuario',
          _subtitulo: `${u.rol_nombre || 'Usuario'} · ${this.formatearFecha(u.fecha_creacion)}`,
          _icono: 'fa-user',
          _statusClass: 'default',
          usuario: u
        });
      });
      actividades.sort((a, b) => b._fecha - a._fecha);
      this.stats.actividadReciente = this.filtrarActividadSinFechasFuturas(actividades).slice(0, 15);
    }
  }

  /**
   * Excluye actividades con fecha futura (datos erróneos como 2041, 2043, 2044)
   * para que en Últimos movimientos solo se muestren registros con fechas válidas.
   */
  private filtrarActividadSinFechasFuturas(items: ActividadItem[]): ActividadItem[] {
    const ahora = Date.now();
    return items.filter((item) => item._fecha <= ahora);
  }

  cargarEstadisticas(): void {
    this.loading = true;
    this.error = null;
    this.cargarDatos().subscribe({
      next: (r) => {
          this.aplicarResultados(r);
          this.error = null;
          this.loading = false;
          setTimeout(() => {
            if (this.isComprador) {
              this.actualizarGraficoBarra();
            } else {
              this.actualizarGraficoPastel();
            }
          }, 150);
      },
      error: (err) => {
        this.loading = false;
        this.error = err?.message ?? 'Error al cargar datos';
        setTimeout(() => this.actualizarGraficoPastel(), 100);
      }
    });
  }


  cambiarTipoPastel(tipo: TipoGraficoPastel): void {
    this.tipoGraficoSeleccionado = tipo;
    this.actualizarGraficoPastel();
  }

  cambiarAnioGraficoEnviosMes(anio: number): void {
    this.anioGraficoEnviosMes = anio;
    this.actualizarGraficoPastel();
  }

  obtenerDatosPastel(): { labels: string[]; values: number[] } {
    switch (this.tipoGraficoSeleccionado) {
      case 'estado_envios': {
        const porEstado = this.stats.envios?.por_estado ?? {};
        const labels = Object.keys(porEstado);
        const values = labels.map((k) => porEstado[k] ?? 0);
        return { labels, values };
      }
      case 'compradores_ciudad': {
        const byCity: Record<string, number> = {};
        for (const p of this.stats.mapaCompradores?.provincias ?? []) {
          for (const c of p.compradores ?? []) {
            const ciudad = (c.ciudad || 'Sin ciudad').trim() || 'Sin ciudad';
            byCity[ciudad] = (byCity[ciudad] ?? 0) + 1;
          }
        }
        const entries = Object.entries(byCity).sort((a, b) => b[1] - a[1]);
        return {
          labels: entries.map(([k]) => k),
          values: entries.map(([, v]) => v)
        };
      }
      case 'productos_categoria': {
        let porCat = this.stats.productosPorCategoria ?? {};
        const hasEstadisticas = Object.keys(porCat).length > 0 && Object.values(porCat).some((v) => (v ?? 0) > 0);
        if (!hasEstadisticas && (this.stats.productos?.length ?? 0) > 0) {
          porCat = {} as Record<string, number>;
          for (const p of this.stats.productos) {
            const c = (p.categoria_nombre ?? p.categoria ?? 'Otros').trim() || 'Otros';
            porCat[c] = (porCat[c] ?? 0) + 1;
          }
        }
        const entries = Object.entries(porCat)
          .filter(([, v]) => (v ?? 0) > 0)
          .sort((a, b) => b[1] - a[1]);
        return {
          labels: entries.map(([k]) => k),
          values: entries.map(([, v]) => v)
        };
      }
      case 'envios_mes': {
        const envios = this.stats.enviosTodos ?? [];
        const anio = this.anioGraficoEnviosMes;
        const enviosDelAnio = envios.filter((e: any) => {
          const f = e.fecha_emision || e.fecha_creacion;
          if (!f) return false;
          return new Date(f).getFullYear() === anio;
        });
        const meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
        const byMonth: Record<string, number> = {};
        for (const m of meses) byMonth[m] = 0;
        for (const e of enviosDelAnio) {
          const f = e.fecha_emision || e.fecha_creacion;
          if (f) {
            const d = new Date(f);
            const key = meses[d.getMonth()];
            byMonth[key] = (byMonth[key] ?? 0) + 1;
          }
        }
        return {
          labels: meses,
          values: meses.map((m) => byMonth[m] ?? 0)
        };
      }
      default:
        return { labels: [], values: [] };
    }
  }

  private actualizarGraficoPastel(): void {
    if (!this.chartPastelRef?.nativeElement) return;

    const { labels, values } = this.obtenerDatosPastel();
    const hasData = values.some((v) => v > 0);
    const titulo = this.opcionesPastel.find((o) => o.id === this.tipoGraficoSeleccionado)?.label ?? '';
    const esEnviosMes = this.tipoGraficoSeleccionado === 'envios_mes';

    const baseOptions: any = {
      responsive: true,
      maintainAspectRatio: false,
      layout: { padding: { top: 16, bottom: 16, left: 16, right: 16 } },
      animation: { duration: 500 },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 16,
            usePointStyle: true,
            pointStyle: 'circle',
            font: { size: 12 }
          }
        },
        title: {
          display: true,
          text: hasData ? titulo : 'Sin datos para la vista seleccionada',
          font: { size: 15, weight: 600 },
          padding: { bottom: 12 }
        },
        tooltip: {
          enabled: hasData,
          padding: 10,
          titleFont: { size: 13 },
          bodyFont: { size: 12 }
        }
      }
    };

    if (!hasData) {
      this.destruirGraficoPastel();
      const config: ChartConfiguration<'doughnut'> = {
        type: 'doughnut',
        data: {
          labels: ['Sin datos'],
          datasets: [{
            data: [1],
            backgroundColor: ['#e5e7eb'],
            borderWidth: 0,
            hoverOffset: 0
          }]
        },
        options: { ...baseOptions, plugins: { ...baseOptions.plugins, legend: { display: false }, tooltip: { enabled: false } } }
      };
      this.chartPastelInstance = new Chart(this.chartPastelRef.nativeElement, config);
      return;
    }

    this.destruirGraficoPastel();

    if (esEnviosMes) {
      const barColors = this.coloresPastel.slice(0, labels.length);
      while (barColors.length < labels.length) {
        barColors.push(this.coloresPastel[barColors.length % this.coloresPastel.length]);
      }
      const config: ChartConfiguration<'bar'> = {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Envíos',
            data: values,
            backgroundColor: barColors,
            borderRadius: 6,
            borderSkipped: false
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          layout: { padding: { top: 24, bottom: 16, left: 16, right: 16 } },
          animation: { duration: 500 },
          plugins: {
            legend: { display: false },
            barDataLabels: true,
            title: {
              display: true,
              text: titulo,
              font: { size: 15, weight: 600 },
              padding: { bottom: 12 }
            },
            tooltip: {
              padding: 10,
              titleFont: { size: 13 },
              bodyFont: { size: 12 },
              callbacks: {
                label: (ctx) => `Envíos: ${ctx.raw}`
              }
            }
          } as any,
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1, font: { size: 11 } },
              grid: { color: '#f3f4f6' }
            },
            x: {
              grid: { display: false },
              ticks: { maxRotation: 45, minRotation: 0, font: { size: 10 } }
            }
          }
        }
      };
      this.chartPastelInstance = new Chart(this.chartPastelRef.nativeElement, config);
      return;
    }

    const bgColors = this.coloresPastel.slice(0, labels.length);
    while (bgColors.length < labels.length) {
      bgColors.push(this.coloresPastel[bgColors.length % this.coloresPastel.length]);
    }

    const config: ChartConfiguration<'doughnut'> = {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: bgColors,
          borderColor: '#fff',
          borderWidth: 2,
          hoverOffset: 12,
          hoverBorderWidth: 2
        }]
      },
      options: baseOptions
    };
    this.chartPastelInstance = new Chart(this.chartPastelRef.nativeElement, config);
  }

  private destruirGraficoPastel(): void {
    if (this.chartPastelInstance) {
      this.chartPastelInstance.destroy();
      this.chartPastelInstance = null;
    }
  }

  private destruirGraficoBarra(): void {
    if (this.chartBarInstance) {
      this.chartBarInstance.destroy();
      this.chartBarInstance = null;
    }
  }

  private actualizarGraficoBarra(): void {
    if (!this.chartBarRef?.nativeElement || !this.dashboardUsuario) return;

    const datos = [
      this.stats.envios.envios_pendientes,
      this.stats.envios.envios_en_transito,
      this.stats.envios.envios_entregados,
      this.stats.envios.envios_cancelados
    ];
    const labels = ['Pendientes', 'En Tránsito', 'Entregados', 'Cancelados'];
    const colores = ['#f59e0b', '#3b82f6', '#10b981', '#64748b'];

    this.destruirGraficoBarra();
    const config: ChartConfiguration<'bar'> = {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Envíos',
          data: datos,
          backgroundColor: colores,
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            padding: 12,
            titleFont: { size: 13, weight: 600 },
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
    this.chartBarInstance = new Chart(this.chartBarRef.nativeElement, config);
  }

  formatearFecha(f: string | undefined): string {
    if (!f) return '-';
    const d = new Date(f);
    return d.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  estadoEtiqueta(estado: string): string {
    const m: Record<string, string> = {
      pendiente: 'Pendiente',
      en_transito: 'En tránsito',
      entregado: 'Entregado',
      cancelado: 'Cancelado'
    };
    return m[estado?.toLowerCase()] ?? estado ?? '-';
  }

  prepararActividadEnvio(envio: any): ActividadItem {
    const fecha = envio.fecha_actualizacion || envio.fecha_emision || envio.fecha_creacion;
    return {
      _tipo: 'envio',
      _fecha: new Date(fecha).getTime(),
      _titulo: 'Envío ' + (envio.hawb || '#' + envio.id),
      _subtitulo: this.estadoEtiqueta(envio.estado) + ' · ' + this.formatearFecha(fecha),
      _icono: 'fa-truck',
      _statusClass: this.getStatusClass(envio.estado),
      envio: envio
    };
  }

  getCurrentYear(): number {
    return new Date().getFullYear();
  }

  abrirDetalle(item: ActividadItem): void {
    this.actividadSeleccionada = item;
  }

  cerrarDetalle(): void {
    this.actividadSeleccionada = null;
  }

  getStatusClass(estado: string): string {
    const m: Record<string, string> = {
      entregado: 'delivered',
      'en_transito': 'transit',
      pendiente: 'pending',
      cancelado: 'cancelled'
    };
    return m[estado?.toLowerCase()] ?? 'default';
  }
}

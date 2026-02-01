import {
  Component,
  OnInit,
  OnDestroy,
  PLATFORM_ID,
  Inject,
  ViewChild,
  ElementRef,
  ChangeDetectorRef,
  HostListener,
} from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { ApiService } from '../../services/api.service';
import {
  PROVINCIAS_ECUADOR,
  ProvinciaEcuador,
  MapaResponse,
  CompradorMapa,
  ProvinciaConCompradores,
  EnvioSimple,
} from '../../models/mapa';
import { Chart, ChartConfiguration, registerables } from 'chart.js';

Chart.register(...registerables);

export type OrdenListado = 'nombre' | 'ciudad' | 'envios';
export const ESTADOS_ENVIO = ['pendiente', 'en_transito', 'entregado', 'cancelado'] as const;

interface CompradorPorCiudad {
  ciudad: string;
  provincia: string;
  total_compradores: number;
  compradores: CompradorMapa[];
  total_envios: number;
}

interface EnvioPorComprador {
  comprador_id: number;
  comprador_nombre: string;
  ciudad: string;
  provincia: string;
  envios: EnvioSimple[];
  total_envios: number;
}

@Component({
  selector: 'app-mapa-compradores',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './mapa-compradores.component.html',
  styleUrl: './mapa-compradores.component.css',
})
export class MapaCompradoresComponent implements OnInit, OnDestroy {
  @ViewChild('chartCompradoresCiudad') chartCompradoresCiudadRef!: ElementRef<HTMLCanvasElement>;
  chartCompradoresCiudadInstance: Chart<'bar'> | null = null;

  private map: L.Map | null = null;
  private markers: L.Marker[] = [];
  private provinciasMarkers: Map<string, L.Marker> = new Map();
  private marcadorProvinciaSeleccionada: L.Marker | null = null;
  private L: typeof import('leaflet') | null = null;
  private subscription = new Subscription();
  private busquedaSubject = new Subject<string>();

  mapaData: MapaResponse | null = null;
  loading = true;
  error: string | null = null;
  provinciaSeleccionada: string | null = null;
  ciudadSeleccionada: string | null = null;
  compradoresProvinciaSeleccionada: CompradorMapa[] = [];
  datosProvinciaSeleccionada: ProvinciaConCompradores | null = null;
  isBrowser = false;

  compradoresPorCiudad: CompradorPorCiudad[] = [];
  enviosPorComprador: EnvioPorComprador[] = [];

  filtroProvincia = '';
  filtroCiudad = '';
  busquedaComprador = '';
  /** Valor mostrado en el input de búsqueda (sincronizado con debounce). */
  busquedaInputDisplay = '';
  filtroEstadoEnvio = '';
  ordenListado: OrdenListado = 'envios';
  provinciasDisponibles: string[] = [];
  ciudadesDisponibles: string[] = [];

  readonly ITEMS_POR_PAGINA = 12;
  listadoPaginaActual = 1;

  mostrarOnboarding = false;
  filtrosColapsados = false;

  private iconoCiudad: L.Icon | null = null;
  private iconoCiudadActiva: L.Icon | null = null;
  private iconoComprador: L.Icon | null = null;

  readonly opcionesOrden: { value: OrdenListado; label: string }[] = [
    { value: 'envios', label: 'Más envíos' },
    { value: 'nombre', label: 'Nombre' },
    { value: 'ciudad', label: 'Ciudad' },
  ];

  readonly opcionesEstado = [
    { value: '', label: 'Todos los estados' },
    { value: 'pendiente', label: 'Pendiente' },
    { value: 'en_transito', label: 'En tránsito' },
    { value: 'entregado', label: 'Entregado' },
    { value: 'cancelado', label: 'Cancelado' },
  ];

  constructor(
    private apiService: ApiService,
    private router: Router,
    private route: ActivatedRoute,
    @Inject(PLATFORM_ID) private platformId: Object,
    private cdr: ChangeDetectorRef
  ) {
    this.isBrowser = isPlatformBrowser(this.platformId);
  }

  get totalFiltrosActivos(): number {
    let n = 0;
    if (this.filtroProvincia) n++;
    if (this.filtroCiudad) n++;
    if (this.busquedaComprador.trim()) n++;
    if (this.filtroEstadoEnvio) n++;
    if (this.provinciaSeleccionada || this.ciudadSeleccionada) n++;
    return n;
  }

  get enviosFiltradosPaginados(): EnvioPorComprador[] {
    const todos = this.obtenerEnviosFiltrados();
    const inicio = (this.listadoPaginaActual - 1) * this.ITEMS_POR_PAGINA;
    return todos.slice(inicio, inicio + this.ITEMS_POR_PAGINA);
  }

  get hayMasEnvios(): boolean {
    const total = this.obtenerEnviosFiltrados().length;
    return this.listadoPaginaActual * this.ITEMS_POR_PAGINA < total;
  }

  get restantesListado(): number {
    return Math.max(
      0,
      this.totalEnviosFiltrados - this.listadoPaginaActual * this.ITEMS_POR_PAGINA
    );
  }

  get totalEnviosFiltrados(): number {
    return this.obtenerEnviosFiltrados().length;
  }

  get hayDatosParaGrafico(): boolean {
    return this.obtenerDatosFiltrados().length > 0;
  }

  async ngOnInit(): Promise<void> {
    if (this.isBrowser) {
      this.L = await import('leaflet');
      this.crearIconosPersonalizados();
      this.aplicarQueryParams();
      this.configurarDebounceBusqueda();
      this.verificarOnboarding();
      this.cargarDatosMapa();
    } else {
      this.loading = false;
      this.error = 'El mapa solo está disponible en el navegador';
    }
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    if (this.provinciaSeleccionada || this.ciudadSeleccionada) {
      this.volverVista();
    }
  }

  private verificarOnboarding(): void {
    try {
      this.mostrarOnboarding = !localStorage.getItem('mapa-compradores-onboarding-v1');
    } catch {
      this.mostrarOnboarding = false;
    }
  }

  cerrarOnboarding(): void {
    this.mostrarOnboarding = false;
    try {
      localStorage.setItem('mapa-compradores-onboarding-v1', 'true');
    } catch {}
    this.cdr.detectChanges();
  }

  private aplicarQueryParams(): void {
    this.subscription.add(
      this.route.queryParams.subscribe((params) => {
        const provincia = params['provincia'] as string | undefined;
        const ciudad = params['ciudad'] as string | undefined;
        if (provincia) {
          this.filtroProvincia = provincia;
          this.onFiltroChange();
        }
        if (ciudad) {
          this.filtroCiudad = ciudad;
          this.onFiltroChange();
        }
      })
    );
  }

  private actualizarQueryParams(): void {
    const queryParams: Record<string, string> = {};
    if (this.filtroProvincia) queryParams['provincia'] = this.filtroProvincia;
    if (this.filtroCiudad) queryParams['ciudad'] = this.filtroCiudad;
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams,
      queryParamsHandling: 'merge',
      replaceUrl: true,
    });
  }

  private configurarDebounceBusqueda(): void {
    this.subscription.add(
      this.busquedaSubject.pipe(debounceTime(300), distinctUntilChanged()).subscribe((valor) => {
        this.busquedaComprador = valor;
        this.busquedaInputDisplay = valor;
        this.listadoPaginaActual = 1;
        this.actualizarVistaFiltrada();
      })
    );
  }

  onBusquedaInput(valor: string): void {
    this.busquedaInputDisplay = valor;
    this.busquedaSubject.next(valor);
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
    if (this.chartCompradoresCiudadInstance) {
      this.chartCompradoresCiudadInstance.destroy();
      this.chartCompradoresCiudadInstance = null;
    }
  }

  private crearIconosPersonalizados(): void {
    if (!this.L) return;

    const svgProvincia = `
      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
        <circle cx="20" cy="20" r="18" fill="#3b82f6" stroke="#1e40af" stroke-width="2" opacity="0.8"/>
        <path d="M20 10 C 16 10 13 13 13 17 C 13 22 20 30 20 30 C 20 30 27 22 27 17 C 27 13 24 10 20 10 Z M 20 20 C 18.3 20 17 18.7 17 17 C 17 15.3 18.3 14 20 14 C 21.7 14 23 15.3 23 17 C 23 18.7 21.7 20 20 20 Z" fill="white"/>
      </svg>
    `;
    this.iconoCiudad = this.L.icon({
      iconUrl: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svgProvincia),
      iconSize: [40, 40],
      iconAnchor: [20, 40],
      popupAnchor: [0, -40],
    });

    const svgProvinciaActiva = `
      <svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 44 44">
        <circle cx="22" cy="22" r="20" fill="#2563eb" stroke="#1d4ed8" stroke-width="3" opacity="1"/>
        <path d="M22 12 C 17 12 14 15 14 19 C 14 24 22 32 22 32 C 22 32 30 24 30 19 C 30 15 27 12 22 12 Z M 22 22 C 20.1 22 18.5 20.4 18.5 18.5 C 18.5 16.6 20.1 15 22 15 C 23.9 15 25.5 16.6 25.5 18.5 C 25.5 20.4 23.9 22 22 22 Z" fill="white"/>
      </svg>
    `;
    this.iconoCiudadActiva = this.L.icon({
      iconUrl: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svgProvinciaActiva),
      iconSize: [44, 44],
      iconAnchor: [22, 44],
      popupAnchor: [0, -44],
    });

    const svgComprador = `
      <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36">
        <circle cx="18" cy="18" r="16" fill="#10b981" stroke="#059669" stroke-width="2.5" opacity="0.95"/>
        <circle cx="18" cy="14" r="5" fill="white"/>
        <path d="M 9 28 C 9 22 12 19 18 19 C 24 19 27 22 27 28 Z" fill="white"/>
      </svg>
    `;
    this.iconoComprador = this.L.icon({
      iconUrl: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svgComprador),
      iconSize: [36, 36],
      iconAnchor: [18, 36],
      popupAnchor: [0, -36],
    });
  }

  private cargarDatosMapa(): void {
    this.loading = true;
    this.error = null;

    this.subscription.add(
      this.apiService.getMapaCompradores().subscribe({
        next: (data: MapaResponse) => {
          this.mapaData = data;
          this.procesarDatos();
          this.loading = false;
          this.actualizarVistaFiltrada();
          setTimeout(() => {
            this.inicializarMapa();
            this.crearGraficoCompradoresPorCiudad();
          }, 0);
        },
        error: () => {
          this.error = 'Error al cargar los datos del mapa';
          this.loading = false;
          this.cdr.detectChanges();
        },
      })
    );
  }

  private procesarDatos(): void {
    if (!this.mapaData) return;

    const ciudadMap = new Map<string, CompradorPorCiudad>();

    this.mapaData.provincias.forEach((provincia) => {
      provincia.compradores.forEach((comprador) => {
        const claveCiudad = `${comprador.ciudad} - ${comprador.provincia}`;
        if (!ciudadMap.has(claveCiudad)) {
          ciudadMap.set(claveCiudad, {
            ciudad: comprador.ciudad,
            provincia: comprador.provincia,
            total_compradores: 0,
            compradores: [],
            total_envios: 0,
          });
        }
        const ciudadData = ciudadMap.get(claveCiudad)!;
        ciudadData.compradores.push(comprador);
        ciudadData.total_compradores++;
        ciudadData.total_envios += comprador.total_envios;
      });
    });

    this.compradoresPorCiudad = Array.from(ciudadMap.values()).sort(
      (a, b) => b.total_compradores - a.total_compradores
    );
    this.provinciasDisponibles = [...new Set(this.compradoresPorCiudad.map((c) => c.provincia))].sort();
    this.ciudadesDisponibles = [...new Set(this.compradoresPorCiudad.map((c) => c.ciudad))].sort();
    this.procesarEnviosPorComprador();
  }

  private procesarEnviosPorComprador(): void {
    const compradorMap = new Map<number, EnvioPorComprador>();

    this.compradoresPorCiudad.forEach((ciudadData) => {
      ciudadData.compradores.forEach((comprador) => {
        if (!compradorMap.has(comprador.id)) {
          compradorMap.set(comprador.id, {
            comprador_id: comprador.id,
            comprador_nombre: comprador.nombre,
            ciudad: comprador.ciudad,
            provincia: comprador.provincia,
            envios: [],
            total_envios: 0,
          });
        }
        const compradorData = compradorMap.get(comprador.id)!;
        compradorData.envios.push(...comprador.envios_recientes);
        compradorData.total_envios = comprador.total_envios;
      });
    });

    this.enviosPorComprador = Array.from(compradorMap.values()).sort(
      (a, b) => b.total_envios - a.total_envios
    );
  }

  private inicializarMapa(): void {
    if (!this.L || !this.isBrowser) return;
    const mapaContainer = document.getElementById('mapa-ecuador');
    if (!mapaContainer) return;

    this.map = this.L.map('mapa-ecuador').setView([-1.8312, -78.1834], 7);
    this.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 15,
      attribution: '© OpenStreetMap contributors',
    }).addTo(this.map);

    this.agregarMarcadoresProvincias();
    this.map.on('zoomend', () => this.manejarCambioZoom());
  }

  private agregarMarcadoresProvincias(): void {
    if (!this.mapaData || !this.L || !this.map) return;

    const provinciasConCompradores = new Map<string, ProvinciaConCompradores>();
    this.mapaData.provincias.forEach((p) => provinciasConCompradores.set(p.provincia, p));

    PROVINCIAS_ECUADOR.forEach((provincia) => {
      const datos = provinciasConCompradores.get(provincia.nombre);
      if (datos && datos.total_compradores > 0) {
        this.agregarMarcadorProvincia(provincia, datos);
      }
    });
  }

  private agregarMarcadorProvincia(provincia: ProvinciaEcuador, datos: ProvinciaConCompradores): void {
    if (!this.L || !this.map || !this.iconoCiudad) return;

    const marker = this.L.marker([provincia.latitud, provincia.longitud], {
      icon: this.iconoCiudad,
    }).addTo(this.map);

    marker.bindPopup(this.crearPopupProvincia(provincia, datos), {
      maxWidth: 400,
      minWidth: 300,
      className: 'popup-provincia-custom',
    });

    marker.on('click', () => this.seleccionarProvincia(provincia.nombre, datos));
    this.provinciasMarkers.set(provincia.nombre, marker);
  }

  private resaltarMarcadorProvincia(provinciaNombre: string | null): void {
    if (!this.L || !this.iconoCiudad || !this.iconoCiudadActiva) return;

    if (this.marcadorProvinciaSeleccionada) {
      this.marcadorProvinciaSeleccionada.setIcon(this.iconoCiudad);
      this.marcadorProvinciaSeleccionada = null;
    }

    if (provinciaNombre) {
      const marker = this.provinciasMarkers.get(provinciaNombre);
      if (marker) {
        marker.setIcon(this.iconoCiudadActiva);
        this.marcadorProvinciaSeleccionada = marker;
      }
    }
  }

  seleccionarProvincia(provinciaNombre: string, datos?: ProvinciaConCompradores): void {
    if (!this.mapaData) return;

    const provinciaData =
      datos || this.mapaData.provincias.find((p) => p.provincia === provinciaNombre);
    if (!provinciaData) return;

    this.provinciaSeleccionada = provinciaNombre;
    this.ciudadSeleccionada = null;
    this.compradoresProvinciaSeleccionada = provinciaData.compradores;
    this.datosProvinciaSeleccionada = provinciaData;
    this.resaltarMarcadorProvincia(provinciaNombre);

    const coords = PROVINCIAS_ECUADOR.find((p) => p.nombre === provinciaNombre);
    if (coords && this.map) {
      this.map.setView([coords.latitud, coords.longitud], 9);
      setTimeout(() => this.mostrarCompradoresIndividuales(provinciaData), 500);
    }

    this.actualizarVistaFiltrada();
  }

  seleccionarCiudad(ciudad: string, provincia: string): void {
    this.ciudadSeleccionada = ciudad;
    this.provinciaSeleccionada = provincia;
    this.resaltarMarcadorProvincia(provincia);

    const ciudadData = this.compradoresPorCiudad.find(
      (c) => c.ciudad === ciudad && c.provincia === provincia
    );

    if (ciudadData) {
      this.compradoresProvinciaSeleccionada = ciudadData.compradores;
      this.actualizarVistaFiltrada();

      const coords = PROVINCIAS_ECUADOR.find((p) => p.nombre === provincia);
      if (coords && this.map) {
        this.map.setView([coords.latitud, coords.longitud], 10);
        setTimeout(
          () =>
            this.mostrarCompradoresIndividuales({
              provincia,
              total_compradores: ciudadData.total_compradores,
              compradores: ciudadData.compradores,
            }),
          500
        );
      }
    }
  }

  private crearPopupProvincia(provincia: ProvinciaEcuador, datos: ProvinciaConCompradores): string {
    return `
      <div class="popup-provincia">
        <h3 style="margin:0 0 10px 0;color:#1e40af;font-size:18px">📍 ${provincia.nombre}</h3>
        <p style="margin:5px 0;color:#4b5563"><strong>Compradores:</strong> ${datos.total_compradores}</p>
        <button style="margin-top:10px;padding:8px 16px;background:#3b82f6;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:500" onclick="this.closest('.leaflet-popup').remove()">Ver compradores</button>
      </div>
    `;
  }

  private mostrarCompradoresIndividuales(provinciaDatos: ProvinciaConCompradores): void {
    if (!this.L || !this.map || !this.iconoComprador) return;

    this.limpiarMarcadoresCompradores();
    const coords = PROVINCIAS_ECUADOR.find((p) => p.nombre === provinciaDatos.provincia);
    if (!coords) return;

    provinciaDatos.compradores.forEach((comprador, index) => {
      const offset = this.calcularOffset(index, provinciaDatos.compradores.length);
      const lat = coords.latitud + offset.lat;
      const lng = coords.longitud + offset.lng;

      const marker = this.L!.marker([lat, lng], { icon: this.iconoComprador! }).addTo(this.map!);
      marker.bindPopup(this.crearPopupComprador(comprador), {
        maxWidth: 500,
        minWidth: 400,
        className: 'popup-comprador-custom',
      });
      marker.on('click', () => this.seleccionarComprador(comprador));
      this.markers.push(marker);
    });
  }

  seleccionarComprador(comprador: CompradorMapa): void {
    this.busquedaComprador = comprador.nombre;
    this.busquedaInputDisplay = comprador.nombre;
    this.provinciaSeleccionada = comprador.provincia || null;
    this.ciudadSeleccionada = comprador.ciudad || null;
    this.listadoPaginaActual = 1;
    this.actualizarVistaFiltrada();
    this.cdr.detectChanges();
  }

  private calcularOffset(index: number, total: number): { lat: number; lng: number } {
    const radius = 0.05;
    const angle = (index / total) * 2 * Math.PI;
    return { lat: radius * Math.cos(angle), lng: radius * Math.sin(angle) };
  }

  private crearPopupComprador(comprador: CompradorMapa): string {
    const enviosHtml =
      comprador.envios_recientes.length > 0
        ? `
        <div style="margin-top:10px;max-height:200px;overflow-y:auto">
          <h4 style="margin:10px 0 5px 0;color:#059669;font-size:14px">📦 Envíos recientes</h4>
          ${comprador.envios_recientes
            .map(
              (e) => `
            <div style="background:#f3f4f6;padding:8px;margin:5px 0;border-radius:4px;border-left:3px solid ${this.getColorEstado(e.estado)}">
              <p style="margin:2px 0;font-size:12px"><strong>HAWB:</strong> ${e.hawb}</p>
              <p style="margin:2px 0;font-size:12px"><strong>Estado:</strong> ${this.getEstadoDisplay(e.estado)}</p>
              <p style="margin:2px 0;font-size:12px"><strong>Peso:</strong> ${e.peso_total} kg | <strong>Valor:</strong> $${e.valor_total}</p>
            </div>
          `
            )
            .join('')}
        </div>
      `
        : '<p style="margin-top:10px;color:#6b7280;font-style:italic">Sin envíos registrados</p>';

    return `
      <div class="popup-comprador">
        <h3 style="margin:0 0 10px 0;color:#059669;font-size:18px">👤 ${comprador.nombre}</h3>
        <p style="margin:5px 0;color:#4b5563;font-size:14px"><strong>Usuario:</strong> ${comprador.username}</p>
        <p style="margin:5px 0;color:#4b5563;font-size:14px"><strong>Email:</strong> ${comprador.correo}</p>
        <p style="margin:5px 0;color:#4b5563;font-size:14px"><strong>Ubicación:</strong> ${comprador.ubicacion_completa}</p>
        <p style="margin:5px 0"><strong>Total envíos:</strong> <span style="background:#3b82f6;color:white;padding:2px 8px;border-radius:12px;font-weight:bold">${comprador.total_envios}</span></p>
        ${enviosHtml}
      </div>
    `;
  }

  private getColorEstado(estado: string): string {
    const colores: Record<string, string> = {
      pendiente: '#f59e0b',
      en_transito: '#3b82f6',
      entregado: '#10b981',
      cancelado: '#ef4444',
    };
    return colores[estado] ?? '#6b7280';
  }

  getEstadoDisplay(estado: string): string {
    const estados: Record<string, string> = {
      pendiente: 'Pendiente',
      en_transito: 'En tránsito',
      entregado: 'Entregado',
      cancelado: 'Cancelado',
    };
    return estados[estado] ?? estado;
  }

  getTotalEnviosSeleccionados(): number {
    if (!this.compradoresProvinciaSeleccionada?.length) return 0;
    return this.compradoresProvinciaSeleccionada.reduce((sum, c) => sum + c.total_envios, 0);
  }

  private limpiarMarcadoresCompradores(): void {
    this.markers.forEach((m) => m.remove());
    this.markers = [];
  }

  private manejarCambioZoom(): void {
    if (!this.map) return;
    if (this.map.getZoom() < 9) {
      this.limpiarMarcadoresCompradores();
      this.provinciaSeleccionada = null;
      this.ciudadSeleccionada = null;
      this.compradoresProvinciaSeleccionada = [];
      this.datosProvinciaSeleccionada = null;
      this.resaltarMarcadorProvincia(null);
      this.actualizarVistaFiltrada();
    }
  }

  volverVista(): void {
    if (this.map) {
      this.map.setView([-1.8312, -78.1834], 7);
      this.limpiarMarcadoresCompradores();
      this.provinciaSeleccionada = null;
      this.ciudadSeleccionada = null;
      this.compradoresProvinciaSeleccionada = [];
      this.datosProvinciaSeleccionada = null;
      this.resaltarMarcadorProvincia(null);
    }
    this.actualizarVistaFiltrada();
  }

  confirmarLimpiarFiltros(): void {
    if (this.totalFiltrosActivos === 0) {
      this.limpiarFiltros();
      return;
    }
    if (typeof window !== 'undefined' && window.confirm('¿Limpiar todos los filtros y la selección del mapa?')) {
      this.limpiarFiltros();
    }
  }

  limpiarFiltros(): void {
    this.filtroProvincia = '';
    this.filtroCiudad = '';
    this.busquedaComprador = '';
    this.busquedaInputDisplay = '';
    this.filtroEstadoEnvio = '';
    this.provinciaSeleccionada = null;
    this.ciudadSeleccionada = null;
    this.listadoPaginaActual = 1;
    this.ciudadesDisponibles = [...new Set(this.compradoresPorCiudad.map((c) => c.ciudad))].sort();
    this.actualizarQueryParams();
    this.actualizarVistaFiltrada();
    this.volverVista();
  }

  verMasListado(): void {
    this.listadoPaginaActual++;
    this.cdr.detectChanges();
  }

  cambiarOrdenListado(orden: OrdenListado): void {
    this.ordenListado = orden;
    this.listadoPaginaActual = 1;
    this.actualizarVistaFiltrada();
  }

  private crearGraficoCompradoresPorCiudad(): void {
    if (!this.chartCompradoresCiudadRef?.nativeElement || !this.isBrowser) return;

    const datosFiltrados = this.obtenerDatosFiltrados();
    const topCiudades = [...datosFiltrados]
      .sort((a, b) => b.total_compradores - a.total_compradores)
      .slice(0, 10);

    const colores = [
      'rgba(59, 130, 246, 0.8)',
      'rgba(16, 185, 129, 0.8)',
      'rgba(245, 158, 11, 0.8)',
      'rgba(139, 92, 246, 0.8)',
      'rgba(236, 72, 153, 0.8)',
      'rgba(20, 184, 166, 0.8)',
      'rgba(251, 146, 60, 0.8)',
      'rgba(99, 102, 241, 0.8)',
      'rgba(239, 68, 68, 0.8)',
      'rgba(34, 197, 94, 0.8)',
    ];

    const config: ChartConfiguration<'bar'> = {
      type: 'bar',
      data: {
        labels: topCiudades.map((c) => `${c.ciudad}\n(${c.provincia})`),
        datasets: [
          {
            label: 'Compradores',
            data: topCiudades.map((c) => c.total_compradores),
            backgroundColor: topCiudades.map((_, i) => colores[i % colores.length]),
            borderColor: topCiudades.map((_, i) => colores[i % colores.length].replace('rgba(', 'rgb(').replace(', 0.8)', ')')),
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              afterLabel: function (this: unknown, tooltipItem: { dataIndex: number }) {
                const c = topCiudades[tooltipItem.dataIndex];
                return `Total envíos: ${c.total_envios}`;
              },
            },
          },
        },
        scales: {
          y: { beginAtZero: true, ticks: { stepSize: 1 } },
          x: { ticks: { maxRotation: 45, minRotation: 45 } },
        },
        onClick: (_, elements) => {
          if (elements.length > 0) {
            const c = topCiudades[elements[0].index];
            this.seleccionarCiudad(c.ciudad, c.provincia);
          }
        },
      },
    };

    if (this.chartCompradoresCiudadInstance) {
      this.chartCompradoresCiudadInstance.destroy();
    }
    this.chartCompradoresCiudadInstance = new Chart(this.chartCompradoresCiudadRef.nativeElement, config);
  }

  obtenerDatosFiltrados(): CompradorPorCiudad[] {
    let datos = [...this.compradoresPorCiudad];
    if (this.filtroProvincia) datos = datos.filter((c) => c.provincia === this.filtroProvincia);
    if (this.filtroCiudad)
      datos = datos.filter((c) => c.ciudad.toLowerCase().includes(this.filtroCiudad.toLowerCase()));
    return datos;
  }

  obtenerEnviosFiltrados(): EnvioPorComprador[] {
    let envios = [...this.enviosPorComprador];

    if (this.provinciaSeleccionada) {
      envios = envios.filter((e) => e.provincia === this.provinciaSeleccionada);
    }
    if (this.ciudadSeleccionada) {
      envios = envios.filter((e) => e.ciudad === this.ciudadSeleccionada);
    }
    if (this.busquedaComprador.trim()) {
      envios = envios.filter((e) =>
        e.comprador_nombre.toLowerCase().includes(this.busquedaComprador.toLowerCase())
      );
    }
    if (this.filtroEstadoEnvio) {
      envios = envios.filter((e) =>
        e.envios.some((ev) => ev.estado === this.filtroEstadoEnvio)
      );
    }

    if (this.ordenListado === 'nombre') {
      envios = [...envios].sort((a, b) => a.comprador_nombre.localeCompare(b.comprador_nombre));
    } else if (this.ordenListado === 'ciudad') {
      envios = [...envios].sort(
        (a, b) => a.ciudad.localeCompare(b.ciudad) || a.provincia.localeCompare(b.provincia)
      );
    } else {
      envios = [...envios].sort((a, b) => b.total_envios - a.total_envios);
    }

    return envios;
  }

  actualizarVistaFiltrada(): void {
    this.onFiltroChange();
    this.cdr.detectChanges();
    setTimeout(() => this.crearGraficoCompradoresPorCiudad(), 100);
  }

  onFiltroChange(): void {
    if (this.filtroProvincia) {
      this.ciudadesDisponibles = [
        ...new Set(
          this.compradoresPorCiudad.filter((c) => c.provincia === this.filtroProvincia).map((c) => c.ciudad)
        ),
      ].sort();
    } else {
      this.ciudadesDisponibles = [...new Set(this.compradoresPorCiudad.map((c) => c.ciudad))].sort();
    }
    this.actualizarQueryParams();
  }

  exportarCSV(): void {
    const filas = this.obtenerEnviosFiltrados();
    const headers = ['Comprador', 'Ciudad', 'Provincia', 'Total envíos'];
    const lineas = [headers.join(';'), ...filas.map((f) => [f.comprador_nombre, f.ciudad, f.provincia, f.total_envios].join(';'))];
    const csv = '\uFEFF' + lineas.join('\r\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `compradores-mapa-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  recargarDatos(): void {
    this.limpiarMarcadoresCompradores();
    this.provinciasMarkers.forEach((m) => m.remove());
    this.provinciasMarkers.clear();
    this.resaltarMarcadorProvincia(null);
    this.marcadorProvinciaSeleccionada = null;

    if (this.map) {
      this.map.remove();
      this.map = null;
    }
    if (this.chartCompradoresCiudadInstance) {
      this.chartCompradoresCiudadInstance.destroy();
      this.chartCompradoresCiudadInstance = null;
    }
    this.cargarDatosMapa();
  }
}

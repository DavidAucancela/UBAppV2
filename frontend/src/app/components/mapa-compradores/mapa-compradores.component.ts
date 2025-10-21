import { Component, OnInit, OnDestroy, PLATFORM_ID, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { CIUDADES_ECUADOR, CiudadEcuador, MapaResponse, CompradorMapa, CiudadConCompradores } from '../../models/mapa';

@Component({
  selector: 'app-mapa-compradores',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './mapa-compradores.component.html',
  styleUrl: './mapa-compradores.component.css'
})
export class MapaCompradoresComponent implements OnInit, OnDestroy {
  private map: any;
  private markers: any[] = [];
  private ciudadesMarkers: Map<string, any> = new Map();
  private L: any; // Leaflet será cargado dinámicamente
  
  mapaData: MapaResponse | null = null;
  loading: boolean = true;
  error: string | null = null;
  ciudadSeleccionada: string | null = null;
  isBrowser: boolean = false;
  
  // Iconos personalizados
  private iconoCiudad: any;
  private iconoComprador: any;
  
  constructor(
    private apiService: ApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(this.platformId);
  }

  async ngOnInit(): Promise<void> {
    if (this.isBrowser) {
      // Importar Leaflet solo en el navegador
      this.L = await import('leaflet');
      this.crearIconosPersonalizados();
      this.cargarDatosMapa();
    } else {
      this.loading = false;
      this.error = 'El mapa solo está disponible en el navegador';
    }
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
    }
  }

  private crearIconosPersonalizados(): void {
    if (!this.L) return;
    
    // Icono para ciudad (cluster de compradores) - SVG con ícono de ubicación
    const svgCiudad = `
      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
        <circle cx="20" cy="20" r="18" fill="#3b82f6" stroke="#1e40af" stroke-width="2" opacity="0.8"/>
        <path d="M20 10 C 16 10 13 13 13 17 C 13 22 20 30 20 30 C 20 30 27 22 27 17 C 27 13 24 10 20 10 Z M 20 20 C 18.3 20 17 18.7 17 17 C 17 15.3 18.3 14 20 14 C 21.7 14 23 15.3 23 17 C 23 18.7 21.7 20 20 20 Z" fill="white"/>
      </svg>
    `;
    
    this.iconoCiudad = this.L.icon({
      iconUrl: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svgCiudad),
      iconSize: [40, 40],
      iconAnchor: [20, 40],
      popupAnchor: [0, -40]
    });

    // Icono para comprador individual - SVG con ícono de persona más visible
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
      popupAnchor: [0, -36]
    });
  }

  private cargarDatosMapa(): void {
    this.loading = true;
    this.error = null;

    this.apiService.getMapaCompradores().subscribe({
      next: (data) => {
        console.log('Datos del mapa recibidos:', data);
        this.mapaData = data;
        this.loading = false;
        // Esperar a que Angular renderice el DOM antes de inicializar el mapa
        setTimeout(() => {
          this.inicializarMapa();
        }, 0);
      },
      error: (error) => {
        this.error = 'Error al cargar los datos del mapa';
        this.loading = false;
        console.error('Error cargando mapa:', error);
      }
    });
  }

  private inicializarMapa(): void {
    if (!this.L || !this.isBrowser) return;
    
    // Verificar que el contenedor del mapa existe
    const mapaContainer = document.getElementById('mapa-ecuador');
    if (!mapaContainer) {
      console.error('Contenedor del mapa no encontrado');
      return;
    }
    
    // Inicializar mapa centrado en Ecuador
    this.map = this.L.map('mapa-ecuador').setView([-1.8312, -78.1834], 7);

    // Agregar capa de mapa con estilo moderno
    this.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.map);

    // Agregar marcadores de ciudades
    this.agregarMarcadoresCiudades();

    // Escuchar eventos de zoom
    this.map.on('zoomend', () => {
      this.manejarCambioZoom();
    });
  }

  private agregarMarcadoresCiudades(): void {
    if (!this.mapaData) return;

    // Crear un mapa de ciudades con compradores
    const ciudadesConCompradores = new Map<string, CiudadConCompradores>();
    this.mapaData.ciudades.forEach(ciudad => {
      ciudadesConCompradores.set(ciudad.ciudad, ciudad);
    });

    // Agregar marcadores para cada ciudad de Ecuador
    CIUDADES_ECUADOR.forEach(ciudad => {
      const datosCiudad = ciudadesConCompradores.get(ciudad.nombre);
      
      if (datosCiudad && datosCiudad.total_compradores > 0) {
        this.agregarMarcadorCiudad(ciudad, datosCiudad);
      }
    });
  }

  private agregarMarcadorCiudad(ciudad: CiudadEcuador, datos: CiudadConCompradores): void {
    if (!this.L) return;
    
    const marker = this.L.marker([ciudad.latitud, ciudad.longitud], {
      icon: this.iconoCiudad
    }).addTo(this.map);

    // Popup para la ciudad con mayor tamaño
    const popupContent = this.crearPopupCiudad(ciudad, datos);
    marker.bindPopup(popupContent, { 
      maxWidth: 400,
      minWidth: 300,
      className: 'popup-ciudad-custom'
    });

    // Al hacer clic, hacer zoom y mostrar compradores individuales
    marker.on('click', () => {
      console.log(`Click en ciudad: ${ciudad.nombre}`, datos);
      this.ciudadSeleccionada = ciudad.nombre;
      this.map.setView([ciudad.latitud, ciudad.longitud], 13);
      setTimeout(() => {
        this.mostrarCompradoresIndividuales(datos);
      }, 500);
    });

    this.ciudadesMarkers.set(ciudad.nombre, marker);
  }

  private crearPopupCiudad(ciudad: CiudadEcuador, datos: CiudadConCompradores): string {
    return `
      <div class="popup-ciudad">
        <h3 style="margin: 0 0 10px 0; color: #1e40af; font-size: 18px;">📍 ${ciudad.nombre}</h3>
        <p style="margin: 5px 0; color: #4b5563;"><strong>Provincia:</strong> ${ciudad.provincia}</p>
        <p style="margin: 5px 0; color: #4b5563;"><strong>Compradores:</strong> ${datos.total_compradores}</p>
        <button 
          style="
            margin-top: 10px;
            padding: 8px 16px;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
          "
          onclick="this.closest('.leaflet-popup').remove()"
        >
          Ver compradores
        </button>
      </div>
    `;
  }

  private mostrarCompradoresIndividuales(ciudadDatos: CiudadConCompradores): void {
    if (!this.L) return;
    
    // Limpiar marcadores anteriores de compradores
    this.limpiarMarcadoresCompradores();

    // Contar compradores válidos con ubicación
    let compradoresConUbicacion = 0;

    // Agregar marcador para cada comprador
    ciudadDatos.compradores.forEach((comprador, index) => {
      // Verificar que el comprador tenga coordenadas válidas
      if (!comprador.latitud || !comprador.longitud) {
        console.warn(`Comprador ${comprador.nombre} no tiene coordenadas`, comprador);
        return; // Saltar este comprador
      }

      compradoresConUbicacion++;

      // Convertir coordenadas a números (pueden venir como strings del backend)
      const latBase = Number(comprador.latitud);
      const lngBase = Number(comprador.longitud);

      // Verificar que las conversiones sean válidas
      if (isNaN(latBase) || isNaN(lngBase)) {
        console.error(`Coordenadas inválidas para ${comprador.nombre}:`, { latitud: comprador.latitud, longitud: comprador.longitud });
        return;
      }

      // Agregar pequeño offset para evitar superposición
      const offset = this.calcularOffset(index, ciudadDatos.compradores.length);
      const lat = latBase + offset.lat;
      const lng = lngBase + offset.lng;

      const marker = this.L.marker([lat, lng], {
        icon: this.iconoComprador
      }).addTo(this.map);

      const popupContent = this.crearPopupComprador(comprador);
      marker.bindPopup(popupContent, { 
        maxWidth: 500,
        minWidth: 400,
        className: 'popup-comprador-custom'
      });

      this.markers.push(marker);
    });

    console.log(`Mostrados ${compradoresConUbicacion} compradores de ${ciudadDatos.compradores.length} total`);
  }

  private calcularOffset(index: number, total: number): { lat: number; lng: number } {
    // Distribuir compradores en círculo para evitar superposición
    const radius = 0.01; // Radio en grados (aproximadamente 1 km)
    const angle = (index / total) * 2 * Math.PI;
    
    return {
      lat: radius * Math.cos(angle),
      lng: radius * Math.sin(angle)
    };
  }

  private crearPopupComprador(comprador: CompradorMapa): string {
    const enviosHtml = comprador.envios_recientes.length > 0
      ? `
        <div style="margin-top: 10px; max-height: 200px; overflow-y: auto;">
          <h4 style="margin: 10px 0 5px 0; color: #059669; font-size: 14px;">📦 Envíos Recientes</h4>
          ${comprador.envios_recientes.map(envio => `
            <div style="
              background: #f3f4f6;
              padding: 8px;
              margin: 5px 0;
              border-radius: 4px;
              border-left: 3px solid ${this.getColorEstado(envio.estado)};
            ">
              <p style="margin: 2px 0; font-size: 12px;"><strong>HAWB:</strong> ${envio.hawb}</p>
              <p style="margin: 2px 0; font-size: 12px;"><strong>Estado:</strong> ${this.getEstadoDisplay(envio.estado)}</p>
              <p style="margin: 2px 0; font-size: 12px;"><strong>Peso:</strong> ${envio.peso_total} kg</p>
              <p style="margin: 2px 0; font-size: 12px;"><strong>Valor:</strong> $${envio.valor_total}</p>
              <p style="margin: 2px 0; font-size: 12px;"><strong>Costo:</strong> $${envio.costo_servicio}</p>
            </div>
          `).join('')}
        </div>
      `
      : '<p style="margin-top: 10px; color: #6b7280; font-style: italic;">Sin envíos registrados</p>';

    return `
      <div class="popup-comprador">
        <h3 style="margin: 0 0 10px 0; color: #059669; font-size: 18px;">👤 ${comprador.nombre}</h3>
        <div style="color: #4b5563; font-size: 14px;">
          <p style="margin: 5px 0;"><strong>Usuario:</strong> ${comprador.username}</p>
          <p style="margin: 5px 0;"><strong>Email:</strong> ${comprador.correo}</p>
          <p style="margin: 5px 0;"><strong>Teléfono:</strong> ${comprador.telefono || 'N/A'}</p>
          <p style="margin: 5px 0;"><strong>Ubicación:</strong> ${comprador.ubicacion_completa}</p>
          <p style="margin: 5px 0;"><strong>Total Envíos:</strong> <span style="
            background: #3b82f6;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: bold;
          ">${comprador.total_envios}</span></p>
        </div>
        ${enviosHtml}
      </div>
    `;
  }

  private getColorEstado(estado: string): string {
    const colores: { [key: string]: string } = {
      'pendiente': '#f59e0b',
      'en_transito': '#3b82f6',
      'entregado': '#10b981',
      'cancelado': '#ef4444'
    };
    return colores[estado] || '#6b7280';
  }

  private getEstadoDisplay(estado: string): string {
    const estados: { [key: string]: string } = {
      'pendiente': '⏳ Pendiente',
      'en_transito': '🚚 En Tránsito',
      'entregado': '✅ Entregado',
      'cancelado': '❌ Cancelado'
    };
    return estados[estado] || estado;
  }

  private limpiarMarcadoresCompradores(): void {
    this.markers.forEach(marker => marker.remove());
    this.markers = [];
  }

  private manejarCambioZoom(): void {
    const zoomLevel = this.map.getZoom();
    
    // Mostrar ciudades cuando zoom < 10, compradores cuando zoom >= 10
    if (zoomLevel < 10) {
      this.limpiarMarcadoresCompradores();
      this.ciudadSeleccionada = null;
    }
  }

  volverVista(): void {
    if (this.map) {
      this.map.setView([-1.8312, -78.1834], 7);
      this.limpiarMarcadoresCompradores();
      this.ciudadSeleccionada = null;
    }
  }

  recargarDatos(): void {
    // Limpiar marcadores existentes
    this.limpiarMarcadoresCompradores();
    this.ciudadesMarkers.forEach(marker => marker.remove());
    this.ciudadesMarkers.clear();
    
    // Si el mapa existe, eliminarlo completamente
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
    
    // Recargar datos
    this.cargarDatosMapa();
  }
}

import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject, debounceTime, distinctUntilChanged, takeUntil } from 'rxjs';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { 
  FiltrosBusquedaEnvio, 
  RespuestaBusquedaEnvio, 
  OPCIONES_ORDENAMIENTO,
  OpcionOrdenamiento 
} from '../../models/busqueda-envio';
import { Envio, EstadosEnvio, ESTADOS_LABELS } from '../../models/envio';

/**
 * Componente para búsqueda avanzada de envíos
 * Permite buscar, filtrar y visualizar envíos con múltiples criterios
 */
@Component({
  selector: 'app-busqueda-envios',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './busqueda-envios.component.html',
  styleUrl: './busqueda-envios.component.css'
})
export class BusquedaEnviosComponent implements OnInit, OnDestroy {
  // Propiedades del componente
  enviosEncontrados: Envio[] = [];
  cargando = false;
  errorMensaje = '';
  mensajeExito = '';
  sinResultados = false;
  
  // Formulario de búsqueda
  formularioBusqueda: FormGroup;
  
  // Paginación
  paginaActual = 1;
  totalPaginas = 1;
  totalResultados = 0;
  elementosPorPagina = 10;
  opcionesElementosPorPagina = [5, 10, 20, 50];
  
  // Ordenamiento
  ordenamientoActual = '-fecha_emision';
  opcionesOrdenamiento = OPCIONES_ORDENAMIENTO;
  
  // Estados y filtros
  estadosDisponibles = Object.entries(ESTADOS_LABELS).map(([valor, etiqueta]) => ({
    valor,
    etiqueta
  }));
  
  // Control de vistas
  mostrarFiltrosAvanzados = false;
  mostrarDetalleModal = false;
  envioSeleccionado: Envio | null = null;
  mostrarMenuExportar = false;
  
  // Destrucción del componente
  private destruir$ = new Subject<void>();
  
  // Debounce para búsqueda
  private busquedaSubject = new Subject<string>();

  constructor(
    private apiService: ApiService,
    public authService: AuthService,
    private fb: FormBuilder,
    private router: Router
  ) {
    // Inicializar formulario de búsqueda
    this.formularioBusqueda = this.fb.group({
      textoBusqueda: [''],
      numeroGuia: [''],
      nombreDestinatario: [''],
      ciudadDestino: [''],
      estado: [''],
      fechaDesde: [''],
      fechaHasta: ['']
    });
  }

  ngOnInit(): void {
    this.configurarBusquedaDebounce();
    this.realizarBusquedaInicial();
    this.configurarCierreMenuExportar();
  }

  ngOnDestroy(): void {
    this.destruir$.next();
    this.destruir$.complete();
  }

  /**
   * Configura el debounce para la búsqueda en tiempo real
   */
  private configurarBusquedaDebounce(): void {
    this.busquedaSubject
      .pipe(
        debounceTime(500),
        distinctUntilChanged(),
        takeUntil(this.destruir$)
      )
      .subscribe(() => {
        this.paginaActual = 1;
        this.buscarEnvios();
      });
  }

  /**
   * Realiza la búsqueda inicial al cargar el componente
   */
  private realizarBusquedaInicial(): void {
    this.buscarEnvios();
  }

  /**
   * Método principal para buscar envíos con los filtros aplicados
   */
  buscarEnvios(): void {
    this.cargando = true;
    this.errorMensaje = '';
    this.sinResultados = false;
    
    const filtros: FiltrosBusquedaEnvio = this.construirFiltros();
    
    this.apiService.buscarEnviosAvanzado(filtros).subscribe({
      next: (respuesta: RespuestaBusquedaEnvio) => {
        this.procesarResultados(respuesta);
        this.cargando = false;
        
        // Mostrar mensaje de éxito
        if (this.enviosEncontrados.length > 0) {
          this.mensajeExito = `✅ Búsqueda completada correctamente. ${this.totalResultados} envío(s) encontrado(s).`;
          setTimeout(() => this.mensajeExito = '', 3000);
        }
      },
      error: (error) => {
        console.error('Error al buscar envíos:', error);
        this.errorMensaje = 'Error al conectar con el servidor. Por favor, intente nuevamente.';
        this.cargando = false;
        this.enviosEncontrados = [];
        this.sinResultados = false;
      }
    });
  }

  /**
   * Construye el objeto de filtros a partir del formulario
   */
  private construirFiltros(): FiltrosBusquedaEnvio {
    const valores = this.formularioBusqueda.value;
    
    return {
      textoBusqueda: valores.textoBusqueda?.trim() || undefined,
      numeroGuia: valores.numeroGuia?.trim() || undefined,
      nombreDestinatario: valores.nombreDestinatario?.trim() || undefined,
      ciudadDestino: valores.ciudadDestino || undefined,
      estado: valores.estado || undefined,
      fechaDesde: valores.fechaDesde || undefined,
      fechaHasta: valores.fechaHasta || undefined,
      pagina: this.paginaActual,
      elementosPorPagina: this.elementosPorPagina,
      ordenarPor: this.ordenamientoActual
    };
  }

  /**
   * Procesa los resultados de la búsqueda
   */
  private procesarResultados(respuesta: RespuestaBusquedaEnvio): void {
    this.enviosEncontrados = respuesta.results || [];
    this.totalResultados = respuesta.count || 0;
    this.calcularPaginacion();
    
    // Verificar si no hay resultados
    if (this.enviosEncontrados.length === 0) {
      this.sinResultados = true;
    }
  }

  /**
   * Calcula la información de paginación
   */
  private calcularPaginacion(): void {
    this.totalPaginas = Math.ceil(this.totalResultados / this.elementosPorPagina);
    if (this.totalPaginas === 0) {
      this.totalPaginas = 1;
      this.paginaActual = 1;
    }
  }

  /**
   * Maneja los cambios en el campo de búsqueda general
   */
  alCambiarBusqueda(): void {
    const texto = this.formularioBusqueda.get('textoBusqueda')?.value || '';
    this.busquedaSubject.next(texto);
  }

  /**
   * Aplica los filtros y realiza la búsqueda
   */
  aplicarFiltros(): void {
    this.paginaActual = 1;
    this.buscarEnvios();
  }

  /**
   * Limpia todos los filtros y reinicia la búsqueda
   */
  limpiarFiltros(): void {
    this.formularioBusqueda.reset();
    this.ordenamientoActual = '-fecha_emision';
    this.paginaActual = 1;
    this.buscarEnvios();
    this.mensajeExito = 'Filtros limpiados correctamente.';
    setTimeout(() => this.mensajeExito = '', 2000);
  }

  /**
   * Cambia el ordenamiento y actualiza los resultados
   */
  cambiarOrdenamiento(ordenamiento: string): void {
    this.ordenamientoActual = ordenamiento;
    this.paginaActual = 1;
    this.buscarEnvios();
  }

  /**
   * Cambia la cantidad de elementos por página
   */
  cambiarElementosPorPagina(cantidad: number): void {
    this.elementosPorPagina = cantidad;
    this.paginaActual = 1;
    this.buscarEnvios();
  }

  /**
   * Alterna la visibilidad de filtros avanzados
   */
  toggleFiltrosAvanzados(): void {
    this.mostrarFiltrosAvanzados = !this.mostrarFiltrosAvanzados;
  }

  // ===== NAVEGACIÓN DE PÁGINAS =====

  /**
   * Navega a la página anterior
   */
  paginaAnterior(): void {
    if (this.paginaActual > 1) {
      this.paginaActual--;
      this.buscarEnvios();
      this.scrollAlInicio();
    }
  }

  /**
   * Navega a la página siguiente
   */
  paginaSiguiente(): void {
    if (this.paginaActual < this.totalPaginas) {
      this.paginaActual++;
      this.buscarEnvios();
      this.scrollAlInicio();
    }
  }

  /**
   * Navega a una página específica
   */
  irAPagina(pagina: number): void {
    if (pagina >= 1 && pagina <= this.totalPaginas) {
      this.paginaActual = pagina;
      this.buscarEnvios();
      this.scrollAlInicio();
    }
  }

  /**
   * Obtiene el rango de páginas a mostrar en la paginación
   */
  obtenerRangoPaginas(): number[] {
    const rango = 2; // Páginas a mostrar antes y después de la actual
    const inicio = Math.max(1, this.paginaActual - rango);
    const fin = Math.min(this.totalPaginas, this.paginaActual + rango);
    
    const paginas: number[] = [];
    for (let i = inicio; i <= fin; i++) {
      paginas.push(i);
    }
    return paginas;
  }

  /**
   * Hace scroll al inicio de la página
   */
  private scrollAlInicio(): void {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // ===== ACCIONES SOBRE ENVÍOS =====

  /**
   * Muestra los detalles completos de un envío
   */
  verDetalles(envio: Envio): void {
    this.cargando = true;
    this.apiService.getEnvio(envio.id!).subscribe({
      next: (envioCompleto) => {
        this.envioSeleccionado = envioCompleto;
        this.mostrarDetalleModal = true;
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al cargar detalles:', error);
        this.errorMensaje = 'Error al cargar los detalles del envío.';
        this.cargando = false;
      }
    });
  }

  /**
   * Cierra el modal de detalles
   */
  cerrarDetalleModal(): void {
    this.mostrarDetalleModal = false;
    this.envioSeleccionado = null;
  }

  /**
   * Descarga el comprobante de un envío en PDF
   */
  descargarComprobante(envio: Envio): void {
    this.mensajeExito = 'Generando comprobante...';
    
    this.apiService.obtenerComprobanteEnvio(envio.id!).subscribe({
      next: (blob) => {
        this.descargarArchivo(blob, `comprobante-${envio.hawb}.pdf`);
        this.mensajeExito = 'Comprobante descargado exitosamente.';
        setTimeout(() => this.mensajeExito = '', 3000);
      },
      error: (error) => {
        console.error('Error al descargar comprobante:', error);
        this.errorMensaje = 'Error al generar el comprobante. Esta funcionalidad estará disponible pronto.';
        this.mensajeExito = '';
        setTimeout(() => this.errorMensaje = '', 5000);
      }
    });
  }

  /**
   * Imprime el comprobante de un envío
   */
  imprimirComprobante(envio: Envio): void {
    this.descargarComprobante(envio);
  }

  /**
   * Muestra el envío en el mapa (si está disponible)
   */
  verEnMapa(envio: Envio): void {
    if (envio.comprador_info?.ciudad) {
      // Redirigir al mapa con filtro por ciudad
      this.router.navigate(['/mapa-compradores'], {
        queryParams: { ciudad: envio.comprador_info.ciudad }
      });
    } else {
      this.errorMensaje = 'No hay información de ubicación para este envío.';
      setTimeout(() => this.errorMensaje = '', 3000);
    }
  }

  /**
   * Configura el cierre automático del menú de exportación al hacer clic fuera
   */
  private configurarCierreMenuExportar(): void {
    document.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      const dropdown = target.closest('.dropdown-exportar');
      if (!dropdown && this.mostrarMenuExportar) {
        this.mostrarMenuExportar = false;
      }
    });
  }

  /**
   * Alterna el menú de exportación
   */
  toggleMenuExportar(): void {
    this.mostrarMenuExportar = !this.mostrarMenuExportar;
  }

  /**
   * Exporta los resultados actuales
   */
  exportarResultados(formato: 'pdf' | 'excel' | 'csv'): void {
    // Cerrar el menú
    this.mostrarMenuExportar = false;
    
    this.mensajeExito = `Exportando resultados en formato ${formato.toUpperCase()}...`;
    
    const filtros = this.construirFiltros();
    
    this.apiService.exportarResultadosBusqueda(filtros, formato).subscribe({
      next: (blob) => {
        const extension = formato === 'excel' ? 'xlsx' : formato;
        this.descargarArchivo(blob, `envios-${new Date().getTime()}.${extension}`);
        this.mensajeExito = 'Resultados exportados exitosamente.';
        setTimeout(() => this.mensajeExito = '', 3000);
      },
      error: (error) => {
        console.error('Error al exportar:', error);
        this.errorMensaje = 'Error al exportar los resultados. Esta funcionalidad estará disponible pronto.';
        this.mensajeExito = '';
        setTimeout(() => this.errorMensaje = '', 5000);
      }
    });
  }

  /**
   * Descarga un archivo blob
   */
  private descargarArchivo(blob: Blob, nombreArchivo: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = nombreArchivo;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  // ===== MÉTODOS AUXILIARES =====

  /**
   * Obtiene la etiqueta del estado
   */
  obtenerEtiquetaEstado(estado: string): string {
    return ESTADOS_LABELS[estado as keyof typeof ESTADOS_LABELS] || estado;
  }

  /**
   * Obtiene la clase CSS del estado
   */
  obtenerClaseEstado(estado: string): string {
    const clases: { [key: string]: string } = {
      'pendiente': 'estado-pendiente',
      'en_transito': 'estado-en-transito',
      'entregado': 'estado-entregado',
      'cancelado': 'estado-cancelado'
    };
    return clases[estado] || 'estado-default';
  }

  /**
   * Formatea una fecha para mostrar
   */
  formatearFecha(fecha: string | undefined): string {
    if (!fecha) return 'N/A';
    
    try {
      const fechaObj = new Date(fecha);
      return fechaObj.toLocaleDateString('es-EC', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return 'Fecha inválida';
    }
  }

  /**
   * Formatea un número como moneda
   */
  formatearMoneda(valor: number | undefined | null): string {
    if (valor === undefined || valor === null || isNaN(valor)) return '$0.00';
    const numero = Number(valor);
    return `$${numero.toFixed(2)}`;
  }

  /**
   * Formatea un peso con unidad
   */
  formatearPeso(peso: number | undefined | null): string {
    if (peso === undefined || peso === null || isNaN(peso)) return '0.00 kg';
    const numero = Number(peso);
    return `${numero.toFixed(2)} kg`;
  }

  /**
   * Verifica si hay filtros activos
   */
  tieneFiltrosActivos(): boolean {
    const valores = this.formularioBusqueda.value;
    return !!(
      valores.textoBusqueda ||
      valores.numeroGuia ||
      valores.nombreDestinatario ||
      valores.ciudadDestino ||
      valores.estado ||
      valores.fechaDesde ||
      valores.fechaHasta
    );
  }

  /**
   * Obtiene el conteo de filtros activos
   */
  contarFiltrosActivos(): number {
    const valores = this.formularioBusqueda.value;
    let conteo = 0;
    
    if (valores.textoBusqueda) conteo++;
    if (valores.numeroGuia) conteo++;
    if (valores.nombreDestinatario) conteo++;
    if (valores.ciudadDestino) conteo++;
    if (valores.estado) conteo++;
    if (valores.fechaDesde) conteo++;
    if (valores.fechaHasta) conteo++;
    
    return conteo;
  }

  /**
   * Verifica si el usuario puede ver acciones avanzadas
   */
  puedeVerAccionesAvanzadas(): boolean {
    return this.authService.isAdmin() || 
           this.authService.isGerente() || 
           this.authService.isDigitador();
  }
}


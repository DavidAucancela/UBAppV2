import { Component, OnInit, OnDestroy, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject, debounceTime, distinctUntilChanged, takeUntil, switchMap, of } from 'rxjs';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { BusquedaService } from '../../services/busqueda.service';
import {
  ConsultaSemantica,
  RespuestaSemantica,
  ResultadoSemantico,
  SugerenciaSemantica,
  SUGERENCIAS_PREDEFINIDAS,
  HistorialBusquedaSemantica,
  ConfiguracionSemantica,
  CONFIGURACION_DEFAULT,
  TipoVistaResultados,
  ModeloEmbedding,
  MODELOS_EMBEDDING_INFO,
  InfoModeloEmbedding
} from '../../models/busqueda-semantica';
import { Envio, ESTADOS_LABELS } from '../../models/envio';
import { CategoriasProducto, CATEGORIAS_LABELS } from '../../models/producto';

/**
 * Componente de Búsqueda Semántica de Envíos
 * Permite búsquedas inteligentes usando procesamiento de lenguaje natural
 */
@Component({
  selector: 'app-busqueda-semantica',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './busqueda-semantica.component.html',
  styleUrl: './busqueda-semantica.component.css'
})
export class BusquedaSemanticaComponent implements OnInit, OnDestroy {
  // Entrada/Salida para integración
  @Input() modoIntegrado = false; // Si está integrado con búsqueda tradicional
  @Output() cambiarModo = new EventEmitter<'exacta' | 'semantica'>();

  // Propiedades del componente
  textoConsulta = '';
  analizando = false;
  errorMensaje = '';
  mensajeExito = '';
  sinResultados = false;
  
  // Resultados
  resultadosSemanticos: ResultadoSemantico[] = [];
  respuestaActual: RespuestaSemantica | null = null;
  
  // Paginación
  paginaActual = 1;
  totalPaginas = 1;
  elementosPorPagina = 10;
  opcionesElementosPorPagina = [5, 10, 20, 50];
  
  // Sugerencias
  sugerenciasVisibles = false;
  sugerenciasPredefinidas = SUGERENCIAS_PREDEFINIDAS;
  sugerenciasDinamicas: SugerenciaSemantica[] = [];
  mostrandoSugerenciasPredefinidas = true;
  
  // Historial
  historialBusquedas: HistorialBusquedaSemantica[] = [];
  mostrarHistorial = false;
  historialColapsado = true;
  
  // Configuración
  configuracion: ConfiguracionSemantica = { ...CONFIGURACION_DEFAULT };
  TipoVistaResultados = TipoVistaResultados;
  
  // Filtros adicionales (opcionales)
  mostrarFiltrosAdicionales = false;
  fechaDesde = '';
  fechaHasta = '';
  estadoFiltro = '';
  ciudadDestinoFiltro = '';
  numeroGuia = '';
  nombreDestinatario = '';
  cedulaDestinatario = '';
  telefonoDestinatario = '';
  correoDestinatario = '';
  categoriaProducto = '';
  pesoMinimo = '';
  pesoMaximo = '';
  valorMinimo = '';
  valorMaximo = '';
  
  // Modelo de embedding seleccionado
  modeloSeleccionado: ModeloEmbedding = ModeloEmbedding.SMALL;
  modelosDisponibles = MODELOS_EMBEDDING_INFO;
  
  // Estados disponibles
  estadosDisponibles = Object.entries(ESTADOS_LABELS).map(([valor, etiqueta]) => ({
    valor,
    etiqueta
  }));

  // Categorías disponibles
  CategoriasProducto = CategoriasProducto;
  categoriasDisponibles = Object.entries(CATEGORIAS_LABELS).map(([valor, etiqueta]) => ({
    valor,
    etiqueta
  }));
  
  // Detalles de envío
  mostrarDetalleModal = false;
  envioSeleccionado: Envio | null = null;
  
  // Estadísticas de embeddings
  estadisticasEmbeddings: any = null;
  cargandoEstadisticas = false;
  generandoEmbeddings = false;
  
  // Math para usar en el template
  Math = Math;
  
  // Control de observables
  private destruir$ = new Subject<void>();
  private consultaSubject = new Subject<string>();

  constructor(
    private apiService: ApiService,
    public authService: AuthService,
    private busquedaService: BusquedaService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.configurarAutocompletado();
    this.cargarHistorial();
    this.cargarConfiguracion();
    // Cargar modelo seleccionado desde configuración
    this.modeloSeleccionado = this.configuracion.modeloEmbedding || ModeloEmbedding.SMALL;
    // Cargar estadísticas de embeddings
    this.cargarEstadisticasEmbeddings();
  }

  ngOnDestroy(): void {
    this.destruir$.next();
    this.destruir$.complete();
  }

  /**
   * Configura el autocompletado con debounce
   */
  private configurarAutocompletado(): void {
    this.consultaSubject
      .pipe(
        debounceTime(300),
        distinctUntilChanged(),
        switchMap(texto => {
          if (texto.length < 3) {
            return of([]);
          }
          return this.apiService.obtenerSugerenciasSemanticas(texto);
        }),
        takeUntil(this.destruir$)
      )
      .subscribe({
        next: (sugerencias) => {
          this.sugerenciasDinamicas = sugerencias;
          this.mostrandoSugerenciasPredefinidas = false;
          this.sugerenciasVisibles = sugerencias.length > 0 || this.textoConsulta.length >= 3;
        },
        error: (error) => {
          console.error('Error obteniendo sugerencias:', error);
          this.sugerenciasDinamicas = [];
        }
      });
  }

  /**
   * Se ejecuta cuando el usuario escribe en el campo
   */
  alEscribirConsulta(): void {
    if (this.textoConsulta.length === 0) {
      this.sugerenciasVisibles = false;
      this.mostrandoSugerenciasPredefinidas = true;
      return;
    }

    this.consultaSubject.next(this.textoConsulta);
  }

  /**
   * Muestra sugerencias predefinidas al hacer focus
   */
  alEnfocarCampo(): void {
    if (this.textoConsulta.length === 0) {
      this.sugerenciasVisibles = true;
      this.mostrandoSugerenciasPredefinidas = true;
    }
  }

  /**
   * Oculta sugerencias al perder focus (con delay para permitir clicks)
   */
  alDesenfocarCampo(): void {
    setTimeout(() => {
      this.sugerenciasVisibles = false;
    }, 200);
  }

  /**
   * Selecciona una sugerencia
   */
  seleccionarSugerencia(sugerencia: SugerenciaSemantica | string): void {
    const texto = typeof sugerencia === 'string' ? sugerencia : sugerencia.texto;
    this.textoConsulta = texto;
    this.sugerenciasVisibles = false;
    this.realizarBusquedaSemantica();
  }

  /**
   * Realiza la búsqueda semántica principal
   */
  realizarBusquedaSemantica(): void {
    if (!this.textoConsulta.trim()) {
      this.errorMensaje = 'Por favor, ingrese una consulta de búsqueda.';
      setTimeout(() => this.errorMensaje = '', 3000);
      return;
    }

    this.analizando = true;
    this.errorMensaje = '';
    this.mensajeExito = '';
    this.sinResultados = false;
    
    const consulta: ConsultaSemantica = {
      texto: this.textoConsulta.trim(),
      limite: this.configuracion.limiteResultados,
      modeloEmbedding: this.modeloSeleccionado,
      filtrosAdicionales: this.construirFiltrosAdicionales()
    };

    this.apiService.buscarEnviosSemantica(consulta).subscribe({
      next: (respuesta) => {
        this.procesarRespuestaSemantica(respuesta);
        // Guardar en historial con toda la información
        this.guardarEnHistorialCompleto(respuesta);
        this.analizando = false;
      },
      error: (error) => {
        console.error('Error en búsqueda semántica:', error);
        this.errorMensaje = 'Error al procesar la búsqueda semántica. Por favor, intente nuevamente.';
        this.analizando = false;
        this.resultadosSemanticos = [];
        this.sinResultados = false;
      }
    });
  }

  /**
   * Construye filtros adicionales si están activos
   */
  private construirFiltrosAdicionales(): any | undefined {
    if (!this.mostrarFiltrosAdicionales) {
      return undefined;
    }

    const filtros: any = {};
    
    // Filtros de fecha
    if (this.fechaDesde) filtros.fechaDesde = this.fechaDesde;
    if (this.fechaHasta) filtros.fechaHasta = this.fechaHasta;
    
    // Filtros de envío
    if (this.estadoFiltro) filtros.estado = this.estadoFiltro;
    if (this.numeroGuia) filtros.numeroGuia = this.numeroGuia.trim();
    
    // Filtros de destinatario/comprador
    if (this.ciudadDestinoFiltro) filtros.ciudadDestino = this.ciudadDestinoFiltro.trim();
    if (this.nombreDestinatario) filtros.nombreDestinatario = this.nombreDestinatario.trim();
    if (this.cedulaDestinatario) filtros.cedulaDestinatario = this.cedulaDestinatario.trim();
    if (this.telefonoDestinatario) filtros.telefonoDestinatario = this.telefonoDestinatario.trim();
    if (this.correoDestinatario) filtros.correoDestinatario = this.correoDestinatario.trim();
    
    // Filtros de producto
    if (this.categoriaProducto) filtros.categoriaProducto = this.categoriaProducto;
    
    // Filtros numéricos
    if (this.pesoMinimo) filtros.pesoMinimo = parseFloat(this.pesoMinimo);
    if (this.pesoMaximo) filtros.pesoMaximo = parseFloat(this.pesoMaximo);
    if (this.valorMinimo) filtros.valorMinimo = parseFloat(this.valorMinimo);
    if (this.valorMaximo) filtros.valorMaximo = parseFloat(this.valorMaximo);

    return Object.keys(filtros).length > 0 ? filtros : undefined;
  }

  /**
   * Procesa la respuesta del servidor
   */
  private procesarRespuestaSemantica(respuesta: RespuestaSemantica): void {
    this.respuestaActual = respuesta;
    
    // Filtrar por umbral de similitud
    this.resultadosSemanticos = respuesta.resultados.filter(
      r => r.puntuacionSimilitud >= this.configuracion.umbralSimilitud
    );
    
    this.sinResultados = this.resultadosSemanticos.length === 0;
    
    // Calcular paginación
    this.paginaActual = 1;
    this.calcularPaginacion();
  }
  
  /**
   * Obtiene los resultados paginados para mostrar
   */
  get resultadosPaginados(): ResultadoSemantico[] {
    const inicio = (this.paginaActual - 1) * this.elementosPorPagina;
    const fin = inicio + this.elementosPorPagina;
    return this.resultadosSemanticos.slice(inicio, fin);
  }
  
  /**
   * Calcula la información de paginación
   */
  private calcularPaginacion(): void {
    this.totalPaginas = Math.ceil(this.resultadosSemanticos.length / this.elementosPorPagina);
    if (this.totalPaginas === 0) {
      this.totalPaginas = 1;
      this.paginaActual = 1;
    }
    // Asegurar que la página actual no exceda el total
    if (this.paginaActual > this.totalPaginas) {
      this.paginaActual = this.totalPaginas;
    }
  }
  
  /**
   * Cambia la cantidad de elementos por página
   */
  cambiarElementosPorPagina(cantidad: number): void {
    this.elementosPorPagina = cantidad;
    this.paginaActual = 1;
    this.calcularPaginacion();
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
   * Navega a la página anterior
   */
  paginaAnterior(): void {
    if (this.paginaActual > 1) {
      this.paginaActual--;
      this.scrollAlInicio();
    }
  }
  
  /**
   * Navega a la página siguiente
   */
  paginaSiguiente(): void {
    if (this.paginaActual < this.totalPaginas) {
      this.paginaActual++;
      this.scrollAlInicio();
    }
  }
  
  /**
   * Navega a una página específica
   */
  irAPagina(pagina: number): void {
    if (pagina >= 1 && pagina <= this.totalPaginas) {
      this.paginaActual = pagina;
      this.scrollAlInicio();
    }
  }
  
  /**
   * Hace scroll al inicio de la página
   */
  private scrollAlInicio(): void {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  /**
   * Guarda la búsqueda en el historial (método simplificado)
   */
  private guardarEnHistorial(consulta: string, totalResultados: number): void {
    this.apiService.guardarHistorialSemantico(consulta, totalResultados).subscribe({
      next: () => {
        this.cargarHistorial();
      },
      error: (error) => {
        console.error('Error guardando historial:', error);
      }
    });
  }

  /**
   * Guarda la búsqueda completa en el historial con toda la información
   */
  private guardarEnHistorialCompleto(respuesta: RespuestaSemantica): void {
    // El backend ya guarda automáticamente en busqueda_semantica, solo recargamos
    this.cargarHistorial();
  }

  /**
   * Carga el historial de búsquedas
   */
  cargarHistorial(): void {
    this.apiService.obtenerHistorialSemantico().subscribe({
      next: (historial) => {
        if (historial && Array.isArray(historial)) {
          this.historialBusquedas = historial.slice(0, 10); // Últimas 10
          console.log('Historial cargado:', this.historialBusquedas.length, 'búsquedas');
        } else {
          console.warn('Historial recibido no es un array:', historial);
          this.historialBusquedas = [];
        }
      },
      error: (error) => {
        console.error('Error cargando historial:', error);
        this.historialBusquedas = [];
        // Mostrar error al usuario si es necesario
        if (error.status !== 401) { // No mostrar error si es de autenticación
          this.errorMensaje = 'Error al cargar el historial de búsquedas';
        }
      }
    });
  }

  /**
   * Selecciona una búsqueda del historial
   */
  usarDelHistorial(busqueda: HistorialBusquedaSemantica): void {
    this.textoConsulta = busqueda.consulta;
    this.mostrarHistorial = false;
    this.realizarBusquedaSemantica();
  }

  /**
   * Limpia el historial
   */
  limpiarHistorial(): void {
    if (confirm('¿Está seguro de que desea limpiar el historial de búsquedas?')) {
      this.apiService.limpiarHistorialSemantico().subscribe({
        next: () => {
          this.historialBusquedas = [];
        },
        error: (error) => {
          console.error('Error limpiando historial:', error);
          this.errorMensaje = 'Error al limpiar el historial.';
        }
      });
    }
  }

  /**
   * Limpia la consulta y resultados
   */
  limpiarBusqueda(): void {
    this.textoConsulta = '';
    this.resultadosSemanticos = [];
    this.respuestaActual = null;
    this.sinResultados = false;
    this.errorMensaje = '';
    this.mensajeExito = '';
  }

  /**
   * Alterna visibilidad de filtros adicionales
   */
  toggleFiltrosAdicionales(): void {
    this.mostrarFiltrosAdicionales = !this.mostrarFiltrosAdicionales;
  }

  /**
   * Alterna visibilidad del historial
   */
  toggleHistorial(): void {
    this.mostrarHistorial = !this.mostrarHistorial;
    // Recargar historial cuando se abre el panel
    if (this.mostrarHistorial) {
      this.cargarHistorial();
    }
  }

  /**
   * Cambia el tipo de vista de resultados
   */
  cambiarTipoVista(tipo: TipoVistaResultados): void {
    this.configuracion.tipoVista = tipo;
    this.guardarConfiguracion();
  }

  /**
   * Abre el modal de detalles de un envío
   */
  verDetalles(resultado: ResultadoSemantico | Envio): void {
    if ('envio' in resultado) {
      this.envioSeleccionado = resultado.envio;
    } else {
      this.envioSeleccionado = resultado;
    }
    this.mostrarDetalleModal = true;
  }

  /**
   * Descarga el comprobante de un envío
   */
  descargarComprobante(envio: Envio): void {
    if (!envio.id) {
      this.errorMensaje = 'No se puede descargar el comprobante de este envío';
      setTimeout(() => this.errorMensaje = '', 3000);
      return;
    }

    this.mensajeExito = 'Generando comprobante...';
    
    this.apiService.obtenerComprobanteEnvio(envio.id).subscribe({
      next: (blob) => {
        const nombreArchivo = `comprobante-${envio.hawb}.pdf`;
        this.descargarArchivo(blob, nombreArchivo);
        this.mensajeExito = 'Comprobante descargado exitosamente.';
        setTimeout(() => this.mensajeExito = '', 3000);
      },
      error: (error) => {
        console.error('Error descargando comprobante:', error);
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
    // Usar el mismo método de descarga y abrir en nueva ventana para imprimir
    this.descargarComprobante(envio);
  }

  /**
   * Muestra el envío en el mapa (si está disponible)
   */
  verEnMapa(envio: Envio): void {
    if (envio.comprador_info?.ciudad) {
      this.router.navigate(['/mapa-compradores'], {
        queryParams: { ciudad: envio.comprador_info.ciudad }
      });
    } else {
      this.errorMensaje = 'No hay información de ubicación para este envío.';
      setTimeout(() => this.errorMensaje = '', 3000);
    }
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

  /**
   * Limpia todos los filtros adicionales
   */
  limpiarFiltrosAdicionales(): void {
    this.fechaDesde = '';
    this.fechaHasta = '';
    this.estadoFiltro = '';
    this.ciudadDestinoFiltro = '';
    this.numeroGuia = '';
    this.nombreDestinatario = '';
    this.cedulaDestinatario = '';
    this.telefonoDestinatario = '';
    this.correoDestinatario = '';
    this.categoriaProducto = '';
    this.pesoMinimo = '';
    this.pesoMaximo = '';
    this.valorMinimo = '';
    this.valorMaximo = '';
  }

  /**
   * Cierra el modal de detalles
   */
  cerrarDetalleModal(): void {
    this.mostrarDetalleModal = false;
    this.envioSeleccionado = null;
  }

  /**
   * Proporciona feedback sobre un resultado
   */
  enviarFeedback(resultado: ResultadoSemantico, esRelevante: boolean): void {
    if (!resultado.envio.id) return;

    this.apiService.enviarFeedbackSemantico(resultado.envio.id, esRelevante).subscribe({
      next: () => {
        this.mensajeExito = esRelevante ? 
          '👍 Gracias por tu feedback positivo' : 
          '👎 Gracias, trabajaremos para mejorar los resultados';
        setTimeout(() => this.mensajeExito = '', 2000);
      },
      error: (error) => {
        console.error('Error enviando feedback:', error);
      }
    });
  }

  /**
   * Cambia entre modo búsqueda exacta y semántica
   */
  cambiarAModoExacto(): void {
    this.cambiarModo.emit('exacta');
  }

  // ===== MÉTODOS AUXILIARES =====

  /**
   * Obtiene clase CSS según puntuación de similitud
   */
  obtenerClaseSimilitud(puntuacion: number): string {
    if (puntuacion >= 0.8) return 'similitud-alta';
    if (puntuacion >= 0.5) return 'similitud-media';
    return 'similitud-baja';
  }

  /**
   * Obtiene color de barra de progreso según similitud
   */
  obtenerColorSimilitud(puntuacion: number): string {
    if (puntuacion >= 0.8) return '#27ae60'; // Verde
    if (puntuacion >= 0.5) return '#f39c12'; // Naranja
    return '#e74c3c'; // Rojo
  }

  /**
   * Obtiene etiqueta del estado
   */
  obtenerEtiquetaEstado(estado: string): string {
    return ESTADOS_LABELS[estado as keyof typeof ESTADOS_LABELS] || estado;
  }

  /**
   * Obtiene clase CSS del estado
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
   * Formatea fecha para mostrar
   */
  formatearFecha(fecha: string | undefined): string {
    if (!fecha) return 'N/A';
    
    try {
      const fechaObj = new Date(fecha);
      return fechaObj.toLocaleDateString('es-EC', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return 'Fecha inválida';
    }
  }

  /**
   * Formatea moneda
   */
  formatearMoneda(valor: number | string | undefined | null): string {
    if (valor === undefined || valor === null || valor === '') return '$0.00';
    
    // Convertir a número si es string
    const valorNumero = typeof valor === 'string' ? parseFloat(valor) : valor;
    
    // Verificar si es un número válido
    if (isNaN(valorNumero)) return '$0.00';
    
    return `$${valorNumero.toFixed(2)}`;
  }

  /**
   * Formatea peso
   */
  formatearPeso(peso: number | string | undefined | null): string {
    if (peso === undefined || peso === null || peso === '') return '0 kg';
    
    // Convertir a número si es string
    const pesoNumero = typeof peso === 'string' ? parseFloat(peso) : peso;
    
    // Verificar si es un número válido
    if (isNaN(pesoNumero)) return '0 kg';
    
    return `${pesoNumero.toFixed(2)} kg`;
  }

  /**
   * Formatea porcentaje de similitud
   */
  formatearPorcentajeSimilitud(puntuacion: number): string {
    return `${(puntuacion * 100).toFixed(0)}%`;
  }

  /**
   * Formatea costo en USD
   */
  formatearCosto(costo: number | undefined): string {
    if (costo === undefined || costo === null) return 'N/A';
    if (costo < 0.0001) {
      return `$${(costo * 1000).toFixed(4)} mil USD`;
    }
    return `$${costo.toFixed(6)} USD`;
  }

  /**
   * Obtiene información del modelo seleccionado
   */
  obtenerInfoModelo(modelo: ModeloEmbedding): InfoModeloEmbedding | undefined {
    return this.modelosDisponibles.find(m => m.modelo === modelo);
  }

  /**
   * Cambia el modelo de embedding seleccionado
   */
  cambiarModeloEmbedding(modelo: ModeloEmbedding): void {
    this.modeloSeleccionado = modelo;
    this.configuracion.modeloEmbedding = modelo;
    this.guardarConfiguracion();
  }

  /**
   * Carga configuración guardada
   */
  private cargarConfiguracion(): void {
    const configGuardada = localStorage.getItem('configuracionSemantica');
    if (configGuardada) {
      try {
        this.configuracion = { ...CONFIGURACION_DEFAULT, ...JSON.parse(configGuardada) };
      } catch (error) {
        console.error('Error cargando configuración:', error);
      }
    }
  }

  /**
   * Guarda configuración en localStorage
   */
  private guardarConfiguracion(): void {
    localStorage.setItem('configuracionSemantica', JSON.stringify(this.configuracion));
  }

  // ===== DESCARGA DE PDF =====

  /**
   * Descarga el PDF de la búsqueda actual
   */
  descargarPdfBusquedaActual(): void {
    if (!this.respuestaActual || !this.respuestaActual.busquedaId) {
      this.errorMensaje = 'No hay búsqueda activa para descargar';
      setTimeout(() => this.errorMensaje = '', 3000);
      return;
    }

    this.descargarPdfBusqueda(this.respuestaActual.busquedaId);
  }

  /**
   * Descarga el PDF de una búsqueda del historial
   * @param busqueda Búsqueda del historial
   */
  descargarPdfHistorial(busqueda: HistorialBusquedaSemantica, event?: Event): void {
    if (event) {
      event.stopPropagation(); // Evitar que se ejecute usarDelHistorial
    }

    if (!busqueda.id) {
      this.errorMensaje = 'No se puede descargar el PDF de esta búsqueda';
      setTimeout(() => this.errorMensaje = '', 3000);
      return;
    }

    this.descargarPdfBusqueda(busqueda.id);
  }

  /**
   * Método común para descargar PDF
   * @param busquedaId ID de la búsqueda
   */
  private descargarPdfBusqueda(busquedaId: number): void {
    this.mensajeExito = '⏳ Generando PDF...';
    
    this.busquedaService.descargarPdfBusquedaSemantica(busquedaId).subscribe({
      next: (blob) => {
        // Generar nombre del archivo
        const fecha = new Date().toISOString().split('T')[0];
        const filename = `busqueda_semantica_${busquedaId}_${fecha}.pdf`;
        
        // Descargar archivo
        this.busquedaService.descargarArchivo(blob, filename);
        
        this.mensajeExito = '✅ PDF descargado correctamente';
        setTimeout(() => this.mensajeExito = '', 3000);
      },
      error: (error) => {
        console.error('Error descargando PDF:', error);
        this.errorMensaje = 'Error al generar el PDF. Por favor, intente nuevamente.';
        setTimeout(() => this.errorMensaje = '', 5000);
      }
    });
  }

  /**
   * Verifica si la búsqueda actual tiene PDF disponible
   */
  tienePdfDisponible(): boolean {
    return !!(this.respuestaActual && this.respuestaActual.busquedaId && this.resultadosSemanticos.length > 0);
  }

  // ===== GESTIÓN DE EMBEDDINGS =====

  /**
   * Carga las estadísticas de embeddings
   */
  cargarEstadisticasEmbeddings(): void {
    this.cargandoEstadisticas = true;
    this.apiService.obtenerEstadisticasEmbeddings().subscribe({
      next: (estadisticas) => {
        this.estadisticasEmbeddings = estadisticas;
        this.cargandoEstadisticas = false;
      },
      error: (error) => {
        console.error('Error cargando estadísticas de embeddings:', error);
        this.cargandoEstadisticas = false;
      }
    });
  }

  /**
   * Genera embeddings para envíos pendientes
   */
  generarEmbeddingsPendientes(): void {
    if (!confirm('¿Desea generar embeddings para los envíos que no tienen embedding? Este proceso puede tardar varios minutos.')) {
      return;
    }

    this.generandoEmbeddings = true;
    this.mensajeExito = 'Generando embeddings... Esto puede tardar varios minutos.';
    this.errorMensaje = '';

    this.apiService.generarEmbeddingsPendientes(false, this.modeloSeleccionado).subscribe({
      next: (resultado) => {
        this.generandoEmbeddings = false;
        if (resultado.error) {
          this.errorMensaje = resultado.error;
          this.mensajeExito = '';
        } else {
          this.mensajeExito = `Embeddings generados: ${resultado.procesados || 0} procesados, ${resultado.errores || 0} errores`;
          // Recargar estadísticas después de generar
          setTimeout(() => {
            this.cargarEstadisticasEmbeddings();
          }, 2000);
        }
        setTimeout(() => {
          this.mensajeExito = '';
          this.errorMensaje = '';
        }, 5000);
      },
      error: (error) => {
        console.error('Error generando embeddings:', error);
        this.generandoEmbeddings = false;
        this.errorMensaje = 'Error al generar embeddings. Por favor, intente nuevamente.';
        this.mensajeExito = '';
        setTimeout(() => this.errorMensaje = '', 5000);
      }
    });
  }
}




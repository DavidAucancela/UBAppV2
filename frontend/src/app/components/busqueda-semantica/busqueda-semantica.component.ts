import { Component, OnInit, OnDestroy, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject, debounceTime, distinctUntilChanged, takeUntil, switchMap, of } from 'rxjs';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
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
  
  // Sugerencias
  sugerenciasVisibles = false;
  sugerenciasPredefinidas = SUGERENCIAS_PREDEFINIDAS;
  sugerenciasDinamicas: SugerenciaSemantica[] = [];
  mostrandoSugerenciasPredefinidas = true;
  
  // Historial
  historialBusquedas: HistorialBusquedaSemantica[] = [];
  mostrarHistorial = false;
  
  // Configuración
  configuracion: ConfiguracionSemantica = { ...CONFIGURACION_DEFAULT };
  TipoVistaResultados = TipoVistaResultados;
  
  // Filtros adicionales (opcionales)
  mostrarFiltrosAdicionales = false;
  fechaDesde = '';
  fechaHasta = '';
  estadoFiltro = '';
  ciudadDestinoFiltro = '';
  
  // Modelo de embedding seleccionado
  modeloSeleccionado: ModeloEmbedding = ModeloEmbedding.SMALL;
  modelosDisponibles = MODELOS_EMBEDDING_INFO;
  
  // Estados disponibles
  estadosDisponibles = Object.entries(ESTADOS_LABELS).map(([valor, etiqueta]) => ({
    valor,
    etiqueta
  }));
  
  // Detalles de envío
  mostrarDetalleModal = false;
  envioSeleccionado: Envio | null = null;
  
  // Control de observables
  private destruir$ = new Subject<void>();
  private consultaSubject = new Subject<string>();

  constructor(
    private apiService: ApiService,
    public authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.configurarAutocompletado();
    this.cargarHistorial();
    this.cargarConfiguracion();
    // Cargar modelo seleccionado desde configuración
    this.modeloSeleccionado = this.configuracion.modeloEmbedding || ModeloEmbedding.SMALL;
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
        
        const costoTexto = respuesta.costoConsulta ? 
          ` Costo: $${respuesta.costoConsulta.toFixed(6)} USD` : '';
        this.mensajeExito = `✅ Búsqueda semántica completada correctamente. ${respuesta.totalEncontrados} resultado(s) encontrado(s) en ${respuesta.tiempoRespuesta}ms.${costoTexto}`;
        setTimeout(() => this.mensajeExito = '', 5000);
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
    
    if (this.fechaDesde) filtros.fechaDesde = this.fechaDesde;
    if (this.fechaHasta) filtros.fechaHasta = this.fechaHasta;
    if (this.estadoFiltro) filtros.estado = this.estadoFiltro;
    if (this.ciudadDestinoFiltro) filtros.ciudadDestino = this.ciudadDestinoFiltro;

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
        this.historialBusquedas = historial.slice(0, 10); // Últimas 10
      },
      error: (error) => {
        console.error('Error cargando historial:', error);
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
          this.mensajeExito = 'Historial limpiado correctamente.';
          setTimeout(() => this.mensajeExito = '', 2000);
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
  verDetalles(resultado: ResultadoSemantico): void {
    this.envioSeleccionado = resultado.envio;
    this.mostrarDetalleModal = true;
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
  formatearMoneda(valor: number | undefined): string {
    if (valor === undefined || valor === null) return '$0.00';
    return `$${valor.toFixed(2)}`;
  }

  /**
   * Formatea peso
   */
  formatearPeso(peso: number | undefined): string {
    if (peso === undefined || peso === null) return '0 kg';
    return `${peso.toFixed(2)} kg`;
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
}




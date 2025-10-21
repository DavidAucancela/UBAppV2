import { Envio } from './envio';

/**
 * Interface para consulta de búsqueda semántica
 */
export interface ConsultaSemantica {
  texto: string;
  filtrosAdicionales?: FiltrosAdicionalesSemantica;
  limite?: number;
}

/**
 * Interface para filtros adicionales opcionales
 */
export interface FiltrosAdicionalesSemantica {
  fechaDesde?: string;
  fechaHasta?: string;
  estado?: string;
  ciudadOrigen?: string;
  ciudadDestino?: string;
}

/**
 * Interface para resultado individual de búsqueda semántica
 */
export interface ResultadoSemantico {
  envio: Envio;
  puntuacionSimilitud: number; // 0.0 a 1.0
  fragmentosRelevantes: string[]; // Fragmentos de texto que coinciden
  razonRelevancia?: string; // Explicación de por qué es relevante
}

/**
 * Interface para respuesta de búsqueda semántica
 */
export interface RespuestaSemantica {
  consulta: string;
  resultados: ResultadoSemantico[];
  totalEncontrados: number;
  tiempoRespuesta: number; // en milisegundos
  modeloUtilizado?: string; // Nombre del modelo de IA usado
}

/**
 * Interface para sugerencias dinámicas
 */
export interface SugerenciaSemantica {
  texto: string;
  icono?: string;
  categoria: 'estado' | 'ciudad' | 'fecha' | 'general';
  ejemplos?: string[];
}

/**
 * Sugerencias predefinidas para ayudar al usuario
 */
export const SUGERENCIAS_PREDEFINIDAS: SugerenciaSemantica[] = [
  {
    texto: 'Envíos entregados en Quito esta semana',
    icono: 'fa-check-circle',
    categoria: 'estado',
    ejemplos: [
      'paquetes entregados en Guayaquil',
      'envíos completados en Cuenca el mes pasado'
    ]
  },
  {
    texto: 'Paquetes pendientes para Guayaquil',
    icono: 'fa-clock',
    categoria: 'estado',
    ejemplos: [
      'envíos en tránsito a Quito',
      'paquetes por entregar en Manta'
    ]
  },
  {
    texto: 'Buscar envíos de María Gómez con retraso',
    icono: 'fa-user',
    categoria: 'general',
    ejemplos: [
      'envíos de Juan Pérez',
      'paquetes retrasados de Ana López'
    ]
  },
  {
    texto: 'Envíos urgentes de la última semana',
    icono: 'fa-shipping-fast',
    categoria: 'fecha',
    ejemplos: [
      'envíos de ayer',
      'paquetes de hoy',
      'envíos del último mes'
    ]
  },
  {
    texto: 'Paquetes pesados enviados a la costa',
    icono: 'fa-weight-hanging',
    categoria: 'general',
    ejemplos: [
      'envíos grandes',
      'paquetes livianos'
    ]
  },
  {
    texto: 'Envíos cancelados este mes',
    icono: 'fa-times-circle',
    categoria: 'estado',
    ejemplos: [
      'envíos rechazados',
      'paquetes devueltos'
    ]
  }
];

/**
 * Interface para historial de búsquedas semánticas
 */
export interface HistorialBusquedaSemantica {
  id: string;
  consulta: string;
  fecha: Date;
  totalResultados: number;
}

/**
 * Interface para métricas de búsqueda semántica
 */
export interface MetricasSemanticas {
  busquedasTotales: number;
  busquedasExitosas: number;
  tiempoPromedioRespuesta: number;
  consultasMasComunes: { consulta: string; frecuencia: number }[];
}

/**
 * Enum para tipos de vista de resultados
 */
export enum TipoVistaResultados {
  LISTA = 'lista',
  TARJETAS = 'tarjetas',
  COMPACTA = 'compacta'
}

/**
 * Interface para configuración de búsqueda semántica
 */
export interface ConfiguracionSemantica {
  mostrarPuntuacion: boolean;
  mostrarFragmentos: boolean;
  mostrarRazonRelevancia: boolean;
  limiteResultados: number;
  umbralSimilitud: number; // 0.0 a 1.0, mínimo score para mostrar
  tipoVista: TipoVistaResultados;
}

/**
 * Configuración por defecto
 */
export const CONFIGURACION_DEFAULT: ConfiguracionSemantica = {
  mostrarPuntuacion: true,
  mostrarFragmentos: true,
  mostrarRazonRelevancia: true,
  limiteResultados: 20,
  umbralSimilitud: 0.3,
  tipoVista: TipoVistaResultados.TARJETAS
};




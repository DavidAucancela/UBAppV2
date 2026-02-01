import { Envio } from './envio';

/**
 * Modelos de embedding disponibles de OpenAI
 */
export enum ModeloEmbedding {
  SMALL = 'text-embedding-3-small',
  LARGE = 'text-embedding-3-large',
  ADA = 'text-embedding-ada-002'
}

/**
 * Información sobre modelos de embedding
 */
export interface InfoModeloEmbedding {
  modelo: ModeloEmbedding;
  nombre: string;
  dimensiones: number;
  costoPor1KTokens: number; // Costo en USD por 1,000 tokens
  descripcion: string;
}

/**
 * Información de modelos disponibles
 */
export const MODELOS_EMBEDDING_INFO: InfoModeloEmbedding[] = [
  {
    modelo: ModeloEmbedding.SMALL,
    nombre: 'Small',
    dimensiones: 1536,
    costoPor1KTokens: 0.00002,
    descripcion: 'Mayor precisión de búsqueda, menor costo'
  },
  {
    modelo: ModeloEmbedding.LARGE,
    nombre: 'Large',
    dimensiones: 3072,
    costoPor1KTokens: 0.00013,
    descripcion: 'Máxima precisión de búsqueda, mayor costo'
  },
  {
    modelo: ModeloEmbedding.ADA,
    nombre: 'Ada',
    dimensiones: 1536,
    costoPor1KTokens: 0.0001,
    descripcion: 'Precisión media de búsqueda, costo intermedio'
  }
];

/**
 * Interface para consulta de búsqueda semántica
 */
export interface ConsultaSemantica {
  texto: string;
  modeloEmbedding?: ModeloEmbedding; // Modelo de embedding a usar
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
  puntuacionSimilitud: number; // 0.0 a 1.0 (Score Combinado)
  
  // Múltiples métricas de similitud
  cosineSimilarity: number;      // Similitud coseno [-1, 1]
  dotProduct: number;            // Producto punto [0, infinito]
  euclideanDistance: number;     // Distancia euclidiana [0, infinito]
  manhattanDistance?: number;    // Distancia Manhattan [0, infinito]
  scoreCombinado?: number;       // Score normalizado [0, 1]
  
  // Métricas de boost
  boostExactas?: number;
  boostProductos?: number;
  coincidenciasExactas?: number;
  
  // NUEVO: Análisis comparativo de métricas
  analisisMetricas?: AnalisisMetricas;
  
  // Información contextual
  fragmentosRelevantes: string[];   // Fragmentos de texto que coinciden
  razonRelevancia?: string;         // Explicación de por qué es relevante
  textoIndexado?: string;           // Texto completo que fue indexado
}

/**
 * Interface para análisis comparativo de métricas de similitud
 */
export interface AnalisisMetricas {
  metricaSeleccionada: string;
  justificacion: {
    teorica: string;
    practica: string;
    ventajas: string[];
    referenciasAcademicas: string[];
  };
  comparacion: {
    cosine: MetricaComparacion;
    dotProduct: MetricaComparacion;
    euclidean: MetricaDistancia;
    manhattan: MetricaDistancia;
  };
  scoreCombinado: {
    valor: number;
    porcentaje: number;
    descripcion: string;
    formula: string;
    componentes: {
      cosineNormalizado: number;
      boostExactas: number;
      contribucionBoost: string;
    };
    ventaja: string;
  };
  conclusion: {
    metricaOptima: string;
    razon: string;
    evidencia: {
      correlacionEuclidean: number;
      diferenciaPorcentual: number;
      nota: string;
    };
    recomendacion: string;
  };
}

/**
 * Interface para métrica de similitud (cosine, dotProduct)
 */
export interface MetricaComparacion {
  valor: number;
  rango: string;
  porcentaje?: number;
  interpretacion: string;
  nivelRelevancia?: string;
  ventaja?: string;
  limitacion?: string;
  problema?: string;
  formula: string;
  casoUso?: string;
  cuandoUsar?: string;
}

/**
 * Interface para métrica de distancia (euclidean, manhattan)
 */
export interface MetricaDistancia {
  valor: number;
  rango: string;
  similitudNormalizada: number;
  porcentajeNormalizado: number;
  interpretacion: string;
  limitacion: string;
  problema: string;
  formula: string;
  cuandoUsar: string;
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
  costoConsulta?: number; // Costo de la consulta en USD
  tokensUtilizados?: number; // Número de tokens utilizados
  busquedaId?: number; // ID de la búsqueda guardada en historial
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
  id: number;
  consulta: string;
  fecha: Date | string;
  totalResultados: number;
  tiempoRespuesta?: number;
  modeloUtilizado?: string;
  costoConsulta?: number;
  tokensUtilizados?: number;
  filtrosAplicados?: any;
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
 * Métricas de similitud disponibles para ordenamiento
 */
export enum MetricaSimilitud {
  COSINE = 'cosine_similarity',
  DOT_PRODUCT = 'dot_product',
  EUCLIDEAN = 'euclidean_distance',
  MANHATTAN = 'manhattan_distance'
}

/**
 * Interface para configuración de búsqueda semántica
 */
export interface ConfiguracionSemantica {
  mostrarPuntuacion: boolean;
  mostrarFragmentos: boolean;
  mostrarRazonRelevancia: boolean;
  mostrarMetricasDetalladas: boolean;  // Mostrar todas las métricas de similitud
  limiteResultados: number;
  umbralSimilitud: number; // 0.0 a 1.0, mínimo score para mostrar
  tipoVista: TipoVistaResultados;
  modeloEmbedding: ModeloEmbedding; // Modelo de embedding por defecto
  mostrarCosto: boolean; // Mostrar costo de consulta
  metricaOrdenamiento: MetricaSimilitud; // Métrica principal para ordenar
}

/**
 * Configuración por defecto
 */
export const CONFIGURACION_DEFAULT: ConfiguracionSemantica = {
  mostrarPuntuacion: true,
  mostrarFragmentos: true,
  mostrarRazonRelevancia: true,
  mostrarMetricasDetalladas: false,
  limiteResultados: 20,
  umbralSimilitud: 0.3,
  tipoVista: TipoVistaResultados.TARJETAS,
  modeloEmbedding: ModeloEmbedding.SMALL,
  mostrarCosto: true,
  metricaOrdenamiento: MetricaSimilitud.COSINE
};




import { Envio } from './envio';

/**
 * Interface para los filtros de búsqueda de envíos
 */
export interface FiltrosBusquedaEnvio {
  // Búsqueda general
  textoBusqueda?: string;
  
  // Filtros específicos
  numeroGuia?: string;
  nombreRemitente?: string;
  nombreDestinatario?: string;
  ciudadOrigen?: string;
  ciudadDestino?: string;
  estado?: string;
  
  // Filtros por fecha
  fechaDesde?: string;
  fechaHasta?: string;
  
  // Paginación y ordenamiento
  pagina?: number;
  elementosPorPagina?: number;
  ordenarPor?: string;
  ordenDireccion?: 'asc' | 'desc';
}

/**
 * Interface para la respuesta de búsqueda paginada
 */
export interface RespuestaBusquedaEnvio {
  count: number;
  next: string | null;
  previous: string | null;
  results: Envio[];
}

/**
 * Interface para estadísticas de búsqueda
 */
export interface EstadisticasBusqueda {
  totalResultados: number;
  porEstado: {
    [key: string]: number;
  };
  pesoTotal: number;
  valorTotal: number;
  costoServicioTotal: number;
}

/**
 * Interface para opciones de ordenamiento
 */
export interface OpcionOrdenamiento {
  valor: string;
  etiqueta: string;
}

/**
 * Opciones de ordenamiento disponibles
 */
export const OPCIONES_ORDENAMIENTO: OpcionOrdenamiento[] = [
  { valor: '-fecha_emision', etiqueta: 'Fecha más reciente' },
  { valor: 'fecha_emision', etiqueta: 'Fecha más antigua' },
  { valor: 'hawb', etiqueta: 'Número de guía (A-Z)' },
  { valor: '-hawb', etiqueta: 'Número de guía (Z-A)' },
  { valor: '-valor_total', etiqueta: 'Valor mayor' },
  { valor: 'valor_total', etiqueta: 'Valor menor' },
  { valor: '-peso_total', etiqueta: 'Peso mayor' },
  { valor: 'peso_total', etiqueta: 'Peso menor' },
  { valor: 'estado', etiqueta: 'Estado (A-Z)' },
];

/**
 * Enum para tipos de exportación
 */
export enum TipoExportacion {
  PDF = 'pdf',
  EXCEL = 'excel',
  CSV = 'csv'
}

/**
 * Interface para configuración de exportación
 */
export interface ConfiguracionExportacion {
  tipo: TipoExportacion;
  incluirProductos: boolean;
  incluirComprador: boolean;
  formatoFecha?: string;
}


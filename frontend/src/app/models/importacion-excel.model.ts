/**
 * Modelo para gestión de importaciones de archivos Excel
 */

export interface ImportacionExcel {
  id: number;
  archivo: string;
  nombre_original: string;
  estado: EstadoImportacion;
  estado_nombre: string;
  usuario: number;
  nombre_usuario: string;
  total_registros: number;
  registros_validos: number;
  registros_errores: number;
  registros_duplicados: number;
  registros_procesados: number;
  errores_validacion: { [key: string]: ErrorValidacion[] };
  columnas_mapeadas: { [key: string]: string };
  registros_seleccionados: number[];
  mensaje_resultado?: string;
  fecha_creacion: string;
  fecha_actualizacion: string;
  fecha_completado?: string;
  porcentaje_exito: number;
}

export type EstadoImportacion = 'pendiente' | 'validando' | 'validado' | 'procesando' | 'completado' | 'error';

export interface ErrorValidacion {
  columna: string;
  mensaje: string;
}

export interface PreviewExcel {
  columnas: string[];
  filas: FilaExcel[];
  total_filas: number;
  errores_detectados?: ErrorDetectado[];
  duplicados?: number[];
}

export interface FilaExcel {
  _indice: number;
  [key: string]: any;
}

export interface ErrorDetectado {
  fila: number;
  columna: string;
  error: string;
}

export interface MapeoColumnas {
  [columnaExcel: string]: string;
}

export interface ResultadoValidacion {
  mensaje: string;
  estadisticas: EstadisticasImportacion;
  errores: ErrorDetectado[];
}

export interface ResultadoProcesamiento {
  mensaje: string;
  estadisticas: EstadisticasImportacion;
}

export interface EstadisticasImportacion {
  total_registros: number;
  registros_validos: number;
  registros_errores: number;
  registros_duplicados?: number;
  registros_procesados?: number;
}

export interface ReporteErrores {
  importacion_id: number;
  nombre_archivo: string;
  fecha: string;
  estado: string;
  estadisticas: EstadisticasImportacion;
  errores: { [key: string]: ErrorValidacion[] };
  mensaje: string;
}

// Campos disponibles para mapear en el Excel
export interface CampoDisponible {
  valor: string;
  etiqueta: string;
  descripcion: string;
  requerido: boolean;
}

export const CAMPOS_DISPONIBLES: CampoDisponible[] = [
  { valor: 'hawb', etiqueta: 'HAWB', descripcion: 'Número de guía (obligatorio)', requerido: true },
  { valor: 'peso_total', etiqueta: 'Peso Total', descripcion: 'Peso total del envío en kg', requerido: false },
  { valor: 'cantidad_total', etiqueta: 'Cantidad Total', descripcion: 'Cantidad total de productos', requerido: false },
  { valor: 'valor_total', etiqueta: 'Valor Total', descripcion: 'Valor total del envío en USD', requerido: false },
  { valor: 'estado', etiqueta: 'Estado', descripcion: 'Estado del envío (pendiente, en_transito, entregado)', requerido: false },
  { valor: 'observaciones', etiqueta: 'Observaciones', descripcion: 'Notas adicionales del envío', requerido: false },
  { valor: 'descripcion', etiqueta: 'Descripción Producto', descripcion: 'Descripción del producto', requerido: false },
  { valor: 'peso', etiqueta: 'Peso Producto', descripcion: 'Peso del producto en kg', requerido: false },
  { valor: 'cantidad', etiqueta: 'Cantidad Producto', descripcion: 'Cantidad del producto', requerido: false },
  { valor: 'valor', etiqueta: 'Valor Producto', descripcion: 'Valor del producto en USD', requerido: false },
  { valor: 'categoria', etiqueta: 'Categoría', descripcion: 'Categoría del producto (electronica, ropa, hogar, deportes, otros)', requerido: false },
];
























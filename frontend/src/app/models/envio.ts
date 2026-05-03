import { Producto, ProductoCreate } from './producto';

export interface CompradorInfo {
  id: number;
  username: string;
  nombre: string;
  correo: string;
  cedula: string;
  rol_nombre: string;
  telefono?: string;
  ciudad?: string;
}

/** Envío tal como lo devuelve la API en listados/detalle (comprador como ID + info expandida). */
export interface Envio {
  id?: number;
  hawb: string;
  peso_total: number;
  cantidad_total: number;
  valor_total: number;
  costo_servicio?: number;
  fecha_emision?: string;
  comprador: number;
  comprador_info?: CompradorInfo;
  estado: string;
  estado_nombre?: string;
  observaciones?: string;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  productos?: Producto[];
  cantidad_productos?: number;
}

/** Envío con comprador completo (cuando la API devuelve depth=1). */
export interface EnvioDetalle extends Omit<Envio, 'comprador'> {
  comprador: CompradorInfo;
}

/** Payload para crear un envío (comprador como ID). */
export interface EnvioCreate {
  hawb: string;
  comprador: number;
  estado?: string;
  observaciones?: string;
  productos?: ProductoCreate[];
}

/** Payload para actualizar un envío (todos los campos opcionales). */
export interface EnvioUpdate {
  hawb?: string;
  comprador?: number;
  estado?: string;
  observaciones?: string;
}

export enum EstadosEnvio {
  PENDIENTE = 'pendiente',
  EN_TRANSITO = 'en_transito',
  ENTREGADO = 'entregado',
  CANCELADO = 'cancelado'
}

export const ESTADOS_LABELS = {
  [EstadosEnvio.PENDIENTE]: 'Pendiente',
  [EstadosEnvio.EN_TRANSITO]: 'En Tránsito',
  [EstadosEnvio.ENTREGADO]: 'Entregado',
  [EstadosEnvio.CANCELADO]: 'Cancelado'
};

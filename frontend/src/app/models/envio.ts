import { Producto, ProductoCreate } from './producto';

export interface Envio {
  id?: number;
  hawb: string;
  peso_total: number;
  cantidad_total: number;
  valor_total: number;
  fecha_emision?: string;
  comprador: number;
  comprador_info?: {
    id: number;
    username: string;
    nombre: string;
    correo: string;
    cedula: string;
    rol_nombre: string;
    telefono?: string;
  };
  estado: string;
  estado_nombre?: string;
  observaciones?: string;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  productos?: Producto[];
  cantidad_productos?: number;
}

export interface EnvioCreate {
  hawb: string;
  comprador: number;
  estado?: string;
  observaciones?: string;
  productos?: ProductoCreate[];
}

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

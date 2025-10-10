export interface Producto {
  id?: number;
  descripcion: string;
  peso: number;
  cantidad: number;
  valor: number;
  categoria: string;
  categoria_nombre?: string;
  envio: number;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
}

export interface ProductoCreate {
  descripcion: string;
  peso: number;
  cantidad: number;
  valor: number;
  categoria: string;
  envio?: number;
}

export interface ProductoUpdate {
  descripcion?: string;
  peso?: number;
  cantidad?: number;
  valor?: number;
  categoria?: string;
}

export enum CategoriasProducto {
  ELECTRONICA = 'electronica',
  ROPA = 'ropa',
  HOGAR = 'hogar',
  DEPORTES = 'deportes',
  OTROS = 'otros'
}

export const CATEGORIAS_LABELS = {
  [CategoriasProducto.ELECTRONICA]: 'Electrónica',
  [CategoriasProducto.ROPA]: 'Ropa',
  [CategoriasProducto.HOGAR]: 'Hogar',
  [CategoriasProducto.DEPORTES]: 'Deportes',
  [CategoriasProducto.OTROS]: 'Otros'
};

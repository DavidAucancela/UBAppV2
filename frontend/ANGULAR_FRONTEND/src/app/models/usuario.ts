export interface Usuario {
  id?: number;
  username: string;
  nombre: string;
  correo: string;
  cedula: string;
  rol: number;
  rol_nombre?: string;
  telefono?: string;
  fecha_nacimiento?: string;
  direccion?: string;
  tiene_discapacidad?: boolean;
  tipo_discapacidad?: string;
  notas_accesibilidad?: string;
  es_activo: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  password?: string;
  password_confirm?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  user: Usuario;
  token?: string;
}

export enum Roles {
  ADMIN = 1,
  GERENTE = 2,
  DIGITADOR = 3,
  COMPRADOR = 4
}

export const ROLES_LABELS = {
  [Roles.ADMIN]: 'Admin',
  [Roles.GERENTE]: 'Gerente',
  [Roles.DIGITADOR]: 'Digitador',
  [Roles.COMPRADOR]: 'Comprador'
};

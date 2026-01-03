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
  provincia?: string;
  canton?: string;
  ciudad?: string;
  ubicacion_completa?: string;
  cupo_anual?: number;
  es_activo: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
  password?: string;
  password_confirm?: string;
}

export interface DashboardUsuario {
  usuario: Usuario;
  cupo_anual: number;
  peso_usado: number;
  peso_disponible: number;
  porcentaje_usado: number;
  total_envios: number;
  envios_pendientes: number;
  envios_en_transito: number;
  envios_entregados: number;
  envios_cancelados: number;
  peso_total: number;
  valor_total: number;
  costo_servicio_total: number;
  anio: number;
}

export interface EstadisticasCupo {
  cupo_anual: number;
  peso_usado: number;
  peso_disponible: number;
  porcentaje_usado: number;
  anio: number;
  alerta: 'success' | 'info' | 'warning';
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

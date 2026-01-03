export interface ProvinciaEcuador {
  nombre: string;
  latitud: number;
  longitud: number;
}

export interface CompradorMapa {
  id: number;
  username: string;
  nombre: string;
  correo: string;
  telefono: string;
  provincia: string;
  canton: string;
  ciudad: string;
  ubicacion_completa: string;
  rol_nombre: string;
  total_envios: number;
  envios_recientes: EnvioSimple[];
}

export interface EnvioSimple {
  id: number;
  hawb: string;
  estado: string;
  fecha_emision: string;
  peso_total: number;
  valor_total: number;
  costo_servicio: number;
}

export interface ProvinciaConCompradores {
  provincia: string;
  total_compradores: number;
  compradores: CompradorMapa[];
}

export interface MapaResponse {
  provincias: ProvinciaConCompradores[];
  total_compradores: number;
}

// Coordenadas centrales de las provincias de Ecuador para el mapa
export const PROVINCIAS_ECUADOR: ProvinciaEcuador[] = [
  { nombre: 'Pichincha', latitud: -0.1807, longitud: -78.4678 },
  { nombre: 'Guayas', latitud: -2.1894, longitud: -79.8849 },
  { nombre: 'Azuay', latitud: -2.9001, longitud: -79.0059 },
  { nombre: 'Manabí', latitud: -1.0544, longitud: -80.4535 },
  { nombre: 'Tungurahua', latitud: -1.2490, longitud: -78.6167 },
  { nombre: 'Loja', latitud: -3.9930, longitud: -79.2042 },
  { nombre: 'Esmeraldas', latitud: 0.9681, longitud: -79.6517 },
  { nombre: 'Chimborazo', latitud: -1.6711, longitud: -78.6475 },
  { nombre: 'El Oro', latitud: -3.2581, longitud: -79.9553 },
  { nombre: 'Santo Domingo de los Tsáchilas', latitud: -0.2521, longitud: -79.1749 },
  { nombre: 'Imbabura', latitud: 0.3499, longitud: -78.1263 },
  { nombre: 'Los Ríos', latitud: -1.0285, longitud: -79.4602 }
];




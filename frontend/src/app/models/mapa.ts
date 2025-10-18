export interface CiudadEcuador {
  nombre: string;
  latitud: number;
  longitud: number;
  provincia: string;
}

export interface CompradorMapa {
  id: number;
  username: string;
  nombre: string;
  correo: string;
  telefono: string;
  ciudad: string;
  latitud: number;
  longitud: number;
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

export interface CiudadConCompradores {
  ciudad: string;
  total_compradores: number;
  compradores: CompradorMapa[];
}

export interface MapaResponse {
  ciudades: CiudadConCompradores[];
  total_compradores: number;
}

// Coordenadas de las principales ciudades de Ecuador
export const CIUDADES_ECUADOR: CiudadEcuador[] = [
  { nombre: 'Quito', latitud: -0.1807, longitud: -78.4678, provincia: 'Pichincha' },
  { nombre: 'Guayaquil', latitud: -2.1894, longitud: -79.8849, provincia: 'Guayas' },
  { nombre: 'Cuenca', latitud: -2.9001, longitud: -79.0059, provincia: 'Azuay' },
  { nombre: 'Ambato', latitud: -1.2490, longitud: -78.6167, provincia: 'Tungurahua' },
  { nombre: 'Manta', latitud: -0.9677, longitud: -80.7089, provincia: 'Manabí' },
  { nombre: 'Loja', latitud: -3.9930, longitud: -79.2042, provincia: 'Loja' },
  { nombre: 'Esmeraldas', latitud: 0.9681, longitud: -79.6517, provincia: 'Esmeraldas' },
  { nombre: 'Riobamba', latitud: -1.6711, longitud: -78.6475, provincia: 'Chimborazo' },
  { nombre: 'Machala', latitud: -3.2581, longitud: -79.9553, provincia: 'El Oro' },
  { nombre: 'Santo Domingo', latitud: -0.2521, longitud: -79.1749, provincia: 'Santo Domingo de los Tsáchilas' },
  { nombre: 'Ibarra', latitud: 0.3499, longitud: -78.1263, provincia: 'Imbabura' },
  { nombre: 'Portoviejo', latitud: -1.0544, longitud: -80.4535, provincia: 'Manabí' },
  { nombre: 'Durán', latitud: -2.1703, longitud: -79.8382, provincia: 'Guayas' },
  { nombre: 'Quevedo', latitud: -1.0285, longitud: -79.4602, provincia: 'Los Ríos' },
  { nombre: 'Milagro', latitud: -2.1344, longitud: -79.5922, provincia: 'Guayas' }
];


export interface Notificacion {
  id: number;
  tipo: 'nuevo_envio' | 'envio_asignado' | 'estado_cambiado' | 'general';
  titulo: string;
  mensaje: string;
  leida: boolean;
  fecha_creacion: string;
  fecha_lectura?: string;
  enlace?: string;
  metadata?: {
    envio_id?: number;
    estado_anterior?: string;
    estado_nuevo?: string;
    [key: string]: any;
  };
}

export interface NotificacionResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Notificacion[];
}

export interface NotificacionCount {
  total: number;
  no_leidas: number;
}








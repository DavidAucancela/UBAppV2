import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { Usuario } from '../models/usuario';
import { Envio, EnvioCreate, EnvioUpdate } from '../models/envio';
import { Producto, ProductoCreate, ProductoUpdate } from '../models/producto';
import { FiltrosBusquedaEnvio, RespuestaBusquedaEnvio, EstadisticasBusqueda } from '../models/busqueda-envio';
import { ConsultaSemantica, RespuestaSemantica, SugerenciaSemantica, HistorialBusquedaSemantica, MetricasSemanticas } from '../models/busqueda-semantica';
import { environment } from '../environments/environment';

export interface UbicacionesResponse {
  provincias?: string[];
  cantones?: string[];
  ciudades?: string[];
  total: number;
}

export interface CoordenaddasResponse {
  provincia: string;
  canton: string;
  ciudad: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  // ===== USUARIOS =====
  getUsuarios(): Observable<Usuario[]> {
    // El backend ahora devuelve todos los usuarios sin paginación
    // El frontend manejará la paginación del lado del cliente
    return this.http.get<any>(`${this.apiUrl}/usuarios/`).pipe(
      map(response => {
        // Si el backend devuelve paginación, extraer results
        if (response && response.results && Array.isArray(response.results)) {
          return response.results;
        }
        // Si devuelve array directo, usarlo
        return Array.isArray(response) ? response : [];
      })
    );
  }

  getUsuario(id: number): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}/usuarios/${id}/`);
  }

  createUsuario(usuario: Usuario): Observable<Usuario> {
    return this.http.post<Usuario>(`${this.apiUrl}/usuarios/`, usuario);
  }

  registerComprador(usuario: Usuario): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/usuarios/auth/register/`, usuario);
  }

  updateUsuario(id: number, usuario: Usuario): Observable<Usuario> {
    return this.http.put<Usuario>(`${this.apiUrl}/usuarios/${id}/`, usuario);
  }

  actualizarUsuarioParcial(id: number, usuario: Partial<Usuario>): Observable<Usuario> {
    return this.http.patch<Usuario>(`${this.apiUrl}/usuarios/${id}/`, usuario);
  }

  deleteUsuario(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/usuarios/${id}/`);
  }

  getCompradores(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(`${this.apiUrl}/usuarios/compradores/`);
  }

  getUsuariosPorRol(rol: number): Observable<Usuario[]> {
    const params = new HttpParams().set('rol', rol.toString());
    return this.http.get<Usuario[]>(`${this.apiUrl}/usuarios/por_rol/`, { params });
  }

  getEstadisticasUsuarios(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/usuarios/estadisticas/`);
  }

  changePassword(userId: number, passwordData: { current_password: string, new_password: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/usuarios/${userId}/change_password/`, passwordData);
  }

  actualizarPerfil(data: Partial<Usuario>): Observable<Usuario> {
    return this.http.put<Usuario>(`${this.apiUrl}/usuarios/actualizar_perfil/`, data);
  }

  cambiarPasswordPerfil(passwordData: { password_actual: string, password_nuevo: string, password_confirm: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/usuarios/cambiar_password/`, passwordData);
  }

  getUbicacionesProvincias(): Observable<UbicacionesResponse> {
    return this.http.get<UbicacionesResponse>(`${this.apiUrl}/usuarios/ubicaciones/provincias/`);
  }

  getUbicacionesCantones(provincia: string): Observable<UbicacionesResponse> {
    return this.http.get<UbicacionesResponse>(`${this.apiUrl}/usuarios/ubicaciones/cantones/`, {
      params: { provincia }
    });
  }

  getUbicacionesCiudades(provincia: string, canton: string): Observable<UbicacionesResponse> {
    return this.http.get<UbicacionesResponse>(`${this.apiUrl}/usuarios/ubicaciones/ciudades/`, {
      params: { provincia, canton }
    });
  }

  getUbicacionesCoordenadas(provincia: string, canton: string, ciudad: string): Observable<CoordenaddasResponse> {
    return this.http.get<CoordenaddasResponse>(`${this.apiUrl}/usuarios/ubicaciones/coordenadas/`, {
      params: { provincia, canton, ciudad }
    });
  }

  // ===== MAPA DE COMPRADORES =====
  getMapaCompradores(provincia?: string): Observable<any> {
    let params = new HttpParams();
    if (provincia) {
      params = params.set('provincia', provincia);
    }
    return this.http.get<any>(`${this.apiUrl}/usuarios/mapa_compradores/`, { params });
  }

  getEnviosComprador(compradorId: number, estado?: string): Observable<any> {
    let params = new HttpParams();
    if (estado) {
      params = params.set('estado', estado);
    }
    return this.http.get<any>(`${this.apiUrl}/usuarios/${compradorId}/envios_comprador/`, { params });
  }

  // ===== ENVÍOS =====
  getEnvios(): Observable<Envio[]> {
    // Solicitar un page_size grande para obtener todos los envíos
    const params = new HttpParams().set('page_size', '10000');
    return this.http.get<any>(`${this.apiUrl}/envios/envios/`, { params }).pipe(
      // Manejar respuesta paginada del backend
      map((response: any) => {
        // Si la respuesta tiene 'results', es una respuesta paginada
        if (response && response.results) {
          return response.results as Envio[];
        }
        // Si es un array directo, devolverlo
        return Array.isArray(response) ? response : [];
      })
    );
  }

  getEnvio(id: number): Observable<Envio> {
    return this.http.get<Envio>(`${this.apiUrl}/envios/envios/${id}/`);
  }

  createEnvio(envio: EnvioCreate): Observable<Envio> {
    return this.http.post<Envio>(`${this.apiUrl}/envios/envios/`, envio);
  }

  updateEnvio(id: number, envio: EnvioUpdate): Observable<Envio> {
    return this.http.put<Envio>(`${this.apiUrl}/envios/envios/${id}/`, envio);
  }

  deleteEnvio(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/envios/envios/${id}/`);
  }

  getMisEnvios(): Observable<Envio[]> {
    // Solicitar un page_size grande para obtener todos los envíos
    const params = new HttpParams().set('page_size', '10000');
    return this.http.get<any>(`${this.apiUrl}/envios/envios/mis_envios/`, { params }).pipe(
      // Manejar respuesta paginada del backend
      map((response: any) => {
        // Si la respuesta tiene 'results', es una respuesta paginada
        if (response && response.results) {
          return response.results as Envio[];
        }
        // Si la respuesta tiene 'envios', es del endpoint mis_envios
        if (response && response.envios) {
          return response.envios as Envio[];
        }
        // Si es un array directo, devolverlo
        return Array.isArray(response) ? response : [];
      })
    );
  }

  getEnviosPorEstado(estado: string): Observable<Envio[]> {
    const params = new HttpParams().set('estado', estado);
    return this.http.get<Envio[]>(`${this.apiUrl}/envios/envios/por_estado/`, { params });
  }

  cambiarEstadoEnvio(id: number, estado: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/envios/envios/${id}/cambiar_estado/`, { estado });
  }

  getEstadisticasEnvios(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/envios/envios/estadisticas/`);
  }

  calcularCostoEnvio(productos: any[]): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/envios/envios/calcular_costo/`, { productos });
  }

  // ===== PRODUCTOS =====
  getProductos(): Observable<Producto[]> {
    const params = new HttpParams().set('page_size', '10000');
    return this.http.get<any>(`${this.apiUrl}/envios/productos/`, { params }).pipe(
      map((res: any) => {
        if (res?.results && Array.isArray(res.results)) return res.results;
        return Array.isArray(res) ? res : [];
      })
    );
  }

  getProducto(id: number): Observable<Producto> {
    return this.http.get<Producto>(`${this.apiUrl}/envios/productos/${id}/`);
  }

  createProducto(producto: ProductoCreate): Observable<Producto> {
    return this.http.post<Producto>(`${this.apiUrl}/envios/productos/`, producto);
  }

  updateProducto(id: number, producto: ProductoUpdate): Observable<Producto> {
    return this.http.put<Producto>(`${this.apiUrl}/envios/productos/${id}/`, producto);
  }

  deleteProducto(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/envios/productos/${id}/`);
  }

  getProductosPorCategoria(categoria: string): Observable<Producto[]> {
    const params = new HttpParams().set('categoria', categoria);
    return this.http.get<Producto[]>(`${this.apiUrl}/envios/productos/por_categoria/`, { params });
  }

  getEstadisticasProductos(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/envios/productos/estadisticas/`);
  }

  // ===== TARIFAS =====
  getTarifas(): Observable<any[]> {
    const params = new HttpParams().set('page_size', '10000');
    return this.http.get<any>(`${this.apiUrl}/envios/tarifas/`, { params }).pipe(
      map((res: any) => {
        if (res?.results && Array.isArray(res.results)) return res.results;
        return Array.isArray(res) ? res : [];
      })
    );
  }

  getTarifa(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/envios/tarifas/${id}/`);
  }

  createTarifa(tarifa: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/envios/tarifas/`, tarifa);
  }

  updateTarifa(id: number, tarifa: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/envios/tarifas/${id}/`, tarifa);
  }

  deleteTarifa(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/envios/tarifas/${id}/`);
  }

  getTarifasPorCategoria(categoria: string): Observable<any[]> {
    const params = new HttpParams().set('categoria', categoria);
    return this.http.get<any[]>(`${this.apiUrl}/envios/tarifas/por_categoria/`, { params });
  }

  buscarTarifa(categoria: string, peso: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/envios/tarifas/buscar_tarifa/`, { categoria, peso });
  }

  // ===== BÚSQUEDA =====
  buscar(termino: string, tipo: string = 'general'): Observable<any> {
    const params = new HttpParams()
      .set('q', termino)
      .set('tipo', tipo);
    return this.http.get<any>(`${this.apiUrl}/busqueda/buscar/`, { params });
  }

  getHistorialBusqueda(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/busqueda/historial/`);
  }

  limpiarHistorialBusqueda(): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/busqueda/limpiar_historial/`);
  }

  getEstadisticasBusqueda(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/busqueda/estadisticas/`);
  }

  // ===== BÚSQUEDA AVANZADA DE ENVÍOS =====
  
  /**
   * Busca envíos con filtros avanzados
   * @param filtros Objeto con los criterios de búsqueda
   * @returns Observable con la respuesta paginada de envíos
   */
  buscarEnviosAvanzado(filtros: FiltrosBusquedaEnvio): Observable<RespuestaBusquedaEnvio> {
    let params = new HttpParams();
    
    // Agregar parámetros solo si tienen valor
    if (filtros.textoBusqueda) {
      params = params.set('search', filtros.textoBusqueda);
    }
    if (filtros.numeroGuia) {
      params = params.set('hawb', filtros.numeroGuia);
    }
    if (filtros.nombreRemitente) {
      params = params.set('remitente', filtros.nombreRemitente);
    }
    if (filtros.nombreDestinatario) {
      params = params.set('comprador__nombre__icontains', filtros.nombreDestinatario);
    }
    if (filtros.ciudadOrigen) {
      params = params.set('ciudad_origen', filtros.ciudadOrigen);
    }
    if (filtros.ciudadDestino) {
      params = params.set('comprador__ciudad__icontains', filtros.ciudadDestino);
    }
    if (filtros.estado) {
      params = params.set('estado', filtros.estado);
    }
    if (filtros.fechaDesde) {
      params = params.set('fecha_emision__gte', filtros.fechaDesde);
    }
    if (filtros.fechaHasta) {
      params = params.set('fecha_emision__lte', filtros.fechaHasta);
    }
    if (filtros.ordenarPor) {
      params = params.set('ordering', filtros.ordenarPor);
    }
    if (filtros.pagina) {
      params = params.set('page', filtros.pagina.toString());
    }
    if (filtros.elementosPorPagina) {
      params = params.set('page_size', filtros.elementosPorPagina.toString());
    }
    
    return this.http.get<RespuestaBusquedaEnvio>(`${this.apiUrl}/envios/envios/`, { params });
  }

  /**
   * Obtiene estadísticas de los resultados de búsqueda
   * @param filtros Filtros aplicados
   * @returns Observable con estadísticas calculadas
   */
  obtenerEstadisticasBusquedaEnvios(filtros: FiltrosBusquedaEnvio): Observable<EstadisticasBusqueda> {
    let params = new HttpParams();
    
    if (filtros.textoBusqueda) params = params.set('search', filtros.textoBusqueda);
    if (filtros.numeroGuia) params = params.set('hawb', filtros.numeroGuia);
    if (filtros.estado) params = params.set('estado', filtros.estado);
    if (filtros.fechaDesde) params = params.set('fecha_emision__gte', filtros.fechaDesde);
    if (filtros.fechaHasta) params = params.set('fecha_emision__lte', filtros.fechaHasta);
    
    return this.http.get<EstadisticasBusqueda>(`${this.apiUrl}/envios/envios/estadisticas/`, { params });
  }

  /**
   * Exporta los resultados de búsqueda en el formato especificado
   * @param filtros Filtros aplicados
   * @param formato Formato de exportación (pdf, excel, csv)
   * @returns Observable con el blob del archivo
   */
  exportarResultadosBusqueda(filtros: FiltrosBusquedaEnvio, formato: string): Observable<Blob> {
    let params = new HttpParams();
    
    if (filtros.textoBusqueda) params = params.set('search', filtros.textoBusqueda);
    if (filtros.numeroGuia) params = params.set('hawb', filtros.numeroGuia);
    if (filtros.estado) params = params.set('estado', filtros.estado);
    if (filtros.fechaDesde) params = params.set('fecha_emision__gte', filtros.fechaDesde);
    if (filtros.fechaHasta) params = params.set('fecha_emision__lte', filtros.fechaHasta);
    
    params = params.set('formato', formato);
    
    return this.http.get(`${this.apiUrl}/envios/envios/exportar/`, { 
      params, 
      responseType: 'blob' 
    });
  }

  /**
   * Obtiene un comprobante de envío en PDF
   * @param envioId ID del envío
   * @returns Observable con el blob del PDF
   */
  obtenerComprobanteEnvio(envioId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/envios/envios/${envioId}/comprobante/`, {
      responseType: 'blob'
    });
  }

  // ===== BÚSQUEDA SEMÁNTICA DE ENVÍOS =====

  /**
   * Realiza una búsqueda semántica de envíos usando IA
   * @param consulta Consulta semántica con texto libre
   * @returns Observable con resultados ordenados por relevancia
   */
  buscarEnviosSemantica(consulta: ConsultaSemantica): Observable<RespuestaSemantica> {
    return this.http.post<RespuestaSemantica>(`${this.apiUrl}/busqueda/semantica/`, consulta);
  }

  /**
   * Obtiene sugerencias de búsqueda mientras el usuario escribe
   * @param textoIncompleto Texto parcial que el usuario está escribiendo
   * @returns Observable con sugerencias relevantes
   */
  obtenerSugerenciasSemanticas(textoIncompleto: string): Observable<SugerenciaSemantica[]> {
    const params = new HttpParams().set('q', textoIncompleto);
    return this.http.get<SugerenciaSemantica[]>(`${this.apiUrl}/busqueda/semantica/sugerencias/`, { params });
  }

  /**
   * Guarda una búsqueda en el historial del usuario
   * @param consulta Texto de la consulta realizada
   * @param totalResultados Número de resultados encontrados
   * @returns Observable con confirmación
   */
  guardarHistorialSemantico(consulta: string, totalResultados: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/busqueda/semantica/historial/`, {
      consulta,
      totalResultados
    });
  }

  /**
   * Obtiene el historial de búsquedas semánticas del usuario
   * @returns Observable con lista de búsquedas anteriores
   */
  obtenerHistorialSemantico(): Observable<HistorialBusquedaSemantica[]> {
    return this.http.get<HistorialBusquedaSemantica[]>(`${this.apiUrl}/busqueda/semantica/historial/`);
  }

  /**
   * Limpia el historial de búsquedas semánticas
   * @returns Observable con confirmación
   */
  limpiarHistorialSemantico(): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/busqueda/semantica/historial/`);
  }

  /**
   * Obtiene métricas y estadísticas de búsquedas semánticas
   * @returns Observable con métricas agregadas
   */
  obtenerMetricasSemanticas(): Observable<MetricasSemanticas> {
    return this.http.get<MetricasSemanticas>(`${this.apiUrl}/busqueda/semantica/metricas/`);
  }

  /**
   * Obtiene estadísticas de embeddings de envíos
   * @returns Observable con estadísticas de embeddings
   */
  obtenerEstadisticasEmbeddings(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/busqueda/semantica/estadisticas-embeddings/`);
  }

  /**
   * Genera embeddings para envíos pendientes
   * @param forzarRegeneracion Si true, regenera todos los embeddings
   * @param modelo Modelo de embedding a usar
   * @returns Observable con resultado de la operación
   */
  generarEmbeddingsPendientes(forzarRegeneracion: boolean = false, modelo?: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/busqueda/semantica/generar-embeddings/`, {
      forzarRegeneracion,
      modelo
    });
  }

  /**
   * Proporciona feedback sobre la relevancia de un resultado
   * @param resultadoId ID del resultado evaluado
   * @param esRelevante Si el resultado fue útil o no
   * @returns Observable con confirmación
   */
  enviarFeedbackSemantico(resultadoId: number, esRelevante: boolean): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/busqueda/semantica/feedback/`, {
      resultadoId,
      esRelevante
    });
  }

  // ===== NOTIFICACIONES =====
  
  /**
   * Obtiene las notificaciones del usuario autenticado
   * @returns Observable con lista de notificaciones
   */
  getNotificaciones(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/notificaciones/`);
  }

  /**
   * Obtiene el contador de notificaciones no leídas
   * @returns Observable con total y no leídas
   */
  getContadorNotificaciones(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/notificaciones/contador/`);
  }
}

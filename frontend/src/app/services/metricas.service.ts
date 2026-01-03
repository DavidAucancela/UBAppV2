import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

/**
 * Servicio para gestionar métricas y pruebas del dashboard experimental
 */
@Injectable({
  providedIn: 'root'
})
export class MetricasService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  // ==================== PRUEBAS CONTROLADAS SEMÁNTICAS ====================

  getPruebasControladas(activa?: boolean): Observable<any[]> {
    let params = new HttpParams();
    if (activa !== undefined) {
      params = params.set('activa', activa.toString());
    }
    return this.http.get<any[]>(`${this.apiUrl}/metricas/pruebas-controladas/`, { params });
  }

  crearPruebaControlada(prueba: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/metricas/pruebas-controladas/`, prueba);
  }

  ejecutarPruebaControlada(pruebaId: number, filtros?: any, limite?: number): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/metricas/pruebas-controladas/${pruebaId}/ejecutar/`,
      { filtros, limite: limite || 20 }
    );
  }

  // ==================== MÉTRICAS SEMÁNTICAS ====================

  getMetricasSemanticas(fechaDesde?: string, fechaHasta?: string): Observable<any[]> {
    let params = new HttpParams();
    if (fechaDesde) params = params.set('fecha_desde', fechaDesde);
    if (fechaHasta) params = params.set('fecha_hasta', fechaHasta);
    return this.http.get<any[]>(`${this.apiUrl}/metricas/metricas-semanticas/`, { params });
  }

  getEstadisticasSemanticas(fechaDesde?: string, fechaHasta?: string): Observable<any> {
    let params = new HttpParams();
    if (fechaDesde) params = params.set('fecha_desde', fechaDesde);
    if (fechaHasta) params = params.set('fecha_hasta', fechaHasta);
    return this.http.get<any>(`${this.apiUrl}/metricas/metricas-semanticas/estadisticas/`, { params });
  }

  // ==================== REGISTROS DE GENERACIÓN DE EMBEDDINGS ====================

  getRegistrosEmbedding(estado?: string, tipoProceso?: string): Observable<any[]> {
    let params = new HttpParams();
    if (estado) params = params.set('estado', estado);
    if (tipoProceso) params = params.set('tipo_proceso', tipoProceso);
    return this.http.get<any[]>(`${this.apiUrl}/metricas/registros-embedding/`, { params });
  }

  getEstadisticasEmbedding(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/metricas/registros-embedding/estadisticas/`);
  }

  // ==================== PRUEBAS DE CARGA ====================

  getPruebasCarga(tipoPrueba?: string, nivelCarga?: number): Observable<any[]> {
    let params = new HttpParams();
    if (tipoPrueba) params = params.set('tipo_prueba', tipoPrueba);
    if (nivelCarga) params = params.set('nivel_carga', nivelCarga.toString());
    return this.http.get<any[]>(`${this.apiUrl}/metricas/pruebas-carga/`, { params });
  }

  ejecutarPruebaCargaBusqueda(nivelCarga: number, consultas: string[], nombrePrueba?: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/metricas/pruebas-carga/ejecutar_busqueda/`, {
      nivel_carga: nivelCarga,
      consultas,
      nombre_prueba: nombrePrueba
    });
  }

  // ==================== MÉTRICAS DE RENDIMIENTO ====================

  getMetricasRendimiento(proceso?: string, nivelCarga?: number, fechaDesde?: string, fechaHasta?: string): Observable<any[]> {
    let params = new HttpParams();
    if (proceso) params = params.set('proceso', proceso);
    if (nivelCarga) params = params.set('nivel_carga', nivelCarga.toString());
    if (fechaDesde) params = params.set('fecha_desde', fechaDesde);
    if (fechaHasta) params = params.set('fecha_hasta', fechaHasta);
    return this.http.get<any[]>(`${this.apiUrl}/metricas/metricas-rendimiento/`, { params });
  }

  getEstadisticasRendimiento(proceso?: string, nivelCarga?: number): Observable<any> {
    let params = new HttpParams();
    if (proceso) params = params.set('proceso', proceso);
    if (nivelCarga) params = params.set('nivel_carga', nivelCarga.toString());
    return this.http.get<any>(`${this.apiUrl}/metricas/metricas-rendimiento/estadisticas/`, { params });
  }

  // ==================== REGISTROS MANUALES DE ENVÍOS ====================

  getRegistrosManuales(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/metricas/registros-manuales/`);
  }

  registrarEnvioManual(hawb: string, tiempoSegundos: number, datosEnvios?: any, notas?: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/metricas/registros-manuales/registrar/`, {
      hawb,
      tiempo_registro_segundos: tiempoSegundos,
      datos_envio: datosEnvios,
      notas
    });
  }

  getEstadisticasRegistrosManuales(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/metricas/registros-manuales/estadisticas/`);
  }

  // ==================== EXPORTACIÓN CSV ====================

  exportarMetricasSemanticasCSV(fechaDesde?: string, fechaHasta?: string): Observable<Blob> {
    let params = new HttpParams();
    if (fechaDesde) params = params.set('fecha_desde', fechaDesde);
    if (fechaHasta) params = params.set('fecha_hasta', fechaHasta);
    return this.http.get(`${this.apiUrl}/metricas/exportacion/metricas_semanticas/`, {
      params,
      responseType: 'blob'
    });
  }

  exportarMetricasRendimientoCSV(fechaDesde?: string, fechaHasta?: string): Observable<Blob> {
    let params = new HttpParams();
    if (fechaDesde) params = params.set('fecha_desde', fechaDesde);
    if (fechaHasta) params = params.set('fecha_hasta', fechaHasta);
    return this.http.get(`${this.apiUrl}/metricas/exportacion/metricas_rendimiento/`, {
      params,
      responseType: 'blob'
    });
  }

  descargarArchivo(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}


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

  getMetricasSemanticas(fechaDesde?: string, fechaHasta?: string, page?: number, pageSize?: number): Observable<any> {
    let params = new HttpParams();
    if (fechaDesde) params = params.set('fecha_desde', fechaDesde);
    if (fechaHasta) params = params.set('fecha_hasta', fechaHasta);
    if (page) params = params.set('page', page.toString());
    if (pageSize) params = params.set('page_size', pageSize.toString());
    return this.http.get<any>(`${this.apiUrl}/metricas/metricas-semanticas/`, { params });
  }

  getEstadisticasSemanticas(fechaDesde?: string, fechaHasta?: string): Observable<any> {
    let params = new HttpParams();
    if (fechaDesde) params = params.set('fecha_desde', fechaDesde);
    if (fechaHasta) params = params.set('fecha_hasta', fechaHasta);
    return this.http.get<any>(`${this.apiUrl}/metricas/metricas-semanticas/estadisticas/`, { params });
  }

  /** Reporte comparativo de eficiencia del panel semántico (MRR, NDCG@10, Precision@5) */
  getReporteComparativo(fechaDesde?: string, fechaHasta?: string): Observable<{
    filas: Array<{
      id: number;
      consulta: string;
      consulta_completa?: string;
      fecha_calculo: string;
      mrr: number | null;
      ndcg_10: number | null;
      precision_5: number | null;
      total_resultados: number;
      total_relevantes_encontrados: number;
      interpretacion_mrr: { nivel: string; etiqueta: string; descripcion: string };
      interpretacion_ndcg: { nivel: string; etiqueta: string; descripcion: string };
      interpretacion_precision: { nivel: string; etiqueta: string; descripcion: string };
    }>;
    resumen: {
      total_evaluaciones: number;
      mrr_promedio: number;
      mrr_maximo: number;
      mrr_minimo: number;
      ndcg_10_promedio: number;
      precision_5_promedio: number;
      interpretacion_global: { nivel: string; etiqueta: string; descripcion: string };
    };
  }> {
    let params = new HttpParams();
    if (fechaDesde) params = params.set('fecha_desde', fechaDesde);
    if (fechaHasta) params = params.set('fecha_hasta', fechaHasta);
    return this.http.get<any>(`${this.apiUrl}/metricas/metricas-semanticas/reporte-comparativo/`, { params });
  }

  // ==================== REGISTROS DE GENERACIÓN DE EMBEDDINGS ====================

  getRegistrosEmbedding(estado?: string, tipoProceso?: string, page?: number, pageSize?: number): Observable<any> {
    let params = new HttpParams();
    if (estado) params = params.set('estado', estado);
    if (tipoProceso) params = params.set('tipo_proceso', tipoProceso);
    if (page) params = params.set('page', page.toString());
    if (pageSize) params = params.set('page_size', pageSize.toString());
    return this.http.get<any>(`${this.apiUrl}/metricas/registros-embedding/`, { params });
  }

  getEstadisticasEmbedding(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/metricas/registros-embedding/estadisticas/`);
  }

  // ==================== PRUEBAS DE CARGA ====================

  getPruebasCarga(tipoPrueba?: string, nivelCarga?: number, fechaDesde?: string, fechaHasta?: string): Observable<any[]> {
    let params = new HttpParams();
    if (tipoPrueba) params = params.set('tipo_prueba', tipoPrueba);
    if (nivelCarga) params = params.set('nivel_carga', nivelCarga.toString());
    if (fechaDesde) params = params.set('fecha_desde', fechaDesde);
    if (fechaHasta) params = params.set('fecha_hasta', fechaHasta);
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

  exportarPruebasCargaCSV(): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/metricas/exportacion/pruebas_carga/`, {
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

  // ==================== PRUEBAS DEL SISTEMA ====================

  /**
   * Lista todos los tests disponibles en el sistema
   */
  listarTests(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/metricas/pruebas-sistema/listar_tests/`);
  }

  /**
   * Ejecuta los tests unitarios del sistema
   * @param app Nombre de la aplicación (archivos, busqueda, usuarios) o null para todas
   * @param testSuite Nombre del test suite específico o null para todos
   */
  ejecutarTests(app?: string, testSuite?: string): Observable<any> {
    const body: any = {};
    if (app) body.app = app;
    if (testSuite) body.test_suite = testSuite;
    
    return this.http.post<any>(`${this.apiUrl}/metricas/pruebas-sistema/ejecutar_tests/`, body);
  }

  /**
   * Ejecuta las pruebas de rendimiento del sistema
   */
  ejecutarPruebasRendimiento(): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/metricas/pruebas-sistema/ejecutar_rendimiento/`, {});
  }

  /**
   * Obtiene estadísticas de las pruebas ejecutadas
   */
  getEstadisticasPruebas(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/metricas/pruebas-sistema/estadisticas_pruebas/`);
  }

  /**
   * Obtiene todas las pruebas de rendimiento guardadas
   */
  getPruebasRendimientoGuardadas(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/metricas/pruebas-sistema/pruebas_rendimiento_guardadas/`);
  }

  /**
   * Obtiene el detalle completo de una prueba de rendimiento
   */
  getDetallePruebaRendimiento(pruebaId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/metricas/pruebas-sistema/${pruebaId}/detalle_prueba_rendimiento/`);
  }

  /**
   * Ejecuta pruebas de rendimiento completas según ISO 25010
   * @param iteraciones Número de iteraciones por prueba (default: 24)
   */
  ejecutarPruebaRendimientoCompleta(iteraciones: number = 24): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/metricas/pruebas-sistema/ejecutar_rendimiento_completo/`, {
      iteraciones
    });
  }

  // ==================== DETALLES DE PROCESOS M1-M14 ====================

  /**
   * Obtiene detalles de procesos de rendimiento
   * @param codigoProceso Código del proceso (M1-M14) opcional
   * @param pruebaId ID de la prueba específica opcional
   */
  getDetallesProcesos(codigoProceso?: string, pruebaId?: number): Observable<any[]> {
    let params = new HttpParams();
    if (codigoProceso) params = params.set('codigo_proceso', codigoProceso);
    if (pruebaId) params = params.set('prueba_id', pruebaId.toString());
    return this.http.get<any[]>(`${this.apiUrl}/metricas/pruebas-sistema/detalles_procesos/`, { params });
  }
}



import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

/**
 * Servicio para gestionar búsquedas tradicionales y semánticas
 * Incluye funcionalidades de descarga de PDFs
 */
@Injectable({
  providedIn: 'root'
})
export class BusquedaService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  // ==================== BÚSQUEDA TRADICIONAL ====================

  /**
   * Realiza una búsqueda tradicional
   */
  buscar(termino: string, tipo: string = 'general'): Observable<any> {
    const params = new HttpParams()
      .set('q', termino)
      .set('tipo', tipo);
    return this.http.get<any>(`${this.apiUrl}/busqueda/buscar/`, { params });
  }

  /**
   * Obtiene el historial de búsquedas tradicionales
   */
  getHistorialTradicional(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/busqueda/`);
  }

  /**
   * Limpia el historial de búsquedas tradicionales
   */
  limpiarHistorialTradicional(): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/busqueda/limpiar_historial/`);
  }

  /**
   * Descarga el PDF de una búsqueda tradicional específica
   * @param busquedaId ID de la búsqueda tradicional
   * @returns Observable con el blob del PDF
   */
  descargarPdfBusquedaTradicional(busquedaId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/busqueda/${busquedaId}/descargar-pdf/`, {
      responseType: 'blob'
    });
  }

  // ==================== BÚSQUEDA SEMÁNTICA ====================

  /**
   * Realiza una búsqueda semántica
   */
  buscarSemantica(consulta: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/busqueda/semantica/`, consulta);
  }

  /**
   * Obtiene sugerencias para búsqueda semántica
   */
  obtenerSugerencias(query: string = ''): Observable<any[]> {
    const params = query ? new HttpParams().set('q', query) : new HttpParams();
    return this.http.get<any[]>(`${this.apiUrl}/busqueda/semantica/sugerencias/`, { params });
  }

  /**
   * Obtiene el historial de búsquedas semánticas
   */
  getHistorialSemantico(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/busqueda/semantica/historial/`);
  }

  /**
   * Guarda una búsqueda en el historial semántico
   */
  guardarHistorialSemantico(consulta: string, totalResultados: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/busqueda/semantica/historial/`, {
      consulta,
      totalResultados
    });
  }

  /**
   * Limpia el historial semántico
   */
  limpiarHistorialSemantico(): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/busqueda/semantica/historial/`);
  }

  /**
   * Obtiene métricas de búsquedas semánticas
   */
  obtenerMetricasSemanticas(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/busqueda/semantica/metricas/`);
  }

  /**
   * Descarga el PDF de una búsqueda semántica específica
   * @param busquedaId ID de la búsqueda semántica
   * @returns Observable con el blob del PDF
   */
  descargarPdfBusquedaSemantica(busquedaId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/busqueda/semantica/${busquedaId}/descargar-pdf/`, {
      responseType: 'blob'
    });
  }

  // ==================== UTILIDADES ====================

  /**
   * Helper para descargar un blob como archivo
   * @param blob Blob a descargar
   * @param filename Nombre del archivo
   */
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


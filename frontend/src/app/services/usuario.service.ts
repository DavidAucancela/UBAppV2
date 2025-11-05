import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';
import { DashboardUsuario, EstadisticasCupo } from '../models/usuario';
import { Envio } from '../models/envio';

@Injectable({
  providedIn: 'root'
})
export class UsuarioService {
  private apiUrl = `${environment.apiUrl}/usuarios`;

  constructor(private http: HttpClient) { }

  /**
   * Obtiene el dashboard del usuario actual con estadísticas
   */
  getDashboardUsuario(anio?: number): Observable<{ dashboard: DashboardUsuario, envios_recientes: Envio[] }> {
    let params = new HttpParams();
    if (anio) {
      params = params.set('anio', anio.toString());
    }
    return this.http.get<{ dashboard: DashboardUsuario, envios_recientes: Envio[] }>(
      `${this.apiUrl}/dashboard_usuario/`,
      { params }
    );
  }

  /**
   * Obtiene las estadísticas de cupo anual del usuario
   */
  getEstadisticasCupo(anio?: number): Observable<EstadisticasCupo> {
    let params = new HttpParams();
    if (anio) {
      params = params.set('anio', anio.toString());
    }
    return this.http.get<EstadisticasCupo>(
      `${this.apiUrl}/estadisticas_cupo/`,
      { params }
    );
  }

  /**
   * Obtiene los envíos del usuario actual
   */
  getMisEnvios(filtros?: { estado?: string, fecha_desde?: string, fecha_hasta?: string }): Observable<{ envios: Envio[], total_envios: number }> {
    let params = new HttpParams();
    if (filtros) {
      if (filtros.estado) {
        params = params.set('estado', filtros.estado);
      }
      if (filtros.fecha_desde) {
        params = params.set('fecha_desde', filtros.fecha_desde);
      }
      if (filtros.fecha_hasta) {
        params = params.set('fecha_hasta', filtros.fecha_hasta);
      }
    }
    return this.http.get<{ envios: Envio[], total_envios: number }>(
      `${this.apiUrl}/mis_envios/`,
      { params }
    );
  }
}





import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
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
  latitud: number;
  longitud: number;
}

@Injectable({
  providedIn: 'root'
})
export class UbicacionesService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  /**
   * Obtiene todas las provincias de Ecuador
   */
  getProvincias(): Observable<UbicacionesResponse> {
    return this.http.get<UbicacionesResponse>(`${this.apiUrl}/usuarios/ubicaciones/provincias/`);
  }

  /**
   * Obtiene los cantones de una provincia específica
   */
  getCantones(provincia: string): Observable<UbicacionesResponse> {
    return this.http.get<UbicacionesResponse>(`${this.apiUrl}/usuarios/ubicaciones/cantones/`, {
      params: { provincia }
    });
  }

  /**
   * Obtiene las ciudades de un cantón específico
   */
  getCiudades(provincia: string, canton: string): Observable<UbicacionesResponse> {
    return this.http.get<UbicacionesResponse>(`${this.apiUrl}/usuarios/ubicaciones/ciudades/`, {
      params: { provincia, canton }
    });
  }

  /**
   * Obtiene las coordenadas de una ubicación específica
   */
  getCoordenadas(provincia: string, canton: string, ciudad: string): Observable<CoordenaddasResponse> {
    return this.http.get<CoordenaddasResponse>(`${this.apiUrl}/usuarios/ubicaciones/coordenadas/`, {
      params: { provincia, canton, ciudad }
    });
  }
}













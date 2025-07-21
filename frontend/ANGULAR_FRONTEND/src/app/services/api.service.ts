import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Usuario } from '../models/usuario';
import { Envio, EnvioCreate, EnvioUpdate } from '../models/envio';
import { Producto, ProductoCreate, ProductoUpdate } from '../models/producto';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  // ===== USUARIOS =====
  getUsuarios(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(`${this.apiUrl}/usuarios/`);
  }

  getUsuario(id: number): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}/usuarios/${id}/`);
  }

  createUsuario(usuario: Usuario): Observable<Usuario> {
    return this.http.post<Usuario>(`${this.apiUrl}/usuarios/`, usuario);
  }

  updateUsuario(id: number, usuario: Usuario): Observable<Usuario> {
    return this.http.put<Usuario>(`${this.apiUrl}/usuarios/${id}/`, usuario);
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

  // ===== ENVÍOS =====
  getEnvios(): Observable<Envio[]> {
    return this.http.get<Envio[]>(`${this.apiUrl}/envios/envios/`);
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
    return this.http.get<Envio[]>(`${this.apiUrl}/envios/envios/mis_envios/`);
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

  // ===== PRODUCTOS =====
  getProductos(): Observable<Producto[]> {
    return this.http.get<Producto[]>(`${this.apiUrl}/envios/productos/`);
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
}

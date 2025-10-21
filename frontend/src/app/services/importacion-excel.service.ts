import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, BehaviorSubject, throwError } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import * as XLSX from 'xlsx';
import {
  ImportacionExcel,
  PreviewExcel,
  MapeoColumnas,
  ResultadoValidacion,
  ResultadoProcesamiento,
  ReporteErrores,
  FilaExcel
} from '../models/importacion-excel.model';
import { environment } from '../environments/environment';

/**
 * Servicio para gestionar importaciones de archivos Excel
 */
@Injectable({
  providedIn: 'root'
})
export class ImportacionExcelService {
  private apiUrl = `${environment.apiUrl}/envios/importaciones-excel`;
  
  // Estado del proceso de importación actual
  private importacionActualSubject = new BehaviorSubject<ImportacionExcel | null>(null);
  public importacionActual$ = this.importacionActualSubject.asObservable();
  
  private previewDatosSubject = new BehaviorSubject<PreviewExcel | null>(null);
  public previewDatos$ = this.previewDatosSubject.asObservable();

  constructor(private http: HttpClient) { }

  /**
   * Lee un archivo Excel localmente (sin enviarlo al backend)
   * Útil para preview rápido antes de subir
   */
  leerArchivoLocal(archivo: File): Promise<PreviewExcel> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e: any) => {
        try {
          const datos = new Uint8Array(e.target.result);
          const workbook = XLSX.read(datos, { type: 'array' });
          
          // Leer la primera hoja
          const nombrePrimeraHoja = workbook.SheetNames[0];
          const hoja = workbook.Sheets[nombrePrimeraHoja];
          
          // Convertir a JSON
          const datosJson: any[] = XLSX.utils.sheet_to_json(hoja, { raw: false });
          
          if (datosJson.length === 0) {
            reject(new Error('El archivo Excel está vacío'));
            return;
          }
          
          // Obtener columnas
          const columnas = Object.keys(datosJson[0]);
          
          // Convertir filas agregando índice
          const filas: FilaExcel[] = datosJson.map((fila, indice) => ({
            _indice: indice,
            ...fila
          }));
          
          const preview: PreviewExcel = {
            columnas,
            filas: filas.slice(0, 50), // Limitar a 50 filas
            total_filas: datosJson.length
          };
          
          // Guardar en el estado
          this.previewDatosSubject.next(preview);
          
          resolve(preview);
        } catch (error) {
          reject(new Error('Error al leer el archivo Excel: ' + error));
        }
      };
      
      reader.onerror = () => {
        reject(new Error('Error al leer el archivo'));
      };
      
      reader.readAsArrayBuffer(archivo);
    });
  }

  /**
   * Sube un archivo Excel al backend
   */
  subirArchivo(archivo: File, nombreOriginal?: string): Observable<ImportacionExcel> {
    const formData = new FormData();
    formData.append('archivo', archivo);
    formData.append('nombre_original', nombreOriginal || archivo.name);
    
    return this.http.post<ImportacionExcel>(this.apiUrl + '/', formData).pipe(
      tap(importacion => {
        this.importacionActualSubject.next(importacion);
        console.log('✅ Archivo subido correctamente:', importacion);
      }),
      catchError(error => {
        console.error('❌ Error al subir archivo:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Obtiene la vista previa de un archivo subido
   */
  obtenerPreview(importacionId: number, limite: number = 50): Observable<PreviewExcel> {
    const params = new HttpParams().set('limite', limite.toString());
    
    return this.http.get<PreviewExcel>(`${this.apiUrl}/${importacionId}/preview/`, { params }).pipe(
      tap(preview => {
        this.previewDatosSubject.next(preview);
        console.log('✅ Vista previa obtenida:', preview);
      }),
      catchError(error => {
        console.error('❌ Error al obtener vista previa:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Valida los datos según el mapeo de columnas
   */
  validarDatos(importacionId: number, mapeoColumnas: MapeoColumnas): Observable<ResultadoValidacion> {
    const body = { columnas_mapeadas: mapeoColumnas };
    
    return this.http.post<ResultadoValidacion>(`${this.apiUrl}/${importacionId}/validar/`, body).pipe(
      tap(resultado => {
        console.log('✅ Validación completada:', resultado);
        // Actualizar la importación actual
        this.obtenerImportacion(importacionId).subscribe();
      }),
      catchError(error => {
        console.error('❌ Error al validar datos:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Procesa e importa los datos a la base de datos
   */
  procesarDatos(
    importacionId: number, 
    compradorId: number,
    registrosSeleccionados?: number[]
  ): Observable<ResultadoProcesamiento> {
    const body: any = { comprador_id: compradorId };
    if (registrosSeleccionados && registrosSeleccionados.length > 0) {
      body.registros_seleccionados = registrosSeleccionados;
    }
    
    return this.http.post<ResultadoProcesamiento>(`${this.apiUrl}/${importacionId}/procesar/`, body).pipe(
      tap(resultado => {
        console.log('✅ Procesamiento completado:', resultado);
        // Actualizar la importación actual
        this.obtenerImportacion(importacionId).subscribe();
      }),
      catchError(error => {
        console.error('❌ Error al procesar datos:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Obtiene una importación específica
   */
  obtenerImportacion(id: number): Observable<ImportacionExcel> {
    return this.http.get<ImportacionExcel>(`${this.apiUrl}/${id}/`).pipe(
      tap(importacion => {
        this.importacionActualSubject.next(importacion);
      })
    );
  }

  /**
   * Lista todas las importaciones del usuario
   */
  listarImportaciones(params?: any): Observable<{ count: number; results: ImportacionExcel[] }> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    
    return this.http.get<{ count: number; results: ImportacionExcel[] }>(this.apiUrl + '/', { params: httpParams });
  }

  /**
   * Obtiene el reporte de errores de una importación
   */
  obtenerReporteErrores(importacionId: number): Observable<ReporteErrores> {
    return this.http.get<ReporteErrores>(`${this.apiUrl}/${importacionId}/reporte_errores/`);
  }

  /**
   * Obtiene estadísticas generales de importaciones
   */
  obtenerEstadisticas(): Observable<any> {
    return this.http.get(`${this.apiUrl}/estadisticas/`);
  }

  /**
   * Descarga un archivo de ejemplo para importación
   */
  descargarPlantillaEjemplo(): void {
    // Crear datos de ejemplo
    const datosEjemplo = [
      {
        'HAWB': 'HAWB001',
        'Peso Total': 5.5,
        'Cantidad Total': 2,
        'Valor Total': 150.00,
        'Estado': 'pendiente',
        'Descripción Producto': 'Laptop Dell',
        'Peso Producto': 2.5,
        'Cantidad Producto': 1,
        'Valor Producto': 100.00,
        'Categoría': 'electronica',
        'Observaciones': 'Envío urgente'
      },
      {
        'HAWB': 'HAWB002',
        'Peso Total': 1.2,
        'Cantidad Total': 3,
        'Valor Total': 45.50,
        'Estado': 'pendiente',
        'Descripción Producto': 'Camiseta Nike',
        'Peso Producto': 0.4,
        'Cantidad Producto': 3,
        'Valor Producto': 45.50,
        'Categoría': 'ropa',
        'Observaciones': ''
      }
    ];
    
    // Crear workbook
    const ws = XLSX.utils.json_to_sheet(datosEjemplo);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Datos');
    
    // Descargar
    XLSX.writeFile(wb, 'plantilla_importacion_envios.xlsx');
    console.log('✅ Plantilla de ejemplo descargada');
  }

  /**
   * Limpia el estado actual
   */
  limpiarEstado(): void {
    this.importacionActualSubject.next(null);
    this.previewDatosSubject.next(null);
  }

  /**
   * Detecta duplicados en una columna específica
   */
  detectarDuplicados(filas: FilaExcel[], nombreColumna: string): number[] {
    const valores = new Map<any, number[]>();
    const duplicados: number[] = [];
    
    filas.forEach(fila => {
      const valor = fila[nombreColumna];
      if (valor !== null && valor !== undefined && valor !== '') {
        if (!valores.has(valor)) {
          valores.set(valor, []);
        }
        valores.get(valor)!.push(fila._indice);
      }
    });
    
    // Identificar duplicados
    valores.forEach((indices) => {
      if (indices.length > 1) {
        duplicados.push(...indices);
      }
    });
    
    return duplicados;
  }

  /**
   * Valida formato de datos localmente antes de enviar al backend
   */
  validarDatosLocalmente(filas: FilaExcel[], mapeoColumnas: MapeoColumnas): any[] {
    const errores: any[] = [];
    
    filas.forEach(fila => {
      const erroresFila: any[] = [];
      
      // Validar campos según el mapeo
      Object.entries(mapeoColumnas).forEach(([columnaExcel, campoModelo]) => {
        const valor = fila[columnaExcel];
        
        // Validar HAWB (obligatorio)
        if (campoModelo === 'hawb' && (!valor || valor.toString().trim() === '')) {
          erroresFila.push({
            columna: columnaExcel,
            error: 'HAWB es obligatorio'
          });
        }
        
        // Validar números
        if (['peso', 'peso_total', 'valor', 'valor_total'].includes(campoModelo)) {
          if (valor && isNaN(Number(valor))) {
            erroresFila.push({
              columna: columnaExcel,
              error: 'Debe ser un número válido'
            });
          }
        }
        
        // Validar enteros
        if (['cantidad', 'cantidad_total'].includes(campoModelo)) {
          if (valor && (!Number.isInteger(Number(valor)) || Number(valor) < 0)) {
            erroresFila.push({
              columna: columnaExcel,
              error: 'Debe ser un número entero positivo'
            });
          }
        }
      });
      
      if (erroresFila.length > 0) {
        errores.push({
          fila: fila._indice + 2, // +2 porque Excel empieza en 1 y hay header
          errores: erroresFila
        });
      }
    });
    
    return errores;
  }

  /**
   * Exporta errores a Excel para revisión
   */
  exportarErrores(reporte: ReporteErrores): void {
    const datosErrores: any[] = [];
    
    Object.entries(reporte.errores).forEach(([fila, errores]) => {
      errores.forEach(error => {
        datosErrores.push({
          'Fila': fila.replace('fila_', ''),
          'Columna': error.columna,
          'Error': error.mensaje
        });
      });
    });
    
    if (datosErrores.length === 0) {
      console.log('✅ No hay errores para exportar');
      return;
    }
    
    // Crear workbook
    const ws = XLSX.utils.json_to_sheet(datosErrores);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Errores');
    
    // Descargar
    const nombreArchivo = `errores_${reporte.nombre_archivo}_${new Date().getTime()}.xlsx`;
    XLSX.writeFile(wb, nombreArchivo);
    console.log('✅ Reporte de errores exportado:', nombreArchivo);
  }
}


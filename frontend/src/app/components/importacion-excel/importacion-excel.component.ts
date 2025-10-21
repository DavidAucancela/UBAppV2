import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ImportacionExcelService } from '../../services/importacion-excel.service';
import {
  ImportacionExcel,
  PreviewExcel,
  FilaExcel,
  MapeoColumnas,
  CAMPOS_DISPONIBLES,
  CampoDisponible,
  ErrorDetectado
} from '../../models/importacion-excel.model';

/**
 * Componente para cargar y procesar archivos Excel
 */
@Component({
  selector: 'app-importacion-excel',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './importacion-excel.component.html',
  styleUrls: ['./importacion-excel.component.css']
})
export class ImportacionExcelComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  // Estados del proceso
  paso: number = 1; // 1: Cargar, 2: Mapear, 3: Validar, 4: Procesar
  cargando: boolean = false;
  mensajeError: string = '';
  mensajeExito: string = '';
  
  // Archivo seleccionado
  archivoSeleccionado: File | null = null;
  
  // Preview de datos
  previewDatos: PreviewExcel | null = null;
  
  // Importación actual
  importacionActual: ImportacionExcel | null = null;
  
  // Mapeo de columnas
  mapeoColumnas: MapeoColumnas = {};
  camposDisponibles = CAMPOS_DISPONIBLES;
  
  // Selección de registros
  todosSeleccionados: boolean = true;
  registrosSeleccionados: Set<number> = new Set();
  
  // Validación
  erroresValidacion: ErrorDetectado[] = [];
  duplicados: number[] = [];
  
  // Comprador seleccionado
  compradorId: number | null = null;
  
  // Paginación de la tabla
  paginaActual: number = 1;
  filasPorPagina: number = 10;

  constructor(private importacionExcelService: ImportacionExcelService) {}

  ngOnInit(): void {
    // Suscribirse a cambios en la importación actual
    this.importacionExcelService.importacionActual$
      .pipe(takeUntil(this.destroy$))
      .subscribe(importacion => {
        this.importacionActual = importacion;
      });

    // Suscribirse a cambios en preview
    this.importacionExcelService.previewDatos$
      .pipe(takeUntil(this.destroy$))
      .subscribe(preview => {
        this.previewDatos = preview;
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    this.importacionExcelService.limpiarEstado();
  }

  /**
   * Maneja la selección de archivo
   */
  onArchivoSeleccionado(event: any): void {
    const archivo = event.target.files[0];
    if (!archivo) return;

    // Validar tipo de archivo
    const nombreArchivo = archivo.name.toLowerCase();
    if (!nombreArchivo.endsWith('.xlsx') && !nombreArchivo.endsWith('.xls')) {
      this.mostrarError('Por favor seleccione un archivo Excel (.xlsx o .xls)');
      return;
    }

    this.archivoSeleccionado = archivo;
    this.mensajeError = '';
    
    // Vista previa local rápida
    this.cargarVistaPrevia();
  }

  /**
   * Carga vista previa del archivo localmente
   */
  async cargarVistaPrevia(): Promise<void> {
    if (!this.archivoSeleccionado) return;

    this.cargando = true;
    this.mensajeError = '';

    try {
      this.previewDatos = await this.importacionExcelService.leerArchivoLocal(this.archivoSeleccionado);
      this.mostrarExito('✅ Archivo cargado correctamente. Total de filas: ' + this.previewDatos.total_filas);
      
      // Inicializar mapeo automático
      this.inicializarMapeoAutomatico();
      
    } catch (error: any) {
      this.mostrarError('Error al leer el archivo: ' + error.message);
    } finally {
      this.cargando = false;
    }
  }

  /**
   * Intenta mapear automáticamente las columnas
   */
  inicializarMapeoAutomatico(): void {
    if (!this.previewDatos) return;

    this.mapeoColumnas = {};
    
    this.previewDatos.columnas.forEach(columna => {
      const columnaNormalizada = columna.toLowerCase().trim()
        .replace(/\s+/g, '_')
        .replace(/[áàäâ]/g, 'a')
        .replace(/[éèëê]/g, 'e')
        .replace(/[íìïî]/g, 'i')
        .replace(/[óòöô]/g, 'o')
        .replace(/[úùüû]/g, 'u');

      // Buscar coincidencias
      const campo = this.camposDisponibles.find(c => 
        columnaNormalizada.includes(c.valor) || 
        c.valor.includes(columnaNormalizada) ||
        c.etiqueta.toLowerCase().replace(/\s+/g, '_') === columnaNormalizada
      );

      if (campo) {
        this.mapeoColumnas[columna] = campo.valor;
      }
    });

    console.log('Mapeo automático:', this.mapeoColumnas);
  }

  /**
   * Sube el archivo al backend
   */
  subirArchivo(): void {
    if (!this.archivoSeleccionado) {
      this.mostrarError('Por favor seleccione un archivo');
      return;
    }

    this.cargando = true;
    this.mensajeError = '';

    this.importacionExcelService.subirArchivo(this.archivoSeleccionado)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (importacion) => {
          this.importacionActual = importacion;
          this.mostrarExito('✅ Archivo subido correctamente');
          
          // Obtener preview del backend
          this.obtenerPreviewBackend(importacion.id);
        },
        error: (error) => {
          this.mostrarError('Error al subir el archivo: ' + (error.error?.error || error.message));
          this.cargando = false;
        }
      });
  }

  /**
   * Obtiene la vista previa desde el backend
   */
  obtenerPreviewBackend(importacionId: number): void {
    this.importacionExcelService.obtenerPreview(importacionId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (preview) => {
          this.previewDatos = preview;
          this.duplicados = preview.duplicados || [];
          
          if (this.duplicados.length > 0) {
            this.mostrarError(`⚠️ Se detectaron ${this.duplicados.length} registros duplicados`);
          }
          
          this.paso = 2; // Avanzar a mapeo
          this.cargando = false;
        },
        error: (error) => {
          this.mostrarError('Error al obtener vista previa: ' + (error.error?.error || error.message));
          this.cargando = false;
        }
      });
  }

  /**
   * Valida los datos con el backend
   */
  validarDatos(): void {
    if (!this.importacionActual) {
      this.mostrarError('No hay archivo cargado');
      return;
    }

    // Validar que al menos HAWB esté mapeado
    const hawbMapeado = Object.values(this.mapeoColumnas).includes('hawb');
    if (!hawbMapeado) {
      this.mostrarError('El campo HAWB es obligatorio. Por favor mapearlo.');
      return;
    }

    this.cargando = true;
    this.mensajeError = '';

    this.importacionExcelService.validarDatos(this.importacionActual.id, this.mapeoColumnas)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (resultado) => {
          this.erroresValidacion = resultado.errores;
          
          if (resultado.errores.length === 0) {
            this.mostrarExito('✅ ' + resultado.mensaje + '. Todos los datos son válidos.');
          } else {
            this.mostrarError(`⚠️ Se encontraron ${resultado.errores.length} errores de validación`);
          }
          
          this.paso = 3; // Avanzar a selección
          this.cargando = false;
          
          // Inicializar todos como seleccionados
          this.seleccionarTodos(true);
        },
        error: (error) => {
          this.mostrarError('Error al validar: ' + (error.error?.error || error.message));
          this.cargando = false;
        }
      });
  }

  /**
   * Procesa e importa los datos
   */
  procesarDatos(): void {
    if (!this.importacionActual) {
      this.mostrarError('No hay archivo cargado');
      return;
    }

    if (!this.compradorId) {
      this.mostrarError('Por favor seleccione un comprador');
      return;
    }

    const registrosSeleccionados = this.todosSeleccionados 
      ? undefined 
      : Array.from(this.registrosSeleccionados);

    this.cargando = true;
    this.mensajeError = '';

    this.importacionExcelService.procesarDatos(
      this.importacionActual.id,
      this.compradorId,
      registrosSeleccionados
    ).pipe(takeUntil(this.destroy$))
    .subscribe({
      next: (resultado) => {
        this.mostrarExito('✅ ' + resultado.mensaje);
        this.paso = 4; // Completado
        this.cargando = false;
      },
      error: (error) => {
        this.mostrarError('Error al procesar: ' + (error.error?.error || error.message));
        this.cargando = false;
      }
    });
  }

  /**
   * Selecciona/deselecciona todos los registros
   */
  seleccionarTodos(seleccionar: boolean): void {
    this.todosSeleccionados = seleccionar;
    
    if (seleccionar) {
      this.registrosSeleccionados.clear();
      if (this.previewDatos) {
        this.previewDatos.filas.forEach(fila => {
          this.registrosSeleccionados.add(fila._indice);
        });
      }
    } else {
      this.registrosSeleccionados.clear();
    }
  }

  /**
   * Toggle selección de un registro
   */
  toggleSeleccion(indice: number): void {
    if (this.registrosSeleccionados.has(indice)) {
      this.registrosSeleccionados.delete(indice);
    } else {
      this.registrosSeleccionados.add(indice);
    }
    
    this.actualizarTodosSeleccionados();
  }

  /**
   * Actualiza el estado de "todos seleccionados"
   */
  actualizarTodosSeleccionados(): void {
    if (!this.previewDatos) return;
    this.todosSeleccionados = this.registrosSeleccionados.size === this.previewDatos.total_filas;
  }

  /**
   * Verifica si una fila tiene errores
   */
  tieneError(indice: number): boolean {
    return this.erroresValidacion.some(e => e.fila === indice + 2);
  }

  /**
   * Verifica si una fila está duplicada
   */
  esDuplicado(indice: number): boolean {
    return this.duplicados.includes(indice);
  }

  /**
   * Descarga la plantilla de ejemplo
   */
  descargarPlantilla(): void {
    this.importacionExcelService.descargarPlantillaEjemplo();
    this.mostrarExito('✅ Plantilla de ejemplo descargada');
  }

  /**
   * Descarga el reporte de errores
   */
  descargarReporteErrores(): void {
    if (!this.importacionActual) return;

    this.importacionExcelService.obtenerReporteErrores(this.importacionActual.id)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (reporte) => {
          this.importacionExcelService.exportarErrores(reporte);
          this.mostrarExito('✅ Reporte de errores descargado');
        },
        error: (error) => {
          this.mostrarError('Error al descargar reporte: ' + error.message);
        }
      });
  }

  /**
   * Reinicia el proceso
   */
  reiniciar(): void {
    this.paso = 1;
    this.archivoSeleccionado = null;
    this.previewDatos = null;
    this.importacionActual = null;
    this.mapeoColumnas = {};
    this.erroresValidacion = [];
    this.duplicados = [];
    this.registrosSeleccionados.clear();
    this.mensajeError = '';
    this.mensajeExito = '';
    this.importacionExcelService.limpiarEstado();
  }

  /**
   * Obtiene las filas paginadas
   */
  get filasPaginadas(): FilaExcel[] {
    if (!this.previewDatos) return [];
    const inicio = (this.paginaActual - 1) * this.filasPorPagina;
    const fin = inicio + this.filasPorPagina;
    return this.previewDatos.filas.slice(inicio, fin);
  }

  /**
   * Total de páginas
   */
  get totalPaginas(): number {
    if (!this.previewDatos) return 0;
    return Math.ceil(this.previewDatos.filas.length / this.filasPorPagina);
  }

  /**
   * Muestra mensaje de error
   */
  private mostrarError(mensaje: string): void {
    this.mensajeError = mensaje;
    this.mensajeExito = '';
    setTimeout(() => {
      this.mensajeError = '';
    }, 8000);
  }

  /**
   * Muestra mensaje de éxito
   */
  private mostrarExito(mensaje: string): void {
    this.mensajeExito = mensaje;
    this.mensajeError = '';
    setTimeout(() => {
      this.mensajeExito = '';
    }, 5000);
  }

  /**
   * Obtiene las columnas mapeadas
   */
  get columnasMapeadas(): string[] {
    return Object.keys(this.mapeoColumnas);
  }

  /**
   * Verifica si el mapeo es válido
   */
  get mapeoValido(): boolean {
    return Object.values(this.mapeoColumnas).includes('hawb');
  }

  /**
   * Obtiene la descripción de un campo mapeado
   */
  obtenerDescripcionCampo(columna: string): string {
    const valorMapeado = this.mapeoColumnas[columna];
    if (!valorMapeado) return '';
    const campo = this.camposDisponibles.find(c => c.valor === valorMapeado);
    return campo?.descripcion || '';
  }
}


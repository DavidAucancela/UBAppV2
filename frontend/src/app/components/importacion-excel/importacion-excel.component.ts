import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ImportacionExcelService } from '../../services/importacion-excel.service';
import { ApiService } from '../../services/api.service';
import {
  ImportacionExcel,
  PreviewExcel,
  FilaExcel,
  MapeoColumnas,
  CAMPOS_DISPONIBLES,
  CampoDisponible,
  ErrorDetectado,
  CompradorPendiente,
  ActualizacionFila
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
  columnasIgnoradas = ['factura comercial', 'factura_comercial', '_empty', '_empty_1', 'unnamed: 0', 'unnamed: 1'];
  valoresVacios = ['', '-', '--', '—', 'n/a', 'na', 's/n', 'n.d'];
  palabrasClavePropagacion = [
    'nombre', 'consignatario', 'comprador', 'cliente',
    'ruc', 'cedula', 'cedula', 'cédula', 'identificacion', 'identificación',
    'direccion', 'dirección', 'telefono', 'teléfono', 'correo', 'email'
  ];
  datosActualizados: Record<number, { [columna: string]: any }> = {};
  compradoresPendientes: CompradorPendiente[] = [];
  estadoCompradores: Record<number, 'pendiente' | 'guardando' | 'guardado' | 'error'> = {};
  
  // Selección de registros
  todosSeleccionados: boolean = true;
  registrosSeleccionados: Set<number> = new Set();
  
  // Gestión de comprador cuando no hay columnas de consignatario
  tieneColumnasConsignatario: boolean = false;
  compradorSeleccionadoId: number | null = null;
  usuariosDisponibles: any[] = [];
  mostrarSeleccionComprador: boolean = false;
  modoCrearUsuario: boolean = false;
  nuevoUsuario: any = {
    nombre: '',
    cedula: '',
    correo: '',
    telefono: '',
    direccion: ''
  };
  
  // Validación
  erroresValidacion: ErrorDetectado[] = [];
  duplicados: number[] = [];
  
  // Paginación de la tabla
  paginaActual: number = 1;
  filasPorPagina: number = 10;
  
  // Exponer Math para usar en el template
  Math = Math;

  constructor(
    private importacionExcelService: ImportacionExcelService,
    private apiService: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    // Suscribirse a cambios en la importación actual
    this.importacionExcelService.importacionActual$
      .pipe(takeUntil(this.destroy$))
      .subscribe((importacion) => {
        this.importacionActual = importacion;
      });

    // Suscribirse a cambios en preview
    this.importacionExcelService.previewDatos$
      .pipe(takeUntil(this.destroy$))
      .subscribe((preview) => {
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
      const preview = await this.importacionExcelService.leerArchivoLocal(this.archivoSeleccionado);
      this.previewDatos = this.normalizarPreview(preview);
      this.datosActualizados = {};
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
   * Normaliza la vista previa eliminando columnas no usadas y propagando valores
   */
  private normalizarPreview(preview: PreviewExcel | null): PreviewExcel {
    if (!preview) {
      return {
        columnas: [],
        filas: [],
        total_filas: 0
      };
    }

    const columnasUtiles = preview.columnas.filter(col => !this.esColumnaIgnorada(col));
    const filasNormalizadas: FilaExcel[] = preview.filas.map(fila => {
      const nueva: FilaExcel = { _indice: fila._indice };
      columnasUtiles.forEach(col => {
        nueva[col] = fila[col];
      });
      return nueva;
    });

    this.propagarValoresConsignatario(filasNormalizadas, columnasUtiles);

    return {
      ...preview,
      columnas: columnasUtiles,
      filas: filasNormalizadas
    };
  }

  /**
   * Verifica si el archivo tiene columnas de consignatario y ruc/cedula
   */
  verificarColumnasConsignatario(): boolean {
    if (!this.previewDatos) return false;
    
    // Verificar si hay columnas mapeadas a consignatario_nombre y consignatario_identificacion
    const tieneConsignatario = Object.values(this.mapeoColumnas).includes('consignatario_nombre');
    const tieneRuc = Object.values(this.mapeoColumnas).includes('consignatario_identificacion');
    
    // También verificar si existen columnas con nombres similares aunque no estén mapeadas
    const columnasConsignatario = this.previewDatos.columnas.some(col => {
      const normalizado = this.normalizarTexto(col);
      return normalizado.includes('consignatario') || 
             normalizado.includes('destinatario') || 
             normalizado.includes('cliente') ||
             normalizado.includes('comprador');
    });
    
    const columnasRuc = this.previewDatos.columnas.some(col => {
      const normalizado = this.normalizarTexto(col);
      return normalizado.includes('ruc') || 
             normalizado.includes('cedula') || 
             normalizado.includes('cédula') ||
             normalizado.includes('identificacion') ||
             normalizado.includes('identificación');
    });
    
    return (tieneConsignatario && tieneRuc) || (columnasConsignatario && columnasRuc);
  }

  /**
   * Genera valores HAWB automáticamente desde el sistema
   * IGNORA completamente el HAWB del archivo Excel
   * El HAWB se generará automáticamente en el backend al crear cada envío
   */
  generarHawbAutomatico(): void {
    if (!this.previewDatos || !this.columnaHawb) return;

    // Guardar referencias locales para evitar problemas de tipos
    const previewDatos = this.previewDatos;
    const columnaHawb = this.columnaHawb;

    // Obtener el siguiente HAWB del sistema
    this.apiService.getEnvios().subscribe({
      next: (envios) => {
        const hawbNumbers: number[] = [];
        
        // Extraer números de HAWBs existentes
        envios.forEach((envio: any) => {
          const match = envio.hawb?.match(/(\d+)$/);
          if (match) {
            hawbNumbers.push(parseInt(match[1], 10));
          }
        });
        
        // Calcular el siguiente número HAWB
        let siguienteNumero = 1;
        if (hawbNumbers.length > 0) {
          const maxNumber = Math.max(...hawbNumbers);
          siguienteNumero = maxNumber + 1;
        }
        
        // Marcar todas las filas para que el backend ignore el HAWB del archivo
        // y genere automáticamente el siguiente HAWB secuencial
        if (columnaHawb && previewDatos) {
          previewDatos.filas.forEach((fila) => {
            // Limpiar el HAWB del archivo (el backend lo generará automáticamente)
            fila[columnaHawb] = '';
            this.registrarCambio(fila._indice, columnaHawb, '');
          });
        }
      },
      error: (error) => {
        console.error('Error obteniendo envíos para generar HAWB:', error);
        // En caso de error, simplemente limpiar los HAWBs del archivo
        if (columnaHawb && previewDatos) {
          previewDatos.filas.forEach((fila) => {
            fila[columnaHawb] = '';
            this.registrarCambio(fila._indice, columnaHawb, '');
          });
        }
      }
    });
  }

  /**
   * Extrae el número de un valor HAWB (puede ser string o número)
   */
  private extraerNumeroHawb(valor: any): number | null {
    if (typeof valor === 'number') {
      return valor;
    }
    if (typeof valor === 'string') {
      // Intentar extraer números del string
      const numeros = valor.match(/\d+/);
      if (numeros) {
        return parseInt(numeros[0], 10);
      }
    }
    return null;
  }

  private esColumnaIgnorada(nombre: string): boolean {
    const normalizado = this.normalizarTexto(nombre);
    return this.columnasIgnoradas.some(col => normalizado.includes(col));
  }

  private normalizarTexto(valor: string): string {
    return valor
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, '_')
      .replace(/[^a-z0-9_]/g, '')
      .trim();
  }

  private propagarValoresConsignatario(filas: FilaExcel[], columnas: string[]): void {
    const columnasPropagables = columnas.filter(col => {
      const normalizado = this.normalizarTexto(col);
      return this.palabrasClavePropagacion.some(palabra => normalizado.includes(palabra));
    });

    // Columnas especiales que también deben propagarse (peso y fecha_emision)
    const columnasEspeciales = columnas.filter(col => {
      const normalizado = this.normalizarTexto(col);
      return normalizado.includes('peso') || normalizado.includes('fecha');
    });

    const todasLasColumnas = [...new Set([...columnasPropagables, ...columnasEspeciales])];
    const ultimoValor: Record<string, any> = {};

    filas.forEach(fila => {
      todasLasColumnas.forEach(col => {
        const valor = fila[col];
        const valorStr = valor ? String(valor).trim() : '';
        
        // Manejar el caso especial "- -" que significa copiar el valor anterior
        if (valorStr === '-' || valorStr === '--' || valorStr === '- -') {
          if (ultimoValor[col] !== undefined) {
            fila[col] = ultimoValor[col];
            this.registrarCambio(fila._indice, col, ultimoValor[col]);
          }
        } else if (this.esValorVacio(valor)) {
          if (ultimoValor[col] !== undefined) {
            fila[col] = ultimoValor[col];
            this.registrarCambio(fila._indice, col, ultimoValor[col]);
          }
        } else {
          ultimoValor[col] = valor;
        }
      });
    });
  }

  private esValorVacio(valor: any): boolean {
    if (valor === null || valor === undefined) {
      return true;
    }
    if (typeof valor === 'string') {
      return this.valoresVacios.includes(valor.trim().toLowerCase());
    }
    return false;
  }

  /**
   * Intenta mapear automáticamente las columnas
   */
  inicializarMapeoAutomatico(): void {
    if (!this.previewDatos) return;

    this.mapeoColumnas = {};
    
    // Mapeo de variaciones de nombres de columnas (ordenado por prioridad)
    // Las variaciones más específicas primero
    const mapeoVariaciones: { [key: string]: string[] } = {
      'hawb': ['hawb', 'numero guia', 'numero_guia', 'guia', 'n° guía', 'n° guia', 'numero de guia', 'numero guía', 'número guía'],
      'consignatario_nombre': ['consignatario', 'destinatario', 'cliente', 'comprador'],
      'consignatario_identificacion': ['ruc', 'r.u.c', 'cedula', 'cédula', 'documento', 'identificacion', 'identificación'],
      'fecha_emision': ['fecha_emision', 'fecha de emision', 'fecha emisión', 'fecha factura', 'fecha documento', 'fecha'],
      'peso_total': ['peso total', 'peso_total', 'peso kg', 'peso_kg', 'peso en kg', 'peso_en_kg'],
      'peso': ['peso producto', 'peso_producto'],
      'cantidad_total': ['cantidad total', 'cantidad_total', 'total unidades', 'total_unidades'],
      'cantidad': ['cantidad producto', 'cantidad_producto', 'unidades fisicas', 'unidades_fisicas', 'unidades', 'cantidad'],
      'valor_total': ['valor total', 'valor_total', 'valor fob', 'valor_fob', 'valor en usd', 'valor_en_usd'],
      'valor': ['valor producto', 'valor_producto', 'valor unitario', 'valor_unitario', 'precio', 'precio unitario'],
      'descripcion': ['descripcion', 'descripción', 'descripcion producto', 'descripcion_producto', 'producto', 'nombre producto', 'nombre_producto'],
      'categoria': ['categoria', 'categoría', 'categoria producto', 'categoria_producto', 'tipo', 'tipo producto'],
      'estado': ['estado', 'estado envio', 'estado_envio', 'status'],
      'observaciones': ['observaciones', 'notas', 'comentarios', 'observacion', 'comentario']
    };
    
    // Detectar si el formato es el nuevo (tiene CONSIGNATARIO, RUC, etc.)
    const tieneConsignatario = this.previewDatos.columnas.some(c => 
      c.toLowerCase().includes('consignatario')
    );
    
    this.previewDatos.columnas.forEach(columna => {
      const columnaOriginal = columna;
      const columnaNormalizada = columna.toLowerCase().trim()
        .replace(/\s+/g, '_')
        .replace(/[áàäâ]/g, 'a')
        .replace(/[éèëê]/g, 'e')
        .replace(/[íìïî]/g, 'i')
        .replace(/[óòöô]/g, 'o')
        .replace(/[úùüû]/g, 'u')
        .replace(/ñ/g, 'n')
        .replace(/[^a-z0-9_]/g, ''); // Eliminar caracteres especiales

      // Buscar coincidencias exactas primero
      let campoEncontrado: CampoDisponible | undefined;
      
      // Si es el nuevo formato, priorizar mapeos específicos
      if (tieneConsignatario) {
        // En el nuevo formato, "PESO KG" es peso_total, no peso de producto
        if (columnaNormalizada.includes('peso') && columnaNormalizada.includes('kg')) {
          campoEncontrado = this.camposDisponibles.find(c => c.valor === 'peso_total');
        }
        // "VALOR FOB" es valor_total
        else if (columnaNormalizada.includes('valor') && columnaNormalizada.includes('fob')) {
          campoEncontrado = this.camposDisponibles.find(c => c.valor === 'valor_total');
        }
        // "UNIDADES FISICAS" es cantidad (de producto)
        else if (columnaNormalizada.includes('unidades') || columnaNormalizada.includes('fisicas')) {
          campoEncontrado = this.camposDisponibles.find(c => c.valor === 'cantidad');
        }
        // "DESCRIPCIÓN" es descripción de producto
        else if (columnaNormalizada.includes('descripcion') || columnaNormalizada.includes('descripción')) {
          campoEncontrado = this.camposDisponibles.find(c => c.valor === 'descripcion');
        }
      }
      
      // Si no se encontró con la lógica específica, buscar en variaciones
      if (!campoEncontrado) {
        for (const [campoValor, variaciones] of Object.entries(mapeoVariaciones)) {
          if (variaciones.some(v => columnaNormalizada.includes(v) || v.includes(columnaNormalizada))) {
            campoEncontrado = this.camposDisponibles.find(c => c.valor === campoValor);
            if (campoEncontrado) break;
          }
        }
      }
      
      // Si no se encontró, buscar coincidencias parciales
      if (!campoEncontrado) {
        campoEncontrado = this.camposDisponibles.find(c => {
          const valorNormalizado = c.valor.toLowerCase();
          const etiquetaNormalizada = c.etiqueta.toLowerCase().replace(/\s+/g, '_');
          return columnaNormalizada.includes(valorNormalizado) || 
                 valorNormalizado.includes(columnaNormalizada) ||
                 etiquetaNormalizada === columnaNormalizada ||
                 columnaNormalizada.includes(etiquetaNormalizada);
        });
      }

      if (campoEncontrado) {
        this.mapeoColumnas[columnaOriginal] = campoEncontrado.valor;
      }
      // Si no se encuentra, simplemente no se mapea (se ignora)
    });

    console.log('Mapeo automático:', this.mapeoColumnas);
    
    // Generar HAWB automáticamente después del mapeo
    if (this.columnaHawb) {
      this.generarHawbAutomatico();
    }
    
    // Verificar si tiene columnas de consignatario
    this.tieneColumnasConsignatario = this.verificarColumnasConsignatario();
    this.mostrarSeleccionComprador = !this.tieneColumnasConsignatario;
    
    // Si no tiene columnas de consignatario, cargar usuarios disponibles
    if (!this.tieneColumnasConsignatario) {
      this.cargarUsuariosDisponibles();
    }
    
    // Forzar detección de cambios después de inicializar el mapeo
    this.cdr.detectChanges();
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
        next: (importacion: ImportacionExcel) => {
          this.importacionActual = importacion;
          this.mostrarExito('✅ Archivo subido correctamente');
          
          // Obtener preview del backend
          this.obtenerPreviewBackend(importacion.id);
        },
        error: (error: any) => {
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
        next: (preview: PreviewExcel) => {
          const normalizado = this.normalizarPreview(preview);
          this.previewDatos = normalizado;
          this.datosActualizados = {};
          this.duplicados = normalizado.duplicados || [];
          
          // Inicializar mapeo automático después de obtener el preview
          this.inicializarMapeoAutomatico();
          
          // Verificar columnas de consignatario después del mapeo
          this.tieneColumnasConsignatario = this.verificarColumnasConsignatario();
          this.mostrarSeleccionComprador = !this.tieneColumnasConsignatario;
          
          if (this.duplicados.length > 0) {
            this.mostrarError(`⚠️ Se detectaron ${this.duplicados.length} registros duplicados`);
          }
          
          this.paso = 2; // Avanzar a mapeo
          this.cargando = false;
        },
        error: (error: any) => {
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

    // Si no tiene columnas de consignatario, verificar que se haya seleccionado un comprador
    if (!this.tieneColumnasConsignatario && !this.compradorSeleccionadoId && !this.modoCrearUsuario) {
      this.mostrarError('Debe seleccionar un comprador o crear uno nuevo para continuar');
      return;
    }

    // Si está en modo crear usuario, validar datos del nuevo usuario
    if (this.modoCrearUsuario) {
      if (!this.nuevoUsuario.nombre || !this.nuevoUsuario.cedula) {
        this.mostrarError('El nombre y la cédula son obligatorios para crear un nuevo usuario');
        return;
      }
    }

    // Validar campos obligatorios (excluyendo consignatario si no hay columnas)
    const camposObligatorios = this.obtenerCamposObligatorios();
    const faltantes = camposObligatorios.filter(campo => !Object.values(this.mapeoColumnas).includes(campo));
    if (faltantes.length > 0) {
      this.mostrarError(`Los campos obligatorios (${faltantes.join(', ')}) deben estar mapeados.`);
      return;
    }

    this.cargando = true;
    this.mensajeError = '';

    this.importacionExcelService.validarDatos(this.importacionActual.id, this.mapeoColumnas)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (resultado: any) => {
          this.erroresValidacion = resultado.errores;
          
          if (resultado.errores.length === 0) {
            this.mostrarExito('✅ ' + resultado.mensaje + '. Todos los datos son válidos.');
          } else {
            this.mostrarError(`⚠️ Se encontraron ${resultado.errores.length} errores de validación`);
          }
          
          this.paso = 3; // Avanzar a selección
          this.cargando = false;
          
          // Reiniciar paginación al avanzar al paso 3
          this.paginaActual = 1;
          
          // Inicializar todos como seleccionados
          this.seleccionarTodos(true);
        },
        error: (error: any) => {
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

    // Si no tiene columnas de consignatario, verificar que se haya seleccionado un comprador
    let compradorId: number | null = null;
    
    if (!this.tieneColumnasConsignatario) {
      if (this.modoCrearUsuario) {
        // Crear el nuevo usuario primero
        this.crearNuevoUsuario().then(usuarioCreado => {
          if (usuarioCreado) {
            compradorId = usuarioCreado.id!;
            this.procesarDatosConComprador(compradorId);
          }
        });
        return;
      } else if (this.compradorSeleccionadoId) {
        compradorId = this.compradorSeleccionadoId;
      } else {
        this.mostrarError('Debe seleccionar un comprador o crear uno nuevo para continuar');
        return;
      }
    }

    this.procesarDatosConComprador(compradorId);
  }

  /**
   * Procesa los datos con el comprador seleccionado
   */
  private procesarDatosConComprador(compradorId: number | null): void {
    if (!this.importacionActual) return;

    const registrosSeleccionados = this.todosSeleccionados 
      ? undefined 
      : Array.from(this.registrosSeleccionados);
    const actualizaciones = this.obtenerActualizaciones();

    this.cargando = true;
    this.mensajeError = '';

    this.importacionExcelService.procesarDatos(
      this.importacionActual.id,
      registrosSeleccionados,
      actualizaciones,
      compradorId
    ).pipe(takeUntil(this.destroy$))
    .subscribe({
      next: (resultado) => {
        this.mostrarExito('✅ ' + resultado.mensaje);
        this.datosActualizados = {};
        this.compradoresPendientes = resultado.compradores_pendientes || [];
        this.estadoCompradores = {};
        this.compradoresPendientes.forEach(cp => {
          if (cp.id) {
            this.estadoCompradores[cp.id] = 'pendiente';
          }
        });
        this.paso = 4; // Completado
        this.cargando = false;
      },
      error: (error: any) => {
        this.mostrarError('Error al procesar: ' + (error.error?.error || error.message));
        this.cargando = false;
      }
    });
  }

  /**
   * Carga los usuarios disponibles del sistema
   */
  cargarUsuariosDisponibles(): void {
    this.apiService.getCompradores()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (usuarios) => {
          this.usuariosDisponibles = usuarios;
        },
        error: (error) => {
          console.error('Error al cargar usuarios:', error);
          this.mostrarError('Error al cargar lista de usuarios');
        }
      });
  }

  /**
   * Crea un nuevo usuario comprador
   */
  crearNuevoUsuario(): Promise<any> {
    return new Promise((resolve, reject) => {
      const nuevoUsuario = {
        username: this.nuevoUsuario.cedula,
        nombre: this.nuevoUsuario.nombre,
        cedula: this.nuevoUsuario.cedula,
        correo: this.nuevoUsuario.correo || '',
        telefono: this.nuevoUsuario.telefono || '',
        direccion: this.nuevoUsuario.direccion || '',
        rol: 4, // Comprador
        es_activo: true
      };

      this.apiService.createUsuario(nuevoUsuario)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (usuarioCreado) => {
            this.mostrarExito(`✅ Usuario ${usuarioCreado.nombre} creado exitosamente`);
            this.compradorSeleccionadoId = usuarioCreado.id!;
            this.modoCrearUsuario = false;
            resolve(usuarioCreado);
          },
          error: (error) => {
            this.mostrarError('Error al crear usuario: ' + (error.error?.error || error.message));
            reject(error);
          }
        });
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
          if (!this.tieneError(fila._indice)) {
            this.registrosSeleccionados.add(fila._indice);
          }
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
        next: (reporte: any) => {
          this.importacionExcelService.exportarErrores(reporte);
          this.mostrarExito('✅ Reporte de errores descargado');
        },
        error: (error: any) => {
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
    this.datosActualizados = {};
    this.compradoresPendientes = [];
    this.estadoCompradores = {};
    this.mensajeError = '';
    this.mensajeExito = '';
    this.tieneColumnasConsignatario = false;
    this.compradorSeleccionadoId = null;
    this.usuariosDisponibles = [];
    this.mostrarSeleccionComprador = false;
    this.modoCrearUsuario = false;
    this.nuevoUsuario = {
      nombre: '',
      cedula: '',
      correo: '',
      telefono: '',
      direccion: ''
    };
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
    if (!this.mapeoColumnas || Object.keys(this.mapeoColumnas).length === 0) {
      return false;
    }
    
    const camposObligatorios = this.obtenerCamposObligatorios();
    // Filtrar valores nulos, undefined o cadenas vacías
    const valoresMapeados = Object.values(this.mapeoColumnas).filter(
      valor => valor !== null && valor !== undefined && valor !== ''
    );
    
    const esValido = camposObligatorios.every(campo => valoresMapeados.includes(campo));
    
    // Debug: descomentar para ver qué está pasando
    // console.log('Validación mapeo:', {
    //   camposObligatorios,
    //   valoresMapeados,
    //   mapeoColumnas: this.mapeoColumnas,
    //   esValido
    // });
    
    return esValido;
  }

  /**
   * Maneja el cambio en el mapeo de una columna
   */
  onMapeoCambiado(): void {
    // Si se mapea HAWB, generar valores automáticamente
    if (this.columnaHawb) {
      this.generarHawbAutomatico();
    }
    
    // Actualizar verificación de columnas de consignatario
    this.tieneColumnasConsignatario = this.verificarColumnasConsignatario();
    this.mostrarSeleccionComprador = !this.tieneColumnasConsignatario;
    
    // Si no tiene columnas de consignatario y aún no se han cargado usuarios, cargarlos
    if (!this.tieneColumnasConsignatario && this.usuariosDisponibles.length === 0) {
      this.cargarUsuariosDisponibles();
    }
    
    // Forzar detección de cambios
    this.cdr.detectChanges();
  }

  /**
   * Obtiene los campos obligatorios que faltan por mapear
   */
  get camposObligatoriosFaltantes(): string[] {
    if (!this.mapeoColumnas || Object.keys(this.mapeoColumnas).length === 0) {
      return this.obtenerCamposObligatorios();
    }
    
    const camposObligatorios = this.obtenerCamposObligatorios();
    const valoresMapeados = Object.values(this.mapeoColumnas).filter(
      valor => valor !== null && valor !== undefined && valor !== ''
    );
    
    return camposObligatorios.filter(campo => !valoresMapeados.includes(campo));
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

  /**
   * Cambia al modo de crear nuevo usuario
   */
  activarModoCrearUsuario(): void {
    this.modoCrearUsuario = true;
    this.compradorSeleccionadoId = null;
  }

  /**
   * Cancela el modo de crear usuario y vuelve a selección
   */
  cancelarCrearUsuario(): void {
    this.modoCrearUsuario = false;
    this.nuevoUsuario = {
      nombre: '',
      cedula: '',
      correo: '',
      telefono: '',
      direccion: ''
    };
  }
  
  obtenerColumnaPorCampo(campo: string): string | null {
    const entrada = Object.entries(this.mapeoColumnas).find(([, valor]) => valor === campo);
    return entrada ? entrada[0] : null;
  }
  
  get columnaHawb(): string | null {
    return this.obtenerColumnaPorCampo('hawb');
  }

  get columnaConsignatario(): string | null {
    return this.obtenerColumnaPorCampo('consignatario_nombre');
  }

  get columnaRuc(): string | null {
    return this.obtenerColumnaPorCampo('consignatario_identificacion');
  }

  get columnaDescripcion(): string | null {
    return this.obtenerColumnaPorCampo('descripcion');
  }

  get columnaPesoProducto(): string | null {
    return this.obtenerColumnaPorCampo('peso');
  }

  get columnaCantidadProducto(): string | null {
    return this.obtenerColumnaPorCampo('cantidad');
  }

  get columnaValorProducto(): string | null {
    return this.obtenerColumnaPorCampo('valor');
  }

  registrarCambio(indice: number, columna: string, valor: any): void {
    if (!columna) return;
    if (!this.datosActualizados[indice]) {
      this.datosActualizados[indice] = {};
    }
    this.datosActualizados[indice][columna] = valor;
  }

  private obtenerActualizaciones(): ActualizacionFila[] {
    return Object.entries(this.datosActualizados).map(([indice, valores]) => ({
      indice: Number(indice),
      valores
    }));
  }

  get pesosCompletos(): boolean {
    if (!this.previewDatos) return true;
    const columnaPeso = this.obtenerColumnaPorCampo('peso');
    if (!columnaPeso) return true;
    if (this.registrosSeleccionados.size === 0) return false;

    const filasSeleccionadas = this.previewDatos.filas.filter(fila =>
      this.registrosSeleccionados.has(fila._indice)
    );

    return filasSeleccionadas.every(fila => !this.esValorVacio(fila[columnaPeso]));
  }

  private obtenerCamposObligatorios(): string[] {
    const camposObligatorios = this.camposDisponibles
      .filter(campo => campo.requerido)
      .map(campo => campo.valor);
    
    // Si no tiene columnas de consignatario, no requerir consignatario_nombre ni consignatario_identificacion
    if (!this.tieneColumnasConsignatario) {
      return camposObligatorios.filter(
        campo => campo !== 'consignatario_nombre' && campo !== 'consignatario_identificacion'
      );
    }
    
    return camposObligatorios;
  }

  guardarCompradorPendiente(comprador: CompradorPendiente): void {
    if (!comprador?.id) return;
    this.estadoCompradores[comprador.id] = 'guardando';

    const payload: Partial<CompradorPendiente> = {};
    if (comprador.correo !== undefined) payload.correo = comprador.correo;
    if (comprador.telefono !== undefined) payload.telefono = comprador.telefono;
    if (comprador.direccion !== undefined) payload.direccion = comprador.direccion;

    this.apiService.actualizarUsuarioParcial(comprador.id, payload)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.estadoCompradores[comprador.id!] = 'guardado';
          this.mostrarExito(`Datos del comprador ${comprador.nombre} actualizados.`);
        },
        error: (error: any) => {
          this.estadoCompradores[comprador.id!] = 'error';
          this.mostrarError('Error al actualizar comprador: ' + (error.error?.error || error.message));
        }
      });
  }
}


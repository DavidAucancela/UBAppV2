import { Component, OnInit, HostListener, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormArray } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { ApiService } from '../../../services/api.service';
import { AuthService } from '../../../services/auth.service';
import { Envio, EnvioCreate, EstadosEnvio, ESTADOS_LABELS } from '../../../models/envio';
import { Producto, ProductoCreate, CategoriasProducto, CATEGORIAS_LABELS } from '../../../models/producto';
import { Usuario } from '../../../models/usuario';

@Component({
  selector: 'app-envios-list',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './envios-list.component.html',
  styleUrl: './envios-list.component.css'
})
export class EnviosListComponent implements OnInit, OnDestroy {
  envios: Envio[] = [];
  filteredEnvios: Envio[] = [];
  compradores: Usuario[] = [];
  productosExistentes: Producto[] = [];
  loading = false;
  submitting = false;
  showModal = false;
  showDetailModal = false;
  editingEnvio: Envio | null = null;
  selectedEnvio: Envio | null = null;
  
  // Cálculo de costos
  costoServicioCalculado = 0;
  detallesCostos: any[] = [];
  calculandoCosto = false;
  
  // Filters
  searchTerm = '';
  selectedEstado = '';
  selectedComprador = '';
  
  // Pagination
  paginaActual = 1;
  itemsPerPage = 50;
  totalPaginas = 1;
  totalResultados = 0;
  opcionesElementosPorPagina = [25, 50, 100, 200];
  
  // Messages
  successMessage = '';
  errorMessage = '';
  
  // Dropdown estado
  openDropdownEnvioId: number | null = null;
  
  // Vista: 'grid' = tarjetas, 'table' = tabla
  viewMode: 'grid' | 'table' = 'grid';
  
  // Selección múltiple y acciones masivas
  selectedIds = new Set<number>();
  bulkActionInProgress = false;
  
  // Form
  envioForm: FormGroup;
  ESTADOS_LABELS = ESTADOS_LABELS;
  CATEGORIAS_LABELS = CATEGORIAS_LABELS;
  EstadosEnvio = EstadosEnvio;
  CategoriasProducto = CategoriasProducto;

  constructor(
    private apiService: ApiService,
    public authService: AuthService,
    private fb: FormBuilder,
    private route: ActivatedRoute
  ) {
    this.envioForm = this.fb.group({
      hawb: ['', [Validators.required]],
      comprador: ['', [Validators.required]],
      estado: [EstadosEnvio.PENDIENTE, [Validators.required]],
      observaciones: [''],
      productos: this.fb.array([])
    });
  }

  ngOnInit(): void {
    // Leer query params para prefiltrar
    this.route.queryParamMap.subscribe((params) => {
      const estado = params.get('estado');
      const comprador = params.get('comprador');
      if (estado) this.selectedEstado = estado;
      if (comprador) this.selectedComprador = comprador;
      this.loadEnvios();
      this.loadCompradores();
    });
    
    // Agregar listener global para cerrar dropdowns al hacer click fuera
    document.addEventListener('click', this.handleGlobalClick.bind(this));
  }

  ngOnDestroy(): void {
    // Remover listener global
    document.removeEventListener('click', this.handleGlobalClick.bind(this));
  }

  handleGlobalClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    
    // Cerrar dropdown de estado si el click es afuera
    if (this.openDropdownEnvioId !== null) {
      const dropdown = target.closest('.dropdown-estado');
      if (!dropdown) {
        this.openDropdownEnvioId = null;
      }
    }
  }

  toggleViewMode(): void {
    this.viewMode = this.viewMode === 'grid' ? 'table' : 'grid';
  }

  get productos(): FormArray {
    return this.envioForm.get('productos') as FormArray;
  }

  loadEnvios(): void {
    this.loading = true;
    
    // Si es comprador, solo cargar sus envíos
    if (this.authService.isComprador()) {
      this.apiService.getMisEnvios().subscribe({
        next: (envios) => {
          // getMisEnvios() ahora siempre devuelve un array
          this.envios = envios;
          this.applyFilters();
          this.loading = false;
        },
        error: (error) => {
          console.error('Error cargando envíos:', error);
          this.errorMessage = 'Error al cargar los envíos';
          this.loading = false;
        }
      });
    } else {
      // Admin, Gerente, Digitador pueden ver todos
      this.apiService.getEnvios().subscribe({
        next: (envios) => {
          // getEnvios() ahora siempre devuelve un array
          this.envios = envios;
          this.applyFilters();
          this.loading = false;
        },
        error: (error) => {
          console.error('Error cargando envíos:', error);
          this.errorMessage = 'Error al cargar los envíos';
          this.loading = false;
        }
      });
    }
  }

  loadCompradores(): void {
    this.apiService.getCompradores().subscribe({
      next: (response) => {
        // El backend puede devolver un array o un objeto con 'results'
        this.compradores = Array.isArray(response) ? response : (response as any).results || [];
      },
      error: (error) => {
        console.error('Error cargando compradores:', error);
      }
    });
  }

  loadProductosExistentes(): void {
    this.apiService.getProductos().subscribe({
      next: (response) => {
        this.productosExistentes = Array.isArray(response) ? response : (response as any).results || [];
      },
      error: (error) => {
        console.error('Error cargando productos:', error);
      }
    });
  }

  /**
   * Normaliza valores decimales: convierte coma a punto
   * Acepta tanto coma como punto como separador decimal
   */
  private normalizarDecimal(valor: any): string {
    if (valor === null || valor === undefined) {
      return '0';
    }
    if (typeof valor === 'number') {
      return valor.toString();
    }
    // Convertir a string y normalizar
    let valorStr = String(valor).trim();
    // Si tiene coma y punto, asumir formato europeo (1.234,56 -> 1234.56)
    if (valorStr.includes('.') && valorStr.includes(',')) {
      // Eliminar puntos (separadores de miles) y convertir coma a punto
      valorStr = valorStr.replace(/\./g, '').replace(',', '.');
    }
    // Si solo tiene coma, convertir a punto
    else if (valorStr.includes(',')) {
      valorStr = valorStr.replace(',', '.');
    }
    return valorStr;
  }

  /**
   * Redondea un número a un número específico de decimales
   * Usa un método más preciso para evitar problemas de precisión de punto flotante
   * @param valor El valor a redondear
   * @param decimales Número de decimales (por defecto 2)
   * @returns Número redondeado con exactamente el número de decimales especificado
   */
  private redondearDecimal(valor: number, decimales: number = 2): number {
    if (valor === null || valor === undefined || isNaN(valor)) {
      return 0;
    }
    // Usar Math.round con factor para evitar problemas de precisión de punto flotante
    const factor = Math.pow(10, decimales);
    // Redondear y dividir, luego usar toFixed y parseFloat para asegurar exactamente 2 decimales
    const redondeado = Math.round((valor + Number.EPSILON) * factor) / factor;
    // Convertir a string con exactamente el número de decimales y luego a número
    // Esto asegura que cuando se serialice a JSON tenga exactamente 2 decimales
    return parseFloat(redondeado.toFixed(decimales));
  }

  calcularCostoServicio(): void {
    const productosData = this.productos.value.map((p: any) => {
      const pesoRaw = parseFloat(this.normalizarDecimal(p.peso)) || 0;
      const valorRaw = parseFloat(this.normalizarDecimal(p.valor)) || 0;
      return {
        descripcion: p.descripcion,
        categoria: p.categoria,
        peso: this.redondearDecimal(pesoRaw, 2),
        cantidad: parseInt(p.cantidad) || 1,
        valor: this.redondearDecimal(valorRaw, 2)
      };
    });

    // Filtrar productos válidos
    const productosValidos = productosData.filter((p: any) => 
      p.categoria && p.peso > 0 && p.cantidad > 0
    );

    if (productosValidos.length === 0) {
      this.costoServicioCalculado = 0;
      this.detallesCostos = [];
      return;
    }

    this.calculandoCosto = true;
    this.apiService.calcularCostoEnvio(productosValidos).subscribe({
      next: (response) => {
        this.costoServicioCalculado = response.costo_total || 0;
        this.detallesCostos = response.detalles || [];
        this.calculandoCosto = false;
      },
      error: (error) => {
        console.error('Error calculando costo:', error);
        this.costoServicioCalculado = 0;
        this.detallesCostos = [];
        this.calculandoCosto = false;
      }
    });
  }

  applyFilters(): void {
    // Asegurarse de que envios sea un array
    if (!Array.isArray(this.envios)) {
      this.envios = [];
    }
    let filtered = [...this.envios];

    // Search filter
    if (this.searchTerm) {
      const search = this.searchTerm.toLowerCase();
      filtered = filtered.filter(envio =>
        envio.hawb.toLowerCase().includes(search) ||
        envio.comprador_info?.nombre.toLowerCase().includes(search) ||
        envio.comprador_info?.cedula.toLowerCase().includes(search)
      );
    }

    // Estado filter
    if (this.selectedEstado) {
      filtered = filtered.filter(envio => envio.estado === this.selectedEstado);
    }

    // Comprador filter
    if (this.selectedComprador) {
      filtered = filtered.filter(envio => envio.comprador === parseInt(this.selectedComprador));
    }

    this.filteredEnvios = filtered;
    this.calculatePagination();
  }

  calculatePagination(): void {
    this.totalResultados = this.filteredEnvios.length;
    this.totalPaginas = Math.ceil(this.filteredEnvios.length / this.itemsPerPage);
    if (this.totalPaginas === 0) {
      this.totalPaginas = 1;
      this.paginaActual = 1;
    }
    // Asegurar que la página actual no exceda el total
    if (this.paginaActual > this.totalPaginas) {
      this.paginaActual = this.totalPaginas;
    }
  }

  onSearchChange(): void {
    this.paginaActual = 1;
    this.applyFilters();
  }

  onEstadoFilterChange(): void {
    this.paginaActual = 1;
    this.applyFilters();
  }

  onCompradorFilterChange(): void {
    this.paginaActual = 1;
    this.applyFilters();
  }

  cambiarElementosPorPagina(cantidad: number): void {
    this.itemsPerPage = cantidad;
    this.paginaActual = 1;
    this.calculatePagination();
  }

  obtenerRangoPaginas(): number[] {
    const rango = 2; // Páginas a mostrar antes y después de la actual
    const inicio = Math.max(1, this.paginaActual - rango);
    const fin = Math.min(this.totalPaginas, this.paginaActual + rango);
    
    const paginas: number[] = [];
    for (let i = inicio; i <= fin; i++) {
      paginas.push(i);
    }
    return paginas;
  }

  paginaAnterior(): void {
    if (this.paginaActual > 1) {
      this.paginaActual--;
      this.scrollAlInicio();
    }
  }

  paginaSiguiente(): void {
    if (this.paginaActual < this.totalPaginas) {
      this.paginaActual++;
      this.scrollAlInicio();
    }
  }

  irAPagina(pagina: number): void {
    if (pagina >= 1 && pagina <= this.totalPaginas) {
      this.paginaActual = pagina;
      this.scrollAlInicio();
    }
  }

  private scrollAlInicio(): void {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  openCreateModal(): void {
    this.editingEnvio = null;
    this.envioForm.reset({
      estado: EstadosEnvio.PENDIENTE,
      hawb: '' // Inicializar vacío, se generará después
    });
    this.productos.clear();
    this.costoServicioCalculado = 0;
    this.detallesCostos = [];
    this.errorMessage = '';
    this.addProducto(); // Agregar un producto por defecto
    this.loadProductosExistentes();
    this.showModal = true;
    
    // Generar HAWB después de abrir el modal
    this.generateNextHAWB();
  }

  generateNextHAWB(): void {
    // Obtener todos los HAWBs existentes
    this.apiService.getEnvios().subscribe({
      next: (envios) => {
        // getEnvios() ahora siempre devuelve un array
        const hawbNumbers: number[] = [];
        
        // Extraer números de HAWBs existentes
        envios.forEach((envio: Envio) => {
          const match = envio.hawb.match(/(\d+)$/);
          if (match) {
            hawbNumbers.push(parseInt(match[1], 10));
          }
        });
        
        // Generar el siguiente HAWB
        let nextNumber = 1;
        if (hawbNumbers.length > 0) {
          const maxNumber = Math.max(...hawbNumbers);
          nextNumber = maxNumber + 1;
        }
        
        // Formatear HAWB (ej: HAW000001, HAW000002, etc.)
        const nextHAWB = `HAW${String(nextNumber).padStart(6, '0')}`;
        
        // Establecer el HAWB en el formulario
        this.envioForm.patchValue({
          hawb: nextHAWB
        });
      },
      error: (error) => {
        console.error('Error generando HAWB:', error);
        // En caso de error, usar un HAWB por defecto basado en timestamp
        const timestamp = Date.now();
        const defaultHAWB = `HAW${String(timestamp % 1000000).padStart(6, '0')}`;
        this.envioForm.patchValue({
          hawb: defaultHAWB
        });
      }
    });
  }

  editEnvio(envio: Envio): void {
    this.editingEnvio = envio;
    this.envioForm.patchValue({
      hawb: envio.hawb,
      comprador: envio.comprador,
      estado: envio.estado,
      observaciones: envio.observaciones || ''
    });
    
    // Cargar productos
    this.productos.clear();
    this.costoServicioCalculado = envio.costo_servicio || 0;
    this.detallesCostos = [];
    
    if (envio.productos && envio.productos.length > 0) {
      envio.productos.forEach(producto => {
        const productoGroup = this.fb.group({
          descripcion: [producto.descripcion, Validators.required],
          peso: [producto.peso, [Validators.required, Validators.min(0.01)]],
          cantidad: [producto.cantidad, [Validators.required, Validators.min(1)]],
          valor: [producto.valor, [Validators.required, Validators.min(0)]],
          categoria: [producto.categoria, Validators.required],
          productoExistenteId: ['']
        });
        
        // Suscribirse a cambios para recalcular costo
        productoGroup.valueChanges.subscribe(() => {
          this.calcularCostoServicio();
        });
        
        this.productos.push(productoGroup);
      });
    }
    
    this.loadProductosExistentes();
    this.calcularCostoServicio();
    this.showModal = true;
  }

  viewEnvio(envio: Envio): void {
    // Cargar detalles completos del envío
    this.apiService.getEnvio(envio.id!).subscribe({
      next: (envioDetalle) => {
        this.selectedEnvio = envioDetalle;
        this.showDetailModal = true;
      },
      error: (error) => {
        console.error('Error cargando detalle del envío:', error);
        this.errorMessage = 'Error al cargar el detalle del envío';
      }
    });
  }

  deleteEnvio(envio: Envio): void {
    if (confirm(`¿Estás seguro de que quieres eliminar el envío "${envio.hawb}"?`)) {
      this.apiService.deleteEnvio(envio.id!).subscribe({
        next: () => {
          this.successMessage = 'Envío eliminado exitosamente';
          this.loadEnvios();
          setTimeout(() => this.successMessage = '', 3000);
        },
        error: (error) => {
          console.error('Error eliminando envío:', error);
          this.errorMessage = 'Error al eliminar el envío';
          setTimeout(() => this.errorMessage = '', 3000);
        }
      });
    }
  }

  toggleDropdownEstado(envioId: number, event?: Event): void {
    if (event) {
      event.stopPropagation();
    }
    this.openDropdownEnvioId = this.openDropdownEnvioId === envioId ? null : envioId;
  }

  isDropdownOpen(envioId: number): boolean {
    return this.openDropdownEnvioId === envioId;
  }

  cambiarEstado(envio: Envio, nuevoEstado: string): void {
    this.apiService.cambiarEstadoEnvio(envio.id!, nuevoEstado).subscribe({
      next: () => {
        this.successMessage = 'Estado actualizado exitosamente';
        this.openDropdownEnvioId = null; // Cerrar dropdown
        this.loadEnvios();
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error) => {
        console.error('Error cambiando estado:', error);
        console.error('Error completo:', JSON.stringify(error, null, 2));
        
        // Mostrar mensaje de error más descriptivo
        let errorMsg = 'Error al cambiar el estado';
        if (error.error) {
          if (typeof error.error === 'string') {
            errorMsg = error.error;
          } else if (error.error.error) {
            errorMsg = error.error.error;
          } else if (error.error.estado) {
            errorMsg = Array.isArray(error.error.estado) 
              ? error.error.estado.join(', ') 
              : error.error.estado;
          } else if (error.error.detalle) {
            errorMsg = error.error.detalle;
          }
        }
        
        this.errorMessage = errorMsg;
        this.openDropdownEnvioId = null; // Cerrar dropdown
        setTimeout(() => this.errorMessage = '', 5000);
      }
    });
  }

  addProducto(): void {
    const productoGroup = this.fb.group({
      descripcion: ['', Validators.required],
      peso: [0, [Validators.required, Validators.min(0.01)]],
      cantidad: [1, [Validators.required, Validators.min(1)]],
      valor: [0, [Validators.required, Validators.min(0)]],
      categoria: ['', Validators.required],
      productoExistenteId: ['']
    });
    
    // Suscribirse a cambios para recalcular costo
    productoGroup.valueChanges.subscribe(() => {
      this.calcularCostoServicio();
    });
    
    this.productos.push(productoGroup);
  }

  onProductoExistenteSelected(index: number, productoId: string): void {
    if (!productoId) return;
    
    const productoSeleccionado = this.productosExistentes.find(p => p.id?.toString() === productoId);
    if (productoSeleccionado) {
      const productoGroup = this.productos.at(index) as FormGroup;
      productoGroup.patchValue({
        descripcion: productoSeleccionado.descripcion,
        peso: productoSeleccionado.peso,
        cantidad: 1,
        valor: productoSeleccionado.valor,
        categoria: productoSeleccionado.categoria
      });
      this.calcularCostoServicio();
    }
  }

  removeProducto(index: number): void {
    if (this.productos.length > 1) {
      this.productos.removeAt(index);
      this.calcularCostoServicio();
    }
  }

  closeModal(): void {
    this.showModal = false;
    this.editingEnvio = null;
    this.envioForm.reset();
    this.productos.clear();
    this.errorMessage = '';
  }

  closeDetailModal(): void {
    this.showDetailModal = false;
    this.selectedEnvio = null;
  }

  // Cerrar dropdown cuando se hace click fuera
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.dropdown-estado')) {
      this.openDropdownEnvioId = null;
    }
  }

  onSubmit(): void {
    if (this.envioForm.valid) {
      // Validar que el HAWB no esté vacío
      const hawb = this.envioForm.value.hawb?.trim();
      if (!hawb) {
        this.errorMessage = 'El HAWB es requerido. Por favor, espere a que se genere automáticamente.';
        this.submitting = false;
        setTimeout(() => this.errorMessage = '', 5000);
        return;
      }

      // Validar que haya al menos un producto válido
      const productosValidos = this.envioForm.value.productos
        .map((p: any) => {
          const pesoRaw = parseFloat(this.normalizarDecimal(p.peso)) || 0;
          const valorRaw = parseFloat(this.normalizarDecimal(p.valor)) || 0;
          return {
            descripcion: p.descripcion?.trim(),
            categoria: p.categoria,
            peso: this.redondearDecimal(pesoRaw, 2),
            cantidad: parseInt(p.cantidad) || 1,
            valor: this.redondearDecimal(valorRaw, 2)
          };
        })
        .filter((p: any) => p.descripcion && p.categoria && p.peso > 0 && p.cantidad > 0);

      if (productosValidos.length === 0) {
        this.errorMessage = 'Debe agregar al menos un producto válido al envío.';
        this.submitting = false;
        setTimeout(() => this.errorMessage = '', 5000);
        return;
      }

      // Asegurar que comprador sea un número
      const compradorId = typeof this.envioForm.value.comprador === 'string' 
        ? parseInt(this.envioForm.value.comprador, 10) 
        : this.envioForm.value.comprador;

      if (!compradorId || isNaN(compradorId)) {
        this.errorMessage = 'Debe seleccionar un comprador válido.';
        this.submitting = false;
        setTimeout(() => this.errorMessage = '', 5000);
        return;
      }

      this.submitting = true;
      
      const formData: EnvioCreate = {
        hawb: hawb,
        comprador: compradorId,
        estado: this.envioForm.value.estado || EstadosEnvio.PENDIENTE,
        observaciones: (this.envioForm.value.observaciones || '').trim(),
        productos: productosValidos
      };

      if (this.editingEnvio) {
        // Update existing envio
        this.apiService.updateEnvio(this.editingEnvio.id!, formData).subscribe({
          next: () => {
            this.successMessage = 'Envío actualizado exitosamente';
            this.closeModal();
            this.loadEnvios();
            this.submitting = false;
            setTimeout(() => this.successMessage = '', 3000);
          },
          error: (error) => {
            console.error('Error actualizando envío:', error);
            this.errorMessage = 'Error al actualizar el envío';
            this.submitting = false;
            setTimeout(() => this.errorMessage = '', 3000);
          }
        });
      } else {
        // Create new envio
        this.apiService.createEnvio(formData).subscribe({
          next: () => {
            this.successMessage = 'Envío creado exitosamente';
            this.closeModal();
            this.loadEnvios();
            this.submitting = false;
            setTimeout(() => this.successMessage = '', 3000);
          },
          error: (error) => {
            console.error('Error creando envío:', error);
            console.error('Error completo:', JSON.stringify(error, null, 2));
            
            // Mostrar mensaje de error más descriptivo
            let errorMsg = 'Error al crear el envío';
            if (error.error) {
              // Si hay detalles del serializer
              if (error.error.detalles) {
                const detalles = error.error.detalles;
                const errores = Object.keys(detalles).map(key => {
                  const valor = detalles[key];
                  return `${key}: ${Array.isArray(valor) ? valor.join(', ') : valor}`;
                });
                if (errores.length > 0) {
                  errorMsg = errores.join('; ');
                }
              } else if (typeof error.error === 'string') {
                errorMsg = error.error;
              } else if (error.error.detail) {
                errorMsg = error.error.detail;
              } else if (error.error.detalle) {
                errorMsg = error.error.detalle;
              } else if (error.error.non_field_errors) {
                errorMsg = Array.isArray(error.error.non_field_errors) 
                  ? error.error.non_field_errors.join(', ') 
                  : error.error.non_field_errors;
              } else if (error.error.hawb) {
                errorMsg = `HAWB: ${Array.isArray(error.error.hawb) ? error.error.hawb.join(', ') : error.error.hawb}`;
              } else if (error.error.comprador) {
                errorMsg = `Comprador: ${Array.isArray(error.error.comprador) ? error.error.comprador.join(', ') : error.error.comprador}`;
              } else if (error.error.productos) {
                errorMsg = `Productos: ${Array.isArray(error.error.productos) ? error.error.productos.join(', ') : error.error.productos}`;
              } else {
                // Mostrar todos los errores de validación
                const errores = Object.keys(error.error).map(key => {
                  const valor = error.error[key];
                  return `${key}: ${Array.isArray(valor) ? valor.join(', ') : valor}`;
                });
                if (errores.length > 0) {
                  errorMsg = errores.join('; ');
                }
              }
            }
            
            this.errorMessage = errorMsg;
            this.submitting = false;
            setTimeout(() => this.errorMessage = '', 8000);
          }
        });
      }
    } else {
      this.markFormGroupTouched();
    }
  }

  private markFormGroupTouched(): void {
    Object.keys(this.envioForm.controls).forEach(key => {
      const control = this.envioForm.get(key);
      control?.markAsTouched();
    });
    
    // Marcar también los productos
    this.productos.controls.forEach(producto => {
      Object.keys((producto as FormGroup).controls).forEach(key => {
        producto.get(key)?.markAsTouched();
      });
    });
  }

  // Helper methods
  getEstadoLabel(estado: string): string {
    return ESTADOS_LABELS[estado as keyof typeof ESTADOS_LABELS] || estado;
  }

  getEstadoClass(estado: string): string {
    switch (estado) {
      case EstadosEnvio.ENTREGADO:
        return 'badge-success';
      case EstadosEnvio.EN_TRANSITO:
        return 'badge-warning';
      case EstadosEnvio.PENDIENTE:
        return 'badge-info';
      case EstadosEnvio.CANCELADO:
        return 'badge-danger';
      default:
        return '';
    }
  }

  getCategoriaLabel(categoria: string): string {
    return CATEGORIAS_LABELS[categoria as keyof typeof CATEGORIAS_LABELS] || categoria;
  }

  getCategoriaIcon(categoria: string): string {
    const iconos: { [key: string]: string } = {
      'electronica': 'fa-laptop',
      'ropa': 'fa-tshirt',
      'hogar': 'fa-home',
      'deportes': 'fa-futbol',
      'otros': 'fa-box'
    };
    return iconos[categoria] || 'fa-box';
  }

  canEditEnvio(envio: Envio): boolean {
    return this.authService.canManageEnvios();
  }

  canDeleteEnvio(envio: Envio): boolean {
    return this.authService.isAdmin() || this.authService.isGerente();
  }

  canChangeEstado(envio: Envio): boolean {
    return this.authService.canManageEnvios();
  }

  get paginatedEnvios(): Envio[] {
    const startIndex = (this.paginaActual - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    return this.filteredEnvios.slice(startIndex, endIndex);
  }

  get inicioRango(): number {
    if (this.totalResultados === 0) return 0;
    return (this.paginaActual - 1) * this.itemsPerPage + 1;
  }

  get finRango(): number {
    return Math.min(this.paginaActual * this.itemsPerPage, this.totalResultados);
  }

  // Calcular totales del formulario
  get totalPeso(): number {
    return this.productos.controls.reduce((sum, control) => {
      return sum + (control.get('peso')?.value || 0) * (control.get('cantidad')?.value || 0);
    }, 0);
  }

  get totalValor(): number {
    return this.productos.controls.reduce((sum, control) => {
      return sum + (control.get('valor')?.value || 0) * (control.get('cantidad')?.value || 0);
    }, 0);
  }

  get totalCantidad(): number {
    return this.productos.controls.reduce((sum, control) => {
      return sum + (control.get('cantidad')?.value || 0);
    }, 0);
  }

  getCostoProducto(index: number): number {
    if (this.detallesCostos && this.detallesCostos[index]) {
      return this.detallesCostos[index].costo_total || 0;
    }
    return 0;
  }

  getTotalCostoServicio(): number {
    return this.costoServicioCalculado;
  }

  // --- Selección múltiple y acciones masivas ---
  toggleSelection(envio: Envio): void {
    if (!envio.id) return;
    if (this.selectedIds.has(envio.id)) {
      this.selectedIds.delete(envio.id);
    } else {
      this.selectedIds.add(envio.id);
    }
    this.selectedIds = new Set(this.selectedIds);
  }

  isSelected(envio: Envio): boolean {
    return envio.id != null && this.selectedIds.has(envio.id);
  }

  selectAllOnPage(): void {
    const ids = this.paginatedEnvios.map(e => e.id).filter((id): id is number => id != null);
    const allSelected = ids.length > 0 && ids.every(id => this.selectedIds.has(id));
    if (allSelected) {
      ids.forEach(id => this.selectedIds.delete(id));
    } else {
      ids.forEach(id => this.selectedIds.add(id));
    }
    this.selectedIds = new Set(this.selectedIds);
  }

  clearSelection(): void {
    this.selectedIds.clear();
    this.selectedIds = new Set(this.selectedIds);
  }

  get selectedCount(): number {
    return this.selectedIds.size;
  }

  bulkDelete(): void {
    const ids = Array.from(this.selectedIds);
    if (ids.length === 0) return;
    if (!confirm(`¿Eliminar ${ids.length} envío(s) seleccionado(s)? Esta acción no se puede deshacer.`)) return;
    this.bulkActionInProgress = true;
    this.errorMessage = '';
    const calls = ids.map(id => this.apiService.deleteEnvio(id).pipe(
      map(() => ({ id, ok: true })),
      catchError(() => of({ id, ok: false }))
    ));
    forkJoin(calls).subscribe({
      next: (results) => {
        const ok = results.filter(r => r.ok).length;
        const fail = results.filter(r => !r.ok).length;
        this.successMessage = fail === 0
          ? `${ok} envío(s) eliminado(s) correctamente.`
          : `${ok} eliminado(s). ${fail} fallaron.`;
        this.clearSelection();
        this.loadEnvios();
        this.bulkActionInProgress = false;
        setTimeout(() => this.successMessage = '', 4000);
      },
      error: () => {
        this.errorMessage = 'Error al eliminar envíos.';
        this.bulkActionInProgress = false;
        setTimeout(() => this.errorMessage = '', 3000);
      }
    });
  }

  bulkChangeEstado(estado: string): void {
    const ids = Array.from(this.selectedIds);
    if (ids.length === 0) return;
    const label = this.getEstadoLabel(estado);
    if (!confirm(`¿Cambiar el estado a "${label}" en ${ids.length} envío(s) seleccionado(s)?`)) return;
    this.bulkActionInProgress = true;
    this.errorMessage = '';
    const calls = ids.map(id => this.apiService.cambiarEstadoEnvio(id, estado).pipe(
      map(() => ({ id, ok: true })),
      catchError(() => of({ id, ok: false }))
    ));
    forkJoin(calls).subscribe({
      next: (results) => {
        const ok = results.filter(r => r.ok).length;
        const fail = results.filter(r => !r.ok).length;
        this.successMessage = fail === 0
          ? `${ok} envío(s) actualizado(s) a "${label}".`
          : `${ok} actualizado(s). ${fail} fallaron.`;
        this.clearSelection();
        this.loadEnvios();
        this.bulkActionInProgress = false;
        setTimeout(() => this.successMessage = '', 4000);
      },
      error: () => {
        this.errorMessage = 'Error al cambiar estado de envíos.';
        this.bulkActionInProgress = false;
        setTimeout(() => this.errorMessage = '', 3000);
      }
    });
  }
}
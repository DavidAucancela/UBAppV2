# 🚀 PLANTILLA PARA COMPONENTES FALTANTES

Guía para implementar EnviosListComponent y ProductosListComponent basándose en el patrón exitoso de UsuariosListComponent.

---

## 1. ENVIOS LIST COMPONENT

### Archivo: `src/app/components/envios/envios-list/envios-list.component.ts`

```typescript
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormArray } from '@angular/forms';
import { ApiService } from '../../../services/api.service';
import { AuthService } from '../../../services/auth.service';
import { Envio, EnvioCreate, EstadosEnvio, ESTADOS_LABELS } from '../../../models/envio';
import { ProductoCreate, CategoriasProducto, CATEGORIAS_LABELS } from '../../../models/producto';
import { Usuario } from '../../../models/usuario';

@Component({
  selector: 'app-envios-list',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './envios-list.component.html',
  styleUrl: './envios-list.component.css'
})
export class EnviosListComponent implements OnInit {
  envios: Envio[] = [];
  filteredEnvios: Envio[] = [];
  compradores: Usuario[] = [];
  loading = false;
  submitting = false;
  showModal = false;
  showDetailModal = false;
  editingEnvio: Envio | null = null;
  selectedEnvio: Envio | null = null;
  
  // Filters
  searchTerm = '';
  selectedEstado = '';
  selectedComprador = '';
  
  // Pagination
  currentPage = 1;
  itemsPerPage = 10;
  totalPages = 1;
  
  // Messages
  successMessage = '';
  errorMessage = '';
  
  // Form
  envioForm: FormGroup;
  ESTADOS_LABELS = ESTADOS_LABELS;
  CATEGORIAS_LABELS = CATEGORIAS_LABELS;
  EstadosEnvio = EstadosEnvio;
  CategoriasProducto = CategoriasProducto;

  constructor(
    private apiService: ApiService,
    public authService: AuthService,
    private fb: FormBuilder
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
    this.loadEnvios();
    this.loadCompradores();
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
      next: (compradores) => {
        this.compradores = compradores;
      },
      error: (error) => {
        console.error('Error cargando compradores:', error);
      }
    });
  }

  applyFilters(): void {
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
    this.totalPages = Math.ceil(this.filteredEnvios.length / this.itemsPerPage);
    this.currentPage = Math.min(this.currentPage, this.totalPages);
    if (this.totalPages === 0) this.currentPage = 1;
  }

  onSearchChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  onEstadoFilterChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  onCompradorFilterChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
    }
  }

  openCreateModal(): void {
    this.editingEnvio = null;
    this.envioForm.reset({
      estado: EstadosEnvio.PENDIENTE
    });
    this.productos.clear();
    this.addProducto(); // Agregar un producto por defecto
    this.showModal = true;
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
    if (envio.productos && envio.productos.length > 0) {
      envio.productos.forEach(producto => {
        this.productos.push(this.fb.group({
          descripcion: [producto.descripcion, Validators.required],
          peso: [producto.peso, [Validators.required, Validators.min(0.01)]],
          cantidad: [producto.cantidad, [Validators.required, Validators.min(1)]],
          valor: [producto.valor, [Validators.required, Validators.min(0)]],
          categoria: [producto.categoria, Validators.required]
        }));
      });
    }
    
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

  cambiarEstado(envio: Envio, nuevoEstado: string): void {
    this.apiService.cambiarEstadoEnvio(envio.id!, nuevoEstado).subscribe({
      next: () => {
        this.successMessage = 'Estado actualizado exitosamente';
        this.loadEnvios();
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error) => {
        console.error('Error cambiando estado:', error);
        this.errorMessage = 'Error al cambiar el estado';
        setTimeout(() => this.errorMessage = '', 3000);
      }
    });
  }

  addProducto(): void {
    const productoGroup = this.fb.group({
      descripcion: ['', Validators.required],
      peso: [0, [Validators.required, Validators.min(0.01)]],
      cantidad: [1, [Validators.required, Validators.min(1)]],
      valor: [0, [Validators.required, Validators.min(0)]],
      categoria: ['', Validators.required]
    });
    this.productos.push(productoGroup);
  }

  removeProducto(index: number): void {
    if (this.productos.length > 1) {
      this.productos.removeAt(index);
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

  onSubmit(): void {
    if (this.envioForm.valid) {
      this.submitting = true;
      const formData: EnvioCreate = {
        hawb: this.envioForm.value.hawb,
        comprador: this.envioForm.value.comprador,
        estado: this.envioForm.value.estado,
        observaciones: this.envioForm.value.observaciones,
        productos: this.envioForm.value.productos
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
            this.errorMessage = 'Error al crear el envío';
            this.submitting = false;
            setTimeout(() => this.errorMessage = '', 3000);
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
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    return this.filteredEnvios.slice(startIndex, endIndex);
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
}
```

---

## 2. PRODUCTOS LIST COMPONENT

### Archivo: `src/app/components/productos/productos-list/productos-list.component.ts`

```typescript
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ApiService } from '../../../services/api.service';
import { AuthService } from '../../../services/auth.service';
import { Producto, ProductoCreate, CategoriasProducto, CATEGORIAS_LABELS } from '../../../models/producto';

@Component({
  selector: 'app-productos-list',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './productos-list.component.html',
  styleUrl: './productos-list.component.css'
})
export class ProductosListComponent implements OnInit {
  productos: Producto[] = [];
  filteredProductos: Producto[] = [];
  loading = false;
  submitting = false;
  showModal = false;
  editingProducto: Producto | null = null;
  
  // Filters
  searchTerm = '';
  selectedCategoria = '';
  
  // Pagination
  currentPage = 1;
  itemsPerPage = 10;
  totalPages = 1;
  
  // Messages
  successMessage = '';
  errorMessage = '';
  
  // Form
  productoForm: FormGroup;
  CATEGORIAS_LABELS = CATEGORIAS_LABELS;
  CategoriasProducto = CategoriasProducto;

  constructor(
    private apiService: ApiService,
    public authService: AuthService,
    private fb: FormBuilder
  ) {
    this.productoForm = this.fb.group({
      descripcion: ['', [Validators.required]],
      peso: [0, [Validators.required, Validators.min(0.01)]],
      cantidad: [1, [Validators.required, Validators.min(1)]],
      valor: [0, [Validators.required, Validators.min(0)]],
      categoria: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    this.loadProductos();
  }

  loadProductos(): void {
    this.loading = true;
    this.apiService.getProductos().subscribe({
      next: (productos) => {
        this.productos = productos;
        this.applyFilters();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando productos:', error);
        this.errorMessage = 'Error al cargar los productos';
        this.loading = false;
      }
    });
  }

  applyFilters(): void {
    let filtered = [...this.productos];

    // Search filter
    if (this.searchTerm) {
      const search = this.searchTerm.toLowerCase();
      filtered = filtered.filter(producto =>
        producto.descripcion.toLowerCase().includes(search)
      );
    }

    // Categoria filter
    if (this.selectedCategoria) {
      filtered = filtered.filter(producto => producto.categoria === this.selectedCategoria);
    }

    this.filteredProductos = filtered;
    this.calculatePagination();
  }

  calculatePagination(): void {
    this.totalPages = Math.ceil(this.filteredProductos.length / this.itemsPerPage);
    this.currentPage = Math.min(this.currentPage, this.totalPages);
    if (this.totalPages === 0) this.currentPage = 1;
  }

  onSearchChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  onCategoriaFilterChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
    }
  }

  openCreateModal(): void {
    this.editingProducto = null;
    this.productoForm.reset({
      peso: 0,
      cantidad: 1,
      valor: 0
    });
    this.showModal = true;
  }

  editProducto(producto: Producto): void {
    this.editingProducto = producto;
    this.productoForm.patchValue({
      descripcion: producto.descripcion,
      peso: producto.peso,
      cantidad: producto.cantidad,
      valor: producto.valor,
      categoria: producto.categoria
    });
    this.showModal = true;
  }

  deleteProducto(producto: Producto): void {
    if (confirm(`¿Estás seguro de que quieres eliminar el producto "${producto.descripcion}"?`)) {
      this.apiService.deleteProducto(producto.id!).subscribe({
        next: () => {
          this.successMessage = 'Producto eliminado exitosamente';
          this.loadProductos();
          setTimeout(() => this.successMessage = '', 3000);
        },
        error: (error) => {
          console.error('Error eliminando producto:', error);
          this.errorMessage = 'Error al eliminar el producto';
          setTimeout(() => this.errorMessage = '', 3000);
        }
      });
    }
  }

  closeModal(): void {
    this.showModal = false;
    this.editingProducto = null;
    this.productoForm.reset();
    this.errorMessage = '';
  }

  onSubmit(): void {
    if (this.productoForm.valid) {
      this.submitting = true;
      const formData: ProductoCreate = this.productoForm.value;

      if (this.editingProducto) {
        // Update
        this.apiService.updateProducto(this.editingProducto.id!, formData).subscribe({
          next: () => {
            this.successMessage = 'Producto actualizado exitosamente';
            this.closeModal();
            this.loadProductos();
            this.submitting = false;
            setTimeout(() => this.successMessage = '', 3000);
          },
          error: (error) => {
            console.error('Error actualizando producto:', error);
            this.errorMessage = 'Error al actualizar el producto';
            this.submitting = false;
            setTimeout(() => this.errorMessage = '', 3000);
          }
        });
      } else {
        // Create
        this.apiService.createProducto(formData).subscribe({
          next: () => {
            this.successMessage = 'Producto creado exitosamente';
            this.closeModal();
            this.loadProductos();
            this.submitting = false;
            setTimeout(() => this.successMessage = '', 3000);
          },
          error: (error) => {
            console.error('Error creando producto:', error);
            this.errorMessage = 'Error al crear el producto';
            this.submitting = false;
            setTimeout(() => this.errorMessage = '', 3000);
          }
        });
      }
    } else {
      this.markFormGroupTouched();
    }
  }

  private markFormGroupTouched(): void {
    Object.keys(this.productoForm.controls).forEach(key => {
      const control = this.productoForm.get(key);
      control?.markAsTouched();
    });
  }

  // Helper methods
  getCategoriaLabel(categoria: string): string {
    return CATEGORIAS_LABELS[categoria as keyof typeof CATEGORIAS_LABELS] || categoria;
  }

  get paginatedProductos(): Producto[] {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    return this.filteredProductos.slice(startIndex, endIndex);
  }

  // Calcular valor total por producto
  getValorTotal(producto: Producto): number {
    return producto.valor * producto.cantidad;
  }

  getPesoTotal(producto: Producto): number {
    return producto.peso * producto.cantidad;
  }
}
```

---

## 3. CHECKLIST DE IMPLEMENTACIÓN

### Para Envíos:
- [ ] Copiar código del componente
- [ ] Crear template HTML (ver UsuariosListComponent como referencia)
- [ ] Crear estilos CSS
- [ ] Implementar formulario de productos dinámicos
- [ ] Implementar modal de detalle
- [ ] Implementar cambio de estado
- [ ] Probar CRUD completo
- [ ] Probar filtros y búsqueda
- [ ] Probar paginación
- [ ] Probar permisos por rol

### Para Productos:
- [ ] Copiar código del componente
- [ ] Crear template HTML
- [ ] Crear estilos CSS
- [ ] Probar CRUD completo
- [ ] Probar filtros por categoría
- [ ] Probar búsqueda
- [ ] Probar paginación

---

## 4. NOTAS IMPORTANTES

1. **HTML Templates:** Usar el template de UsuariosListComponent como base
2. **Estilos:** Reutilizar los estilos existentes
3. **Formularios Dinámicos:** FormArray para productos dentro de envíos
4. **Validaciones:** Mantener coherencia con otros componentes
5. **Permisos:** Verificar roles antes de mostrar botones
6. **Notificaciones:** Usar NotificationService cuando esté implementado
7. **Confirmaciones:** Crear modal de confirmación en lugar de confirm()

---

**Tiempo estimado de implementación:**
- EnviosListComponent: 6-8 horas
- ProductosListComponent: 3-4 horas
- Templates HTML: 4-6 horas
- Testing: 2-3 horas
- **TOTAL: 15-21 horas (~2-3 días)**


import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ApiService } from '../../../services/api.service';
import { AuthService } from '../../../services/auth.service';
import { Producto, ProductoCreate, ProductoUpdate, CategoriasProducto, CATEGORIAS_LABELS } from '../../../models/producto';
import { Envio } from '../../../models/envio';

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
  envios: Envio[] = [];
  loading = false;
  submitting = false;
  loadingEnvios = false;
  showModal = false;
  editingProducto: Producto | null = null;
  
  // Filters
  searchTerm = '';
  selectedCategoria = '';
  sortBy: 'descripcion' | 'categoria' | 'peso' | 'cantidad' | 'valor' = 'descripcion';
  sortOrder: 'asc' | 'desc' = 'desc';
  viewMode: 'grid' | 'table' = 'grid';
  
  // Pagination
  currentPage = 1;
  itemsPerPage = 12;
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
      categoria: ['', [Validators.required]],
      envio: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    this.loadProductos();
  }

  loadProductos(): void {
    this.loading = true;
    this.errorMessage = '';
    this.apiService.getProductos().subscribe({
      next: (response) => {
        // El backend puede devolver un array o un objeto con 'results'
        const productosData = Array.isArray(response) ? response : (response as any).results || [];
        this.productos = productosData;
        console.log('Productos cargados:', this.productos.length);
        this.applyFilters();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando productos:', error);
        this.errorMessage = 'Error al cargar los productos: ' + (error.error?.error || error.message);
        this.loading = false;
        this.productos = [];
        this.filteredProductos = [];
      }
    });
  }

  applyFilters(): void {
    // Asegurarse de que productos sea un array
    if (!Array.isArray(this.productos)) {
      this.productos = [];
    }
    let filtered = [...this.productos];

    // Search filter
    if (this.searchTerm && this.searchTerm.trim()) {
      const search = this.searchTerm.toLowerCase().trim();
      filtered = filtered.filter(producto =>
        producto.descripcion && producto.descripcion.toLowerCase().includes(search)
      );
    }

    // Categoria filter
    if (this.selectedCategoria && this.selectedCategoria.trim()) {
      filtered = filtered.filter(producto => producto.categoria === this.selectedCategoria);
    }

    // Sort
    filtered = this.sortProductos(filtered);

    this.filteredProductos = filtered;
    console.log('Productos filtrados:', this.filteredProductos.length);
    this.calculatePagination();
  }

  sortProductos(productos: Producto[]): Producto[] {
    const sorted = [...productos];
    sorted.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (this.sortBy) {
        case 'descripcion':
          aValue = a.descripcion.toLowerCase();
          bValue = b.descripcion.toLowerCase();
          break;
        case 'categoria':
          aValue = a.categoria;
          bValue = b.categoria;
          break;
        case 'peso':
          aValue = a.peso;
          bValue = b.peso;
          break;
        case 'cantidad':
          aValue = a.cantidad;
          bValue = b.cantidad;
          break;
        case 'valor':
          aValue = a.valor;
          bValue = b.valor;
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return this.sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return this.sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return sorted;
  }

  onSortChange(field: 'descripcion' | 'categoria' | 'peso' | 'cantidad' | 'valor'): void {
    if (this.sortBy === field) {
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortBy = field;
      this.sortOrder = 'desc';
    }
    this.currentPage = 1;
    this.applyFilters();
  }

  toggleViewMode(): void {
    this.viewMode = this.viewMode === 'grid' ? 'table' : 'grid';
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
    this.errorMessage = '';
    this.productoForm.reset({
      descripcion: '',
      categoria: '',
      peso: 0,
      cantidad: 1,
      valor: 0,
      envio: ''
    });
    this.loadEnvios();
    this.showModal = true;
  }

  loadEnvios(): void {
    this.loadingEnvios = true;
    if (this.authService.isComprador()) {
      this.apiService.getMisEnvios().subscribe({
        next: (response) => {
          this.envios = Array.isArray(response) ? response : (response as any).results || [];
          this.loadingEnvios = false;
        },
        error: (error) => {
          console.error('Error cargando envíos:', error);
          this.loadingEnvios = false;
        }
      });
    } else {
      this.apiService.getEnvios().subscribe({
        next: (response) => {
          this.envios = Array.isArray(response) ? response : (response as any).results || [];
          this.loadingEnvios = false;
        },
        error: (error) => {
          console.error('Error cargando envíos:', error);
          this.loadingEnvios = false;
        }
      });
    }
  }

  editProducto(producto: Producto): void {
    this.editingProducto = producto;
    this.errorMessage = '';
    this.productoForm.patchValue({
      descripcion: producto.descripcion,
      peso: producto.peso,
      cantidad: producto.cantidad,
      valor: producto.valor,
      categoria: producto.categoria,
      envio: producto.envio
    });
    // No necesitamos cargar envíos al editar, solo usamos el existente
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
      this.errorMessage = '';
      
      const envioId = this.productoForm.get('envio')?.value;
      
      // Validaciones adicionales
      if (!this.productoForm.get('descripcion')?.value?.trim()) {
        this.errorMessage = 'La descripción es requerida';
        this.submitting = false;
        return;
      }

      if (!this.productoForm.get('categoria')?.value) {
        this.errorMessage = 'Debe seleccionar una categoría';
        this.submitting = false;
        return;
      }

      if (!envioId && !this.editingProducto) {
        this.errorMessage = 'Debe seleccionar un envío';
        this.submitting = false;
        return;
      }

      const peso = parseFloat(this.productoForm.get('peso')?.value) || 0;
      const cantidad = parseInt(this.productoForm.get('cantidad')?.value) || 1;
      const valor = parseFloat(this.productoForm.get('valor')?.value) || 0;

      if (peso <= 0) {
        this.errorMessage = 'El peso debe ser mayor a 0';
        this.submitting = false;
        return;
      }

      if (cantidad < 1) {
        this.errorMessage = 'La cantidad debe ser al menos 1';
        this.submitting = false;
        return;
      }

      if (valor < 0) {
        this.errorMessage = 'El valor no puede ser negativo';
        this.submitting = false;
        return;
      }

      // Para crear, envio es requerido
      const envioIdFinal = this.editingProducto ? this.editingProducto.envio : (envioId ? parseInt(envioId) : null);
      
      if (!envioIdFinal) {
        this.errorMessage = 'Debe seleccionar un envío';
        this.submitting = false;
        return;
      }

      const formData: ProductoCreate = {
        descripcion: this.productoForm.get('descripcion')?.value?.trim() || '',
        categoria: this.productoForm.get('categoria')?.value || '',
        peso: peso,
        cantidad: cantidad,
        valor: valor,
        envio: envioIdFinal
      };

      if (this.editingProducto) {
        // Update - incluir el envio del producto original (requerido por el backend)
        if (!this.editingProducto.envio) {
          this.errorMessage = 'Error: El producto no tiene un envío asociado';
          this.submitting = false;
          return;
        }

        const updateData: ProductoUpdate = {
          descripcion: formData.descripcion,
          categoria: formData.categoria,
          peso: formData.peso,
          cantidad: formData.cantidad,
          valor: formData.valor,
          envio: this.editingProducto.envio // Incluir el envio original
        };
        
        this.apiService.updateProducto(this.editingProducto.id!, updateData).subscribe({
          next: () => {
            this.successMessage = 'Producto actualizado exitosamente';
            this.closeModal();
            this.loadProductos();
            this.submitting = false;
            setTimeout(() => this.successMessage = '', 3000);
          },
          error: (error) => {
            console.error('Error actualizando producto:', error);
            this.errorMessage = 'Error al actualizar el producto: ' + (error.error?.error || error.error?.message || error.message || 'Error desconocido');
            this.submitting = false;
            setTimeout(() => this.errorMessage = '', 5000);
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
            this.errorMessage = 'Error al crear el producto: ' + (error.error?.error || error.error?.message || error.message || 'Error desconocido');
            this.submitting = false;
            setTimeout(() => this.errorMessage = '', 5000);
          }
        });
      }
    } else {
      this.markFormGroupTouched();
      this.errorMessage = 'Por favor complete todos los campos requeridos correctamente';
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

  // Estadísticas generales
  get totalProductos(): number {
    return this.filteredProductos.length;
  }

  get totalPeso(): number {
    return this.filteredProductos.reduce((sum, p) => sum + this.getPesoTotal(p), 0);
  }

  get totalValor(): number {
    return this.filteredProductos.reduce((sum, p) => sum + this.getValorTotal(p), 0);
  }

  get productosPorCategoria(): { [key: string]: number } {
    const counts: { [key: string]: number } = {};
    this.filteredProductos.forEach(p => {
      counts[p.categoria] = (counts[p.categoria] || 0) + 1;
    });
    return counts;
  }

  // TrackBy para mejorar el rendimiento de *ngFor
  trackByProductoId(index: number, producto: Producto): any {
    return producto.id || index;
  }
}
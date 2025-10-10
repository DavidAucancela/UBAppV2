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
      next: (response) => {
        // El backend puede devolver un array o un objeto con 'results'
        this.productos = Array.isArray(response) ? response : (response as any).results || [];
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
    // Asegurarse de que productos sea un array
    if (!Array.isArray(this.productos)) {
      this.productos = [];
    }
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
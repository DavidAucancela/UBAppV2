import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { CategoriasProducto, CATEGORIAS_LABELS } from '../../models/producto';

interface Tarifa {
  id?: number;
  categoria: string;
  categoria_nombre?: string;
  peso_minimo: number;
  peso_maximo: number;
  precio_por_kg: number;
  cargo_base: number;
  activa: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
}

@Component({
  selector: 'app-tarifas-list',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './tarifas-list.component.html',
  styleUrl: './tarifas-list.component.css'
})
export class TarifasListComponent implements OnInit {
  tarifas: Tarifa[] = [];
  filteredTarifas: Tarifa[] = [];
  loading = false;
  submitting = false;
  showModal = false;
  editingTarifa: Tarifa | null = null;
  
  // Filters
  selectedCategoria = '';
  showActivasOnly = true;
  
  // Messages
  successMessage = '';
  errorMessage = '';
  
  // Form
  tarifaForm: FormGroup;
  CATEGORIAS_LABELS = CATEGORIAS_LABELS;
  CategoriasProducto = CategoriasProducto;
  
  categoriasDisponibles = Object.entries(CATEGORIAS_LABELS).map(([valor, etiqueta]) => ({
    valor,
    etiqueta
  }));

  constructor(
    private apiService: ApiService,
    public authService: AuthService,
    private fb: FormBuilder
  ) {
    this.tarifaForm = this.fb.group({
      categoria: ['', [Validators.required]],
      peso_minimo: [0, [Validators.required, Validators.min(0.01)]],
      peso_maximo: [0, [Validators.required, Validators.min(0.01)]],
      precio_por_kg: [0, [Validators.required, Validators.min(0)]],
      cargo_base: [0, [Validators.required, Validators.min(0)]],
      activa: [true]
    });
  }

  ngOnInit(): void {
    this.loadTarifas();
  }

  loadTarifas(): void {
    this.loading = true;
    this.apiService.getTarifas().subscribe({
      next: (response) => {
        this.tarifas = Array.isArray(response) ? response : (response as any).results || [];
        this.applyFilters();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando tarifas:', error);
        this.errorMessage = 'Error al cargar las tarifas';
        this.loading = false;
      }
    });
  }

  applyFilters(): void {
    let filtered = [...this.tarifas];

    // Categoría filter
    if (this.selectedCategoria) {
      filtered = filtered.filter(tarifa => tarifa.categoria === this.selectedCategoria);
    }

    // Activas only filter
    if (this.showActivasOnly) {
      filtered = filtered.filter(tarifa => tarifa.activa);
    }

    // Ordenar por categoría y peso mínimo
    filtered.sort((a, b) => {
      if (a.categoria !== b.categoria) {
        return a.categoria.localeCompare(b.categoria);
      }
      return a.peso_minimo - b.peso_minimo;
    });

    this.filteredTarifas = filtered;
  }

  onCategoriaFilterChange(): void {
    this.applyFilters();
  }

  onActivasFilterChange(): void {
    this.applyFilters();
  }

  openCreateModal(): void {
    this.editingTarifa = null;
    this.tarifaForm.reset({
      categoria: '',
      peso_minimo: 0,
      peso_maximo: 0,
      precio_por_kg: 0,
      cargo_base: 0,
      activa: true
    });
    this.showModal = true;
  }

  editTarifa(tarifa: Tarifa): void {
    this.editingTarifa = tarifa;
    this.tarifaForm.patchValue({
      categoria: tarifa.categoria,
      peso_minimo: tarifa.peso_minimo,
      peso_maximo: tarifa.peso_maximo,
      precio_por_kg: tarifa.precio_por_kg,
      cargo_base: tarifa.cargo_base,
      activa: tarifa.activa
    });
    this.showModal = true;
  }

  deleteTarifa(tarifa: Tarifa): void {
    if (!tarifa.id) return;
    
    if (confirm(`¿Estás seguro de que quieres eliminar la tarifa de ${this.getCategoriaLabel(tarifa.categoria)} (${tarifa.peso_minimo}kg - ${tarifa.peso_maximo}kg)?`)) {
      this.apiService.deleteTarifa(tarifa.id).subscribe({
        next: () => {
          this.successMessage = 'Tarifa eliminada exitosamente';
          this.loadTarifas();
          setTimeout(() => this.successMessage = '', 3000);
        },
        error: (error) => {
          console.error('Error eliminando tarifa:', error);
          this.errorMessage = 'Error al eliminar la tarifa';
          setTimeout(() => this.errorMessage = '', 3000);
        }
      });
    }
  }

  closeModal(): void {
    this.showModal = false;
    this.editingTarifa = null;
    this.tarifaForm.reset();
    this.errorMessage = '';
  }

  onSubmit(): void {
    if (this.tarifaForm.valid) {
      // Validar que peso_maximo > peso_minimo
      const pesoMinimo = parseFloat(this.tarifaForm.value.peso_minimo);
      const pesoMaximo = parseFloat(this.tarifaForm.value.peso_maximo);
      
      if (pesoMaximo <= pesoMinimo) {
        this.errorMessage = 'El peso máximo debe ser mayor que el peso mínimo';
        setTimeout(() => this.errorMessage = '', 3000);
        return;
      }

      this.submitting = true;
      const formData = {
        categoria: this.tarifaForm.value.categoria,
        peso_minimo: pesoMinimo,
        peso_maximo: pesoMaximo,
        precio_por_kg: parseFloat(this.tarifaForm.value.precio_por_kg),
        cargo_base: parseFloat(this.tarifaForm.value.cargo_base),
        activa: this.tarifaForm.value.activa
      };

      if (this.editingTarifa && this.editingTarifa.id) {
        // Update existing tarifa
        this.apiService.updateTarifa(this.editingTarifa.id, formData).subscribe({
          next: () => {
            this.successMessage = 'Tarifa actualizada exitosamente';
            this.closeModal();
            this.loadTarifas();
            this.submitting = false;
            setTimeout(() => this.successMessage = '', 3000);
          },
          error: (error) => {
            console.error('Error actualizando tarifa:', error);
            this.errorMessage = error.error?.error || error.error?.detalle || 'Error al actualizar la tarifa';
            this.submitting = false;
            setTimeout(() => this.errorMessage = '', 5000);
          }
        });
      } else {
        // Create new tarifa
        this.apiService.createTarifa(formData).subscribe({
          next: () => {
            this.successMessage = 'Tarifa creada exitosamente';
            this.closeModal();
            this.loadTarifas();
            this.submitting = false;
            setTimeout(() => this.successMessage = '', 3000);
          },
          error: (error) => {
            console.error('Error creando tarifa:', error);
            this.errorMessage = error.error?.error || error.error?.detalle || 'Error al crear la tarifa';
            this.submitting = false;
            setTimeout(() => this.errorMessage = '', 5000);
          }
        });
      }
    } else {
      this.markFormGroupTouched();
    }
  }

  private markFormGroupTouched(): void {
    Object.keys(this.tarifaForm.controls).forEach(key => {
      const control = this.tarifaForm.get(key);
      control?.markAsTouched();
    });
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

  toggleActiva(tarifa: Tarifa): void {
    if (!tarifa.id) return;
    
    const updatedTarifa = { ...tarifa, activa: !tarifa.activa };
    this.apiService.updateTarifa(tarifa.id, updatedTarifa).subscribe({
      next: () => {
        this.successMessage = `Tarifa ${updatedTarifa.activa ? 'activada' : 'desactivada'} exitosamente`;
        this.loadTarifas();
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error) => {
        console.error('Error actualizando estado de tarifa:', error);
        this.errorMessage = 'Error al actualizar el estado de la tarifa';
        setTimeout(() => this.errorMessage = '', 3000);
      }
    });
  }

  calcularCostoEjemplo(tarifa: Tarifa, pesoEjemplo: number = 1): number {
    return parseFloat(tarifa.cargo_base.toString()) + (pesoEjemplo * parseFloat(tarifa.precio_por_kg.toString()));
  }
}


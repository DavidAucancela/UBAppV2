import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../../../services/api.service';
import { AuthService } from '../../../services/auth.service';
import { Usuario, Roles, ROLES_LABELS } from '../../../models/usuario';

@Component({
  selector: 'app-usuarios-list',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './usuarios-list.component.html',
  styleUrls: ['./usuarios-list.component.css']
})
export class UsuariosListComponent implements OnInit {
  usuarios: Usuario[] = [];
  filteredUsuarios: Usuario[] = [];
  loading = false;
  submitting = false;
  showModal = false;
  showViewModal = false;
  editingUsuario: Usuario | null = null;
  selectedUsuario: Usuario | null = null;
  hidePassword = true;
  
  // Filters
  searchTerm = '';
  selectedRole = '';
  selectedStatus = '';
  
  // Pagination
  currentPage = 1;
  itemsPerPage = 10;
  totalPages = 1;
  
  // Messages
  successMessage = '';
  errorMessage = '';
  
  // Form
  usuarioForm: FormGroup;
  ROLES_LABELS = ROLES_LABELS;

  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private fb: FormBuilder,
    private route: ActivatedRoute
  ) {
    this.usuarioForm = this.fb.group({
      username: ['', [Validators.required]],
      nombre: ['', [Validators.required]],
      correo: ['', [Validators.required, Validators.email]],
      cedula: ['', [Validators.required]],
      rol: ['', [Validators.required]],
      telefono: [''],
      password: ['', [Validators.required, Validators.minLength(6)]],
      es_activo: [true]
    });
  }

  ngOnInit(): void {
    // Leer query params para prefiltrar por rol/estado
    this.route.queryParamMap.subscribe((params) => {
      const rol = params.get('rol');
      const activo = params.get('activo');
      if (rol) this.selectedRole = String(rol);
      if (activo !== null) this.selectedStatus = String(activo);
      this.loadUsuarios();
    });
  }

  loadUsuarios(): void {
    this.loading = true;
    this.apiService.getUsuarios().subscribe({
      next: (response) => {
        // El backend puede devolver un array o un objeto con 'results'
        this.usuarios = Array.isArray(response) ? response : (response as any).results || [];
        this.applyFilters();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando usuarios:', error);
        this.errorMessage = 'Error al cargar los usuarios';
        this.loading = false;
      }
    });
  }

  applyFilters(): void {
    // Asegurarse de que usuarios sea un array
    if (!Array.isArray(this.usuarios)) {
      this.usuarios = [];
    }
    let filtered = [...this.usuarios];

    // Search filter
    if (this.searchTerm) {
      const search = this.searchTerm.toLowerCase();
      filtered = filtered.filter(usuario =>
        (usuario.username || '').toLowerCase().includes(search) ||
        (usuario.nombre || '').toLowerCase().includes(search) ||
        (usuario.correo || '').toLowerCase().includes(search) ||
        (usuario.cedula || '').toLowerCase().includes(search)
      );
    }

    // Role filter
    if (this.selectedRole) {
      filtered = filtered.filter(usuario => usuario.rol === parseInt(this.selectedRole));
    }

    // Status filter
    if (this.selectedStatus !== '') {
      const isActive = this.selectedStatus === 'true';
      filtered = filtered.filter(usuario => usuario.es_activo === isActive);
    }

    this.filteredUsuarios = filtered;
    this.calculatePagination();
  }

  calculatePagination(): void {
    this.totalPages = Math.ceil(this.filteredUsuarios.length / this.itemsPerPage);
    this.currentPage = Math.min(this.currentPage, this.totalPages);
    if (this.totalPages === 0) this.currentPage = 1;
  }

  onSearchChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  onRoleFilterChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  onStatusFilterChange(): void {
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
    this.editingUsuario = null;
    this.usuarioForm.reset({
      es_activo: true
    });
    this.showModal = true;
    this.hidePassword = true;
    // Asegurar validadores de contraseña para creación
    const passwordCtrl = this.usuarioForm.get('password');
    passwordCtrl?.setValidators([Validators.required, Validators.minLength(6)]);
    passwordCtrl?.updateValueAndValidity();
    this.submitting = false;
  }

  editUsuario(usuario: Usuario): void {
    this.editingUsuario = usuario;
    this.usuarioForm.patchValue({
      username: usuario.username,
      nombre: usuario.nombre,
      correo: usuario.correo,
      cedula: usuario.cedula,
      rol: usuario.rol,
      telefono: usuario.telefono || '',
      es_activo: usuario.es_activo,
      password: '' // No mostrar contraseña al editar
    });
    this.showModal = true;
    this.hidePassword = true;
    // Quitar validadores de contraseña en edición
    const passwordCtrl = this.usuarioForm.get('password');
    passwordCtrl?.clearValidators();
    passwordCtrl?.updateValueAndValidity();
    this.submitting = false;
  }

  viewUsuario(usuario: Usuario): void {
    this.selectedUsuario = { ...usuario };
    if (usuario.id) {
      this.apiService.getUsuario(usuario.id).subscribe({
        next: (detallado) => {
          this.selectedUsuario = detallado;
          this.showViewModal = true;
        },
        error: () => {
          // Si falla, mostramos al menos los datos existentes
          this.showViewModal = true;
        }
      });
    } else {
      this.showViewModal = true;
    }
  }

  closeViewModal(): void {
    this.showViewModal = false;
    this.selectedUsuario = null;
  }

  deleteUsuario(usuario: Usuario): void {
    if (confirm(`¿Estás seguro de que quieres eliminar al usuario "${usuario.nombre}"?`)) {
      this.apiService.deleteUsuario(usuario.id!).subscribe({
        next: () => {
          this.successMessage = 'Usuario eliminado exitosamente';
          this.loadUsuarios();
          setTimeout(() => this.successMessage = '', 3000);
        },
        error: (error) => {
          console.error('Error eliminando usuario:', error);
          this.errorMessage = 'Error al eliminar el usuario';
          setTimeout(() => this.errorMessage = '', 3000);
        }
      });
    }
  }

  closeModal(): void {
    this.showModal = false;
    this.editingUsuario = null;
    this.usuarioForm.reset();
    this.errorMessage = '';
    this.submitting = false;
  }

  onSubmit(): void {
    if (this.usuarioForm.valid) {
      this.submitting = true;
      const formData = this.usuarioForm.value;

      if (this.editingUsuario) {
        // Update existing user
        this.apiService.updateUsuario(this.editingUsuario.id!, formData).subscribe({
          next: () => {
            this.successMessage = 'Usuario actualizado exitosamente';
            this.closeModal();
            this.loadUsuarios();
            setTimeout(() => this.successMessage = '', 3000);
            this.submitting = false;
          },
          error: (error) => {
            console.error('Error actualizando usuario:', error);
            this.errorMessage = 'Error al actualizar el usuario';
            this.submitting = false;
            this.setBackendErrors(error?.error);
            setTimeout(() => this.errorMessage = '', 3000);
          }
        });
      } else {
        // Create new user
        this.apiService.createUsuario(formData).subscribe({
          next: () => {
            this.successMessage = 'Usuario creado exitosamente';
            this.closeModal();
            this.loadUsuarios();
            setTimeout(() => this.successMessage = '', 3000);
            this.submitting = false;
          },
          error: (error) => {
            console.error('Error creando usuario:', error);
            this.errorMessage = 'Error al crear el usuario';
            this.submitting = false;
            this.setBackendErrors(error?.error);
            setTimeout(() => this.errorMessage = '', 3000);
          }
        });
      }
    } else {
      this.markFormGroupTouched();
    }
  }

  private markFormGroupTouched(): void {
    Object.keys(this.usuarioForm.controls).forEach(key => {
      const control = this.usuarioForm.get(key);
      control?.markAsTouched();
    });
  }

  private setBackendErrors(apiErrors: any): void {
    if (!apiErrors || typeof apiErrors !== 'object') return;
    Object.keys(apiErrors).forEach((key) => {
      const control = this.usuarioForm.get(key);
      const messages = apiErrors[key];
      const message = Array.isArray(messages) ? messages[0] : String(messages);
      if (control) {
        control.setErrors({ ...(control.errors || {}), server: message });
        control.markAsTouched();
      } else {
        // Si no existe control, mostrar como error general
        this.errorMessage = message;
      }
    });
  }

  // Helper methods for template
  getRoleLabel(rol: number): string {
    return ROLES_LABELS[rol as keyof typeof ROLES_LABELS] || 'Desconocido';
  }

  getRoleClass(rol: number): string {
    switch (rol) {
      case Roles.ADMIN:
        return 'admin';
      case Roles.GERENTE:
        return 'gerente';
      case Roles.DIGITADOR:
        return 'digitador';
      case Roles.COMPRADOR:
        return 'comprador';
      default:
        return '';
    }
  }

  canDeleteUsuario(usuario: Usuario): boolean {
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser) return false;
    
    // No permitir eliminar el propio usuario
    if (currentUser.id === usuario.id) return false;
    
    // Solo admin y gerente pueden eliminar usuarios
    return this.authService.canManageUsers();
  }

  // Get paginated users
  get paginatedUsuarios(): Usuario[] {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    return this.filteredUsuarios.slice(startIndex, endIndex);
  }
}

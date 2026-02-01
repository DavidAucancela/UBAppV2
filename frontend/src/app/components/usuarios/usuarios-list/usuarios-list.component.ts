import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
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
  paginaActual = 1;
  itemsPerPage = 10;
  totalPaginas = 1;
  totalResultados = 0;
  opcionesElementosPorPagina = [10, 25, 50, 100, 200];
  
  // Messages
  successMessage = '';
  errorMessage = '';
  
  // Selección múltiple y acciones masivas
  selectedIds = new Set<number>();
  bulkActionInProgress = false;
  
  // Form
  usuarioForm: FormGroup;
  ROLES_LABELS = ROLES_LABELS;

  // Ubicaciones
  provincias: string[] = [];
  cantones: string[] = [];
  ciudades: string[] = [];
  loadingCantones = false;
  loadingCiudades = false;

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
      provincia: [''],
      canton: [''],
      ciudad: [''],
      password: ['', [Validators.required, Validators.minLength(6)]],
      es_activo: [true]
    });
  }

  ngOnInit(): void {
    // Cargar provincias al iniciar
    this.cargarProvincias();
    
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
        // El servicio ya maneja la extracción de results si hay paginación
        this.usuarios = Array.isArray(response) ? response : [];
        console.log(`Usuarios cargados: ${this.usuarios.length}`);
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
    this.totalResultados = this.filteredUsuarios.length;
    this.totalPaginas = Math.ceil(this.filteredUsuarios.length / this.itemsPerPage);
    if (this.totalPaginas === 0) {
      this.totalPaginas = 1;
      this.paginaActual = 1;
    }
    // Asegurar que la página actual no exceda el total
    if (this.paginaActual > this.totalPaginas) {
      this.paginaActual = this.totalPaginas;
    }
    console.log('Paginación usuarios:', {
      totalResultados: this.totalResultados,
      itemsPerPage: this.itemsPerPage,
      totalPaginas: this.totalPaginas,
      paginaActual: this.paginaActual
    });
  }

  onSearchChange(): void {
    this.paginaActual = 1;
    this.applyFilters();
  }

  onRoleFilterChange(): void {
    this.paginaActual = 1;
    this.applyFilters();
  }

  onStatusFilterChange(): void {
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
    this.editingUsuario = null;
    this.usuarioForm.reset({
      es_activo: true
    });
    // Limpiar listas de ubicaciones
    this.cantones = [];
    this.ciudades = [];
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
      provincia: usuario.provincia || '',
      canton: usuario.canton || '',
      ciudad: usuario.ciudad || '',
      es_activo: usuario.es_activo,
      password: '' // No mostrar contraseña al editar
    });
    
    // Cargar cantones y ciudades si existen
    if (usuario.provincia) {
      this.apiService.getUbicacionesCantones(usuario.provincia).subscribe({
        next: (data) => {
          this.cantones = data.cantones || [];
        }
      });
    }
    
    if (usuario.provincia && usuario.canton) {
      this.apiService.getUbicacionesCiudades(usuario.provincia, usuario.canton).subscribe({
        next: (data) => {
          this.ciudades = data.ciudades || [];
        }
      });
    }
    
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
      const formData: any = { ...this.usuarioForm.value };

      // Limpiar y preparar datos antes de enviar
      // Convertir rol a número si existe
      if (formData.rol && formData.rol !== '') {
        formData.rol = parseInt(formData.rol, 10);
      }

      // Remover campos vacíos, null o undefined
      Object.keys(formData).forEach(key => {
        const value = formData[key];
        if (value === '' || value === null || value === undefined) {
          delete formData[key];
        }
      });

      // Si estamos editando, no enviar password si está vacío
      if (this.editingUsuario) {
        if (!formData.password || formData.password === '') {
          delete formData.password;
        }
        // En edición, no enviar campos de ubicación vacíos si ya existen en el usuario
        if (!formData.provincia && !this.editingUsuario.provincia) {
          delete formData.provincia;
        }
        if (!formData.canton && !this.editingUsuario.canton) {
          delete formData.canton;
        }
        if (!formData.ciudad && !this.editingUsuario.ciudad) {
          delete formData.ciudad;
        }
      }

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

  // --- Selección múltiple y acciones masivas ---
  toggleSelection(usuario: Usuario): void {
    if (!usuario.id) return;
    if (this.selectedIds.has(usuario.id)) {
      this.selectedIds.delete(usuario.id);
    } else {
      this.selectedIds.add(usuario.id);
    }
    this.selectedIds = new Set(this.selectedIds);
  }

  isSelected(usuario: Usuario): boolean {
    return usuario.id != null && this.selectedIds.has(usuario.id);
  }

  selectAllOnPage(): void {
    const ids = this.paginatedUsuarios.map(u => u.id).filter((id): id is number => id != null);
    const allSelected = ids.length > 0 && ids.every(id => this.selectedIds.has(id));
    if (allSelected) {
      ids.forEach(id => this.selectedIds.delete(id));
    } else {
      ids.forEach(id => this.selectedIds.add(id));
    }
    this.selectedIds = new Set(this.selectedIds);
  }

  areAllSelected(): boolean {
    if (this.paginatedUsuarios.length === 0) return false;
    return this.paginatedUsuarios.every(u => this.isSelected(u));
  }

  clearSelection(): void {
    this.selectedIds.clear();
    this.selectedIds = new Set(this.selectedIds);
  }

  get selectedCount(): number {
    return this.selectedIds.size;
  }

  get canBulkDelete(): boolean {
    if (!this.authService.canManageUsers()) return false;
    const currentId = this.authService.getCurrentUser()?.id;
    return Array.from(this.selectedIds).some(id => id !== currentId);
  }

  bulkDelete(): void {
    const currentId = this.authService.getCurrentUser()?.id;
    const toDelete = Array.from(this.selectedIds).filter(id => id !== currentId);
    if (toDelete.length === 0) {
      this.errorMessage = 'No puedes eliminar tu propio usuario. Deselecciónate o elimina solo otros.';
      setTimeout(() => this.errorMessage = '', 3000);
      return;
    }
    if (!confirm(`¿Eliminar ${toDelete.length} usuario(s) seleccionado(s)? Esta acción no se puede deshacer.`)) return;
    this.bulkActionInProgress = true;
    this.errorMessage = '';
    const calls = toDelete.map(id => this.apiService.deleteUsuario(id).pipe(
      map(() => ({ id, ok: true })),
      catchError(err => of({ id, ok: false, err }))
    ));
    forkJoin(calls).subscribe({
      next: (results) => {
        const ok = results.filter(r => r.ok).length;
        const fail = results.filter(r => !r.ok).length;
        this.successMessage = fail === 0
          ? `${ok} usuario(s) eliminado(s) correctamente.`
          : `${ok} eliminado(s). ${fail} fallaron.`;
        this.clearSelection();
        this.loadUsuarios();
        this.bulkActionInProgress = false;
        setTimeout(() => this.successMessage = '', 4000);
      },
      error: () => {
        this.errorMessage = 'Error al eliminar usuarios.';
        this.bulkActionInProgress = false;
        setTimeout(() => this.errorMessage = '', 3000);
      }
    });
  }

  bulkActivate(): void {
    const ids = Array.from(this.selectedIds);
    if (ids.length === 0) return;
    if (!confirm(`¿Activar ${ids.length} usuario(s) seleccionado(s)?`)) return;
    this.bulkActionInProgress = true;
    this.errorMessage = '';
    const calls = ids.map(id => this.apiService.actualizarUsuarioParcial(id, { es_activo: true }).pipe(
      map(() => ({ id, ok: true })),
      catchError(() => of({ id, ok: false }))
    ));
    forkJoin(calls).subscribe({
      next: (results) => {
        const ok = results.filter(r => r.ok).length;
        this.successMessage = `${ok} usuario(s) activado(s) correctamente.`;
        this.clearSelection();
        this.loadUsuarios();
        this.bulkActionInProgress = false;
        setTimeout(() => this.successMessage = '', 4000);
      },
      error: () => {
        this.errorMessage = 'Error al activar usuarios.';
        this.bulkActionInProgress = false;
        setTimeout(() => this.errorMessage = '', 3000);
      }
    });
  }

  bulkDeactivate(): void {
    const ids = Array.from(this.selectedIds);
    const currentId = this.authService.getCurrentUser()?.id;
    const includingSelf = currentId != null && ids.includes(currentId);
    if (ids.length === 0) return;
    if (includingSelf) {
      this.errorMessage = 'No puedes desactivar tu propio usuario. Quítate de la selección.';
      setTimeout(() => this.errorMessage = '', 3000);
      return;
    }
    if (!confirm(`¿Desactivar ${ids.length} usuario(s) seleccionado(s)?`)) return;
    this.bulkActionInProgress = true;
    this.errorMessage = '';
    const calls = ids.map(id => this.apiService.actualizarUsuarioParcial(id, { es_activo: false }).pipe(
      map(() => ({ id, ok: true })),
      catchError(() => of({ id, ok: false }))
    ));
    forkJoin(calls).subscribe({
      next: (results) => {
        const ok = results.filter(r => r.ok).length;
        this.successMessage = `${ok} usuario(s) desactivado(s) correctamente.`;
        this.clearSelection();
        this.loadUsuarios();
        this.bulkActionInProgress = false;
        setTimeout(() => this.successMessage = '', 4000);
      },
      error: () => {
        this.errorMessage = 'Error al desactivar usuarios.';
        this.bulkActionInProgress = false;
        setTimeout(() => this.errorMessage = '', 3000);
      }
    });
  }

  // Get paginated users
  get paginatedUsuarios(): Usuario[] {
    const startIndex = (this.paginaActual - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    return this.filteredUsuarios.slice(startIndex, endIndex);
  }

  get inicioRango(): number {
    if (this.totalResultados === 0) return 0;
    return (this.paginaActual - 1) * this.itemsPerPage + 1;
  }

  get finRango(): number {
    return Math.min(this.paginaActual * this.itemsPerPage, this.totalResultados);
  }

  // Métodos de ubicaciones
  cargarProvincias(): void {
    this.apiService.getUbicacionesProvincias().subscribe({
      next: (data) => {
        this.provincias = data.provincias || [];
      },
      error: (error) => {
        console.error('Error cargando provincias:', error);
      }
    });
  }

  onProvinciaChange(event: Event): void {
    const provincia = (event.target as HTMLSelectElement).value;
    
    // Limpiar cantones y ciudades
    this.usuarioForm.patchValue({
      canton: '',
      ciudad: ''
    });
    this.cantones = [];
    this.ciudades = [];
    
    if (!provincia) return;
    
    // Cargar cantones
    this.loadingCantones = true;
    this.apiService.getUbicacionesCantones(provincia).subscribe({
      next: (data) => {
        this.cantones = data.cantones || [];
        this.loadingCantones = false;
      },
      error: (error) => {
        console.error('Error cargando cantones:', error);
        this.loadingCantones = false;
      }
    });
  }

  onCantonChange(event: Event): void {
    const canton = (event.target as HTMLSelectElement).value;
    const provincia = this.usuarioForm.get('provincia')?.value;
    
    // Limpiar ciudades
    this.usuarioForm.patchValue({
      ciudad: ''
    });
    this.ciudades = [];
    
    if (!canton || !provincia) return;
    
    // Cargar ciudades
    this.loadingCiudades = true;
    this.apiService.getUbicacionesCiudades(provincia, canton).subscribe({
      next: (data) => {
        this.ciudades = data.ciudades || [];
        this.loadingCiudades = false;
      },
      error: (error) => {
        console.error('Error cargando ciudades:', error);
        this.loadingCiudades = false;
      }
    });
  }

  /**
   * Maneja el cambio de ciudad (por si se necesita alguna lógica adicional)
   */
  onCiudadChange(event: Event): void {
    const ciudad = (event.target as HTMLSelectElement).value;
    // Por ahora no se necesita lógica adicional, pero el método debe existir
    // para evitar el error en el template
  }

}

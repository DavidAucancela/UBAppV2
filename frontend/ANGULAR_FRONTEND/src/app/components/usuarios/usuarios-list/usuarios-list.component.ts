import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { UsuarioService } from '../../../services/usuario.service';
import { AuthService } from '../../../services/auth.service';
import { Usuario, Roles, ROLES_LABELS } from '../../../models/usuario';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-usuarios-list',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './usuarios-list.component.html',
  styleUrl: './usuarios-list.component.css'
})
export class UsuariosListComponent implements OnInit, OnDestroy {
  usuarios: Usuario[] = [];
  filteredUsuarios: Usuario[] = [];
  loading = false;
  submitting = false;
  showModal = false;
  showDetailModal = false;
  showPasswordModal = false;
  editingUsuario: Usuario | null = null;
  selectedUsuario: Usuario | null = null;
  hidePassword = true;
  hidePasswordConfirm = true;
  
  // Filters
  searchTerm = '';
  selectedRole = '';
  selectedStatus = '';
  selectedVerified = '';
  
  // Pagination
  currentPage = 1;
  itemsPerPage = 10;
  totalPages = 1;
  
  // Messages
  successMessage = '';
  errorMessage = '';
  
  // Forms
  usuarioForm: FormGroup;
  passwordForm: FormGroup;
  
  // Constants
  ROLES_LABELS = ROLES_LABELS;
  
  // Subscriptions
  private subscriptions: Subscription = new Subscription();
  
  // Statistics
  estadisticas: any = null;
  showStats = false;

  constructor(
    private usuarioService: UsuarioService,
    private authService: AuthService,
    private fb: FormBuilder
  ) {
    this.usuarioForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      nombre: ['', [Validators.required]],
      correo: ['', [Validators.required, Validators.email]],
      cedula: ['', [Validators.required, Validators.minLength(8)]],
      rol: ['', [Validators.required]],
      telefono: ['', [Validators.pattern(/^[0-9+\-\s]+$/)]],
      fecha_nacimiento: [''],
      direccion: [''],
      tiene_discapacidad: [false],
      tipo_discapacidad: [''],
      notas_accesibilidad: [''],
      password: [''],
      password_confirm: [''],
      es_activo: [true]
    });
    
    this.passwordForm = this.fb.group({
      password_actual: ['', Validators.required],
      password_nuevo: ['', [Validators.required, Validators.minLength(8)]],
      password_confirm: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
    
    // Validación condicional para discapacidad
    this.usuarioForm.get('tiene_discapacidad')?.valueChanges.subscribe(value => {
      const tipoControl = this.usuarioForm.get('tipo_discapacidad');
      if (value) {
        tipoControl?.setValidators([Validators.required]);
      } else {
        tipoControl?.clearValidators();
        tipoControl?.setValue('');
      }
      tipoControl?.updateValueAndValidity();
    });
  }

  ngOnInit(): void {
    this.loadUsuarios();
    this.loadEstadisticas();
    
    // Suscribirse a actualizaciones de usuarios
    this.subscriptions.add(
      this.usuarioService.usuariosActualizados$.subscribe(actualizado => {
        if (actualizado) {
          this.loadUsuarios();
          this.loadEstadisticas();
        }
      })
    );
  }
  
  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  loadUsuarios(): void {
    this.loading = true;
    this.usuarioService.getUsuarios().subscribe({
      next: (usuarios) => {
        this.usuarios = usuarios;
        this.applyFilters();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando usuarios:', error);
        this.showError('Error al cargar los usuarios');
        this.loading = false;
      }
    });
  }
  
  loadEstadisticas(): void {
    if (this.authService.canManageUsers()) {
      this.usuarioService.getEstadisticas().subscribe({
        next: (stats) => {
          this.estadisticas = stats;
        },
        error: (error) => {
          console.error('Error cargando estadísticas:', error);
        }
      });
    }
  }

  applyFilters(): void {
    let filtered = [...this.usuarios];

    // Search filter
    if (this.searchTerm) {
      const search = this.searchTerm.toLowerCase();
      filtered = filtered.filter(usuario =>
        usuario.username.toLowerCase().includes(search) ||
        usuario.nombre?.toLowerCase().includes(search) ||
        usuario.correo?.toLowerCase().includes(search) ||
        usuario.cedula?.toLowerCase().includes(search)
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
    
    // Verified filter
    if (this.selectedVerified !== '') {
      const isVerified = this.selectedVerified === 'true';
      filtered = filtered.filter(usuario => usuario.email_verificado === isVerified);
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

  onFilterChange(): void {
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
      es_activo: true,
      tiene_discapacidad: false
    });
    
    // Hacer obligatoria la contraseña para nuevos usuarios
    this.usuarioForm.get('password')?.setValidators([Validators.required, Validators.minLength(8)]);
    this.usuarioForm.get('password_confirm')?.setValidators([Validators.required]);
    this.usuarioForm.get('password')?.updateValueAndValidity();
    this.usuarioForm.get('password_confirm')?.updateValueAndValidity();
    
    this.showModal = true;
    this.hidePassword = true;
    this.hidePasswordConfirm = true;
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
      fecha_nacimiento: usuario.fecha_nacimiento || '',
      direccion: usuario.direccion || '',
      tiene_discapacidad: usuario.tiene_discapacidad || false,
      tipo_discapacidad: usuario.tipo_discapacidad || '',
      notas_accesibilidad: usuario.notas_accesibilidad || '',
      es_activo: usuario.es_activo,
      password: '',
      password_confirm: ''
    });
    
    // La contraseña es opcional al editar
    this.usuarioForm.get('password')?.clearValidators();
    this.usuarioForm.get('password_confirm')?.clearValidators();
    this.usuarioForm.get('password')?.updateValueAndValidity();
    this.usuarioForm.get('password_confirm')?.updateValueAndValidity();
    
    this.showModal = true;
    this.hidePassword = true;
    this.hidePasswordConfirm = true;
  }

  viewUsuario(usuario: Usuario): void {
    this.selectedUsuario = usuario;
    this.showDetailModal = true;
  }
  
  closeDetailModal(): void {
    this.showDetailModal = false;
    this.selectedUsuario = null;
  }

  deleteUsuario(usuario: Usuario): void {
    if (confirm(`¿Estás seguro de que quieres eliminar al usuario "${usuario.nombre}"? Esta acción no se puede deshacer.`)) {
      this.usuarioService.deleteUsuario(usuario.id!).subscribe({
        next: () => {
          this.showSuccess('Usuario eliminado exitosamente');
        },
        error: (error) => {
          console.error('Error eliminando usuario:', error);
          this.showError(error.error?.error || 'Error al eliminar el usuario');
        }
      });
    }
  }
  
  toggleUsuarioStatus(usuario: Usuario): void {
    const action = usuario.es_activo ? 'desactivar' : 'activar';
    if (confirm(`¿Estás seguro de que quieres ${action} al usuario "${usuario.nombre}"?`)) {
      this.usuarioService.activarDesactivarUsuario(usuario.id!).subscribe({
        next: (response) => {
          this.showSuccess(response.message);
        },
        error: (error) => {
          console.error('Error cambiando estado:', error);
          this.showError(error.error?.error || 'Error al cambiar el estado del usuario');
        }
      });
    }
  }
  
  forzarCambioPassword(usuario: Usuario): void {
    if (confirm(`¿Quieres forzar a "${usuario.nombre}" a cambiar su contraseña en el próximo inicio de sesión?`)) {
      this.usuarioService.forzarCambioPassword(usuario.id!).subscribe({
        next: (response) => {
          this.showSuccess(response.message);
        },
        error: (error) => {
          console.error('Error:', error);
          this.showError(error.error?.error || 'Error al forzar cambio de contraseña');
        }
      });
    }
  }
  
  desbloquearUsuario(usuario: Usuario): void {
    this.usuarioService.desbloquearUsuario(usuario.id!).subscribe({
      next: (response) => {
        this.showSuccess(response.message);
      },
      error: (error) => {
        console.error('Error:', error);
        this.showError(error.error?.error || 'Error al desbloquear usuario');
      }
    });
  }
  
  openPasswordModal(usuario: Usuario): void {
    this.selectedUsuario = usuario;
    this.passwordForm.reset();
    this.showPasswordModal = true;
  }
  
  closePasswordModal(): void {
    this.showPasswordModal = false;
    this.selectedUsuario = null;
    this.passwordForm.reset();
  }
  
  onPasswordSubmit(): void {
    if (this.passwordForm.valid && this.selectedUsuario) {
      const passwords = this.passwordForm.value;
      
      // Validar contraseña segura
      const validacion = this.usuarioService.validarPasswordSeguro(passwords.password_nuevo);
      if (!validacion.valido) {
        this.showError(validacion.mensaje!);
        return;
      }
      
      this.submitting = true;
      this.usuarioService.cambiarPassword(passwords).subscribe({
        next: (response) => {
          this.showSuccess('Contraseña actualizada correctamente');
          this.closePasswordModal();
          this.submitting = false;
        },
        error: (error) => {
          console.error('Error cambiando contraseña:', error);
          this.showError(error.error?.error || 'Error al cambiar la contraseña');
          this.submitting = false;
        }
      });
    }
  }

  closeModal(): void {
    this.showModal = false;
    this.editingUsuario = null;
    this.usuarioForm.reset();
    this.errorMessage = '';
  }

  onSubmit(): void {
    if (this.usuarioForm.valid) {
      const formData = this.usuarioForm.value;
      
      // Validar contraseña si se proporciona
      if (formData.password) {
        const validacion = this.usuarioService.validarPasswordSeguro(formData.password);
        if (!validacion.valido) {
          this.showError(validacion.mensaje!);
          return;
        }
        
        if (formData.password !== formData.password_confirm) {
          this.showError('Las contraseñas no coinciden');
          return;
        }
      }
      
      // Validar email
      if (!this.usuarioService.validarEmail(formData.correo)) {
        this.showError('El formato del correo electrónico no es válido');
        return;
      }
      
      // Validar cédula
      if (!this.usuarioService.validarCedula(formData.cedula)) {
        this.showError('La cédula debe tener al menos 8 dígitos');
        return;
      }
      
      // Validar teléfono si se proporciona
      if (formData.telefono && !this.usuarioService.validarTelefono(formData.telefono)) {
        this.showError('El teléfono debe contener solo números');
        return;
      }
      
      this.submitting = true;

      if (this.editingUsuario) {
        // Update existing user
        // Si no se proporciona contraseña, eliminarla del objeto
        if (!formData.password) {
          delete formData.password;
          delete formData.password_confirm;
        }
        
        this.usuarioService.updateUsuario(this.editingUsuario.id!, formData).subscribe({
          next: () => {
            this.showSuccess('Usuario actualizado exitosamente');
            this.closeModal();
            this.submitting = false;
          },
          error: (error) => {
            console.error('Error actualizando usuario:', error);
            this.showError(error.error?.error || 'Error al actualizar el usuario');
            this.submitting = false;
          }
        });
      } else {
        // Create new user
        this.usuarioService.createUsuario(formData).subscribe({
          next: () => {
            this.showSuccess('Usuario creado exitosamente. Se ha enviado un email de verificación.');
            this.closeModal();
            this.submitting = false;
          },
          error: (error) => {
            console.error('Error creando usuario:', error);
            if (error.error?.errors) {
              const errors = error.error.errors.join(', ');
              this.showError(errors);
            } else {
              this.showError(error.error?.error || 'Error al crear el usuario');
            }
            this.submitting = false;
          }
        });
      }
    } else {
      this.markFormGroupTouched(this.usuarioForm);
    }
  }

  private markFormGroupTouched(formGroup: FormGroup): void {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();
    });
  }
  
  private passwordMatchValidator(formGroup: FormGroup): {[key: string]: boolean} | null {
    const password = formGroup.get('password_nuevo');
    const confirmPassword = formGroup.get('password_confirm');
    
    if (password?.value !== confirmPassword?.value) {
      confirmPassword?.setErrors({ passwordMismatch: true });
      return { passwordMismatch: true };
    }
    
    return null;
  }
  
  private showSuccess(message: string): void {
    this.successMessage = message;
    setTimeout(() => this.successMessage = '', 5000);
  }
  
  private showError(message: string): void {
    this.errorMessage = message;
    setTimeout(() => this.errorMessage = '', 5000);
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
    
    // Solo admin puede eliminar usuarios
    return this.authService.isAdmin();
  }
  
  canEditUsuario(usuario: Usuario): boolean {
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser) return false;
    
    // Puede editar su propio perfil
    if (currentUser.id === usuario.id) return true;
    
    // Admin y gerente pueden editar otros usuarios
    return this.authService.canManageUsers();
  }
  
  canManageUsuario(usuario: Usuario): boolean {
    return this.authService.canManageUsers();
  }
  
  isUsuarioBloqueado(usuario: Usuario): boolean {
    return !!(usuario.bloqueado_hasta && new Date(usuario.bloqueado_hasta) > new Date());
  }
  
  formatDate(date: string | undefined): string {
    if (!date) return 'N/A';
    return new Date(date).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
  
  formatDateTime(date: string | undefined): string {
    if (!date) return 'N/A';
    return new Date(date).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  // Get paginated users
  get paginatedUsuarios(): Usuario[] {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    return this.filteredUsuarios.slice(startIndex, endIndex);
  }
}
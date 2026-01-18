import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../services/api.service';
import { Usuario } from '../../models/usuario';
import { CambioPasswordComponent } from '../shared/cambio-password/cambio-password.component';

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, CambioPasswordComponent],
  templateUrl: './perfil.component.html',
  styleUrl: './perfil.component.css'
})
export class PerfilComponent implements OnInit {
  @ViewChild(CambioPasswordComponent) cambioPasswordComponent!: CambioPasswordComponent;
  
  currentUser: Usuario | null = null;
  profileForm!: FormGroup;
  initialFormValues: any = {};
  
  loading = false;
  loadingUbicaciones = false;
  profileSuccess = false;
  profileError: string | null = null;
  hasChanges = false;
  
  // Estados para cambio de contraseña
  passwordLoading = false;
  passwordSuccess = false;
  passwordError: string | null = null;
  passwordData: any = null;

  // Listas para selectores en cascada
  provincias: string[] = [];
  cantones: string[] = [];
  ciudades: string[] = [];

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.initForms();
    this.loadProvincias();
    
    // Cargar datos del usuario después de que el formulario esté inicializado
    // Usar setTimeout para asegurar que el formulario esté completamente listo
    setTimeout(() => {
      this.loadUserData();
    }, 100);
  }

  initForms(): void {
    // Formulario de perfil (sin campos de contraseña)
    this.profileForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3)]],
      correo: ['', [Validators.required, Validators.email]],
      telefono: ['', [Validators.pattern(/^[0-9]{10}$/)]],
      direccion: [''],
      fecha_nacimiento: [''],
      provincia: [''],
      canton: [''],
      ciudad: [''],
      cupo_anual: [null]
    });

    // Suscribirse a cambios en los selectores de ubicación
    this.profileForm.get('provincia')?.valueChanges.subscribe(provincia => {
      if (provincia) {
        this.onProvinciaChange(provincia);
      } else {
        this.cantones = [];
        this.ciudades = [];
        this.profileForm.patchValue({ canton: '', ciudad: '' }, { emitEvent: false });
      }
    });

    this.profileForm.get('canton')?.valueChanges.subscribe(canton => {
      if (canton && this.profileForm.get('provincia')?.value) {
        this.onCantonChange(this.profileForm.get('provincia')?.value, canton);
      } else {
        this.ciudades = [];
        this.profileForm.patchValue({ ciudad: '' }, { emitEvent: false });
      }
    });

    this.profileForm.get('ciudad')?.valueChanges.subscribe(ciudad => {
      // No se requiere acción adicional al cambiar la ciudad
    });

    // Suscribirse a cambios en el formulario para detectar modificaciones
    this.profileForm.valueChanges.subscribe(() => {
      // Usar setTimeout para evitar problemas de sincronización
      setTimeout(() => {
        this.hasChanges = this.hasFormChanges();
      }, 0);
    });
  }


  loadUserData(): void {
    if (this.currentUser) {
      // Formatear fecha de nacimiento para input type="date" (YYYY-MM-DD)
      let fechaNacimiento = '';
      if (this.currentUser.fecha_nacimiento) {
        try {
          // Si viene como string ISO, extraer solo la fecha
          const fecha = new Date(this.currentUser.fecha_nacimiento);
          if (!isNaN(fecha.getTime())) {
            // Formatear a YYYY-MM-DD
            const year = fecha.getFullYear();
            const month = String(fecha.getMonth() + 1).padStart(2, '0');
            const day = String(fecha.getDate()).padStart(2, '0');
            fechaNacimiento = `${year}-${month}-${day}`;
          }
        } catch (e) {
          // Si ya está en formato YYYY-MM-DD, usarlo directamente
          if (typeof this.currentUser.fecha_nacimiento === 'string' && /^\d{4}-\d{2}-\d{2}/.test(this.currentUser.fecha_nacimiento)) {
            fechaNacimiento = this.currentUser.fecha_nacimiento.split('T')[0]; // Tomar solo la parte de fecha
          }
        }
      }

      // Asegurar que todos los campos tengan valores por defecto, incluso si son null/undefined
      const formData = {
        nombre: this.currentUser.nombre || '',
        correo: this.currentUser.correo || '',
        telefono: this.currentUser.telefono || '',
        direccion: this.currentUser.direccion || '',
        fecha_nacimiento: fechaNacimiento,
        provincia: this.currentUser.provincia || '',
        canton: this.currentUser.canton || '',
        ciudad: this.currentUser.ciudad || '',
        cupo_anual: this.currentUser.cupo_anual !== null && this.currentUser.cupo_anual !== undefined ? this.currentUser.cupo_anual : null
      };

      // Establecer valores del formulario inmediatamente
      this.profileForm.patchValue(formData, { emitEvent: false });
      
      // Guardar valores iniciales para comparar cambios (usar JSON para deep copy)
      this.initialFormValues = JSON.parse(JSON.stringify(formData));
      
      // Inicializar estado de cambios
      this.hasChanges = false;
      
      // Cargar cantones y ciudades si ya tiene ubicación
      // Esto debe hacerse después de establecer los valores del formulario
      if (this.currentUser.provincia) {
        this.loadCantones(this.currentUser.provincia);
        // Esperar a que se carguen los cantones antes de cargar las ciudades
        setTimeout(() => {
          if (this.currentUser?.canton) {
            this.loadCiudades(this.currentUser.provincia, this.currentUser.canton);
            // Después de cargar las ciudades, asegurar que los valores estén correctos
            setTimeout(() => {
              this.profileForm.patchValue({
                provincia: formData.provincia,
                canton: formData.canton,
                ciudad: formData.ciudad
              }, { emitEvent: false });
              this.profileForm.updateValueAndValidity({ emitEvent: false });
            }, 100);
          }
        }, 200);
      } else {
        // Si no hay ubicación, solo actualizar la validación
        this.profileForm.updateValueAndValidity({ emitEvent: false });
      }
    }
  }

  // Métodos para cargar ubicaciones
  loadProvincias(): void {
    this.loadingUbicaciones = true;
    this.apiService.getUbicacionesProvincias().subscribe({
      next: (response) => {
        this.provincias = response.provincias || [];
        this.loadingUbicaciones = false;
      },
      error: (error) => {
        console.error('Error al cargar provincias:', error);
        this.loadingUbicaciones = false;
      }
    });
  }

  loadCantones(provincia: string): void {
    this.loadingUbicaciones = true;
    this.apiService.getUbicacionesCantones(provincia).subscribe({
      next: (response) => {
        this.cantones = response.cantones || [];
        this.loadingUbicaciones = false;
        
        // Si el usuario ya tiene un cantón seleccionado, asegurarse de que esté en la lista
        const currentCanton = this.profileForm.get('canton')?.value;
        if (currentCanton && !this.cantones.includes(currentCanton)) {
          // Si el cantón actual no está en la lista, limpiarlo
          this.profileForm.patchValue({ canton: '' }, { emitEvent: false });
        }
      },
      error: (error) => {
        console.error('Error al cargar cantones:', error);
        this.loadingUbicaciones = false;
      }
    });
  }

  loadCiudades(provincia: string, canton: string): void {
    this.loadingUbicaciones = true;
    this.apiService.getUbicacionesCiudades(provincia, canton).subscribe({
      next: (response) => {
        this.ciudades = response.ciudades || [];
        this.loadingUbicaciones = false;
        
        // Si el usuario ya tiene una ciudad seleccionada, asegurarse de que esté en la lista
        const currentCiudad = this.profileForm.get('ciudad')?.value;
        if (currentCiudad && !this.ciudades.includes(currentCiudad)) {
          // Si la ciudad actual no está en la lista, limpiarla
          this.profileForm.patchValue({ ciudad: '' }, { emitEvent: false });
        }
      },
      error: (error) => {
        console.error('Error al cargar ciudades:', error);
        this.loadingUbicaciones = false;
      }
    });
  }

  onProvinciaChange(provincia: string): void {
    this.cantones = [];
    this.ciudades = [];
    this.profileForm.patchValue({ 
      canton: '', 
      ciudad: ''
    }, { emitEvent: false });
    this.loadCantones(provincia);
  }

  onCantonChange(provincia: string, canton: string): void {
    this.ciudades = [];
    this.profileForm.patchValue({ 
      ciudad: ''
    }, { emitEvent: false });
    this.loadCiudades(provincia, canton);
  }

  isAdmin(): boolean {
    return this.currentUser?.rol === 1;
  }

  onSubmitProfile(): void {
    // Validar campos básicos
    const basicFieldsValid = this.profileForm.get('nombre')?.valid && 
                             this.profileForm.get('correo')?.valid &&
                             (!this.profileForm.get('telefono')?.value || this.profileForm.get('telefono')?.valid);
    
    if (!basicFieldsValid) {
      Object.keys(this.profileForm.controls).forEach(key => {
        this.profileForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.loading = true;
    this.profileSuccess = false;
    this.profileError = null;

    if (!this.currentUser?.id) {
      this.profileError = 'Error: Usuario no identificado';
      this.loading = false;
      return;
    }

    // Preparar datos del formulario
    const formData = { ...this.profileForm.value };

    // Limpiar datos: convertir strings vacíos a null y eliminar campos no permitidos
    const cleanData: any = {};
    
    // Solo incluir campos que se pueden actualizar
    const allowedFields = ['nombre', 'correo', 'telefono', 'fecha_nacimiento', 'direccion', 
                          'provincia', 'canton', 'ciudad', 'cupo_anual'];
    
    allowedFields.forEach(field => {
      const value = formData[field];
      // Convertir strings vacíos a null, mantener otros valores
      if (value === '' || value === undefined) {
        cleanData[field] = null;
      } else {
        cleanData[field] = value;
      }
    });

    // Usar el endpoint de actualizar perfil
    this.apiService.actualizarPerfil(cleanData).subscribe({
      next: (response) => {
        this.profileSuccess = true;
        this.loading = false;
        
        // Actualizar valores iniciales con los datos actualizados
        const updatedFormData = {
          nombre: response.nombre || '',
          correo: response.correo || '',
          telefono: response.telefono || '',
          direccion: response.direccion || '',
          fecha_nacimiento: response.fecha_nacimiento ? this.formatDateForInput(response.fecha_nacimiento) : '',
          provincia: response.provincia || '',
          canton: response.canton || '',
          ciudad: response.ciudad || '',
          cupo_anual: response.cupo_anual || null
        };
        this.initialFormValues = JSON.parse(JSON.stringify(updatedFormData));
        this.hasChanges = false;
        
        // Actualizar el usuario en el servicio de autenticación
        const updatedUser = { ...this.currentUser, ...response };
        this.authService.updateCurrentUser(updatedUser as Usuario);
        this.currentUser = updatedUser as Usuario;
        
        setTimeout(() => {
          this.profileSuccess = false;
        }, 5000);
      },
      error: (error) => {
        console.error('Error al actualizar perfil:', error);
        
        // Mostrar errores específicos del backend
        if (error.error) {
          if (error.error.detail) {
            this.profileError = error.error.detail;
          } else if (typeof error.error === 'string') {
            this.profileError = error.error;
          } else if (error.error.message) {
            this.profileError = error.error.message;
          } else if (error.error.non_field_errors) {
            this.profileError = Array.isArray(error.error.non_field_errors) 
              ? error.error.non_field_errors.join(', ') 
              : error.error.non_field_errors;
          } else {
            // Mostrar el primer error de campo encontrado
            const firstError = Object.values(error.error)[0];
            if (Array.isArray(firstError)) {
              this.profileError = firstError[0];
            } else if (typeof firstError === 'string') {
              this.profileError = firstError;
            } else {
              this.profileError = 'Error al actualizar el perfil. Verifica los datos ingresados.';
            }
          }
        } else {
          this.profileError = 'Error al actualizar el perfil. Por favor, intenta nuevamente.';
        }
        
        this.loading = false;
      }
    });
  }


  onPasswordChange(passwordData: any): void {
    this.passwordData = passwordData;
  }

  onSubmitPassword(): void {
    // Verificar que el componente de contraseña esté disponible y sea válido
    if (!this.cambioPasswordComponent) {
      this.passwordError = 'Error: Componente de contraseña no disponible';
      return;
    }

    // Verificar que el formulario de contraseña sea válido
    if (!this.cambioPasswordComponent.isValid) {
      this.passwordError = 'Por favor, completa correctamente todos los campos de contraseña';
      // Marcar todos los campos como touched para mostrar errores
      Object.keys(this.cambioPasswordComponent.passwordForm.controls).forEach(key => {
        this.cambioPasswordComponent.passwordForm.get(key)?.markAsTouched();
      });
      return;
    }

    if (!this.passwordData) {
      this.passwordError = 'Por favor, completa todos los campos de contraseña';
      return;
    }

    const { currentPassword, newPassword, confirmPassword } = this.passwordData;

    // Validar que todos los campos estén llenos
    if (!currentPassword || !newPassword || !confirmPassword) {
      this.passwordError = 'Todos los campos son requeridos';
      return;
    }

    // Validar que las contraseñas coincidan
    if (newPassword !== confirmPassword) {
      this.passwordError = 'Las contraseñas no coinciden';
      return;
    }

    // Validar longitud mínima
    if (newPassword.length < 6) {
      this.passwordError = 'La nueva contraseña debe tener al menos 6 caracteres';
      return;
    }

    this.passwordLoading = true;
    this.passwordError = null;
    this.passwordSuccess = false;

    const passwordData = {
      password_actual: currentPassword,
      password_nuevo: newPassword,
      password_confirm: newPassword
    };

    this.apiService.cambiarPasswordPerfil(passwordData).subscribe({
      next: () => {
        this.passwordSuccess = true;
        this.passwordLoading = false;
        this.passwordData = null;
        
        // Limpiar el formulario de contraseña
        if (this.cambioPasswordComponent) {
          this.cambioPasswordComponent.reset();
        }
        
        setTimeout(() => {
          this.passwordSuccess = false;
        }, 5000);
      },
      error: (error) => {
        console.error('Error al cambiar contraseña:', error);
        this.passwordError = error.error?.error || 
                           error.error?.password_actual || 
                           error.error?.detail ||
                           'Error al cambiar la contraseña. Verifica tu contraseña actual.';
        this.passwordLoading = false;
      }
    });
  }

  hasFormChanges(): boolean {
    if (!this.currentUser || !this.initialFormValues) return false;

    const currentValues = this.profileForm.value;
    
    // Normalizar valores para comparación
    const normalize = (value: any): string => {
      if (value === null || value === undefined) return '';
      if (typeof value === 'number') return String(value);
      return String(value).trim();
    };
    
    // Comparar campos básicos
    if (normalize(currentValues.nombre) !== normalize(this.initialFormValues.nombre)) return true;
    if (normalize(currentValues.correo) !== normalize(this.initialFormValues.correo)) return true;
    if (normalize(currentValues.telefono) !== normalize(this.initialFormValues.telefono)) return true;
    if (normalize(currentValues.direccion) !== normalize(this.initialFormValues.direccion)) return true;
    
    // Comparar fecha de nacimiento (normalizar formato)
    const fechaActual = normalize(currentValues.fecha_nacimiento);
    const fechaInicial = normalize(this.initialFormValues.fecha_nacimiento);
    if (fechaActual !== fechaInicial) return true;
    
    if (normalize(currentValues.provincia) !== normalize(this.initialFormValues.provincia)) return true;
    if (normalize(currentValues.canton) !== normalize(this.initialFormValues.canton)) return true;
    if (normalize(currentValues.ciudad) !== normalize(this.initialFormValues.ciudad)) return true;
    
    // Comparar cupo_anual (manejar números y null)
    const cupoActual = currentValues.cupo_anual === null || currentValues.cupo_anual === '' ? null : Number(currentValues.cupo_anual);
    const cupoInicial = this.initialFormValues.cupo_anual === null || this.initialFormValues.cupo_anual === '' ? null : Number(this.initialFormValues.cupo_anual);
    if (cupoActual !== cupoInicial) return true;
    
    return false;
  }


  /**
   * Formatea una fecha para el input type="date" (YYYY-MM-DD)
   */
  formatDateForInput(date: string | Date): string {
    if (!date) return '';
    try {
      const fecha = typeof date === 'string' ? new Date(date) : date;
      if (isNaN(fecha.getTime())) return '';
      const year = fecha.getFullYear();
      const month = String(fecha.getMonth() + 1).padStart(2, '0');
      const day = String(fecha.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    } catch (e) {
      // Si ya está en formato YYYY-MM-DD, retornarlo
      if (typeof date === 'string' && /^\d{4}-\d{2}-\d{2}/.test(date)) {
        return date.split('T')[0];
      }
      return '';
    }
  }

  // Helpers para validación
  isFieldInvalid(form: FormGroup, fieldName: string): boolean {
    const field = form.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }

  getFieldError(form: FormGroup, fieldName: string): string {
    const field = form.get(fieldName);
    if (!field || !field.errors) return '';

    if (field.errors['required']) return 'Este campo es requerido';
    if (field.errors['email']) return 'Correo electrónico inválido';
    if (field.errors['minlength']) {
      return `Mínimo ${field.errors['minlength'].requiredLength} caracteres`;
    }
    if (field.errors['pattern']) return 'Formato inválido';
    
    return 'Campo inválido';
  }

  /**
   * Verifica si el formulario es válido para guardar
   */
  isFormValid(): boolean {
    // Validar campos básicos requeridos
    const nombreValid = this.profileForm.get('nombre')?.valid;
    const correoValid = this.profileForm.get('correo')?.valid;
    const telefonoValid = !this.profileForm.get('telefono')?.value || this.profileForm.get('telefono')?.valid;
    
    return nombreValid && correoValid && telefonoValid;
  }
}

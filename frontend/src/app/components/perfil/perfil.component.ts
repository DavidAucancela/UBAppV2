import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../services/api.service';
import { Usuario } from '../../models/usuario';

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './perfil.component.html',
  styleUrl: './perfil.component.css'
})
export class PerfilComponent implements OnInit {
  currentUser: Usuario | null = null;
  profileForm!: FormGroup;
  initialFormValues: any = {};
  
  showCurrentPassword = false;
  showNewPassword = false;
  showConfirmPassword = false;
  changePasswordEnabled = false;
  
  loading = false;
  loadingUbicaciones = false;
  profileSuccess = false;
  profileError: string | null = null;
  hasChanges = false;

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
    this.loadUserData();
  }

  initForms(): void {
    // Formulario unificado de perfil
    this.profileForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3)]],
      correo: ['', [Validators.required, Validators.email]],
      telefono: ['', [Validators.pattern(/^[0-9]{10}$/)]],
      direccion: [''],
      fecha_nacimiento: [''],
      provincia: [''],
      canton: [''],
      ciudad: [''],
      cupo_anual: [null],
      // Campos de contraseña (opcionales)
      currentPassword: [''],
      newPassword: [''],
      confirmPassword: ['']
    }, { validators: this.passwordValidator.bind(this) });

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
      this.hasChanges = this.hasFormChanges();
    });
  }

  passwordValidator(g: FormGroup) {
    // Solo validar contraseña si está habilitada
    if (!this.changePasswordEnabled) {
      return null;
    }

    const currentPassword = g.get('currentPassword')?.value;
    const newPassword = g.get('newPassword')?.value;
    const confirmPassword = g.get('confirmPassword')?.value;

    // Si se intenta cambiar la contraseña, todos los campos son requeridos
    if (!currentPassword || !newPassword || !confirmPassword) {
      return { passwordIncomplete: true };
    }
    
    // Validar longitud mínima de la nueva contraseña
    if (newPassword.length < 6) {
      return { passwordMinLength: true };
    }
    
    // Validar que las contraseñas coincidan
    if (newPassword !== confirmPassword) {
      return { passwordMismatch: true };
    }
    
    return null;
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

      const formData = {
        nombre: this.currentUser.nombre || '',
        correo: this.currentUser.correo || '',
        telefono: this.currentUser.telefono || '',
        direccion: this.currentUser.direccion || '',
        fecha_nacimiento: fechaNacimiento,
        provincia: this.currentUser.provincia || '',
        canton: this.currentUser.canton || '',
        ciudad: this.currentUser.ciudad || '',
        cupo_anual: this.currentUser.cupo_anual || null,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      };

      this.profileForm.patchValue(formData, { emitEvent: false });
      
      // Guardar valores iniciales para comparar cambios (usar JSON para deep copy)
      this.initialFormValues = JSON.parse(JSON.stringify(formData));
      delete this.initialFormValues.currentPassword;
      delete this.initialFormValues.newPassword;
      delete this.initialFormValues.confirmPassword;
      
      // Inicializar estado de cambios
      this.hasChanges = false;

      // Cargar cantones y ciudades si ya tiene ubicación
      if (this.currentUser.provincia) {
        this.loadCantones(this.currentUser.provincia);
        if (this.currentUser.canton) {
          this.loadCiudades(this.currentUser.provincia, this.currentUser.canton);
        }
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
    // Validar solo campos básicos (contraseña se valida con el validador personalizado)
    const basicFieldsValid = this.profileForm.get('nombre')?.valid && 
                             this.profileForm.get('correo')?.valid &&
                             (!this.profileForm.get('telefono')?.value || this.profileForm.get('telefono')?.valid);
    
    if (!basicFieldsValid || this.profileForm.errors) {
      Object.keys(this.profileForm.controls).forEach(key => {
        this.profileForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.loading = true;
    this.profileSuccess = false;
    this.profileError = null;

    const userId = this.currentUser?.id;
    if (!userId) {
      this.profileError = 'Error: Usuario no identificado';
      this.loading = false;
      return;
    }

    // Preparar datos del formulario (sin campos de contraseña por ahora)
    const formData = { ...this.profileForm.value };
    const currentPassword = formData.currentPassword;
    const newPassword = formData.newPassword;
    
    // Eliminar campos de contraseña del objeto de datos del perfil
    delete formData.currentPassword;
    delete formData.newPassword;
    delete formData.confirmPassword;

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

    // Usar el endpoint correcto de actualizar perfil
    this.apiService.actualizarPerfil(cleanData).subscribe({
      next: (response) => {
        // Si el checkbox está activado y se proporcionó contraseña, actualizarla también
        if (this.changePasswordEnabled && currentPassword && newPassword) {
          const passwordData = {
            password_actual: currentPassword,
            password_nuevo: newPassword,
            password_confirm: newPassword
          };

          this.apiService.cambiarPasswordPerfil(passwordData).subscribe({
            next: () => {
              this.profileSuccess = true;
              this.loading = false;
              
              // Limpiar campos de contraseña y desactivar checkbox
              this.changePasswordEnabled = false;
              this.profileForm.patchValue({
                currentPassword: '',
                newPassword: '',
                confirmPassword: ''
              }, { emitEvent: false });
              
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
              this.profileError = error.error?.error || error.error?.password_actual || 'Error al cambiar la contraseña. Verifica tu contraseña actual.';
              this.loading = false;
            }
          });
        } else {
          // Solo se actualizó el perfil
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
        }
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


  onPasswordCheckboxChange(event: any): void {
    this.changePasswordEnabled = event.target.checked;
    
    if (!this.changePasswordEnabled) {
      // Limpiar campos de contraseña si se desactiva el checkbox
      this.profileForm.patchValue({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }, { emitEvent: false });
    } else {
      // Agregar validadores cuando se activa
      this.profileForm.get('currentPassword')?.setValidators([Validators.required]);
      this.profileForm.get('newPassword')?.setValidators([Validators.required, Validators.minLength(6)]);
      this.profileForm.get('confirmPassword')?.setValidators([Validators.required]);
    }
    
    // Actualizar validación
    this.profileForm.get('currentPassword')?.updateValueAndValidity({ emitEvent: false });
    this.profileForm.get('newPassword')?.updateValueAndValidity({ emitEvent: false });
    this.profileForm.get('confirmPassword')?.updateValueAndValidity({ emitEvent: false });
    this.profileForm.updateValueAndValidity();
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
    
    // Si el checkbox de contraseña está activado, verificar si hay cambios
    if (this.changePasswordEnabled) {
      const hasPasswordFields = normalize(currentValues.currentPassword) || 
                                normalize(currentValues.newPassword) || 
                                normalize(currentValues.confirmPassword);
      if (hasPasswordFields) return true;
    }
    
    return false;
  }

  togglePasswordVisibility(field: string): void {
    switch(field) {
      case 'current':
        this.showCurrentPassword = !this.showCurrentPassword;
        break;
      case 'new':
        this.showNewPassword = !this.showNewPassword;
        break;
      case 'confirm':
        this.showConfirmPassword = !this.showConfirmPassword;
        break;
    }
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
    
    // Validaciones de formulario (contraseña)
    if (form.errors?.['passwordIncomplete']) {
      return 'Todos los campos de contraseña son requeridos para cambiar la contraseña';
    }
    if (form.errors?.['passwordMinLength']) {
      return 'La nueva contraseña debe tener al menos 6 caracteres';
    }
    if (form.errors?.['passwordMismatch']) {
      return 'Las contraseñas no coinciden';
    }
    
    return 'Campo inválido';
  }
}

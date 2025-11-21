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
      latitud: [null],
      longitud: [null],
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
        this.profileForm.patchValue({ canton: '', ciudad: '', latitud: null, longitud: null }, { emitEvent: false });
      }
    });

    this.profileForm.get('canton')?.valueChanges.subscribe(canton => {
      if (canton && this.profileForm.get('provincia')?.value) {
        this.onCantonChange(this.profileForm.get('provincia')?.value, canton);
      } else {
        this.ciudades = [];
        this.profileForm.patchValue({ ciudad: '', latitud: null, longitud: null }, { emitEvent: false });
      }
    });

    this.profileForm.get('ciudad')?.valueChanges.subscribe(ciudad => {
      if (ciudad && this.profileForm.get('provincia')?.value && this.profileForm.get('canton')?.value) {
        this.onCiudadChange(
          this.profileForm.get('provincia')?.value,
          this.profileForm.get('canton')?.value,
          ciudad
        );
      }
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
      const formData = {
        nombre: this.currentUser.nombre,
        correo: this.currentUser.correo,
        telefono: this.currentUser.telefono || '',
        direccion: this.currentUser.direccion || '',
        fecha_nacimiento: this.currentUser.fecha_nacimiento || '',
        provincia: this.currentUser.provincia || '',
        canton: this.currentUser.canton || '',
        ciudad: this.currentUser.ciudad || '',
        latitud: this.currentUser.latitud || null,
        longitud: this.currentUser.longitud || null,
        cupo_anual: this.currentUser.cupo_anual || null,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      };

      this.profileForm.patchValue(formData, { emitEvent: false });
      
      // Guardar valores iniciales para comparar cambios
      this.initialFormValues = { ...formData };
      delete this.initialFormValues.currentPassword;
      delete this.initialFormValues.newPassword;
      delete this.initialFormValues.confirmPassword;

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
      ciudad: '', 
      latitud: null, 
      longitud: null 
    }, { emitEvent: false });
    this.loadCantones(provincia);
  }

  onCantonChange(provincia: string, canton: string): void {
    this.ciudades = [];
    this.profileForm.patchValue({ 
      ciudad: '', 
      latitud: null, 
      longitud: null 
    }, { emitEvent: false });
    this.loadCiudades(provincia, canton);
  }

  onCiudadChange(provincia: string, canton: string, ciudad: string): void {
    // Obtener coordenadas de la ciudad seleccionada
    this.apiService.getUbicacionesCoordenadas(provincia, canton, ciudad).subscribe({
      next: (response) => {
        this.profileForm.patchValue({
          latitud: response.latitud,
          longitud: response.longitud
        }, { emitEvent: false });
      },
      error: (error) => {
        console.error('Error al obtener coordenadas:', error);
      }
    });
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
                          'provincia', 'canton', 'ciudad', 'latitud', 'longitud', 'cupo_anual'];
    
    allowedFields.forEach(field => {
      const value = formData[field];
      // Convertir strings vacíos a null, mantener otros valores
      if (value === '' || value === undefined) {
        cleanData[field] = null;
      } else {
        cleanData[field] = value;
      }
    });

    // Primero actualizar el perfil
    this.apiService.updateUsuario(userId, cleanData).subscribe({
      next: (response) => {
        // Si el checkbox está activado y se proporcionó contraseña, actualizarla también
        if (this.changePasswordEnabled && currentPassword && newPassword) {
          const passwordData = {
            current_password: currentPassword,
            new_password: newPassword
          };

          this.apiService.changePassword(userId, passwordData).subscribe({
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
              
              // Actualizar valores iniciales
              this.initialFormValues = { ...cleanData };
              
              // Actualizar el usuario en el servicio de autenticación
              const updatedUser = { ...this.currentUser, ...cleanData };
              this.authService.updateCurrentUser(updatedUser as Usuario);
              
              setTimeout(() => {
                this.profileSuccess = false;
              }, 5000);
            },
            error: (error) => {
              this.profileError = error.error?.message || 'Error al cambiar la contraseña. Verifica tu contraseña actual.';
              this.loading = false;
            }
          });
        } else {
          // Solo se actualizó el perfil
          this.profileSuccess = true;
          this.loading = false;
          
          // Actualizar valores iniciales
          this.initialFormValues = { ...cleanData };
          
          // Actualizar el usuario en el servicio de autenticación
          const updatedUser = { ...this.currentUser, ...cleanData };
          this.authService.updateCurrentUser(updatedUser as Usuario);
          
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
    if (!this.currentUser) return false;

    const currentValues = this.profileForm.value;
    
    // Comparar campos básicos
    if (currentValues.nombre !== this.initialFormValues.nombre) return true;
    if (currentValues.correo !== this.initialFormValues.correo) return true;
    if ((currentValues.telefono || '') !== (this.initialFormValues.telefono || '')) return true;
    if ((currentValues.direccion || '') !== (this.initialFormValues.direccion || '')) return true;
    if ((currentValues.fecha_nacimiento || '') !== (this.initialFormValues.fecha_nacimiento || '')) return true;
    if ((currentValues.provincia || '') !== (this.initialFormValues.provincia || '')) return true;
    if ((currentValues.canton || '') !== (this.initialFormValues.canton || '')) return true;
    if ((currentValues.ciudad || '') !== (this.initialFormValues.ciudad || '')) return true;
    if (currentValues.cupo_anual !== this.initialFormValues.cupo_anual) return true;
    
    // Si el checkbox de contraseña está activado, verificar si hay cambios
    if (this.changePasswordEnabled) {
      if (currentValues.currentPassword || currentValues.newPassword || currentValues.confirmPassword) {
        return true;
      }
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

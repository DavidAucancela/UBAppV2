import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { ApiService } from '../../../services/api.service';
import { Roles, ROLES_LABELS } from '../../../models/usuario';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent implements OnInit {
  registerForm: FormGroup;
  provincias: string[] = [];
  cantones: string[] = [];
  ciudades: string[] = [];
  loading = false;
  loadingCantones = false;
  loadingCiudades = false;
  successMessage = '';
  errorMessage = '';
  readonly ROLES = Roles;
  readonly roleLabels = ROLES_LABELS;
  readonly availableRoles = [Roles.COMPRADOR];

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private router: Router
  ) {
    this.registerForm = this.fb.group({
      username: ['', [Validators.required]],
      nombre: ['', [Validators.required]],
      correo: ['', [Validators.required, Validators.email]],
      cedula: ['', [Validators.required]],
      telefono: [''],
      rol: [Roles.COMPRADOR, [Validators.required]],
      password: ['', [Validators.required, Validators.minLength(8), this.passwordStrengthValidator]],
      password_confirm: ['', [Validators.required]],
      provincia: ['', [Validators.required]],
      canton: ['', [Validators.required]],
      ciudad: ['', [Validators.required]],
      es_activo: [true]
    }, { validators: this.passwordsMatchValidator });
  }

  ngOnInit(): void {
    this.cargarProvincias();
  }

  cargarProvincias(): void {
    this.apiService.getUbicacionesProvincias().subscribe({
      next: (data) => {
        this.provincias = data.provincias || [];
      },
      error: () => {
        this.errorMessage = 'No pudimos cargar las provincias. Intenta nuevamente más tarde.';
      }
    });
  }

  onProvinciaChange(event: Event): void {
    const provincia = (event.target as HTMLSelectElement).value;
    this.registerForm.patchValue({
      canton: '',
      ciudad: ''
    });
    this.cantones = [];
    this.ciudades = [];

    if (!provincia) return;

    this.loadingCantones = true;
    this.apiService.getUbicacionesCantones(provincia).subscribe({
      next: (data) => {
        this.cantones = data.cantones || [];
        this.loadingCantones = false;
      },
      error: () => {
        this.loadingCantones = false;
        this.errorMessage = 'No pudimos cargar los cantones seleccionados.';
      }
    });
  }

  onCantonChange(event: Event): void {
    const canton = (event.target as HTMLSelectElement).value;
    const provincia = this.registerForm.get('provincia')?.value;

    this.registerForm.patchValue({
      ciudad: '',
    });
    this.ciudades = [];

    if (!provincia || !canton) return;

    this.loadingCiudades = true;
    this.apiService.getUbicacionesCiudades(provincia, canton).subscribe({
      next: (data) => {
        this.ciudades = data.ciudades || [];
        this.loadingCiudades = false;
      },
      error: () => {
        this.loadingCiudades = false;
        this.errorMessage = 'No pudimos cargar las ciudades seleccionadas.';
      }
    });
  }

  onSubmit(): void {
    if (this.registerForm.invalid) {
      this.markAllTouched();
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const formValue = { ...this.registerForm.value };
    
    // Limpiar datos antes de enviar
    // Convertir strings vacíos a null para campos opcionales
    if (!formValue.telefono || formValue.telefono.trim() === '') {
      formValue.telefono = null;
    } else {
      // Limpiar formato del teléfono (quitar espacios, guiones, etc.)
      formValue.telefono = formValue.telefono.replace(/[\s-]/g, '').trim();
    }
    
    // Asegurar que password_confirm esté presente (el backend lo necesita)
    if (!formValue.password_confirm) {
      formValue.password_confirm = formValue.password;
    }
    
    // Limpiar valores null para latitud y longitud - solo enviar si tienen valor
    const payload: any = {
      username: formValue.username,
      nombre: formValue.nombre,
      correo: formValue.correo,
      cedula: formValue.cedula,
      telefono: formValue.telefono,
      password: formValue.password,
      password_confirm: formValue.password_confirm,
      provincia: formValue.provincia,
      canton: formValue.canton,
      ciudad: formValue.ciudad,
      rol: 4,  // Siempre comprador para registros públicos
      es_activo: true
    };

    this.apiService.registerComprador(payload).subscribe({
      next: () => {
        this.loading = false;
        this.successMessage = 'Cuenta creada con éxito. En unos segundos te llevaremos al inicio de sesión.';
        setTimeout(() => this.router.navigate(['/login']), 2500);
      },
      error: (error) => {
        this.loading = false;
        // Mostrar errores más detallados del backend
        const errorDetails = error.error;
        if (errorDetails) {
          // Si hay errores de validación del serializer, mostrarlos
          if (typeof errorDetails === 'object') {
            const errorMessages: string[] = [];
            for (const key in errorDetails) {
              if (Array.isArray(errorDetails[key])) {
                errorMessages.push(...errorDetails[key]);
              } else if (typeof errorDetails[key] === 'string') {
                errorMessages.push(errorDetails[key]);
              }
            }
            this.errorMessage = errorMessages.length > 0 
              ? errorMessages.join('. ') 
              : errorDetails.detail || errorDetails.error || errorDetails.message || 'Ocurrió un error al crear la cuenta.';
          } else {
            this.errorMessage = errorDetails.detail || errorDetails.error || errorDetails.message || 'Ocurrió un error al crear la cuenta.';
          }
        } else {
          this.errorMessage = 'Ocurrió un error al crear la cuenta.';
        }
      }
    });
  }

  passwordStrengthValidator(control: AbstractControl): ValidationErrors | null {
    const value = control.value;
    if (!value) return null;

    const errors: any = {};

    // Al menos 8 caracteres
    if (value.length < 8) {
      errors.minLength = true;
    }

    // Al menos una mayúscula
    if (!/[A-Z]/.test(value)) {
      errors.uppercase = true;
    }

    // Al menos una minúscula
    if (!/[a-z]/.test(value)) {
      errors.lowercase = true;
    }

    // Al menos un número
    if (!/[0-9]/.test(value)) {
      errors.number = true;
    }

    // Al menos un carácter especial
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(value)) {
      errors.special = true;
    }

    return Object.keys(errors).length > 0 ? errors : null;
  }

  getControlError(controlName: string): string {
    const control = this.registerForm.get(controlName);
    if (!control || !control.errors || !control.touched) return '';

    if (control.errors['required']) return 'Campo requerido';
    if (control.errors['email']) return 'Correo inválido';
    if (control.errors['minlength']) return 'Ingresa al menos ' + control.errors['minlength'].requiredLength + ' caracteres';
    
    // Errores de contraseña
    if (controlName === 'password') {
      if (control.errors['minLength']) return 'La contraseña debe tener al menos 8 caracteres';
      if (control.errors['uppercase']) return 'Debe contener al menos una letra mayúscula';
      if (control.errors['lowercase']) return 'Debe contener al menos una letra minúscula';
      if (control.errors['number']) return 'Debe contener al menos un número';
      if (control.errors['special']) return 'Debe contener al menos un carácter especial (!@#$%^&*...)';
    }
    
    if (controlName === 'password_confirm' && this.registerForm.errors?.['passwordMismatch']) return 'Las contraseñas no coinciden';
    return '';
  }

  private markAllTouched(): void {
    Object.keys(this.registerForm.controls).forEach((key) => {
      this.registerForm.get(key)?.markAsTouched();
    });
  }

  private passwordsMatchValidator(group: AbstractControl): ValidationErrors | null {
    const password = group.get('password')?.value;
    const confirm = group.get('password_confirm')?.value;
    if (!password || !confirm) return null;
    return password === confirm ? null : { passwordMismatch: true };
  }
}


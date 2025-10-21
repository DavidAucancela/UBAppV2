import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { LoginRequest } from '../../../models/usuario';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  loginForm: FormGroup;
  loading = false;
  hidePassword = true;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.loading = true;
      this.errorMessage = '';
      const credentials: LoginRequest = this.loginForm.value;

      this.authService.login(credentials).subscribe({
        next: (response) => {
          this.loading = false;
          console.log('Login exitoso:', response);
          
          // Redirigir según el rol del usuario
          const user = response.user;
          if (!user || !user.rol) {
            // Si no hay información del rol, ir a inicio por defecto
            this.router.navigate(['/inicio']);
            return;
          }

          // Roles: 1=Admin, 2=Gerente, 3=Digitador, 4=Comprador
          switch (user.rol) {
            case 1: // Admin
              this.router.navigate(['/inicio']);
              break;
            case 2: // Gerente
              this.router.navigate(['/dashboard']); // Dashboard gerencial
              break;
            case 3: // Digitador
              this.router.navigate(['/envios']); // Gestión de envíos
              break;
            case 4: // Comprador
              this.router.navigate(['/dashboard-usuario']); // Dashboard personal
              break;
            default:
              this.router.navigate(['/inicio']);
          }
        },
        error: (error) => {
          this.loading = false;
          console.error('Error de login:', error);
          
          if (error.status === 401) {
            this.errorMessage = 'Credenciales incorrectas. Verifica tu usuario y contraseña.';
          } else if (error.status === 429) {
            this.errorMessage = error.error?.error || 'Demasiados intentos fallidos. Intenta más tarde.';
          } else if (error.status === 0) {
            this.errorMessage = 'Error de conexión. Verifica que el servidor esté funcionando.';
          } else {
            this.errorMessage = error.error?.error || 'Error en el inicio de sesión. Intenta nuevamente.';
          }
        }
      });
    } else {
      this.markFormGroupTouched();
    }
  }

  getErrorMessage(field: string): string {
    const control = this.loginForm.get(field);
    if (control?.hasError('required')) {
      return 'Este campo es requerido';
    }
    if (field === 'password' && control?.hasError('minlength')) {
      return 'La contraseña debe tener al menos 6 caracteres';
    }
    return '';
  }

  private markFormGroupTouched(): void {
    Object.keys(this.loginForm.controls).forEach(key => {
      const control = this.loginForm.get(key);
      control?.markAsTouched();
    });
  }
}

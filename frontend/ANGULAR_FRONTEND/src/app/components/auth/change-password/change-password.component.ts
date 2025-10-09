import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { UsuarioService, PasswordChangeRequest } from '../../../services/usuario.service';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterModule],
  templateUrl: './change-password.component.html',
  styleUrl: './change-password.component.css'
})
export class ChangePasswordComponent implements OnInit {
  passwordForm: FormGroup;
  submitting = false;
  errorMessage = '';
  successMessage = '';
  mustChange = false;
  
  hideCurrentPassword = true;
  hideNewPassword = true;
  hideConfirmPassword = true;
  
  // Validación de contraseña
  passwordStrength = {
    hasMinLength: false,
    hasUpperCase: false,
    hasLowerCase: false,
    hasNumber: false,
    hasSpecial: false,
    isValid: false
  };

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private usuarioService: UsuarioService,
    private authService: AuthService
  ) {
    this.passwordForm = this.fb.group({
      password_actual: ['', [Validators.required]],
      password_nuevo: ['', [Validators.required, Validators.minLength(8)]],
      password_confirm: ['', [Validators.required]]
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    // Verificar si el usuario debe cambiar la contraseña
    const user = this.authService.getCurrentUser();
    if (user?.debe_cambiar_password) {
      this.mustChange = true;
    }
    
    // Monitorear cambios en la nueva contraseña
    this.passwordForm.get('password_nuevo')?.valueChanges.subscribe(password => {
      this.checkPasswordStrength(password);
    });
  }

  onSubmit(): void {
    if (this.passwordForm.valid && this.passwordStrength.isValid) {
      this.submitting = true;
      this.errorMessage = '';
      this.successMessage = '';
      
      const passwords: PasswordChangeRequest = this.passwordForm.value;
      
      this.usuarioService.cambiarPassword(passwords).subscribe({
        next: (response) => {
          this.successMessage = response.message || 'Contraseña actualizada correctamente';
          this.passwordForm.reset();
          this.submitting = false;
          
          // Si era un cambio obligatorio, actualizar el usuario y redirigir
          if (this.mustChange) {
            const user = this.authService.getCurrentUser();
            if (user) {
              user.debe_cambiar_password = false;
              // Actualizar usuario en localStorage
              if (typeof window !== 'undefined' && window.localStorage) {
                localStorage.setItem('currentUser', JSON.stringify(user));
              }
            }
            
            // Redirigir al dashboard después de 2 segundos
            setTimeout(() => {
              this.router.navigate(['/dashboard']);
            }, 2000);
          } else {
            // Si es cambio voluntario, mostrar mensaje de éxito
            setTimeout(() => {
              this.router.navigate(['/usuarios']);
            }, 2000);
          }
        },
        error: (error) => {
          this.errorMessage = error.error?.error || 'Error al cambiar la contraseña';
          this.submitting = false;
        }
      });
    } else {
      this.markFormGroupTouched();
    }
  }

  checkPasswordStrength(password: string): void {
    if (!password) {
      this.passwordStrength = {
        hasMinLength: false,
        hasUpperCase: false,
        hasLowerCase: false,
        hasNumber: false,
        hasSpecial: false,
        isValid: false
      };
      return;
    }
    
    this.passwordStrength = {
      hasMinLength: password.length >= 8,
      hasUpperCase: /[A-Z]/.test(password),
      hasLowerCase: /[a-z]/.test(password),
      hasNumber: /\d/.test(password),
      hasSpecial: /[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]/.test(password),
      isValid: false
    };
    
    this.passwordStrength.isValid = 
      this.passwordStrength.hasMinLength &&
      this.passwordStrength.hasUpperCase &&
      this.passwordStrength.hasLowerCase &&
      this.passwordStrength.hasNumber &&
      this.passwordStrength.hasSpecial;
    
    // Verificar que no sea una contraseña común
    const commonPasswords = [
      'password', '12345678', 'qwerty', 'abc123', 'password123',
      'admin123', 'letmein', 'welcome', 'monkey', '1234567890'
    ];
    
    if (commonPasswords.includes(password.toLowerCase())) {
      this.passwordStrength.isValid = false;
      this.errorMessage = 'Esta contraseña es muy común y no es segura';
    }
  }

  private passwordMatchValidator(formGroup: FormGroup): {[key: string]: boolean} | null {
    const password = formGroup.get('password_nuevo');
    const confirmPassword = formGroup.get('password_confirm');
    
    if (password?.value !== confirmPassword?.value) {
      confirmPassword?.setErrors({ passwordMismatch: true });
      return { passwordMismatch: true };
    } else {
      // Limpiar error si las contraseñas coinciden
      if (confirmPassword?.hasError('passwordMismatch')) {
        confirmPassword?.setErrors(null);
      }
    }
    
    return null;
  }

  private markFormGroupTouched(): void {
    Object.keys(this.passwordForm.controls).forEach(key => {
      const control = this.passwordForm.get(key);
      control?.markAsTouched();
    });
  }

  skipForNow(): void {
    if (!this.mustChange) {
      this.router.navigate(['/dashboard']);
    }
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}

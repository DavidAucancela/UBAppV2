import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { UsuarioService } from '../../../services/usuario.service';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterModule],
  templateUrl: './reset-password.component.html',
  styleUrl: './reset-password.component.css'
})
export class ResetPasswordComponent implements OnInit {
  step: 'request' | 'reset' | 'success' = 'request';
  requestForm: FormGroup;
  resetForm: FormGroup;
  submitting = false;
  errorMessage = '';
  successMessage = '';
  token = '';
  userId = 0;
  hidePassword = true;
  hidePasswordConfirm = true;
  
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
    private route: ActivatedRoute,
    private router: Router,
    private usuarioService: UsuarioService
  ) {
    this.requestForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]]
    });
    
    this.resetForm = this.fb.group({
      new_password: ['', [Validators.required, Validators.minLength(8)]],
      confirm_password: ['', [Validators.required]]
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    // Verificar si hay token en la URL
    this.route.queryParams.subscribe(params => {
      const token = params['token'];
      const userId = params['user'];
      
      if (token && userId) {
        this.token = token;
        this.userId = parseInt(userId);
        this.step = 'reset';
      }
    });
    
    // Monitorear cambios en la contraseña
    this.resetForm.get('new_password')?.valueChanges.subscribe(password => {
      this.checkPasswordStrength(password);
    });
  }

  requestReset(): void {
    if (this.requestForm.valid) {
      this.submitting = true;
      this.errorMessage = '';
      
      this.usuarioService.requestPasswordReset(this.requestForm.value).subscribe({
        next: (response) => {
          this.successMessage = response.message || 'Si el correo existe, recibirás instrucciones para restablecer tu contraseña.';
          this.requestForm.reset();
          this.submitting = false;
        },
        error: (error) => {
          this.errorMessage = 'Error al procesar la solicitud. Por favor intenta de nuevo.';
          this.submitting = false;
        }
      });
    }
  }

  resetPassword(): void {
    if (this.resetForm.valid && this.passwordStrength.isValid) {
      this.submitting = true;
      this.errorMessage = '';
      
      const data = {
        token: this.token,
        user_id: this.userId,
        ...this.resetForm.value
      };
      
      this.usuarioService.confirmPasswordReset(data).subscribe({
        next: (response) => {
          this.step = 'success';
          this.submitting = false;
          
          // Redirigir al login después de 3 segundos
          setTimeout(() => {
            this.router.navigate(['/login']);
          }, 3000);
        },
        error: (error) => {
          this.errorMessage = error.error?.error || 'Error al restablecer la contraseña. El enlace puede haber expirado.';
          this.submitting = false;
        }
      });
    }
  }

  checkPasswordStrength(password: string): void {
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
  }

  private passwordMatchValidator(formGroup: FormGroup): {[key: string]: boolean} | null {
    const password = formGroup.get('new_password');
    const confirmPassword = formGroup.get('confirm_password');
    
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
}













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
  passwordForm!: FormGroup;
  
  showPasswordForm = false;
  showCurrentPassword = false;
  showNewPassword = false;
  showConfirmPassword = false;
  
  loading = false;
  profileSuccess = false;
  passwordSuccess = false;
  profileError: string | null = null;
  passwordError: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.initForms();
    this.loadUserData();
  }

  initForms(): void {
    // Formulario de perfil
    this.profileForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3)]],
      correo: ['', [Validators.required, Validators.email]],
      telefono: ['', [Validators.pattern(/^[0-9]{10}$/)]],
      direccion: ['']
    });

    // Formulario de contraseña
    this.passwordForm = this.fb.group({
      currentPassword: ['', Validators.required],
      newPassword: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
  }

  passwordMatchValidator(g: FormGroup) {
    const newPassword = g.get('newPassword')?.value;
    const confirmPassword = g.get('confirmPassword')?.value;
    return newPassword === confirmPassword ? null : { mismatch: true };
  }

  loadUserData(): void {
    if (this.currentUser) {
      this.profileForm.patchValue({
        nombre: this.currentUser.nombre,
        correo: this.currentUser.correo,
        telefono: this.currentUser.telefono || '',
        direccion: this.currentUser.direccion || ''
      });
    }
  }

  onSubmitProfile(): void {
    if (this.profileForm.invalid) {
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

    this.apiService.updateUsuario(userId, this.profileForm.value).subscribe({
      next: (response) => {
        this.profileSuccess = true;
        this.loading = false;
        
        // Actualizar el usuario en el servicio de autenticación
        const updatedUser = { ...this.currentUser, ...this.profileForm.value };
        this.authService.updateCurrentUser(updatedUser as Usuario);
        
        setTimeout(() => {
          this.profileSuccess = false;
        }, 5000);
      },
      error: (error) => {
        this.profileError = error.error?.message || 'Error al actualizar el perfil';
        this.loading = false;
      }
    });
  }

  onSubmitPassword(): void {
    if (this.passwordForm.invalid) {
      Object.keys(this.passwordForm.controls).forEach(key => {
        this.passwordForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.loading = true;
    this.passwordSuccess = false;
    this.passwordError = null;

    const userId = this.currentUser?.id;
    if (!userId) {
      this.passwordError = 'Error: Usuario no identificado';
      this.loading = false;
      return;
    }

    const passwordData = {
      current_password: this.passwordForm.value.currentPassword,
      new_password: this.passwordForm.value.newPassword
    };

    this.apiService.changePassword(userId, passwordData).subscribe({
      next: () => {
        this.passwordSuccess = true;
        this.loading = false;
        this.passwordForm.reset();
        
        setTimeout(() => {
          this.passwordSuccess = false;
          this.showPasswordForm = false;
        }, 3000);
      },
      error: (error) => {
        this.passwordError = error.error?.message || 'Error al cambiar la contraseña. Verifica tu contraseña actual.';
        this.loading = false;
      }
    });
  }

  togglePasswordForm(): void {
    this.showPasswordForm = !this.showPasswordForm;
    if (!this.showPasswordForm) {
      this.passwordForm.reset();
      this.passwordError = null;
      this.passwordSuccess = false;
    }
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
    
    return 'Campo inválido';
  }
}

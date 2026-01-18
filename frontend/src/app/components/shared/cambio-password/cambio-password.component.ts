import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-cambio-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './cambio-password.component.html',
  styleUrl: './cambio-password.component.css'
})
export class CambioPasswordComponent implements OnInit {
  @Input() showCurrentPassword: boolean = false; // Si es true, muestra campo de contraseña actual
  @Input() requireCurrentPassword: boolean = true; // Si requiere contraseña actual
  @Input() label: string = 'Contraseña';
  @Input() confirmLabel: string = 'Confirmar Contraseña';
  @Input() currentPasswordLabel: string = 'Contraseña Actual';
  @Input() newPasswordLabel: string = 'Nueva Contraseña';
  @Input() minLength: number = 8;
  @Input() showPasswordRequirements: boolean = true;
  @Input() formGroup?: FormGroup; // Opcional: si se pasa un FormGroup externo
  
  @Output() passwordChange = new EventEmitter<any>();
  
  passwordForm: FormGroup;
  showCurrentPasswordField = false;
  showNewPasswordField = false;
  showConfirmPasswordField = false;

  constructor(private fb: FormBuilder) {
    this.passwordForm = this.fb.group({
      currentPassword: [''],
      newPassword: ['', [Validators.required, Validators.minLength(this.minLength)]],
      confirmPassword: ['', [Validators.required]]
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    if (this.showCurrentPassword && this.requireCurrentPassword) {
      this.passwordForm.get('currentPassword')?.setValidators([Validators.required]);
      this.passwordForm.get('currentPassword')?.updateValueAndValidity();
    }
    
    // Emitir cambios al formulario padre
    this.passwordForm.valueChanges.subscribe(value => {
      this.passwordChange.emit(value);
    });
  }

  passwordMatchValidator(form: FormGroup) {
    const newPassword = form.get('newPassword')?.value;
    const confirmPassword = form.get('confirmPassword')?.value;
    
    if (newPassword && confirmPassword && newPassword !== confirmPassword) {
      form.get('confirmPassword')?.setErrors({ passwordMismatch: true });
      return { passwordMismatch: true };
    }
    
    return null;
  }

  togglePasswordVisibility(field: 'current' | 'new' | 'confirm'): void {
    switch(field) {
      case 'current':
        this.showCurrentPasswordField = !this.showCurrentPasswordField;
        break;
      case 'new':
        this.showNewPasswordField = !this.showNewPasswordField;
        break;
      case 'confirm':
        this.showConfirmPasswordField = !this.showConfirmPasswordField;
        break;
    }
  }

  getPasswordError(field: string): string {
    const control = this.passwordForm.get(field);
    if (!control || !control.errors || !control.touched) return '';

    if (control.errors['required']) return 'Este campo es requerido';
    if (control.errors['minlength']) {
      return `Mínimo ${control.errors['minlength'].requiredLength} caracteres`;
    }
    if (control.errors['passwordMismatch']) return 'Las contraseñas no coinciden';
    
    return '';
  }

  getFormError(): string {
    if (this.passwordForm.errors?.['passwordMismatch']) {
      return 'Las contraseñas no coinciden';
    }
    return '';
  }

  get isValid(): boolean {
    return this.passwordForm.valid;
  }

  get value(): any {
    return this.passwordForm.value;
  }

  reset(): void {
    this.passwordForm.reset();
    if (this.showCurrentPassword && this.requireCurrentPassword) {
      this.passwordForm.get('currentPassword')?.setValidators([Validators.required]);
    }
  }

  patchValue(value: any): void {
    this.passwordForm.patchValue(value, { emitEvent: false });
  }
}


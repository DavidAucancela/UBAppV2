import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { UsuarioService } from '../../../services/usuario.service';

@Component({
  selector: 'app-verify-email',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './verify-email.component.html',
  styleUrl: './verify-email.component.css'
})
export class VerifyEmailComponent implements OnInit {
  verifying = false;
  verified = false;
  error = false;
  errorMessage = '';
  email = '';
  resending = false;
  resent = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private usuarioService: UsuarioService
  ) {}

  ngOnInit(): void {
    // Obtener parámetros de la URL
    this.route.queryParams.subscribe(params => {
      const token = params['token'];
      const userId = params['user'];
      
      if (token && userId) {
        this.verifyEmail(token, parseInt(userId));
      }
    });
  }

  verifyEmail(token: string, userId: number): void {
    this.verifying = true;
    this.error = false;
    
    this.usuarioService.verifyEmail({ token, user_id: userId }).subscribe({
      next: (response) => {
        this.verified = true;
        this.verifying = false;
        
        // Redirigir al login después de 3 segundos
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 3000);
      },
      error: (error) => {
        this.error = true;
        this.verifying = false;
        this.errorMessage = error.error?.error || 'Error al verificar el correo electrónico';
      }
    });
  }

  resendVerification(): void {
    if (!this.email) {
      this.errorMessage = 'Por favor ingresa tu correo electrónico';
      return;
    }

    this.resending = true;
    this.error = false;
    this.resent = false;
    
    this.usuarioService.resendVerification(this.email).subscribe({
      next: (response) => {
        this.resent = true;
        this.resending = false;
        this.email = '';
      },
      error: (error) => {
        this.error = true;
        this.resending = false;
        this.errorMessage = 'Error al reenviar el correo de verificación';
      }
    });
  }
}













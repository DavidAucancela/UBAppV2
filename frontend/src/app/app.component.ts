import { Component, OnInit, OnDestroy, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { AuthService } from './services/auth.service';
import { Usuario, ROLES_LABELS } from './models/usuario';
import { Subscription } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { EMPTY } from 'rxjs';
import { NavbarComponent } from './components/navbar/navbar.component';
import { FooterComponent } from './components/footer/footer.component';
import { environment } from './environments/environment';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, NavbarComponent, FooterComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'UBApp';
  loading = false;
  
  private userSubscription: Subscription | null = null;

  constructor(
    public authService: AuthService,
    private router: Router,
    private http: HttpClient,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    // Cargar tema guardado (solo en el navegador)
    if (isPlatformBrowser(this.platformId)) {
      const darkMode = localStorage.getItem('darkMode');
      if (darkMode === 'true') {
        document.body.classList.add('dark-mode');
      }

      // Despertar el backend al iniciar la app (evita errores de cold start en Render free tier)
      this.wakeupBackend();

      // Verificar si hay sesión activa y redirigir automáticamente
      this.checkActiveSession();
    }
  }

  /**
   * Ping al health check del backend para despertarlo si está inactivo (Render free tier).
   * Se ejecuta en silencio al cargar la app, antes de que el usuario intente hacer login.
   */
  private wakeupBackend(): void {
    this.http.get(`${environment.apiUrl}/health/`, { responseType: 'json' })
      .pipe(catchError(() => EMPTY))
      .subscribe();
  }

  private checkActiveSession(): void {
    const currentUser = this.authService.getCurrentUser();
    const currentRoute = this.router.url;
    
    // Si hay sesión activa y está en páginas públicas, redirigir al dashboard correspondiente
    if (currentUser && (currentRoute === '/' || currentRoute === '/login' || currentRoute === '/informacion')) {
      this.redirectToUserDashboard(currentUser);
    }
  }

  private redirectToUserDashboard(user: Usuario): void {
    // Redirigir según el rol del usuario
    switch (user.rol) {
      case 1: // Admin
        this.router.navigate(['/inicio']);
        break;
      case 2: // Gerente
        this.router.navigate(['/inicio']);
        break;
      case 3: // Digitador
        this.router.navigate(['/envios']);
        break;
      case 4: // Comprador
        this.router.navigate(['/dashboard-usuario']);
        break;
      default:
        this.router.navigate(['/inicio']);
    }
  }

  ngOnDestroy(): void {
    if (this.userSubscription) {
      this.userSubscription.unsubscribe();
    }
  }
}

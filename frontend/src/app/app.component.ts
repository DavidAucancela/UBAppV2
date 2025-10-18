import { Component, OnInit, OnDestroy, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { AuthService } from './services/auth.service';
import { Usuario, ROLES_LABELS } from './models/usuario';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'UBApp';
  currentUser: Usuario | null = null;
  showUserMenu = false;
  loading = false;
  ROLES_LABELS = ROLES_LABELS;
  
  private userSubscription: Subscription | null = null;

  constructor(
    public authService: AuthService,
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    // Suscribirse a los cambios del usuario actual
    this.userSubscription = this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });
    
    // Cargar tema guardado (solo en el navegador)
    if (isPlatformBrowser(this.platformId)) {
      const darkMode = localStorage.getItem('darkMode');
      if (darkMode === 'true') {
        document.body.classList.add('dark-mode');
      }
    }
  }

  ngOnDestroy(): void {
    if (this.userSubscription) {
      this.userSubscription.unsubscribe();
    }
  }

  toggleUserMenu(): void {
    this.showUserMenu = !this.showUserMenu;
  }

  closeUserMenu(): void {
    this.showUserMenu = false;
  }

  toggleTheme(): void {
    // Implementar lógica de cambio de tema (solo en el navegador)
    if (isPlatformBrowser(this.platformId)) {
      const body = document.body;
      body.classList.toggle('dark-mode');
      const isDarkMode = body.classList.contains('dark-mode');
      localStorage.setItem('darkMode', isDarkMode ? 'true' : 'false');
    }
  }

  logout(): void {
    this.authService.logout();
    this.showUserMenu = false;
    this.router.navigate(['/login']);
  }

  // Cerrar el menú de usuario cuando se hace clic fuera
  onDocumentClick(event: Event): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.user-menu')) {
      this.showUserMenu = false;
    }
  }

  // Helper method for template
  getRoleLabel(rol: number | undefined): string {
    if (!rol) return 'Usuario';
    return ROLES_LABELS[rol as keyof typeof ROLES_LABELS] || 'Usuario';
  }
}

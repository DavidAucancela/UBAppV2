import { Component, OnInit, OnDestroy, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { RouterLink, RouterLinkActive, Router, NavigationEnd } from '@angular/router';
import { trigger, state, style, transition, animate, stagger, query, animateChild } from '@angular/animations';
import { AuthService } from '../../services/auth.service';
import { NotificacionService } from '../../services/notificacion.service';
import { Usuario, ROLES_LABELS, Roles } from '../../models/usuario';
import { Notificacion, NotificacionCount } from '../../models/notificacion';
import { Subscription, combineLatest, filter } from 'rxjs';
import { EnvioDetailModalComponent } from '../shared/envio-detail-modal/envio-detail-modal.component';

interface NavItem {
  label: string;
  icon: string;
  route: string;
  roles: Roles[];
  order: number;
  subItems?: NavSubItem[];
}

interface NavSubItem {
  label: string;
  icon: string;
  route: string;
}

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, EnvioDetailModalComponent],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css',
  animations: [
    // Animación de la barra completa desde arriba
    trigger('navbarSlide', [
      state('hidden', style({
        transform: 'translateY(-100%)',
        opacity: 0
      })),
      state('visible', style({
        transform: 'translateY(0)',
        opacity: 1
      })),
      transition('hidden => visible', [
        animate('600ms cubic-bezier(0.35, 0, 0.25, 1)')
      ])
    ]),
    
    // Animación de items individuales con efecto escalonado
    trigger('itemAnimation', [
      transition(':enter', [
        style({
          opacity: 0,
          transform: 'translateY(-20px) scale(0.9)'
        }),
        animate('400ms {{delay}}ms cubic-bezier(0.35, 0, 0.25, 1)', style({
          opacity: 1,
          transform: 'translateY(0) scale(1)'
        }))
      ], { params: { delay: 0 } }),
      transition(':leave', [
        animate('300ms ease-out', style({
          opacity: 0,
          transform: 'translateY(-10px) scale(0.95)'
        }))
      ])
    ]),
    
    // Animación del logo con efecto de pulso
    trigger('logoAnimation', [
      state('hidden', style({
        opacity: 0,
        transform: 'scale(0.8) rotate(-10deg)'
      })),
      state('visible', style({
        opacity: 1,
        transform: 'scale(1) rotate(0deg)'
      })),
      transition('hidden => visible', [
        animate('500ms cubic-bezier(0.68, -0.55, 0.265, 1.55)')
      ])
    ]),
    
    // Animación de las acciones del header
    trigger('actionsAnimation', [
      state('hidden', style({
        opacity: 0,
        transform: 'translateX(50px)'
      })),
      state('visible', style({
        opacity: 1,
        transform: 'translateX(0)'
      })),
      transition('hidden => visible', [
        animate('500ms 400ms cubic-bezier(0.35, 0, 0.25, 1)')
      ])
    ]),
    
  ]
})
export class NavbarComponent implements OnInit, OnDestroy {
  currentUser: Usuario | null = null;
  showUserMenu = false;
  navbarState = 'hidden';
  logoState = 'hidden';
  actionsState = 'hidden';
  ROLES_LABELS = ROLES_LABELS;
  shouldHideNavbar = false;
  isDarkMode = false;
  private logoPressTimeoutId: ReturnType<typeof setTimeout> | null = null;
  private logoPressIntervalId: ReturnType<typeof setInterval> | null = null;
  private logoClickSuppressTimeoutId: ReturnType<typeof setTimeout> | null = null;
  private isLogoPressActive = false;
  private logoHoldActivated = false;
  
  // Items de navegación visibles según rol
  visibleNavItems: NavItem[] = [];
  isLoadingNav = false;
  expandedItems: Set<string> = new Set();
  
  private userSubscription: Subscription | null = null;
  private notificacionSubscription: Subscription | null = null;
  
  // Notificaciones
  notificaciones: Notificacion[] = [];
  notificacionCount: NotificacionCount = { total: 0, no_leidas: 0 };
  showNotificacionesDropdown = false;
  
  // Modal de detalles de envío
  showEnvioDetailModal = false;
  selectedEnvioId: number | null = null;
  
  // Definición de todos los items de navegación organizados por categorías
  private allNavItems: NavItem[] = [
    {
      label: 'Mis Envios',
      icon: 'fas fa-truck-loading',
      route: '/mis-envios',
      roles: [Roles.COMPRADOR],
      order: 1
    },
    // ========== ENVÍOS ==========
    {
      label: 'Envíos',
      icon: 'fas fa-truck-loading',
      route: '/envios',
      roles: [Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR],
      order: 1,
      subItems: [
        { label: 'Envíos', icon: 'fas fa-list', route: '/envios' },
        { label: 'Archivos', icon: 'fas fa-upload', route: '/importacion-excel' },
        { label: 'Productos', icon: 'fas fa-box', route: '/productos' },
        { label: 'Tarifas', icon: 'fas fa-dollar-sign', route: '/tarifas' },
      ]
    },
    // ========== BÚSQUEDAS ==========
    {
      label: 'Búsqueda',
      icon: 'fas fa-search',
      route: '/busqueda-envios',
      roles: [Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR],
      order: 2,
      subItems: [
        { label: 'Búsqueda tradicional', icon: 'fas fa-search', route: '/busqueda-envios' },
        { label: 'Búsqueda semántica', icon: 'fas fa-brain', route: '/busqueda-semantica' },
      ]
    },

    // ========== Otros ==========
    {
      label: 'Otros',
      icon: 'fas fa-users',
      route: '/usuarios',
      roles: [Roles.ADMIN, Roles.GERENTE],
      order: 4,
      subItems: [
        { label: 'Mapa', icon: 'fas fa-map-marked-alt', route: '/mapa-compradores' },
        { label: 'Usuarios', icon: 'fas fa-users', route: '/usuarios' },
        { label: 'Actividades', icon: 'fas fa-chart-line', route: '/actividades' },
      ]
    }
  ];

  constructor(
    public authService: AuthService,
    private notificacionService: NotificacionService,
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    // La navbar siempre está visible y fija
    this.navbarState = 'visible';
    this.logoState = 'visible';
    this.actionsState = 'visible';

    this.router.events
    .pipe(filter((event: any) => event instanceof NavigationEnd))
    .subscribe(() => {
      this.checkRouteAndToggleNavbar();
      // Cerrar todos los submenús cuando cambia la ruta
      this.expandedItems.clear();
    });
    
    // Verificar si está en modo oscuro
    if (isPlatformBrowser(this.platformId)) {
      this.isDarkMode = document.body.classList.contains('dark-mode');
      
      // Agregar listener global para cerrar dropdowns al hacer clic afuera
      document.addEventListener('click', this.handleGlobalClick.bind(this));
    }
    
    // Suscribirse a los cambios del usuario actual
    this.userSubscription = this.authService.currentUser$.subscribe((user: Usuario | null) => {
      if (user && user !== this.currentUser) {
        // Usuario acaba de iniciar sesión o cambió
        this.currentUser = user;
        this.animateNavbarEntry();
        this.setupNotificaciones();
      } else if (!user && this.currentUser) {
        // Usuario cerró sesión
        this.currentUser = null;
        this.resetNavItems();
        this.clearNotificaciones();
      } else {
        this.currentUser = user;
        if (user) {
          // Usuario ya estaba logueado (recarga de página)
          this.loadNavItemsByRole();
          this.setupNotificaciones();
        }
      }
    });
  }
  /**
   * Verificar la ruta actual y ocultar/mostrar la navbar
   */
  private checkRouteAndToggleNavbar(): void {
    const currentRoute = this.router.url;
    this.shouldHideNavbar = currentRoute === '/login' || currentRoute === '/register';
    
    if (this.shouldHideNavbar) {
      this.navbarState = 'hidden';
      this.logoState = 'hidden';
      this.actionsState = 'hidden';
    } else {
      this.navbarState = 'visible';
      this.logoState = 'visible';
      this.actionsState = 'visible';
    }
  }
  ngOnDestroy(): void {
    if (this.userSubscription) {
      this.userSubscription.unsubscribe();
    }
    if (this.notificacionSubscription) {
      this.notificacionSubscription.unsubscribe();
    }
    this.clearLogoPressTimers();
    this.clearLogoClickSuppressionTimeout();
    
    // Remover listener global
    if (isPlatformBrowser(this.platformId)) {
      document.removeEventListener('click', this.handleGlobalClick.bind(this));
    }
  }

  /**
   * Manejar clicks globales para cerrar dropdowns
   */
  handleGlobalClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    
    // Verificar si el click es dentro del navbar completo
    const navbarElement = target.closest('header.animated-header');
    const isInsideNavbar = !!navbarElement;
    
    // Verificar si el click es dentro de un submenú desplegado
    const dropdownMenu = target.closest('.dropdown-menu');
    const isInsideDropdown = !!dropdownMenu;
    
    // Cerrar menú de usuario si el click es afuera
    if (this.showUserMenu) {
      const userMenu = target.closest('.user-menu');
      if (!userMenu) {
        this.showUserMenu = false;
      }
    }
    
    // Cerrar menú de notificaciones si el click es afuera
    if (this.showNotificacionesDropdown) {
      const notificationWrapper = target.closest('.notification-wrapper');
      if (!notificationWrapper) {
        this.showNotificacionesDropdown = false;
      }
    }
    
    // Cerrar submenús expandidos
    if (this.expandedItems.size > 0) {
      const navItem = target.closest('.nav-item');
      const navLink = target.closest('.nav-link');
      
      // Si el click es completamente fuera del navbar, cerrar todos los submenús
      if (!isInsideNavbar) {
        this.expandedItems.clear();
      } 
      // Si el click es dentro del navbar pero fuera de cualquier submenú desplegado
      else if (!isInsideDropdown) {
        // Si el click es en un nav-link que NO tiene subitems, cerrar todos los submenús
        if (navLink && navLink instanceof HTMLElement && !navLink.classList.contains('has-submenu')) {
          this.expandedItems.clear();
        }
        // Si el click es en otro nav-item diferente al expandido
        else if (navItem && navItem instanceof HTMLElement) {
          const clickedItemLabel = this.getNavItemLabelFromElement(navItem);
          if (clickedItemLabel) {
            // Si el item clickeado no está expandido, cerrar todos
            if (!this.isExpanded(clickedItemLabel)) {
              this.expandedItems.clear();
            }
          } else {
            // No se pudo determinar el label, cerrar por seguridad
            this.expandedItems.clear();
          }
        }
        // Si el click es en cualquier otra parte del navbar (no en nav-item), cerrar submenús
        else {
          this.expandedItems.clear();
        }
      }
    }
  }
  
  /**
   * Obtener el label del nav-item desde el elemento DOM
   */
  private getNavItemLabelFromElement(element: HTMLElement): string | null {
    const navLink = element.querySelector('.nav-link');
    if (navLink) {
      const span = navLink.querySelector('span');
      if (span) {
        return span.textContent?.trim() || null;
      }
    }
    return null;
  }

  /**
   * Configurar suscripciones de notificaciones para compradores
   */
  private setupNotificaciones(): void {
    if (!this.currentUser || this.currentUser.rol !== Roles.COMPRADOR) {
      this.clearNotificaciones();
      return;
    }

    // Suscribirse a cambios de notificaciones
    this.notificacionSubscription = combineLatest([
      this.notificacionService.notificaciones$,
      this.notificacionService.count$
    ]).subscribe(([notificaciones, count]: [Notificacion[], NotificacionCount]) => {
      this.notificaciones = notificaciones;
      this.notificacionCount = count;
    });

    // Cargar notificaciones iniciales
    this.notificacionService.obtenerNotificaciones().subscribe();
  }

  /**
   * Limpiar notificaciones cuando el usuario cierra sesión
   */
  private clearNotificaciones(): void {
    this.notificaciones = [];
    this.notificacionCount = { total: 0, no_leidas: 0 };
    this.showNotificacionesDropdown = false;
    if (this.notificacionSubscription) {
      this.notificacionSubscription.unsubscribe();
      this.notificacionSubscription = null;
    }
  }

  /**
   * Toggle del dropdown de notificaciones
   */
  toggleNotificacionesDropdown(): void {
    this.showNotificacionesDropdown = !this.showNotificacionesDropdown;
  }

  /**
   * Cerrar dropdown de notificaciones
   */
  closeNotificacionesDropdown(): void {
    this.showNotificacionesDropdown = false;
  }

  /**
   * Marcar notificación como leída
   */
  marcarNotificacionLeida(notificacion: Notificacion, event: Event): void {
    event.stopPropagation();
    
    // Marcar como leída si no lo está
    if (!notificacion.leida) {
      this.notificacionService.marcarComoLeida(notificacion.id).subscribe();
    }
    
    // Si tiene envio_id en metadata, mostrar detalles del envío
    if (notificacion.metadata?.envio_id) {
      this.selectedEnvioId = notificacion.metadata.envio_id;
      this.showEnvioDetailModal = true;
      this.closeNotificacionesDropdown();
    } else if (notificacion.enlace) {
      // Si tiene enlace, navegar
      this.router.navigate([notificacion.enlace]);
      this.closeNotificacionesDropdown();
    }
  }
  
  /**
   * Cerrar modal de detalles de envío
   */
  closeEnvioDetailModal(): void {
    this.showEnvioDetailModal = false;
    this.selectedEnvioId = null;
  }

  /**
   * Marcar todas las notificaciones como leídas
   */
  marcarTodasLeidas(): void {
    this.notificacionService.marcarTodasComoLeidas().subscribe();
  }

  /**
   * Verificar si el usuario es comprador
   */
  isComprador(): boolean {
    return this.currentUser?.rol === Roles.COMPRADOR;
  }

  private animateNavbarEntry(): void {
    // Animar la entrada del navbar
    setTimeout(() => {
      this.logoState = 'visible';
    }, 100);
    
    setTimeout(() => {
      this.navbarState = 'visible';
    }, 200);
    
    setTimeout(() => {
      this.actionsState = 'visible';
    }, 300);
    
    // Cargar items progresivamente
    setTimeout(() => {
      this.loadNavItemsProgressively();
    }, 600);
  }

  private loadNavItemsProgressively(): void {
    if (!this.currentUser) return;
    
    this.isLoadingNav = true;
    const userRole = this.currentUser.rol;
    
    // Filtrar items según el rol con mejor filtrado
    const itemsForRole = this.allNavItems
      .filter(item => {
        if (!item.roles.includes(userRole)) {
          return false;
        }
        // Filtrar subitems también si es necesario
        if (item.subItems) {
          // Por ahora todos los subitems son accesibles si el item principal lo es
        }
        return true;
      })
      .sort((a, b) => a.order - b.order);
    
    // Agregar items uno por uno con delay
    this.visibleNavItems = [];
    itemsForRole.forEach((item, index) => {
      setTimeout(() => {
        this.visibleNavItems.push(item);
        if (index === itemsForRole.length - 1) {
          this.isLoadingNav = false;
        }
      }, index * 150); // 150ms entre cada item
    });
  }

  private loadNavItemsByRole(): void {
    if (!this.currentUser) {
      this.visibleNavItems = [];
      return;
    }
    
    const userRole = this.currentUser.rol;
    // Filtrar items según el rol y también filtrar subitems si tienen restricciones
    this.visibleNavItems = this.allNavItems
      .filter(item => {
        // Verificar si el rol tiene acceso al item principal
        if (!item.roles.includes(userRole)) {
          return false;
        }
        
        // Filtrar subitems también por rol (si en el futuro tienen roles específicos)
        if (item.subItems) {
          // Por ahora todos los subitems son accesibles si el item principal lo es
          // Pero podemos agregar lógica aquí si es necesario
        }
        
        return true;
      })
      .sort((a, b) => a.order - b.order);
  }
  
  /**
   * Toggle para expandir/colapsar subitems
   * Colapsa automáticamente otras categorías cuando se abre una nueva
   */
  toggleSubmenu(itemLabel: string, event?: Event): void {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    
    if (this.expandedItems.has(itemLabel)) {
      // Si ya está expandido, colapsarlo
      this.expandedItems.delete(itemLabel);
    } else {
      // Si no está expandido, colapsar todas las demás y expandir esta
      this.expandedItems.clear();
      this.expandedItems.add(itemLabel);
    }
  }
  
  /**
   * Verificar si un item está expandido
   */
  isExpanded(itemLabel: string): boolean {
    return this.expandedItems.has(itemLabel);
  }
  
  /**
   * Manejar click en item con subitems
   */
  handleItemClick(item: NavItem, event: Event): void {
    if (item.subItems && item.subItems.length > 0) {
      // Si tiene subitems, expandir/colapsar en lugar de navegar
      this.toggleSubmenu(item.label, event);
    }
    // Si no tiene subitems, el routerLink normal manejará la navegación
  }

  /**
   * Manejar click en cualquier elemento de navegación
   * Cierra los submenús si se hace click en otro elemento
   */
  handleNavLinkClick(item: NavItem, event: Event): void {
    // Si el item clickeado tiene subitems, no hacer nada (ya se maneja en handleItemClick)
    if (item.subItems && item.subItems.length > 0) {
      return;
    }
    
    // Si se hace click en un item sin subitems, cerrar todos los submenús
    if (this.expandedItems.size > 0) {
      this.expandedItems.clear();
    }
  }

  private resetNavItems(): void {
    this.visibleNavItems = [];
    this.expandedItems.clear();
    // La navbar permanece visible, solo se limpian los items
  }

  toggleUserMenu(): void {
    this.showUserMenu = !this.showUserMenu;
  }

  closeUserMenu(): void {
    this.showUserMenu = false;
  }

  handleLogoPressStart(event: PointerEvent): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    if (event.pointerType !== 'touch' && event.button !== 0) {
      return;
    }

    this.isLogoPressActive = true;
    this.clearLogoPressTimers();
    this.clearLogoClickSuppressionTimeout();

    this.logoPressTimeoutId = setTimeout(() => {
      if (!this.isLogoPressActive) {
        return;
      }

      this.performLogoHoldToggle();
      this.logoPressIntervalId = setInterval(() => {
        if (this.isLogoPressActive) {
          this.performLogoHoldToggle();
        }
      }, 5000);
    }, 5000);
  }

  handleLogoPressEnd(event?: PointerEvent): void {
    if (!this.isLogoPressActive && !this.logoPressTimeoutId && !this.logoPressIntervalId) {
      return;
    }

    this.isLogoPressActive = false;
    this.clearLogoPressTimers();

    if (this.logoHoldActivated && !this.logoClickSuppressTimeoutId) {
      this.logoClickSuppressTimeoutId = setTimeout(() => {
        this.logoHoldActivated = false;
        this.logoClickSuppressTimeoutId = null;
      }, 400);
    }
  }

  handleLogoClick(event: MouseEvent): void {
    if (!this.logoHoldActivated) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    this.logoHoldActivated = false;
    this.clearLogoClickSuppressionTimeout();
  }

  toggleTheme(): void {
    if (isPlatformBrowser(this.platformId)) {
      const body = document.body;
      body.classList.toggle('dark-mode');
      this.isDarkMode = body.classList.contains('dark-mode');
      localStorage.setItem('darkMode', this.isDarkMode ? 'true' : 'false');
    }
  }

  private performLogoHoldToggle(): void {
    this.logoHoldActivated = true;
    this.toggleTheme();
  }

  private clearLogoPressTimers(): void {
    if (this.logoPressTimeoutId !== null) {
      clearTimeout(this.logoPressTimeoutId);
      this.logoPressTimeoutId = null;
    }

    if (this.logoPressIntervalId !== null) {
      clearInterval(this.logoPressIntervalId);
      this.logoPressIntervalId = null;
    }
  }

  private clearLogoClickSuppressionTimeout(): void {
    if (this.logoClickSuppressTimeoutId !== null) {
      clearTimeout(this.logoClickSuppressTimeoutId);
      this.logoClickSuppressTimeoutId = null;
    }
  }

  logout(): void {
    this.authService.logout();
    this.showUserMenu = false;
    this.router.navigate(['/login']);
  }

  getRoleLabel(rol: number | undefined): string {
    if (!rol) return 'Usuario';
    return ROLES_LABELS[rol as keyof typeof ROLES_LABELS] || 'Usuario';
  }

  getAnimationDelay(index: number): any {
    return { value: '', params: { delay: index * 150 } };
  }

  /**
   * Obtener icono según el tipo de notificación
   */
  getNotificacionIcon(tipo: string): string {
    switch (tipo) {
      case 'nuevo_envio':
      case 'envio_asignado':
        return 'fas fa-truck';
      case 'estado_cambiado':
        return 'fas fa-sync-alt';
      default:
        return 'fas fa-info-circle';
    }
  }

  /**
   * Obtener tiempo relativo desde la fecha
   */
  getTimeAgo(fecha: string): string {
    if (!fecha) return '';
    
    const ahora = new Date();
    const fechaNotificacion = new Date(fecha);
    const diferencia = ahora.getTime() - fechaNotificacion.getTime();
    const segundos = Math.floor(diferencia / 1000);
    const minutos = Math.floor(segundos / 60);
    const horas = Math.floor(minutos / 60);
    const dias = Math.floor(horas / 24);

    if (segundos < 60) return 'Hace un momento';
    if (minutos < 60) return `Hace ${minutos} minuto${minutos > 1 ? 's' : ''}`;
    if (horas < 24) return `Hace ${horas} hora${horas > 1 ? 's' : ''}`;
    if (dias < 7) return `Hace ${dias} día${dias > 1 ? 's' : ''}`;
    
    return fechaNotificacion.toLocaleDateString('es-ES', { 
      day: '2-digit', 
      month: 'short' 
    });
  }
}


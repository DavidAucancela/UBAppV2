import { Component, OnInit, OnDestroy, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { RouterLink, RouterLinkActive, Router } from '@angular/router';
import { trigger, state, style, transition, animate, stagger, query, animateChild } from '@angular/animations';
import { AuthService } from '../../services/auth.service';
import { Usuario, ROLES_LABELS, Roles } from '../../models/usuario';
import { Subscription } from 'rxjs';

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
  imports: [CommonModule, RouterLink, RouterLinkActive],
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
    
    // Animación de mensaje de bienvenida
    trigger('welcomeMessage', [
      transition(':enter', [
        style({
          opacity: 0,
          transform: 'translateY(-30px)'
        }),
        animate('600ms ease-out', style({
          opacity: 1,
          transform: 'translateY(0)'
        }))
      ]),
      transition(':leave', [
        animate('400ms ease-in', style({
          opacity: 0,
          transform: 'translateY(-20px)'
        }))
      ])
    ])
  ]
})
export class NavbarComponent implements OnInit, OnDestroy {
  currentUser: Usuario | null = null;
  showUserMenu = false;
  showWelcomeMessage = false;
  welcomeMessageText = '';
  navbarState = 'hidden';
  logoState = 'hidden';
  actionsState = 'hidden';
  ROLES_LABELS = ROLES_LABELS;
  
  // Items de navegación visibles según rol
  visibleNavItems: NavItem[] = [];
  isLoadingNav = false;
  
  private userSubscription: Subscription | null = null;
  
  // Definición de todos los items de navegación con sus roles permitidos
  private allNavItems: NavItem[] = [
    {
      label: 'Dashboard',
      icon: 'fas fa-home',
      route: '/dashboard',
      roles: [Roles.ADMIN, Roles.GERENTE],
      order: 1
    },
    {
      label: 'Dashboard Usuario',
      icon: 'fas fa-chart-line',
      route: '/dashboard-usuario',
      roles: [Roles.COMPRADOR],
      order: 1
    },
    {
      label: 'Mis Envíos',
      icon: 'fas fa-truck',
      route: '/mis-envios',
      roles: [Roles.COMPRADOR],
      order: 2
    },
    {
      label: 'Usuarios',
      icon: 'fas fa-users',
      route: '/usuarios',
      roles: [Roles.ADMIN, Roles.GERENTE],
      order: 2
    },
    {
      label: 'Envíos',
      icon: 'fas fa-truck',
      route: '/envios',
      roles: [Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR],
      order: 3,
      subItems: [
        { label: 'Envíos Activos', icon: 'fas fa-play-circle', route: '/envios/activos' },
        { label: 'Envíos Pendientes', icon: 'fas fa-clock', route: '/envios/pendientes' },
        { label: 'Envíos Completados', icon: 'fas fa-check-circle', route: '/envios/completados' },
        { label: 'Historial', icon: 'fas fa-history', route: '/envios/historial' }
      ]
    },
    {
      label: 'Búsqueda',
      icon: 'fas fa-search',
      route: '/busqueda',
      roles: [Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR, Roles.COMPRADOR],
      order: 4,
      subItems: [
        { label: 'Búsqueda Semántica', icon: 'fas fa-brain', route: '/busqueda-semantica' },
        { label: 'Búsqueda Tradicional', icon: 'fas fa-filter', route: '/busqueda-envios' },
        { label: 'Búsqueda Avanzada', icon: 'fas fa-search-plus', route: '/busqueda-avanzada' }
      ]
    },
    {
      label: 'Mapa',
      icon: 'fas fa-map-marked-alt',
      route: '/mapa-compradores',
      roles: [Roles.ADMIN, Roles.GERENTE],
      order: 5,
      subItems: [
        { label: 'Rutas de Entrega', icon: 'fas fa-route', route: '/mapa/rutas' },
        { label: 'Áreas de Cobertura', icon: 'fas fa-map', route: '/mapa/cobertura' },
        { label: 'Tiempos de Entrega', icon: 'fas fa-clock', route: '/mapa/tiempos' }
      ]
    },
    {
      label: 'Productos',
      icon: 'fas fa-box',
      route: '/productos',
      roles: [Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR],
      order: 6,
      subItems: [
        { label: 'Inventario', icon: 'fas fa-boxes', route: '/productos/inventario' },
        { label: 'Categorías', icon: 'fas fa-tags', route: '/productos/categorias' },
        { label: 'Almacenes', icon: 'fas fa-warehouse', route: '/productos/almacenes' }
      ]
    },
    {
      label: 'Importar Excel',
      icon: 'fas fa-file-excel',
      route: '/importacion-excel',
      roles: [Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR],
      order: 7
    },
    {
      label: 'Reportes',
      icon: 'fas fa-chart-bar',
      route: '/reportes',
      roles: [Roles.ADMIN, Roles.GERENTE],
      order: 8,
      subItems: [
        { label: 'Reportes de Envíos', icon: 'fas fa-truck', route: '/reportes/envios' },
        { label: 'Reportes de Ventas', icon: 'fas fa-dollar-sign', route: '/reportes/ventas' },
        { label: 'Rendimiento', icon: 'fas fa-tachometer-alt', route: '/reportes/rendimiento' }
      ]
    }
  ];

  constructor(
    public authService: AuthService,
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    // La navbar siempre está visible
    this.navbarState = 'visible';
    this.logoState = 'visible';
    this.actionsState = 'visible';
    
    // Suscribirse a los cambios del usuario actual
    this.userSubscription = this.authService.currentUser$.subscribe(user => {
      if (user && user !== this.currentUser) {
        // Usuario acaba de iniciar sesión o cambió
        this.currentUser = user;
        this.animateNavbarEntry();
      } else if (!user && this.currentUser) {
        // Usuario cerró sesión
        this.currentUser = null;
        this.resetNavItems();
      } else {
        this.currentUser = user;
        if (user) {
          // Usuario ya estaba logueado (recarga de página)
          this.loadNavItemsByRole();
        }
      }
    });
  }

  ngOnDestroy(): void {
    if (this.userSubscription) {
      this.userSubscription.unsubscribe();
    }
  }

  private animateNavbarEntry(): void {
    // Mostrar mensaje de bienvenida
    this.showWelcomeMessage = true;
    this.welcomeMessageText = `¡Bienvenido${this.currentUser?.nombre ? ', ' + this.currentUser.nombre : ''}!`;
    
    // Ocultar mensaje después de 3 segundos
    setTimeout(() => {
      this.showWelcomeMessage = false;
    }, 3000);
    
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
    
    // Filtrar items según el rol
    const itemsForRole = this.allNavItems
      .filter(item => item.roles.includes(userRole))
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
    this.visibleNavItems = this.allNavItems
      .filter(item => item.roles.includes(userRole))
      .sort((a, b) => a.order - b.order);
  }

  private resetNavItems(): void {
    this.visibleNavItems = [];
    this.showWelcomeMessage = false;
    // La navbar permanece visible, solo se limpian los items
  }

  toggleUserMenu(): void {
    this.showUserMenu = !this.showUserMenu;
  }

  closeUserMenu(): void {
    this.showUserMenu = false;
  }

  toggleTheme(): void {
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

  getRoleLabel(rol: number | undefined): string {
    if (!rol) return 'Usuario';
    return ROLES_LABELS[rol as keyof typeof ROLES_LABELS] || 'Usuario';
  }

  getAnimationDelay(index: number): any {
    return { value: '', params: { delay: index * 150 } };
  }
}

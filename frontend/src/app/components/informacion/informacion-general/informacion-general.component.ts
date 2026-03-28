import { Component, OnDestroy, Inject, PLATFORM_ID, AfterViewInit, NgZone } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { RouterModule } from '@angular/router';

interface Stat        { target: number; display: string; suffix: string; label: string; icon: string; }
interface Feature     { icon: string; titulo: string; descripcion: string; bullets: string[]; visual: string; }
interface Step        { numero: string; icon: string; titulo: string; descripcion: string; }
interface Rol         { icon: string; titulo: string; descripcion: string; color: string; accesos: string[]; }
interface Tech        { icon: string; nombre: string; detalle: string; }
interface DemoQuery   { text: string; results: DemoResult[]; }
interface DemoResult  { hawb: string; comprador: string; estado: string; estadoClass: string; ciudad: string; valor: string; }
interface MockupNotif { hawb: string; msg: string; icon: string; }

@Component({
  selector: 'app-informacion-general',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './informacion-general.component.html',
  styleUrls: ['./informacion-general.component.css']
})
export class InformacionGeneralComponent implements AfterViewInit, OnDestroy {

  stats: Stat[] = [
    { target: 10000, display: '0', suffix: '+',  label: 'Envíos gestionados',   icon: 'fas fa-truck-loading' },
    { target: 99,    display: '0', suffix: '%',  label: 'Precisión búsqueda IA', icon: 'fas fa-brain' },
    { target: 4,     display: '0', suffix: '',   label: 'Roles especializados',  icon: 'fas fa-users' },
    { target: 24,    display: '0', suffix: '/7', label: 'Disponibilidad',        icon: 'fas fa-clock' }
  ];

  features: Feature[] = [
    {
      icon: 'fas fa-truck-loading',
      titulo: 'Gestión completa de envíos',
      descripcion: 'Administra el ciclo completo de cada envío internacional con número HAWB único, estados detallados, tarifas automáticas y seguimiento en tiempo real.',
      bullets: [
        'Seguimiento por número HAWB único',
        'Historial completo de estados y fechas',
        'Cálculo automático de tarifas y costos',
        'Importación masiva desde archivos Excel'
      ],
      visual: 'envios'
    },
    {
      icon: 'fas fa-brain',
      titulo: 'Búsqueda semántica con IA',
      descripcion: 'Encuentra cualquier envío usando lenguaje natural. El motor semántico entiende el contexto de tu consulta y devuelve resultados precisos en milisegundos.',
      bullets: [
        'Búsqueda por texto libre en lenguaje natural',
        'Filtros avanzados: estado, fecha, HAWB, comprador',
        'Resultados ordenados por relevancia semántica',
        'Búsqueda unificada en un solo punto de acceso'
      ],
      visual: 'busqueda'
    },
    {
      icon: 'fas fa-map-marked-alt',
      titulo: 'Mapa interactivo de compradores',
      descripcion: 'Visualiza la distribución geográfica de todos tus compradores y destinos en un mapa interactivo con clustering inteligente de marcadores.',
      bullets: [
        'Mapa Leaflet con capas personalizables',
        'Clustering automático de marcadores',
        'Filtros por ciudad y estado de envío',
        'Vista de detalle de cada comprador'
      ],
      visual: 'mapa'
    },
    {
      icon: 'fas fa-chart-line',
      titulo: 'Dashboard personalizado por rol',
      descripcion: 'Cada usuario ve exactamente lo que necesita. Dashboards inteligentes con métricas relevantes según el rol asignado en el sistema.',
      bullets: [
        'Vista de administrador con estadísticas globales',
        'Panel de comprador con mis envíos y notificaciones',
        'Registro de actividad del sistema para gerentes',
        'Acceso rápido a funciones según el rol asignado'
      ],
      visual: 'dashboard'
    }
  ];

  steps: Step[] = [
    {
      numero: '01',
      icon: 'fas fa-user-check',
      titulo: 'Accede con tu rol',
      descripcion: 'Ingresa con tus credenciales. Tu rol se asigna automáticamente y personaliza toda la experiencia según tus funciones dentro del sistema.'
    },
    {
      numero: '02',
      icon: 'fas fa-file-import',
      titulo: 'Registra o importa',
      descripcion: 'Carga envíos manualmente o importa archivos Excel de forma masiva. El sistema valida y procesa los datos de manera automática.'
    },
    {
      numero: '03',
      icon: 'fas fa-search-location',
      titulo: 'Busca, gestiona y analiza',
      descripcion: 'Usa la búsqueda semántica con IA, actualiza estados, visualiza el mapa y accede a las métricas de tu dashboard en tiempo real.'
    }
  ];

  roles: Rol[] = [
    {
      icon: 'fas fa-shield-alt',
      titulo: 'Administrador',
      descripcion: 'Control total del sistema',
      color: 'admin',
      accesos: ['Gestión completa de usuarios', 'Todos los envíos', 'Configuración global', 'Reportes y analytics', 'Mapa de compradores']
    },
    {
      icon: 'fas fa-user-tie',
      titulo: 'Gerente',
      descripcion: 'Visión estratégica y reportes',
      color: 'gerente',
      accesos: ['Dashboard ejecutivo', 'Búsqueda semántica IA', 'Mapa de compradores', 'Registro de actividades', 'Analytics de envíos']
    },
    {
      icon: 'fas fa-keyboard',
      titulo: 'Digitador',
      descripcion: 'Operación y carga de datos',
      color: 'digitador',
      accesos: ['Registro de envíos', 'Importación Excel masiva', 'Gestión de productos', 'Búsqueda avanzada', 'Actualización de estados']
    },
    {
      icon: 'fas fa-shopping-bag',
      titulo: 'Comprador',
      descripcion: 'Seguimiento personal',
      color: 'comprador',
      accesos: ['Mis envíos asignados', 'Notificaciones en tiempo real', 'Historial completo', 'Estado actualizado', 'Detalle de costos']
    }
  ];

  techStack: Tech[] = [
    { icon: 'fas fa-layer-group', nombre: 'Angular 17',     detalle: 'Frontend SSR' },
    { icon: 'fas fa-server',      nombre: 'Django REST',    detalle: 'Backend API' },
    { icon: 'fas fa-database',    nombre: 'PostgreSQL',     detalle: 'Base de datos' },
    { icon: 'fas fa-brain',       nombre: 'Búsqueda IA',    detalle: 'NLP semántico' },
    { icon: 'fas fa-map',         nombre: 'Leaflet Maps',   detalle: 'Mapas interactivos' },
    { icon: 'fas fa-lock',        nombre: 'JWT + Cookies',  detalle: 'Auth segura' }
  ];

  // ── Demo search ────────────────────────────────────────────────────
  demoQueries: DemoQuery[] = [
    {
      text: 'envíos pendientes de María',
      results: [
        { hawb: 'GH-001849', comprador: 'María González', estado: 'Pendiente',    estadoClass: 'pendiente', ciudad: 'Quito',     valor: '$243.80' },
        { hawb: 'GH-001855', comprador: 'María Torres',   estado: 'Pendiente',    estadoClass: 'pendiente', ciudad: 'Guayaquil', valor: '$98.50'  },
      ]
    },
    {
      text: 'paquetes en tránsito esta semana',
      results: [
        { hawb: 'GH-001848', comprador: 'Carlos Ruiz',    estado: 'En tránsito',  estadoClass: 'transito',  ciudad: 'Cuenca',  valor: '$87.20'  },
        { hawb: 'GH-001852', comprador: 'Pedro Alvarado', estado: 'En tránsito',  estadoClass: 'transito',  ciudad: 'Loja',    valor: '$312.40' },
        { hawb: 'GH-001856', comprador: 'Diana Mora',     estado: 'En tránsito',  estadoClass: 'transito',  ciudad: 'Ambato',  valor: '$156.90' },
      ]
    },
    {
      text: 'entregados con valor mayor a $200',
      results: [
        { hawb: 'GH-001847', comprador: 'Ana Martínez',   estado: 'Entregado',    estadoClass: 'entregado', ciudad: 'Quito',     valor: '$243.80' },
        { hawb: 'GH-001853', comprador: 'Luis Torres',    estado: 'Entregado',    estadoClass: 'entregado', ciudad: 'Guayaquil', valor: '$318.60' },
      ]
    }
  ];

  currentDemoText = '';
  demoResults: DemoResult[] = [];
  showDemoResults = false;

  // ── Mockup notification ────────────────────────────────────────────
  mockupNotifs: MockupNotif[] = [
    { hawb: 'GH-001860', msg: 'Nuevo envío registrado', icon: 'fas fa-plus-circle'  },
    { hawb: 'GH-001848', msg: 'Estado actualizado',     icon: 'fas fa-sync-alt'     },
    { hawb: 'GH-001853', msg: 'Entregado exitosamente', icon: 'fas fa-check-circle' },
  ];
  currentMockupNotif: MockupNotif = this.mockupNotifs[0];
  showMockupNotif = false;

  private observers: IntersectionObserver[] = [];
  private typewriterActive = false;
  private mockupInterval: any = null;
  private notifIndex = 0;

  constructor(
    @Inject(PLATFORM_ID) private platformId: Object,
    private zone: NgZone
  ) {}

  ngAfterViewInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.setupScrollAnimations();
      this.setupCounters();
      this.startMockupAnimations();
      this.startSearchDemo();
    }
  }

  private setupScrollAnimations(): void {
    const observer = new IntersectionObserver(
      entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('is-visible'); }),
      { threshold: 0.07, rootMargin: '0px 0px -40px 0px' }
    );
    document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
    this.observers.push(observer);
  }

  private setupCounters(): void {
    const el = document.querySelector('.stats-section');
    if (!el) return;
    const observer = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) {
        this.zone.run(() => this.animateCounters());
        observer.disconnect();
      }
    }, { threshold: 0.25 });
    observer.observe(el);
    this.observers.push(observer);
  }

  private animateCounters(): void {
    const DURATION = 1600;
    this.stats.forEach((stat, i) => {
      const start = performance.now();
      const target = stat.target;
      const fmt = (v: number) => v >= 1000 ? v.toLocaleString('es-ES') : String(v);
      const tick = (now: number) => {
        const p   = Math.min((now - start) / DURATION, 1);
        const val = Math.round((1 - Math.pow(1 - p, 3)) * target);
        this.stats[i].display = fmt(val);
        if (p < 1) requestAnimationFrame(tick);
        else this.stats[i].display = fmt(target);
      };
      requestAnimationFrame(tick);
    });
  }

  private startMockupAnimations(): void {
    const show = () => {
      this.zone.run(() => {
        this.currentMockupNotif = this.mockupNotifs[this.notifIndex % this.mockupNotifs.length];
        this.notifIndex++;
        this.showMockupNotif = true;
        setTimeout(() => this.zone.run(() => this.showMockupNotif = false), 2800);
      });
    };
    setTimeout(show, 2000);
    this.mockupInterval = setInterval(show, 6000);
  }

  private startSearchDemo(): void {
    this.typewriterActive = true;
    let queryIndex = 0;

    const cycle = () => {
      if (!this.typewriterActive) return;
      const query = this.demoQueries[queryIndex];
      this.zone.run(() => { this.currentDemoText = ''; this.showDemoResults = false; });
      let charIndex = 0;

      const typeChar = () => {
        if (!this.typewriterActive) return;
        if (charIndex < query.text.length) {
          this.zone.run(() => this.currentDemoText += query.text[charIndex++]);
          setTimeout(typeChar, 55);
        } else {
          setTimeout(() => {
            if (!this.typewriterActive) return;
            this.zone.run(() => { this.demoResults = query.results; this.showDemoResults = true; });
            setTimeout(() => {
              if (!this.typewriterActive) return;
              this.zone.run(() => this.showDemoResults = false);
              setTimeout(() => {
                const eraseChar = () => {
                  if (!this.typewriterActive) return;
                  if (this.currentDemoText.length > 0) {
                    this.zone.run(() => this.currentDemoText = this.currentDemoText.slice(0, -1));
                    setTimeout(eraseChar, 30);
                  } else {
                    queryIndex = (queryIndex + 1) % this.demoQueries.length;
                    setTimeout(cycle, 500);
                  }
                };
                eraseChar();
              }, 300);
            }, 3200);
          }, 500);
        }
      };
      typeChar();
    };

    setTimeout(cycle, 1200);
  }

  ngOnDestroy(): void {
    this.observers.forEach(o => o.disconnect());
    this.typewriterActive = false;
    if (this.mockupInterval) clearInterval(this.mockupInterval);
  }
}

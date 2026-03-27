import { Component, OnDestroy, Inject, PLATFORM_ID, AfterViewInit, NgZone } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { RouterModule } from '@angular/router';

interface Stat    { target: number; display: string; suffix: string; label: string; icon: string; }
interface Feature { icon: string; titulo: string; descripcion: string; bullets: string[]; visual: string; }
interface Step    { numero: string; icon: string; titulo: string; descripcion: string; }
interface Rol     { icon: string; titulo: string; descripcion: string; color: string; accesos: string[]; }
interface Tech    { icon: string; nombre: string; detalle: string; }

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

  private observers: IntersectionObserver[] = [];

  constructor(
    @Inject(PLATFORM_ID) private platformId: Object,
    private zone: NgZone
  ) {}

  ngAfterViewInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.setupScrollAnimations();
      this.setupCounters();
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

  ngOnDestroy(): void {
    this.observers.forEach(o => o.disconnect());
  }
}

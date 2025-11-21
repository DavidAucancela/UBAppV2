import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-informacion-general',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './informacion-general.component.html',
  styleUrls: ['./informacion-general.component.css']
})
export class InformacionGeneralComponent {
  caracteristicas = [
    {
      icono: 'bi-box-seam',
      titulo: 'Gestión de Envíos',
      descripcion: 'Sistema completo para administrar tus envíos internacionales con seguimiento en tiempo real.'
    },
    {
      icono: 'bi-speedometer2',
      titulo: 'Dashboard Personalizado',
      descripcion: 'Visualiza todas tus estadísticas, cupo anual y envíos desde un panel intuitivo.'
    },
    {
      icono: 'bi-search',
      titulo: 'Búsqueda Avanzada',
      descripcion: 'Encuentra tus envíos rápidamente con nuestro sistema de búsqueda inteligente y semántica.'
    },
    {
      icono: 'bi-file-earmark-excel',
      titulo: 'Importación Excel',
      descripcion: 'Carga múltiples envíos simultáneamente desde archivos Excel de manera sencilla.'
    },
    {
      icono: 'bi-geo-alt',
      titulo: 'Mapa Interactivo',
      descripcion: 'Visualiza la ubicación de compradores y sucursales en un mapa interactivo.'
    },
    {
      icono: 'bi-shield-check',
      titulo: 'Seguro y Confiable',
      descripcion: 'Tu información está protegida con los más altos estándares de seguridad.'
    }
  ];

  beneficios = [
    {
      titulo: 'Control total del cupo anual',
      resumen: 'Visualiza consumos, alertas y proyecciones en tiempo real.',
      descripcion: 'Compara el cupo asignado con el cupo utilizado y recibe recomendaciones automáticas para evitar sobrecostos.',
      categoria: 'Planeación operativa',
      imagen: 'https://images.unsplash.com/photo-1434626881859-194d67b2b86f?auto=format&fit=crop&w=900&q=70',
      detalles: [
        'Tableros interactivos con indicadores diarios',
        'Alertas inteligentes configurables según perfil',
        'Exportación inmediata de reportes en PDF y Excel'
      ]
    },
    {
      titulo: 'Notificaciones en tiempo real',
      resumen: 'Sigue cada hito crítico del envío desde cualquier dispositivo.',
      descripcion: 'Orquesta flujos de comunicación automáticos con compradores y aliados logísticos para garantizar transparencia.',
      categoria: 'Seguimiento inteligente',
      imagen: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=70',
      detalles: [
        'Alertas push, correo y panel unificado',
        'Historial auditado de cada interacción',
        'Reglas personalizadas por tipo de envío'
      ]
    },
    {
      titulo: 'Analítica avanzada de costos',
      resumen: 'Identifica tendencias y puntos de ahorro automáticamente.',
      descripcion: 'Nuestro motor analítico cruza datos financieros y operativos para detectar desvíos y crear escenarios de simulación.',
      categoria: 'Inteligencia de negocios',
      imagen: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=900&q=70',
      detalles: [
        'KPIs financieros listos para presentar a dirección',
        'Simulaciones de tarifas con IA en segundos',
        'Alertas predictivas frente a costos atípicos'
      ]
    },
    {
      titulo: 'Soporte especializado 24/7',
      resumen: 'Acompañamiento humano y automatizado para cada rol.',
      descripcion: 'Nuestro equipo conoce tus procesos y responde con guías, tutoriales y sesiones en vivo para reducir tiempos muertos.',
      categoria: 'Experiencia de usuario',
      imagen: 'https://images.unsplash.com/photo-1529333166437-7750a6dd5a70?auto=format&fit=crop&w=900&q=70',
      detalles: [
        'Base de conocimiento contextual dentro del sistema',
        'Chat integrado con especialistas certificados',
        'Tableros de salud del servicio para anticipar incidentes'
      ]
    }
  ];

  beneficioSeleccionadoIndex = 0;

  get beneficioSeleccionado() {
    return this.beneficios[this.beneficioSeleccionadoIndex];
  }

  seleccionarBeneficio(indice: number): void {
    this.beneficioSeleccionadoIndex = indice;
  }
}


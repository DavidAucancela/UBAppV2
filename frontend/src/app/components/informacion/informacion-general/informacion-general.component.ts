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
    'Control total de tu cupo anual de envíos',
    'Notificaciones en tiempo real del estado de tus paquetes',
    'Reportes detallados de costos y estadísticas',
    'Soporte técnico especializado',
    'Interfaz intuitiva y fácil de usar',
    'Acceso desde cualquier dispositivo'
  ];
}


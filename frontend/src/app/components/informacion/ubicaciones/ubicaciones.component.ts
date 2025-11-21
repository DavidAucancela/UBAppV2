import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

interface Ubicacion {
  nombre: string;
  direccion: string;
  ciudad: string;
  telefono: string;
  email: string;
  horario: string;
  lat: number;
  lng: number;
}

@Component({
  selector: 'app-ubicaciones',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './ubicaciones.component.html',
  styleUrls: ['./ubicaciones.component.css']
})
export class UbicacionesComponent implements OnInit {
  ubicaciones: Ubicacion[] = [
    {
      nombre: 'Oficina Principal - Quito',
      direccion: 'Av. 6 de Diciembre N34-120 y Bosmediano',
      ciudad: 'Quito, Pichincha',
      telefono: '+593 2 234-5678',
      email: 'quito@envios.com',
      horario: 'Lunes a Viernes: 8:00 AM - 6:00 PM',
      lat: -0.1807,
      lng: -78.4678
    },
    {
      nombre: 'Sucursal Guayaquil',
      direccion: 'Av. Francisco de Orellana, Mz. 111, Solar 1',
      ciudad: 'Guayaquil, Guayas',
      telefono: '+593 4 567-8901',
      email: 'guayaquil@envios.com',
      horario: 'Lunes a Viernes: 8:00 AM - 6:00 PM',
      lat: -2.1894,
      lng: -79.8883
    },
    {
      nombre: 'Sucursal Cuenca',
      direccion: 'Av. Remigio Crespo 1-89 y Av. Solano',
      ciudad: 'Cuenca, Azuay',
      telefono: '+593 7 234-5678',
      email: 'cuenca@envios.com',
      horario: 'Lunes a Viernes: 8:30 AM - 5:30 PM',
      lat: -2.9001,
      lng: -79.0059
    }
  ];

  ubicacionSeleccionada: Ubicacion | null = null;

  ngOnInit(): void {
    this.ubicacionSeleccionada = this.ubicaciones[0];
  }

  seleccionarUbicacion(ubicacion: Ubicacion): void {
    this.ubicacionSeleccionada = ubicacion;
  }

  obtenerUrlMapa(ubicacion: Ubicacion): string {
    return `https://www.google.com/maps/embed/v1/place?key=YOUR_GOOGLE_MAPS_API_KEY&q=${ubicacion.lat},${ubicacion.lng}&zoom=15`;
  }

  abrirEnGoogleMaps(ubicacion: Ubicacion): void {
    const url = `https://www.google.com/maps/search/?api=1&query=${ubicacion.lat},${ubicacion.lng}`;
    window.open(url, '_blank');
  }
}














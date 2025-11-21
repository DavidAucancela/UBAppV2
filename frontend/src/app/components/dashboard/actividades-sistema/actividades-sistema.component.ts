import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { forkJoin } from 'rxjs';
import { ApiService } from '../../../services/api.service';

interface Activity {
  type: string;
  description: string;
  time: string;
}

@Component({
  selector: 'app-actividades-sistema',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './actividades-sistema.component.html',
  styleUrl: './actividades-sistema.component.css'
})
export class ActividadesSistemaComponent implements OnInit {
  activities: Activity[] = [];
  loading = true;

  constructor(
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.loadActivities();
  }

  private loadActivities(): void {
    this.loading = true;
    
    // Cargar usuarios y envíos en paralelo
    forkJoin({
      usuarios: this.apiService.getUsuarios(),
      envios: this.apiService.getEnvios()
    }).subscribe({
      next: ({ usuarios, envios }) => {
        const actividades: Activity[] = [];
        
        // Procesar usuarios recientes
        const listaUsuarios = Array.isArray(usuarios) ? usuarios : (usuarios as any).results || [];
        listaUsuarios.slice(0, 20).forEach((u: any) => {
          actividades.push({
            type: 'usuario',
            description: `Nuevo usuario: ${u.nombre || u.username}`,
            time: u.fecha_creacion ? new Date(u.fecha_creacion).toLocaleString() : 'Reciente'
          });
        });
        
        // Procesar envíos recientes
        const listaEnvios = Array.isArray(envios) ? envios : (envios as any).results || [];
        listaEnvios.slice(0, 20).forEach((e: any) => {
          actividades.push({
            type: 'envio',
            description: `Envío ${e.hawb} (${e.estado_nombre || e.estado})`,
            time: e.fecha_creacion ? new Date(e.fecha_creacion).toLocaleString() : 'Reciente'
          });
        });
        
        // Ordenar por fecha (más recientes primero)
        this.activities = actividades.sort((a, b) => {
          const dateA = new Date(a.time).getTime();
          const dateB = new Date(b.time).getTime();
          // Si alguna fecha es inválida, ponerla al final
          if (isNaN(dateA) && isNaN(dateB)) return 0;
          if (isNaN(dateA)) return 1;
          if (isNaN(dateB)) return -1;
          return dateB - dateA;
        }).slice(0, 50); // Limitar a 50 actividades más recientes
        
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.activities = [];
      }
    });
  }

  getActivityIcon(type: string): string {
    switch (type) {
      case 'envio':
        return 'fa-truck';
      case 'usuario':
        return 'fa-user-plus';
      case 'producto':
        return 'fa-box';
      case 'busqueda':
        return 'fa-search';
      default:
        return 'fa-info-circle';
    }
  }
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UsuarioService } from '../../../services/usuario.service';
import { AuthService } from '../../../services/auth.service';
import { DashboardUsuario } from '../../../models/usuario';
import { Envio } from '../../../models/envio';

@Component({
  selector: 'app-dashboard-usuario',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard-usuario.component.html',
  styleUrls: ['./dashboard-usuario.component.css']
})
export class DashboardUsuarioComponent implements OnInit {
  dashboard: DashboardUsuario | null = null;
  enviosRecientes: Envio[] = [];
  loading = true;
  error: string | null = null;
  anioActual = new Date().getFullYear();

  constructor(
    private usuarioService: UsuarioService,
    public authService: AuthService
  ) { }

  ngOnInit(): void {
    this.cargarDashboard();
  }

  cargarDashboard(): void {
    this.loading = true;
    this.error = null;

    this.usuarioService.getDashboardUsuario(this.anioActual).subscribe({
      next: (data) => {
        this.dashboard = data.dashboard;
        this.enviosRecientes = data.envios_recientes;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error al cargar dashboard:', err);
        this.error = 'Error al cargar las estadísticas';
        this.loading = false;
      }
    });
  }

  cambiarAnio(anio: number): void {
    this.anioActual = anio;
    this.cargarDashboard();
  }

  obtenerColorAlerta(): string {
    if (!this.dashboard) return 'success';
    
    const porcentaje = this.dashboard.porcentaje_usado;
    if (porcentaje >= 90) return 'danger';
    if (porcentaje >= 80) return 'warning';
    if (porcentaje >= 50) return 'info';
    return 'success';
  }

  obtenerEstadoEnvio(estado: string): string {
    const estados: { [key: string]: string } = {
      'pendiente': 'Pendiente',
      'en_transito': 'En Tránsito',
      'entregado': 'Entregado',
      'cancelado': 'Cancelado'
    };
    return estados[estado] || estado;
  }

  obtenerClaseEstado(estado: string): string {
    const clases: { [key: string]: string } = {
      'pendiente': 'badge bg-warning',
      'en_transito': 'badge bg-info',
      'entregado': 'badge bg-success',
      'cancelado': 'badge bg-secondary'
    };
    return clases[estado] || 'badge bg-secondary';
  }
}






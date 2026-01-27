import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { UsuarioService } from '../../../services/usuario.service';
import { Envio } from '../../../models/envio';
import { EnvioDetailModalComponent } from '../../shared/envio-detail-modal/envio-detail-modal.component';

@Component({
  selector: 'app-mis-envios',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, EnvioDetailModalComponent],
  templateUrl: './mis-envios.component.html',
  styleUrls: ['./mis-envios.component.css']
})
export class MisEnviosComponent implements OnInit {
  envios: Envio[] = [];
  totalEnvios = 0;
  loading = true;
  error: string | null = null;

  // Filtros
  filtroEstado = '';
  filtroFechaDesde = '';
  filtroFechaHasta = '';

  // Modal de detalles
  selectedEnvioId: number | null = null;
  showDetailModal = false;

  constructor(private usuarioService: UsuarioService) { }

  ngOnInit(): void {
    this.cargarEnvios();
  }

  cargarEnvios(): void {
    this.loading = true;
    this.error = null;

    const filtros: any = {};
    if (this.filtroEstado) filtros.estado = this.filtroEstado;
    if (this.filtroFechaDesde) filtros.fecha_desde = this.filtroFechaDesde;
    if (this.filtroFechaHasta) filtros.fecha_hasta = this.filtroFechaHasta;

    this.usuarioService.getMisEnvios(filtros).subscribe({
      next: (data) => {
        this.envios = data.envios;
        this.totalEnvios = data.total_envios;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error al cargar envíos:', err);
        this.error = 'Error al cargar los envíos';
        this.loading = false;
      }
    });
  }

  aplicarFiltros(): void {
    this.cargarEnvios();
  }

  limpiarFiltros(): void {
    this.filtroEstado = '';
    this.filtroFechaDesde = '';
    this.filtroFechaHasta = '';
    this.cargarEnvios();
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

  verDetalles(envio: Envio): void {
    if (envio.id) {
      this.selectedEnvioId = envio.id;
      this.showDetailModal = true;
    }
  }

  cerrarModal(): void {
    this.showDetailModal = false;
    this.selectedEnvioId = null;
  }
}
























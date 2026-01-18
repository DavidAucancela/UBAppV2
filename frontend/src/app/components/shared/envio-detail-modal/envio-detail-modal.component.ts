import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../services/api.service';
import { Envio, EstadosEnvio, ESTADOS_LABELS } from '../../../models/envio';
import { CategoriasProducto, CATEGORIAS_LABELS } from '../../../models/producto';

@Component({
  selector: 'app-envio-detail-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './envio-detail-modal.component.html',
  styleUrl: './envio-detail-modal.component.css'
})
export class EnvioDetailModalComponent implements OnInit, OnChanges {
  @Input() envioId: number | null = null;
  @Input() show: boolean = false;
  @Output() close = new EventEmitter<void>();

  envio: Envio | null = null;
  loading = false;
  error: string | null = null;

  ESTADOS_LABELS = ESTADOS_LABELS;
  CATEGORIAS_LABELS = CATEGORIAS_LABELS;
  EstadosEnvio = EstadosEnvio;
  CategoriasProducto = CategoriasProducto;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    if (this.envioId && this.show) {
      this.loadEnvio();
    }
  }

  ngOnChanges(): void {
    if (this.envioId && this.show) {
      this.loadEnvio();
    }
  }

  loadEnvio(): void {
    if (!this.envioId) return;

    this.loading = true;
    this.error = null;

    this.apiService.getEnvio(this.envioId).subscribe({
      next: (envio) => {
        this.envio = envio;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando detalle del envío:', error);
        this.error = 'Error al cargar el detalle del envío';
        this.loading = false;
      }
    });
  }

  closeModal(): void {
    this.show = false;
    this.envio = null;
    this.error = null;
    this.close.emit();
  }

  getEstadoLabel(estado: string): string {
    return ESTADOS_LABELS[estado as keyof typeof ESTADOS_LABELS] || estado;
  }

  getEstadoClass(estado: string): string {
    switch (estado) {
      case EstadosEnvio.ENTREGADO:
        return 'badge-success';
      case EstadosEnvio.EN_TRANSITO:
        return 'badge-warning';
      case EstadosEnvio.PENDIENTE:
        return 'badge-info';
      case EstadosEnvio.CANCELADO:
        return 'badge-danger';
      default:
        return '';
    }
  }

  getCategoriaLabel(categoria: string): string {
    return CATEGORIAS_LABELS[categoria as keyof typeof CATEGORIAS_LABELS] || categoria;
  }

  getCategoriaIcon(categoria: string): string {
    const iconos: { [key: string]: string } = {
      'electronica': 'fa-laptop',
      'ropa': 'fa-tshirt',
      'hogar': 'fa-home',
      'deportes': 'fa-futbol',
      'otros': 'fa-box'
    };
    return iconos[categoria] || 'fa-box';
  }
}

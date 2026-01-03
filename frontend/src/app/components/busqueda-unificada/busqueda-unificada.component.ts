import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BusquedaEnviosComponent } from '../busqueda-envios/busqueda-envios.component';
import { BusquedaSemanticaComponent } from '../busqueda-semantica/busqueda-semantica.component';

/**
 * Componente Unificado de Búsqueda de Envíos
 * Integra búsqueda exacta (tradicional) y búsqueda semántica (IA)
 * Permite al usuario alternar entre ambos modos
 */
@Component({
  selector: 'app-busqueda-unificada',
  standalone: true,
  imports: [CommonModule, BusquedaEnviosComponent, BusquedaSemanticaComponent],
  templateUrl: './busqueda-unificada.component.html',
  styleUrl: './busqueda-unificada.component.css'
})
export class BusquedaUnificadaComponent implements OnInit {
  // Modo de búsqueda actual
  modoActual: 'exacta' | 'semantica' = 'exacta';

  /**
   * Cambia entre modo de búsqueda exacta y semántica
   */
  cambiarModo(nuevoModo: 'exacta' | 'semantica'): void {
    this.modoActual = nuevoModo;
    
    // Guardar preferencia del usuario
    localStorage.setItem('preferenciaBusqueda', nuevoModo);
    
    // Scroll suave al cambiar
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  /**
   * Inicializa con la preferencia guardada del usuario
   */
  ngOnInit(): void {
    const preferencia = localStorage.getItem('preferenciaBusqueda');
    if (preferencia === 'semantica' || preferencia === 'exacta') {
      this.modoActual = preferencia;
    }
  }
}




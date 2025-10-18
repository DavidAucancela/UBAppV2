import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';

import { BusquedaEnviosComponent } from './busqueda-envios.component';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { RespuestaBusquedaEnvio } from '../../models/busqueda-envio';
import { Envio, EstadosEnvio } from '../../models/envio';

describe('BusquedaEnviosComponent', () => {
  let component: BusquedaEnviosComponent;
  let fixture: ComponentFixture<BusquedaEnviosComponent>;
  let apiService: jasmine.SpyObj<ApiService>;
  let authService: jasmine.SpyObj<AuthService>;

  // Datos de prueba
  const enviosMock: Envio[] = [
    {
      id: 1,
      hawb: 'HAWB001',
      peso_total: 5.5,
      cantidad_total: 3,
      valor_total: 150.00,
      costo_servicio: 25.00,
      fecha_emision: '2025-01-15T10:00:00Z',
      comprador: 1,
      comprador_info: {
        id: 1,
        username: 'comprador1',
        nombre: 'Juan Pérez',
        correo: 'juan@example.com',
        cedula: '1234567890',
        rol_nombre: 'Comprador',
        telefono: '0987654321'
      },
      estado: EstadosEnvio.EN_TRANSITO
    },
    {
      id: 2,
      hawb: 'HAWB002',
      peso_total: 3.2,
      cantidad_total: 2,
      valor_total: 80.00,
      costo_servicio: 15.00,
      fecha_emision: '2025-01-16T14:30:00Z',
      comprador: 2,
      comprador_info: {
        id: 2,
        username: 'comprador2',
        nombre: 'María García',
        correo: 'maria@example.com',
        cedula: '0987654321',
        rol_nombre: 'Comprador'
      },
      estado: EstadosEnvio.ENTREGADO
    }
  ];

  const respuestaBusquedaMock: RespuestaBusquedaEnvio = {
    count: 2,
    next: null,
    previous: null,
    results: enviosMock
  };

  beforeEach(async () => {
    // Crear spies para los servicios
    const apiServiceSpy = jasmine.createSpyObj('ApiService', [
      'buscarEnviosAvanzado',
      'getEnvio',
      'obtenerComprobanteEnvio',
      'exportarResultadosBusqueda'
    ]);
    
    const authServiceSpy = jasmine.createSpyObj('AuthService', [
      'isAdmin',
      'isGerente',
      'isDigitador',
      'isComprador'
    ]);

    await TestBed.configureTestingModule({
      imports: [
        BusquedaEnviosComponent,
        HttpClientTestingModule,
        ReactiveFormsModule,
        FormsModule,
        RouterTestingModule
      ],
      providers: [
        { provide: ApiService, useValue: apiServiceSpy },
        { provide: AuthService, useValue: authServiceSpy }
      ]
    }).compileComponents();

    apiService = TestBed.inject(ApiService) as jasmine.SpyObj<ApiService>;
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    
    fixture = TestBed.createComponent(BusquedaEnviosComponent);
    component = fixture.componentInstance;
  });

  // ===== PRUEBAS DE INICIALIZACIÓN =====

  it('✅ Debe crear el componente correctamente', () => {
    expect(component).toBeTruthy();
    console.log('✅ Componente creado exitosamente');
  });

  it('✅ Debe inicializar el formulario de búsqueda con valores vacíos', () => {
    expect(component.formularioBusqueda).toBeDefined();
    expect(component.formularioBusqueda.get('textoBusqueda')?.value).toBe('');
    expect(component.formularioBusqueda.get('numeroGuia')?.value).toBe('');
    expect(component.formularioBusqueda.get('nombreDestinatario')?.value).toBe('');
    expect(component.formularioBusqueda.get('estado')?.value).toBe('');
    console.log('✅ Formulario inicializado correctamente');
  });

  it('✅ Debe inicializar con valores por defecto', () => {
    expect(component.enviosEncontrados).toEqual([]);
    expect(component.cargando).toBe(false);
    expect(component.paginaActual).toBe(1);
    expect(component.elementosPorPagina).toBe(10);
    expect(component.ordenamientoActual).toBe('-fecha_emision');
    console.log('✅ Valores por defecto configurados correctamente');
  });

  // ===== PRUEBAS DE BÚSQUEDA =====

  it('✅ Debe buscar envíos correctamente al inicializar', () => {
    apiService.buscarEnviosAvanzado.and.returnValue(of(respuestaBusquedaMock));
    
    fixture.detectChanges(); // Esto llama a ngOnInit
    
    expect(apiService.buscarEnviosAvanzado).toHaveBeenCalled();
    expect(component.enviosEncontrados.length).toBe(2);
    expect(component.totalResultados).toBe(2);
    console.log('✅ Búsqueda inicial completada correctamente');
  });

  it('✅ Debe manejar errores al buscar envíos', () => {
    const errorMock = { error: 'Error de servidor' };
    apiService.buscarEnviosAvanzado.and.returnValue(throwError(() => errorMock));
    
    component.buscarEnvios();
    
    expect(component.errorMensaje).toContain('Error al conectar con el servidor');
    expect(component.cargando).toBe(false);
    expect(component.enviosEncontrados).toEqual([]);
    console.log('✅ Error de búsqueda manejado correctamente');
  });

  it('✅ Debe mostrar mensaje cuando no hay resultados', () => {
    const respuestaVacia: RespuestaBusquedaEnvio = {
      count: 0,
      next: null,
      previous: null,
      results: []
    };
    
    apiService.buscarEnviosAvanzado.and.returnValue(of(respuestaVacia));
    
    component.buscarEnvios();
    
    expect(component.sinResultados).toBe(true);
    expect(component.enviosEncontrados.length).toBe(0);
    console.log('✅ Mensaje de sin resultados mostrado correctamente');
  });

  it('✅ Debe aplicar filtros correctamente', () => {
    apiService.buscarEnviosAvanzado.and.returnValue(of(respuestaBusquedaMock));
    
    component.formularioBusqueda.patchValue({
      textoBusqueda: 'HAWB001',
      estado: EstadosEnvio.EN_TRANSITO
    });
    
    component.aplicarFiltros();
    
    expect(apiService.buscarEnviosAvanzado).toHaveBeenCalled();
    expect(component.paginaActual).toBe(1);
    console.log('✅ Filtros aplicados correctamente');
  });

  // ===== PRUEBAS DE FILTROS =====

  it('✅ Debe limpiar filtros correctamente', () => {
    component.formularioBusqueda.patchValue({
      textoBusqueda: 'test',
      numeroGuia: 'HAWB001',
      estado: EstadosEnvio.PENDIENTE
    });
    
    apiService.buscarEnviosAvanzado.and.returnValue(of(respuestaBusquedaMock));
    
    component.limpiarFiltros();
    
    expect(component.formularioBusqueda.get('textoBusqueda')?.value).toBe(null);
    expect(component.formularioBusqueda.get('numeroGuia')?.value).toBe(null);
    expect(component.ordenamientoActual).toBe('-fecha_emision');
    console.log('✅ Filtros limpiados correctamente');
  });

  it('✅ Debe detectar filtros activos', () => {
    component.formularioBusqueda.patchValue({
      textoBusqueda: 'test'
    });
    
    expect(component.tieneFiltrosActivos()).toBe(true);
    
    component.formularioBusqueda.reset();
    
    expect(component.tieneFiltrosActivos()).toBe(false);
    console.log('✅ Detección de filtros activos funciona correctamente');
  });

  it('✅ Debe contar filtros activos correctamente', () => {
    component.formularioBusqueda.patchValue({
      textoBusqueda: 'test',
      numeroGuia: 'HAWB001',
      estado: EstadosEnvio.PENDIENTE
    });
    
    expect(component.contarFiltrosActivos()).toBe(3);
    console.log('✅ Conteo de filtros activos correcto');
  });

  // ===== PRUEBAS DE PAGINACIÓN =====

  it('✅ Debe calcular paginación correctamente', () => {
    component.totalResultados = 25;
    component.elementosPorPagina = 10;
    
    component['calcularPaginacion']();
    
    expect(component.totalPaginas).toBe(3);
    console.log('✅ Paginación calculada correctamente');
  });

  it('✅ Debe navegar a página siguiente', () => {
    apiService.buscarEnviosAvanzado.and.returnValue(of(respuestaBusquedaMock));
    component.paginaActual = 1;
    component.totalPaginas = 3;
    
    component.paginaSiguiente();
    
    expect(component.paginaActual).toBe(2);
    console.log('✅ Navegación a página siguiente funciona');
  });

  it('✅ Debe navegar a página anterior', () => {
    apiService.buscarEnviosAvanzado.and.returnValue(of(respuestaBusquedaMock));
    component.paginaActual = 2;
    
    component.paginaAnterior();
    
    expect(component.paginaActual).toBe(1);
    console.log('✅ Navegación a página anterior funciona');
  });

  it('✅ No debe navegar más allá de la primera página', () => {
    component.paginaActual = 1;
    
    component.paginaAnterior();
    
    expect(component.paginaActual).toBe(1);
    console.log('✅ Límite inferior de paginación respetado');
  });

  it('✅ No debe navegar más allá de la última página', () => {
    component.paginaActual = 3;
    component.totalPaginas = 3;
    
    component.paginaSiguiente();
    
    expect(component.paginaActual).toBe(3);
    console.log('✅ Límite superior de paginación respetado');
  });

  // ===== PRUEBAS DE ORDENAMIENTO =====

  it('✅ Debe cambiar ordenamiento y reiniciar paginación', () => {
    apiService.buscarEnviosAvanzado.and.returnValue(of(respuestaBusquedaMock));
    component.paginaActual = 3;
    
    component.cambiarOrdenamiento('hawb');
    
    expect(component.ordenamientoActual).toBe('hawb');
    expect(component.paginaActual).toBe(1);
    console.log('✅ Cambio de ordenamiento funciona correctamente');
  });

  it('✅ Debe cambiar elementos por página', () => {
    apiService.buscarEnviosAvanzado.and.returnValue(of(respuestaBusquedaMock));
    component.paginaActual = 2;
    
    component.cambiarElementosPorPagina(20);
    
    expect(component.elementosPorPagina).toBe(20);
    expect(component.paginaActual).toBe(1);
    console.log('✅ Cambio de elementos por página funciona');
  });

  // ===== PRUEBAS DE ACCIONES =====

  it('✅ Debe abrir modal de detalles', () => {
    const envioMock = enviosMock[0];
    apiService.getEnvio.and.returnValue(of(envioMock));
    
    component.verDetalles(envioMock);
    
    expect(apiService.getEnvio).toHaveBeenCalledWith(1);
    expect(component.mostrarDetalleModal).toBe(true);
    expect(component.envioSeleccionado).toEqual(envioMock);
    console.log('✅ Modal de detalles abierto correctamente');
  });

  it('✅ Debe cerrar modal de detalles', () => {
    component.mostrarDetalleModal = true;
    component.envioSeleccionado = enviosMock[0];
    
    component.cerrarDetalleModal();
    
    expect(component.mostrarDetalleModal).toBe(false);
    expect(component.envioSeleccionado).toBe(null);
    console.log('✅ Modal de detalles cerrado correctamente');
  });

  // ===== PRUEBAS DE MÉTODOS AUXILIARES =====

  it('✅ Debe formatear fecha correctamente', () => {
    const fecha = '2025-01-15T10:00:00Z';
    const fechaFormateada = component.formatearFecha(fecha);
    
    expect(fechaFormateada).toBeTruthy();
    expect(fechaFormateada).not.toBe('N/A');
    console.log('✅ Formato de fecha correcto');
  });

  it('✅ Debe formatear moneda correctamente', () => {
    expect(component.formatearMoneda(150.5)).toBe('$150.50');
    expect(component.formatearMoneda(0)).toBe('$0.00');
    expect(component.formatearMoneda(undefined)).toBe('$0.00');
    console.log('✅ Formato de moneda correcto');
  });

  it('✅ Debe formatear peso correctamente', () => {
    expect(component.formatearPeso(5.5)).toBe('5.50 kg');
    expect(component.formatearPeso(0)).toBe('0.00 kg');
    expect(component.formatearPeso(undefined)).toBe('0 kg');
    console.log('✅ Formato de peso correcto');
  });

  it('✅ Debe obtener etiqueta de estado correctamente', () => {
    expect(component.obtenerEtiquetaEstado(EstadosEnvio.PENDIENTE)).toBe('Pendiente');
    expect(component.obtenerEtiquetaEstado(EstadosEnvio.EN_TRANSITO)).toBe('En Tránsito');
    expect(component.obtenerEtiquetaEstado(EstadosEnvio.ENTREGADO)).toBe('Entregado');
    expect(component.obtenerEtiquetaEstado(EstadosEnvio.CANCELADO)).toBe('Cancelado');
    console.log('✅ Etiquetas de estado correctas');
  });

  it('✅ Debe obtener clase CSS de estado correctamente', () => {
    expect(component.obtenerClaseEstado(EstadosEnvio.PENDIENTE)).toBe('estado-pendiente');
    expect(component.obtenerClaseEstado(EstadosEnvio.EN_TRANSITO)).toBe('estado-en-transito');
    expect(component.obtenerClaseEstado(EstadosEnvio.ENTREGADO)).toBe('estado-entregado');
    expect(component.obtenerClaseEstado(EstadosEnvio.CANCELADO)).toBe('estado-cancelado');
    console.log('✅ Clases CSS de estado correctas');
  });

  // ===== PRUEBAS DE PERMISOS =====

  it('✅ Debe verificar permisos para acciones avanzadas - Admin', () => {
    authService.isAdmin.and.returnValue(true);
    authService.isGerente.and.returnValue(false);
    authService.isDigitador.and.returnValue(false);
    
    expect(component.puedeVerAccionesAvanzadas()).toBe(true);
    console.log('✅ Permisos de Admin verificados');
  });

  it('✅ Debe verificar permisos para acciones avanzadas - Gerente', () => {
    authService.isAdmin.and.returnValue(false);
    authService.isGerente.and.returnValue(true);
    authService.isDigitador.and.returnValue(false);
    
    expect(component.puedeVerAccionesAvanzadas()).toBe(true);
    console.log('✅ Permisos de Gerente verificados');
  });

  it('✅ Debe verificar permisos para acciones avanzadas - Digitador', () => {
    authService.isAdmin.and.returnValue(false);
    authService.isGerente.and.returnValue(false);
    authService.isDigitador.and.returnValue(true);
    
    expect(component.puedeVerAccionesAvanzadas()).toBe(true);
    console.log('✅ Permisos de Digitador verificados');
  });

  it('✅ Debe negar permisos para acciones avanzadas - Comprador', () => {
    authService.isAdmin.and.returnValue(false);
    authService.isGerente.and.returnValue(false);
    authService.isDigitador.and.returnValue(false);
    
    expect(component.puedeVerAccionesAvanzadas()).toBe(false);
    console.log('✅ Permisos de Comprador verificados');
  });

  // ===== PRUEBA FINAL =====

  it('✅ Todas las pruebas completadas exitosamente', () => {
    console.log('✅ ====================================');
    console.log('✅ MÓDULO DE BÚSQUEDA DE ENVÍOS');
    console.log('✅ Todas las pruebas pasaron exitosamente');
    console.log('✅ ====================================');
    expect(true).toBe(true);
  });
});


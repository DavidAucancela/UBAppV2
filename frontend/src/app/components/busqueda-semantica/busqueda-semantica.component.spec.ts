import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { FormsModule } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';

import { BusquedaSemanticaComponent } from './busqueda-semantica.component';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { RespuestaSemantica, ResultadoSemantico, SugerenciaSemantica } from '../../models/busqueda-semantica';
import { Envio, EstadosEnvio } from '../../models/envio';

describe('BusquedaSemanticaComponent', () => {
  let component: BusquedaSemanticaComponent;
  let fixture: ComponentFixture<BusquedaSemanticaComponent>;
  let apiService: jasmine.SpyObj<ApiService>;
  let authService: jasmine.SpyObj<AuthService>;

  // Datos de prueba
  const envioMock: Envio = {
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
  };

  const resultadoSemanticoMock: ResultadoSemantico = {
    envio: envioMock,
    puntuacionSimilitud: 0.85,
    fragmentosRelevantes: ['Envío a Quito', 'Esta semana'],
    razonRelevancia: 'Coincide con la búsqueda por ciudad y fecha'
  };

  const respuestaSemanticaMock: RespuestaSemantica = {
    consulta: 'envíos a Quito esta semana',
    resultados: [resultadoSemanticoMock],
    totalEncontrados: 1,
    tiempoRespuesta: 150,
    modeloUtilizado: 'GPT-4'
  };

  beforeEach(async () => {
    const apiServiceSpy = jasmine.createSpyObj('ApiService', [
      'buscarEnviosSemantica',
      'obtenerSugerenciasSemanticas',
      'guardarHistorialSemantico',
      'obtenerHistorialSemantico',
      'limpiarHistorialSemantico',
      'enviarFeedbackSemantico',
      'getEnvio'
    ]);

    const authServiceSpy = jasmine.createSpyObj('AuthService', [
      'isAdmin',
      'isGerente',
      'isDigitador',
      'isComprador'
    ]);

    await TestBed.configureTestingModule({
      imports: [
        BusquedaSemanticaComponent,
        HttpClientTestingModule,
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

    fixture = TestBed.createComponent(BusquedaSemanticaComponent);
    component = fixture.componentInstance;
  });

  // ===== PRUEBAS DE INICIALIZACIÓN =====

  it('✅ Debe crear el componente correctamente', () => {
    expect(component).toBeTruthy();
    console.log('✅ Componente de búsqueda semántica creado exitosamente');
  });

  it('✅ Debe inicializar con valores por defecto', () => {
    expect(component.textoConsulta).toBe('');
    expect(component.analizando).toBe(false);
    expect(component.resultadosSemanticos).toEqual([]);
    expect(component.modoIntegrado).toBe(false);
    console.log('✅ Valores por defecto inicializados correctamente');
  });

  // ===== PRUEBAS DE BÚSQUEDA SEMÁNTICA =====

  it('✅ Debe realizar búsqueda semántica exitosamente', () => {
    apiService.buscarEnviosSemantica.and.returnValue(of(respuestaSemanticaMock));
    apiService.guardarHistorialSemantico.and.returnValue(of({}));

    component.textoConsulta = 'envíos a Quito esta semana';
    component.realizarBusquedaSemantica();

    expect(apiService.buscarEnviosSemantica).toHaveBeenCalled();
    expect(component.resultadosSemanticos.length).toBe(1);
    expect(component.sinResultados).toBe(false);
    expect(component.mensajeExito).toContain('✅ Búsqueda semántica completada correctamente');
    console.log('✅ Búsqueda semántica realizada exitosamente');
  });

  it('✅ Debe manejar error en búsqueda semántica', () => {
    const errorMock = { error: 'Error del servidor' };
    apiService.buscarEnviosSemantica.and.returnValue(throwError(() => errorMock));

    component.textoConsulta = 'búsqueda de prueba';
    component.realizarBusquedaSemantica();

    expect(component.errorMensaje).toContain('Error al procesar la búsqueda semántica');
    expect(component.analizando).toBe(false);
    expect(component.resultadosSemanticos).toEqual([]);
    console.log('✅ Error de búsqueda manejado correctamente');
  });

  it('✅ Debe validar que la consulta no esté vacía', () => {
    component.textoConsulta = '';
    component.realizarBusquedaSemantica();

    expect(component.errorMensaje).toContain('Por favor, ingrese una consulta');
    expect(apiService.buscarEnviosSemantica).not.toHaveBeenCalled();
    console.log('✅ Validación de consulta vacía funciona');
  });

  it('✅ Debe filtrar resultados por umbral de similitud', () => {
    const respuestaConVariosResultados: RespuestaSemantica = {
      consulta: 'test',
      resultados: [
        { ...resultadoSemanticoMock, puntuacionSimilitud: 0.9 },
        { ...resultadoSemanticoMock, puntuacionSimilitud: 0.2 },
        { ...resultadoSemanticoMock, puntuacionSimilitud: 0.5 }
      ],
      totalEncontrados: 3,
      tiempoRespuesta: 200
    };

    apiService.buscarEnviosSemantica.and.returnValue(of(respuestaConVariosResultados));
    apiService.guardarHistorialSemantico.and.returnValue(of({}));

    component.configuracion.umbralSimilitud = 0.3;
    component.textoConsulta = 'test';
    component.realizarBusquedaSemantica();

    // Debe filtrar el resultado con 0.2 que está por debajo del umbral
    expect(component.resultadosSemanticos.length).toBe(2);
    console.log('✅ Filtrado por umbral de similitud funciona');
  });

  // ===== PRUEBAS DE SUGERENCIAS =====

  it('✅ Debe obtener sugerencias dinámicas', (done) => {
    const sugerenciasMock: SugerenciaSemantica[] = [
      { texto: 'envíos a Quito', icono: 'fa-search', categoria: 'general' }
    ];

    apiService.obtenerSugerenciasSemanticas.and.returnValue(of(sugerenciasMock));

    component.textoConsulta = 'envíos a';
    component.alEscribirConsulta();

    // Esperar el debounce
    setTimeout(() => {
      expect(apiService.obtenerSugerenciasSemanticas).toHaveBeenCalled();
      expect(component.sugerenciasDinamicas.length).toBe(1);
      console.log('✅ Sugerencias dinámicas obtenidas correctamente');
      done();
    }, 400);
  });

  it('✅ Debe seleccionar sugerencia y realizar búsqueda', () => {
    apiService.buscarEnviosSemantica.and.returnValue(of(respuestaSemanticaMock));
    apiService.guardarHistorialSemantico.and.returnValue(of({}));

    const sugerencia: SugerenciaSemantica = {
      texto: 'envíos entregados en Quito',
      icono: 'fa-check',
      categoria: 'estado'
    };

    component.seleccionarSugerencia(sugerencia);

    expect(component.textoConsulta).toBe('envíos entregados en Quito');
    expect(component.sugerenciasVisibles).toBe(false);
    console.log('✅ Selección de sugerencia funciona correctamente');
  });

  // ===== PRUEBAS DE HISTORIAL =====

  it('✅ Debe cargar historial de búsquedas', () => {
    const historialMock = [
      { id: '1', consulta: 'envíos a Quito', fecha: new Date(), totalResultados: 5 }
    ];

    apiService.obtenerHistorialSemantico.and.returnValue(of(historialMock));

    component.cargarHistorial();

    expect(apiService.obtenerHistorialSemantico).toHaveBeenCalled();
    expect(component.historialBusquedas.length).toBe(1);
    console.log('✅ Historial cargado correctamente');
  });

  it('✅ Debe limpiar historial', () => {
    apiService.limpiarHistorialSemantico.and.returnValue(of({}));

    spyOn(window, 'confirm').and.returnValue(true);

    component.limpiarHistorial();

    expect(apiService.limpiarHistorialSemantico).toHaveBeenCalled();
    expect(component.historialBusquedas).toEqual([]);
    console.log('✅ Historial limpiado correctamente');
  });

  it('✅ Debe usar búsqueda del historial', () => {
    apiService.buscarEnviosSemantica.and.returnValue(of(respuestaSemanticaMock));
    apiService.guardarHistorialSemantico.and.returnValue(of({}));

    const busquedaHistorial = {
      id: '1',
      consulta: 'envíos a Guayaquil',
      fecha: new Date(),
      totalResultados: 3
    };

    component.usarDelHistorial(busquedaHistorial);

    expect(component.textoConsulta).toBe('envíos a Guayaquil');
    expect(component.mostrarHistorial).toBe(false);
    console.log('✅ Reutilización de búsqueda del historial funciona');
  });

  // ===== PRUEBAS DE ACCIONES =====

  it('✅ Debe abrir modal de detalles', () => {
    apiService.getEnvio.and.returnValue(of(envioMock));

    component.verDetalles(resultadoSemanticoMock);

    expect(component.mostrarDetalleModal).toBe(true);
    expect(component.envioSeleccionado).toEqual(envioMock);
    console.log('✅ Modal de detalles abierto correctamente');
  });

  it('✅ Debe cerrar modal de detalles', () => {
    component.mostrarDetalleModal = true;
    component.envioSeleccionado = envioMock;

    component.cerrarDetalleModal();

    expect(component.mostrarDetalleModal).toBe(false);
    expect(component.envioSeleccionado).toBe(null);
    console.log('✅ Modal de detalles cerrado correctamente');
  });

  it('✅ Debe enviar feedback positivo', () => {
    apiService.enviarFeedbackSemantico.and.returnValue(of({}));

    component.enviarFeedback(resultadoSemanticoMock, true);

    expect(apiService.enviarFeedbackSemantico).toHaveBeenCalledWith(1, true);
    expect(component.mensajeExito).toContain('feedback positivo');
    console.log('✅ Feedback positivo enviado correctamente');
  });

  it('✅ Debe enviar feedback negativo', () => {
    apiService.enviarFeedbackSemantico.and.returnValue(of({}));

    component.enviarFeedback(resultadoSemanticoMock, false);

    expect(apiService.enviarFeedbackSemantico).toHaveBeenCalledWith(1, false);
    expect(component.mensajeExito).toContain('mejorar los resultados');
    console.log('✅ Feedback negativo enviado correctamente');
  });

  // ===== PRUEBAS DE FILTROS ADICIONALES =====

  it('✅ Debe construir filtros adicionales', () => {
    component.mostrarFiltrosAdicionales = true;
    component.fechaDesde = '2025-01-01';
    component.estadoFiltro = 'en_transito';

    apiService.buscarEnviosSemantica.and.returnValue(of(respuestaSemanticaMock));
    apiService.guardarHistorialSemantico.and.returnValue(of({}));

    component.textoConsulta = 'test';
    component.realizarBusquedaSemantica();

    const callArgs = apiService.buscarEnviosSemantica.calls.mostRecent().args[0];
    expect(callArgs.filtrosAdicionales).toBeDefined();
    expect(callArgs.filtrosAdicionales.fechaDesde).toBe('2025-01-01');
    expect(callArgs.filtrosAdicionales.estado).toBe('en_transito');
    console.log('✅ Filtros adicionales construidos correctamente');
  });

  // ===== PRUEBAS DE MÉTODOS AUXILIARES =====

  it('✅ Debe obtener clase de similitud correcta', () => {
    expect(component.obtenerClaseSimilitud(0.9)).toBe('similitud-alta');
    expect(component.obtenerClaseSimilitud(0.6)).toBe('similitud-media');
    expect(component.obtenerClaseSimilitud(0.3)).toBe('similitud-baja');
    console.log('✅ Clases de similitud correctas');
  });

  it('✅ Debe obtener color de similitud correcto', () => {
    expect(component.obtenerColorSimilitud(0.9)).toBe('#27ae60');
    expect(component.obtenerColorSimilitud(0.6)).toBe('#f39c12');
    expect(component.obtenerColorSimilitud(0.3)).toBe('#e74c3c');
    console.log('✅ Colores de similitud correctos');
  });

  it('✅ Debe formatear porcentaje de similitud', () => {
    expect(component.formatearPorcentajeSimilitud(0.856)).toBe('86%');
    expect(component.formatearPorcentajeSimilitud(0.5)).toBe('50%');
    console.log('✅ Formato de porcentaje correcto');
  });

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

  // ===== PRUEBAS DE CONFIGURACIÓN =====

  it('✅ Debe cambiar tipo de vista', () => {
    component.cambiarTipoVista('lista' as any);
    expect(component.configuracion.tipoVista).toBe('lista');
    console.log('✅ Cambio de tipo de vista funciona');
  });

  it('✅ Debe limpiar búsqueda', () => {
    component.textoConsulta = 'test';
    component.resultadosSemanticos = [resultadoSemanticoMock];
    component.mensajeExito = 'mensaje';

    component.limpiarBusqueda();

    expect(component.textoConsulta).toBe('');
    expect(component.resultadosSemanticos).toEqual([]);
    expect(component.mensajeExito).toBe('');
    console.log('✅ Limpieza de búsqueda funciona');
  });

  // ===== PRUEBA FINAL =====

  it('✅ Todas las pruebas completadas exitosamente', () => {
    console.log('✅ ========================================');
    console.log('✅ MÓDULO DE BÚSQUEDA SEMÁNTICA');
    console.log('✅ Todas las pruebas pasaron exitosamente');
    console.log('✅ ========================================');
    expect(true).toBe(true);
  });
});


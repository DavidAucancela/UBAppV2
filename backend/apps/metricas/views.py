"""
Views para la app de métricas.
Endpoints REST para el Dashboard de Pruebas y Métricas.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta

from apps.core.base.base_service import BaseService
from apps.core.pagination import CustomPageNumberPagination
from .models import (
    PruebaControladaSemantica,
    MetricaSemantica,
    RegistroGeneracionEmbedding,
    PruebaCarga,
    MetricaRendimiento,
    RegistroManualEnvio,
    PruebaRendimientoCompleta,
    DetalleProcesoRendimiento
)
from .serializers import (
    PruebaControladaSemanticaSerializer,
    MetricaSemanticaSerializer,
    RegistroGeneracionEmbeddingSerializer,
    PruebaCargaSerializer,
    MetricaRendimientoSerializer,
    RegistroManualEnvioSerializer,
    EjecutarPruebaControladaSerializer,
    EjecutarPruebaCargaSerializer,
    RegistrarEnvioManualSerializer,
    PruebaRendimientoCompletaSerializer,
    DetalleProcesoRendimientoSerializer
)
from .services import (
    MetricaSemanticaService,
    RegistroEmbeddingService,
    MetricaRendimientoService,
    ExportacionMetricasService
)
from .repositories import (
    prueba_controlada_repository,
    metrica_semantica_repository,
    registro_embedding_repository,
    prueba_carga_repository,
    metrica_rendimiento_repository,
    registro_manual_repository
)


class PruebaControladaSemanticaViewSet(viewsets.ModelViewSet):
    """ViewSet para Pruebas Controladas Semánticas"""
    queryset = PruebaControladaSemantica.objects.all()
    serializer_class = PruebaControladaSemanticaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra por pruebas activas si se solicita"""
        queryset = super().get_queryset()
        activa = self.request.query_params.get('activa', None)
        if activa is not None:
            queryset = queryset.filter(activa=activa.lower() == 'true')
        return queryset
    
    @action(detail=True, methods=['post'])
    def ejecutar(self, request, pk=None):
        """Ejecuta una prueba controlada y calcula métricas"""
        BaseService.validar_es_admin(request.user)
        
        prueba = self.get_object()
        serializer = EjecutarPruebaControladaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            metrica = MetricaSemanticaService.ejecutar_prueba_controlada(
                prueba=prueba,
                usuario=request.user,
                filtros=serializer.validated_data.get('filtros'),
                limite=serializer.validated_data.get('limite', 20)
            )
            
            return Response({
                'mensaje': 'Prueba ejecutada exitosamente',
                'metrica': MetricaSemanticaSerializer(metrica).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            BaseService.log_error(e, "Error ejecutando prueba controlada", usuario_id=request.user.id)
            return Response(
                {'error': f'Error ejecutando prueba: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MetricaSemanticaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Métricas Semánticas (solo lectura)"""
    queryset = MetricaSemantica.objects.all()
    serializer_class = MetricaSemanticaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        """Filtra por rango de fechas si se proporciona"""
        queryset = super().get_queryset()
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        
        if fecha_desde:
            queryset = queryset.filter(fecha_calculo__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_calculo__lte=fecha_hasta)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas agregadas de métricas semánticas"""
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)
        
        estadisticas = MetricaSemanticaService.obtener_estadisticas(fecha_desde, fecha_hasta)
        return Response(estadisticas)

    @action(detail=False, methods=['get'], url_path='reporte-comparativo')
    def reporte_comparativo(self, request):
        """
        Obtiene reporte comparativo de eficiencia del panel semántico.
        Tabla de MRR, NDCG@10, Precision@5 por evaluación + resumen con interpretación.
        """
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)
        
        reporte = MetricaSemanticaService.obtener_reporte_comparativo(fecha_desde, fecha_hasta)
        return Response(reporte)


class RegistroGeneracionEmbeddingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Registros de Generación de Embeddings (solo lectura)"""
    queryset = RegistroGeneracionEmbedding.objects.all()
    serializer_class = RegistroGeneracionEmbeddingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        """Filtra por estado y tipo de proceso"""
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado', None)
        tipo_proceso = self.request.query_params.get('tipo_proceso', None)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        if tipo_proceso:
            queryset = queryset.filter(tipo_proceso=tipo_proceso)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de generación de embeddings"""
        estadisticas = RegistroEmbeddingService.obtener_estadisticas()
        return Response(estadisticas)


class PruebaCargaViewSet(viewsets.ModelViewSet):
    """ViewSet para Pruebas de Carga"""
    queryset = PruebaCarga.objects.all()
    serializer_class = PruebaCargaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra por tipo de prueba, nivel de carga y fechas"""
        queryset = super().get_queryset()
        tipo_prueba = self.request.query_params.get('tipo_prueba', None)
        nivel_carga = self.request.query_params.get('nivel_carga', None)
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        
        if tipo_prueba:
            queryset = queryset.filter(tipo_prueba=tipo_prueba)
        if nivel_carga:
            queryset = queryset.filter(nivel_carga=int(nivel_carga))
        if fecha_desde:
            queryset = queryset.filter(fecha_ejecucion__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_ejecucion__lte=fecha_hasta)
        
        return queryset.order_by('-fecha_ejecucion')
    
    @action(detail=False, methods=['post'])
    def ejecutar_busqueda(self, request):
        """Ejecuta una prueba de carga de búsqueda semántica"""
        BaseService.validar_es_admin(request.user)
        
        serializer = EjecutarPruebaCargaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            prueba = MetricaRendimientoService.ejecutar_prueba_carga_busqueda(
                nivel_carga=serializer.validated_data['nivel_carga'],
                consultas=serializer.validated_data['consultas'],
                usuario=request.user,
                nombre_prueba=serializer.validated_data.get('nombre_prueba')
            )
            
            return Response({
                'mensaje': 'Prueba de carga ejecutada exitosamente',
                'prueba': PruebaCargaSerializer(prueba).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            BaseService.log_error(e, "Error ejecutando prueba de carga", usuario_id=request.user.id)
            return Response(
                {'error': f'Error ejecutando prueba: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MetricaRendimientoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Métricas de Rendimiento (solo lectura)"""
    queryset = MetricaRendimiento.objects.all()
    serializer_class = MetricaRendimientoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra por proceso y nivel de carga"""
        queryset = super().get_queryset()
        proceso = self.request.query_params.get('proceso', None)
        nivel_carga = self.request.query_params.get('nivel_carga', None)
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        
        if proceso:
            queryset = queryset.filter(proceso=proceso)
        if nivel_carga:
            queryset = queryset.filter(nivel_carga=int(nivel_carga))
        if fecha_desde:
            queryset = queryset.filter(fecha_medicion__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_medicion__lte=fecha_hasta)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de rendimiento"""
        proceso = request.query_params.get('proceso', None)
        nivel_carga = request.query_params.get('nivel_carga', None)
        
        if nivel_carga:
            nivel_carga = int(nivel_carga)
        
        estadisticas = MetricaRendimientoService.obtener_estadisticas_rendimiento(
            proceso=proceso,
            nivel_carga=nivel_carga
        )
        return Response(estadisticas)


class RegistroManualEnvioViewSet(viewsets.ModelViewSet):
    """ViewSet para Registros Manuales de Envíos"""
    queryset = RegistroManualEnvio.objects.all()
    serializer_class = RegistroManualEnvioSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Asigna el usuario actual al crear"""
        serializer.save(registrado_por=self.request.user)
    
    @action(detail=False, methods=['post'])
    def registrar(self, request):
        """Registra un tiempo de registro manual de envío"""
        serializer = RegistrarEnvioManualSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            registro = MetricaRendimientoService.registrar_envio_manual(
                hawb=serializer.validated_data['hawb'],
                tiempo_registro_segundos=serializer.validated_data['tiempo_registro_segundos'],
                usuario=request.user,
                datos_envio=serializer.validated_data.get('datos_envio'),
                notas=serializer.validated_data.get('notas')
            )
            
            return Response({
                'mensaje': 'Registro manual guardado exitosamente',
                'registro': RegistroManualEnvioSerializer(registro).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            BaseService.log_error(e, "Error registrando envío manual", usuario_id=request.user.id)
            return Response(
                {'error': f'Error registrando: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de registros manuales"""
        estadisticas = registro_manual_repository.obtener_estadisticas()
        return Response(estadisticas)


class ExportacionMetricasViewSet(viewsets.ViewSet):
    """ViewSet para exportación de métricas a CSV"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def metricas_semanticas(self, request):
        """Exporta métricas semánticas a CSV"""
        BaseService.validar_es_admin(request.user)
        
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)
        
        csv_content = ExportacionMetricasService.exportar_metricas_semanticas_csv(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
        
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="metricas_semanticas.csv"'
        return response
    
    @action(detail=False, methods=['get'])
    def metricas_rendimiento(self, request):
        """Exporta métricas de rendimiento a CSV"""
        BaseService.validar_es_admin(request.user)
        
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)
        
        csv_content = ExportacionMetricasService.exportar_metricas_rendimiento_csv(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
        
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="metricas_rendimiento.csv"'
        return response
    
    @action(detail=False, methods=['get'])
    def pruebas_carga(self, request):
        """Exporta pruebas de carga a CSV"""
        BaseService.validar_es_admin(request.user)
        
        csv_content = ExportacionMetricasService.exportar_pruebas_carga_csv()
        
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pruebas_carga.csv"'
        return response


class PruebasSistemaViewSet(viewsets.ViewSet):
    """ViewSet para ejecutar y visualizar pruebas del sistema"""
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Desactivar paginación por defecto
    
    @action(detail=False, methods=['post'])
    def ejecutar_rendimiento(self, request):
        """
        Ejecuta las pruebas de rendimiento del sistema (versión optimizada para dashboard)
        NOTA: Esta versión es más rápida que el comando completo
        """
        BaseService.validar_es_admin(request.user)
        
        import time
        import statistics
        import psutil
        import os
        from decimal import Decimal
        from apps.archivos.services import EnvioService
        from apps.archivos.models import Envio
        from apps.busqueda.services import BusquedaSemanticaService
        from django.contrib.auth import get_user_model
        
        Usuario = get_user_model()
        
        try:
            resultados = {
                'fecha_inicio': timezone.now().isoformat(),
                'usuario': request.user.username
            }
            
            # Obtener comprador para pruebas
            comprador = Usuario.objects.filter(rol=4).first()
            if not comprador:
                return Response(
                    {'error': 'No hay compradores disponibles para pruebas'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            salida = []
            salida.append("="*80)
            salida.append("PRUEBAS DE RENDIMIENTO DEL SISTEMA (Versión Rápida)")
            salida.append("="*80)
            salida.append(f"Usuario: {request.user.username}")
            salida.append(f"Fecha: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
            salida.append("")
            
            # 1. TIEMPO DE RESPUESTA: Registro de Envíos (5 iteraciones rápidas)
            salida.append("1. TIEMPO DE RESPUESTA - Registro de Envíos")
            tiempos_web = []
            
            for i in range(5):  # Solo 5 en lugar de 30
                datos_envio = {
                    'hawb': f'TEST-PERF-{int(time.time())}-{i}',
                    'peso_total': Decimal('10.50'),
                    'cantidad_total': 1,
                    'valor_total': Decimal('100.00'),
                    'comprador': comprador,
                    'estado': 'pendiente',
                    'productos': [{
                        'descripcion': f'Producto test {i}',
                        'categoria': 'electronica',
                        'peso': Decimal('5.25'),
                        'cantidad': 1,
                        'valor': Decimal('50.00')
                    }]
                }
                
                inicio = time.time()
                try:
                    envio = EnvioService.crear_envio(datos_envio, request.user)
                    tiempo_seg = time.time() - inicio
                    tiempos_web.append(tiempo_seg)
                    envio.delete()  # Limpiar
                except Exception as e:
                    salida.append(f"  Error en iteración {i+1}: {str(e)}")
            
            if tiempos_web:
                media_web = statistics.mean(tiempos_web)
                salida.append(f"  Tiempo promedio (sistema web): {media_web:.4f} segundos")
                salida.append(f"  Tiempo manual estimado: 240 segundos")
                mejora = 240 / media_web if media_web > 0 else 0
                salida.append(f"  Mejora: {mejora:.1f}x más rápido")
                resultados['tiempo_respuesta'] = {
                    'web_promedio': media_web,
                    'manual_estimado': 240,
                    'mejora': mejora
                }
            
            salida.append("")
            
            # 2. TIEMPO DE ESPERA: Búsqueda (SIN embeddings reales, solo búsqueda básica)
            salida.append("2. TIEMPO DE ESPERA - Búsqueda Básica (sin OpenAI)")
            cargas = [1, 5, 10]  # Reducido de 1, 10, 30
            
            for carga in cargas:
                tiempos = []
                for rep in range(3):  # Solo 3 repeticiones
                    inicio = time.time()
                    for i in range(carga):
                        # Búsqueda básica SIN llamar a OpenAI
                        Envio.objects.filter(estado='pendiente')[:10]
                    tiempo_total = (time.time() - inicio) * 1000
                    tiempos.append(tiempo_total)
                
                if tiempos:
                    media = statistics.mean(tiempos)
                    salida.append(f"  Carga {carga}: {media:.2f} ms promedio")
            
            salida.append("")
            
            # 3. UTILIZACIÓN DE RECURSOS: Registro (solo 3 iteraciones)
            salida.append("3. UTILIZACIÓN DE RECURSOS - Registro")
            proceso = psutil.Process(os.getpid())
            
            for carga in [1, 5]:  # Solo 2 cargas
                cpus = []
                mems = []
                
                for rep in range(2):  # Solo 2 repeticiones
                    proceso.cpu_percent()
                    mem_inicial = proceso.memory_info().rss / 1024 / 1024
                    
                    for i in range(carga):
                        datos = {
                            'hawb': f'TEST-REC-{int(time.time())}-{rep}-{i}',
                            'peso_total': Decimal('5.0'),
                            'cantidad_total': 1,
                            'valor_total': Decimal('50.00'),
                            'comprador': comprador,
                            'estado': 'pendiente',
                            'productos': [{
                                'descripcion': 'Test',
                                'categoria': 'electronica',
                                'peso': Decimal('5.0'),
                                'cantidad': 1,
                                'valor': Decimal('50.00')
                            }]
                        }
                        try:
                            envio = EnvioService.crear_envio(datos, request.user)
                            cpu = proceso.cpu_percent(interval=0.1)
                            mem = proceso.memory_info().rss / 1024 / 1024
                            cpus.append(cpu)
                            mems.append(mem - mem_inicial)
                            envio.delete()
                        except:
                            pass
                
                if cpus and mems:
                    cpu_prom = statistics.mean(cpus)
                    mem_prom = statistics.mean(mems)
                    salida.append(f"  Carga {carga}: CPU={cpu_prom:.2f}%, RAM={mem_prom:.2f}MB")
            
            salida.append("")
            salida.append("="*80)
            salida.append("PRUEBAS COMPLETADAS")
            salida.append("="*80)
            salida.append("")
            salida.append("NOTA: Esta es una versión optimizada para el dashboard.")
            salida.append("Para pruebas completas, ejecute desde terminal:")
            salida.append("  python manage.py pruebas_rendimiento --usuario admin")
            salida.append("")
            
            return Response({
                'mensaje': 'Pruebas de rendimiento ejecutadas exitosamente',
                'salida': '\n'.join(salida),
                'fecha_ejecucion': timezone.now().isoformat(),
                'resultados': resultados
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            BaseService.log_error(e, "Error ejecutando pruebas de rendimiento", usuario_id=request.user.id)
            return Response(
                {'error': f'Error ejecutando pruebas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def ejecutar_tests(self, request):
        """
        Ejecuta los tests unitarios del sistema y retorna resultados
        """
        try:
            BaseService.validar_es_admin(request.user)
        except Exception as e:
            return Response(
                {'error': f'No tiene permisos para ejecutar tests: {str(e)}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from io import StringIO
        import sys
        from django.test.utils import get_runner
        from django.conf import settings
        
        try:
            # Obtener parámetros
            app_name = request.data.get('app', None)  # ej: 'archivos', 'busqueda', 'usuarios'
            test_suite = request.data.get('test_suite', None)  # ej: 'EnvioTestCase'
            
            # Preparar argumentos
            if app_name and test_suite:
                test_labels = [f'apps.{app_name}.tests.{test_suite}']
            elif app_name:
                test_labels = [f'apps.{app_name}']
            else:
                test_labels = []
            
            # Capturar salida
            output = StringIO()
            sys.stdout = output
            sys.stderr = output
            
            # Ejecutar tests
            TestRunner = get_runner(settings)
            test_runner = TestRunner(verbosity=2, interactive=False, keepdb=True)
            failures = test_runner.run_tests(test_labels)
            
            # Restaurar stdout/stderr
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            
            # Obtener salida
            output_text = output.getvalue()
            
            # Analizar resultados
            resultado = {
                'mensaje': 'Tests ejecutados',
                'exitoso': failures == 0,
                'total_fallos': failures,
                'salida': output_text,
                'fecha_ejecucion': timezone.now().isoformat()
            }
            
            return Response(resultado, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Restaurar stdout/stderr
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            
            BaseService.log_error(e, "Error ejecutando tests", usuario_id=request.user.id)
            return Response(
                {'error': f'Error ejecutando tests: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def listar_tests(self, request):
        """Lista todos los tests disponibles en el sistema"""
        try:
            BaseService.validar_es_admin(request.user)
        except Exception as e:
            return Response(
                {'error': f'No tiene permisos para acceder a esta información: {str(e)}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            tests_disponibles = {
                'archivos': {
                    'nombre': 'Envíos, Productos y Tarifas',
                    'suites': [
                        {'nombre': 'EnvioTestCase', 'descripcion': 'Tests básicos de envíos'},
                        {'nombre': 'TarifaTestCase', 'descripcion': 'Tests de tarifas'},
                        {'nombre': 'EnvioPerformanceTestCase', 'descripcion': 'Tests de rendimiento de envíos'},
                    ]
                },
                'busqueda': {
                    'nombre': 'Búsqueda Semántica',
                    'suites': [
                        {'nombre': 'BusquedaSemanticaTestCase', 'descripcion': 'Tests de búsqueda semántica'},
                        {'nombre': 'BusquedaSemanticaPerformanceTestCase', 'descripcion': 'Tests de rendimiento'},
                        {'nombre': 'BusquedaSemanticaPrecisionTestCase', 'descripcion': 'Tests de precisión'},
                    ]
                },
                'usuarios': {
                    'nombre': 'Usuarios y Autenticación',
                    'suites': [
                        {'nombre': 'UsuarioTestCase', 'descripcion': 'Tests de usuarios'},
                        {'nombre': 'AutenticacionTestCase', 'descripcion': 'Tests de autenticación'},
                        {'nombre': 'PermisosRolesTestCase', 'descripcion': 'Tests de permisos y roles'},
                        {'nombre': 'UsuarioPerformanceTestCase', 'descripcion': 'Tests de rendimiento'},
                    ]
                }
            }
            
            return Response(tests_disponibles)
        except Exception as e:
            BaseService.log_error(e, "Error listando tests disponibles", usuario_id=request.user.id)
            return Response(
                {'error': f'Error listando tests: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def estadisticas_pruebas(self, request):
        """Retorna estadísticas de las últimas pruebas ejecutadas"""
        try:
            BaseService.validar_es_admin(request.user)
        except Exception as e:
            return Response(
                {'error': f'No tiene permisos para acceder a esta información: {str(e)}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Obtener pruebas de rendimiento guardadas
            pruebas = PruebaRendimientoCompleta.objects.filter(completada=True).order_by('-fecha_ejecucion')[:10]
            
            estadisticas = {
                'ultima_ejecucion': None,
                'total_pruebas': pruebas.count(),
                'pruebas_completadas': pruebas.filter(completada=True).count(),
                'mejora_promedio': 0.0,
                'pruebas_recientes': []
            }
            
            if pruebas.exists():
                ultima = pruebas.first()
                estadisticas['ultima_ejecucion'] = ultima.fecha_ejecucion.isoformat()
                
                # Calcular mejora promedio
                mejoras = [p.mejora_factor for p in pruebas if p.mejora_factor]
                if mejoras:
                    estadisticas['mejora_promedio'] = sum(mejoras) / len(mejoras)
                
                # Pruebas recientes
                estadisticas['pruebas_recientes'] = [
                    {
                        'id': p.id,
                        'fecha': p.fecha_ejecucion.isoformat(),
                        'mejora': p.mejora_factor,
                        'tiempo_manual': p.tiempo_respuesta_manual_promedio,
                        'tiempo_web': p.tiempo_respuesta_web_promedio
                    }
                    for p in pruebas[:5]
                ]
            
            return Response(estadisticas)
        except Exception as e:
            BaseService.log_error(e, "Error obteniendo estadísticas de pruebas", usuario_id=request.user.id)
            return Response(
                {'error': f'Error obteniendo estadísticas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def pruebas_rendimiento_guardadas(self, request):
        """Lista todas las pruebas de rendimiento guardadas"""
        try:
            BaseService.validar_es_admin(request.user)
        except Exception as e:
            return Response(
                {'error': f'No tiene permisos para acceder a esta información: {str(e)}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            pruebas = PruebaRendimientoCompleta.objects.all().order_by('-fecha_ejecucion')
            
            # Como pagination_class = None, no usar paginación
            serializer = PruebaRendimientoCompletaSerializer(pruebas, many=True)
            return Response(serializer.data)
        except Exception as e:
            BaseService.log_error(e, "Error obteniendo pruebas de rendimiento guardadas", usuario_id=request.user.id)
            return Response(
                {'error': f'Error obteniendo pruebas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def detalle_prueba_rendimiento(self, request, pk=None):
        """Obtiene el detalle completo de una prueba de rendimiento"""
        BaseService.validar_es_admin(request.user)
        
        try:
            prueba = PruebaRendimientoCompleta.objects.get(pk=pk)
            serializer = PruebaRendimientoCompletaSerializer(prueba)
            
            # Obtener también los detalles de procesos individuales
            detalles_procesos = DetalleProcesoRendimiento.objects.filter(prueba=prueba)
            detalles_serializer = DetalleProcesoRendimientoSerializer(detalles_procesos, many=True)
            
            response_data = serializer.data
            response_data['detalles_procesos'] = detalles_serializer.data
            
            return Response(response_data)
        except PruebaRendimientoCompleta.DoesNotExist:
            return Response(
                {'error': 'Prueba no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def detalles_procesos(self, request):
        """Obtiene todos los detalles de procesos de rendimiento"""
        BaseService.validar_es_admin(request.user)
        
        try:
            # Filtros opcionales
            codigo_proceso = request.query_params.get('codigo_proceso', None)
            prueba_id = request.query_params.get('prueba_id', None)
            
            queryset = DetalleProcesoRendimiento.objects.all()
            
            if codigo_proceso:
                queryset = queryset.filter(codigo_proceso=codigo_proceso)
            if prueba_id:
                queryset = queryset.filter(prueba_id=prueba_id)
            
            queryset = queryset.order_by('-fecha_medicion')[:100]
            
            serializer = DetalleProcesoRendimientoSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            BaseService.log_error(e, "Error obteniendo detalles de procesos", usuario_id=request.user.id)
            return Response(
                {'error': f'Error obteniendo detalles: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def ejecutar_rendimiento_completo(self, request):
        """
        Ejecuta pruebas de rendimiento completas según ISO 25010.
        Ejecuta el comando de Django pruebas_rendimiento con las iteraciones especificadas.
        """
        BaseService.validar_es_admin(request.user)
        
        try:
            from django.core.management import call_command
            from io import StringIO
            import json
            import sys
            
            iteraciones = request.data.get('iteraciones', 24)
            username = request.user.username
            
            # Capturar salida del comando
            output = StringIO()
            error_output = StringIO()
            
            # Guardar stdout y stderr originales
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            try:
                # Redirigir stdout y stderr
                sys.stdout = output
                sys.stderr = error_output
                
                # Ejecutar el comando de pruebas de rendimiento
                # Nota: El comando puede tardar varios minutos dependiendo de las iteraciones
                # El comando está en apps/busqueda/management/commands/pruebas_rendimiento.py
                try:
                    # Intentar ejecutar el comando de pruebas de rendimiento
                    # El comando está en apps/busqueda/management/commands/pruebas_rendimiento.py
                    call_command(
                        'pruebas_rendimiento',
                        usuario=username,
                        iteraciones=iteraciones,
                        verbosity=0,  # Reducir verbosidad para evitar problemas con StringIO
                        interactive=False  # No esperar input del usuario
                    )
                except Exception as cmd_error:
                    # Capturar error específico del comando
                    error_msg = str(cmd_error)
                    import traceback
                    error_trace = traceback.format_exc()
                    error_output.write(f"\nError durante ejecución del comando: {error_msg}\n")
                    error_output.write(f"Traceback: {error_trace}\n")
                    BaseService.log_error(cmd_error, "Error ejecutando comando pruebas_rendimiento", usuario_id=request.user.id)
                    # No relanzar la excepción, continuar para buscar resultados guardados
                    # Si el comando falla, aún podemos buscar resultados previos
            finally:
                # Restaurar stdout y stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            
            output_text = output.getvalue()
            error_text = error_output.getvalue()
            
            # Obtener la última prueba guardada (buscar por usuario o por fecha reciente)
            prueba_guardada = PruebaRendimientoCompleta.objects.filter(
                usuario_ejecutor=request.user
            ).order_by('-fecha_ejecucion').first()
            
            # Si no hay prueba del usuario actual, buscar la más reciente
            if not prueba_guardada:
                prueba_guardada = PruebaRendimientoCompleta.objects.order_by('-fecha_ejecucion').first()
            
            if prueba_guardada and prueba_guardada.resultados_json:
                resultados = prueba_guardada.resultados_json
                
                # Formatear resultados para el frontend
                resultado_formateado = {
                    'registro': resultados.get('registro', {}),
                    'listado': resultados.get('listado', {}),
                    'busqueda_ia': resultados.get('busqueda_ia', {}),
                    'grado_cumplimiento': resultados.get('grado_cumplimiento', 0),
                    'fecha_ejecucion': prueba_guardada.fecha_ejecucion.isoformat(),
                    'salida': output_text,
                    'errores': error_text if error_text else None
                }
                
                return Response({
                    'mensaje': 'Pruebas de rendimiento completas ejecutadas exitosamente',
                    'prueba_id': prueba_guardada.id,
                    'fecha_ejecucion': prueba_guardada.fecha_ejecucion.isoformat(),
                    'resultados': resultado_formateado
                }, status=status.HTTP_200_OK)
            else:
                # Si no hay resultados guardados, retornar mensaje con salida
                return Response({
                    'mensaje': 'Pruebas ejecutadas, pero no se encontraron resultados guardados',
                    'salida': output_text,
                    'errores': error_text if error_text else None,
                    'advertencia': 'Los resultados pueden no haberse guardado correctamente. Verifique los logs del servidor.'
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            BaseService.log_error(e, "Error ejecutando prueba completa de rendimiento", usuario_id=request.user.id)
            import traceback
            from django.conf import settings
            return Response(
                {
                    'error': f'Error ejecutando pruebas: {str(e)}',
                    'detalle': traceback.format_exc() if settings.DEBUG else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
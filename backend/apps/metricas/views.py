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
from .models import (
    PruebaControladaSemantica,
    MetricaSemantica,
    RegistroGeneracionEmbedding,
    PruebaCarga,
    MetricaRendimiento,
    RegistroManualEnvio
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
    RegistrarEnvioManualSerializer
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


class RegistroGeneracionEmbeddingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Registros de Generación de Embeddings (solo lectura)"""
    queryset = RegistroGeneracionEmbedding.objects.all()
    serializer_class = RegistroGeneracionEmbeddingSerializer
    permission_classes = [IsAuthenticated]
    
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
        """Filtra por tipo de prueba y nivel de carga"""
        queryset = super().get_queryset()
        tipo_prueba = self.request.query_params.get('tipo_prueba', None)
        nivel_carga = self.request.query_params.get('nivel_carga', None)
        
        if tipo_prueba:
            queryset = queryset.filter(tipo_prueba=tipo_prueba)
        if nivel_carga:
            queryset = queryset.filter(nivel_carga=int(nivel_carga))
        
        return queryset
    
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

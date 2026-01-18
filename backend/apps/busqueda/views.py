"""
Views para la app de búsqueda
Usan la arquitectura en capas (servicios y repositorios)
"""
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, throttle_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import BusquedaTradicional, EmbeddingBusqueda
from .serializers import (
    BusquedaTradicionalSerializer, 
    BusquedaTradicionalListSerializer,
    EmbeddingBusquedaSerializer,
    HistorialSemanticaSerializer
)
from .services import BusquedaTradicionalService, BusquedaSemanticaService
from .repositories import busqueda_tradicional_repository, embedding_busqueda_repository
from .pdf_service import PDFBusquedaService
from apps.core.throttling import BusquedaRateThrottle, BusquedaSemanticaRateThrottle

Usuario = get_user_model()


@extend_schema_view(
    list=extend_schema(
        summary="Listar historial de búsquedas",
        description="Obtiene el historial de búsquedas tradicionales del usuario autenticado",
        tags=['busqueda']
    ),
    retrieve=extend_schema(
        summary="Obtener búsqueda por ID",
        description="Obtiene los detalles de una búsqueda específica del historial",
        tags=['busqueda']
    ),
    destroy=extend_schema(
        summary="Eliminar búsqueda del historial",
        description="Elimina una búsqueda específica del historial del usuario",
        tags=['busqueda']
    ),
)
class BusquedaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para búsquedas tradicionales y semánticas.
    
    Permite realizar búsquedas en usuarios, envíos y productos, así como
    búsquedas semánticas usando IA con OpenAI embeddings.
    
    **Arquitectura**: Usa servicios y repositorios (capa de lógica de negocio).
    """
    queryset = BusquedaTradicional.objects.all()
    serializer_class = BusquedaTradicionalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['termino_busqueda']
    ordering_fields = ['fecha_busqueda']
    ordering = ['-fecha_busqueda']

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return BusquedaTradicionalListSerializer
        return BusquedaTradicionalSerializer

    def get_queryset(self):
        """Filtra el queryset según el usuario - usa repositorio"""
        return busqueda_tradicional_repository.filtrar_por_usuario(self.request.user)

    # ==================== BÚSQUEDA TRADICIONAL ====================

    @extend_schema(
        summary="Búsqueda tradicional",
        description="""
        Realiza una búsqueda tradicional (texto) en usuarios, envíos y productos.
        
        **Tipos de búsqueda disponibles:**
        - `general`: Busca en todos los tipos de entidades
        - `usuarios`: Solo busca en usuarios
        - `envios`: Solo busca en envíos
        - `productos`: Solo busca en productos
        
        **Permisos:** Los resultados se filtran según el rol del usuario autenticado.
        """,
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Término de búsqueda',
            ),
            OpenApiParameter(
                name='tipo',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Tipo de búsqueda: general, usuarios, envios, productos',
                enum=['general', 'usuarios', 'envios', 'productos'],
            ),
        ],
        tags=['busqueda'],
        responses={
            200: {
                'description': 'Resultados de la búsqueda',
                'examples': {
                    'application/json': {
                        'query': 'ejemplo',
                        'tipo': 'general',
                        'total_resultados': 5,
                        'resultados': {
                            'usuarios': [],
                            'envios': [],
                            'productos': []
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        Realiza una búsqueda tradicional en usuarios, envíos y productos.
        Delegado al servicio BusquedaTradicionalService.
        """
        query = request.query_params.get('q', '')
        tipo = request.query_params.get('tipo', 'general')
        
        if not query:
            return Response(
                {'error': 'Término de búsqueda requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resultado = BusquedaTradicionalService.buscar(
            query=query,
            tipo=tipo,
            usuario=request.user
        )
        
        return Response(resultado)

    @action(detail=False, methods=['get'])
    def historial(self, request):
        """Obtiene el historial de búsquedas del usuario"""
        historial = self.get_queryset()
        page = self.paginate_queryset(historial)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(historial, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def limpiar_historial(self, request):
        """Limpia el historial de búsquedas del usuario"""
        busqueda_tradicional_repository.limpiar_historial_usuario(request.user)
        return Response({'message': 'Historial limpiado correctamente'})

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de búsquedas del usuario"""
        busquedas_populares = busqueda_tradicional_repository.obtener_busquedas_populares(
            request.user, limite=5
        )
        total = busqueda_tradicional_repository.contar(usuario=request.user)
        
        from django.utils import timezone
        busquedas_hoy = busqueda_tradicional_repository.filtrar(
            usuario=request.user,
            fecha_busqueda__date=timezone.now().date()
        ).count()

        return Response({
            'total_busquedas': total,
            'busquedas_hoy': busquedas_hoy,
            'busquedas_populares': busquedas_populares
        })

    # ==================== BÚSQUEDA SEMÁNTICA ====================
    
    @extend_schema(
        summary="Búsqueda semántica con IA",
        description="""
        Realiza una búsqueda semántica de envíos usando embeddings de OpenAI.
        
        Esta búsqueda utiliza procesamiento de lenguaje natural para encontrar
        envíos relevantes basándose en el significado de la consulta, no solo
        en coincidencias exactas de texto.
        
        **Características:**
        - Usa embeddings de OpenAI (text-embedding-3-small por defecto)
        - Calcula similitud semántica usando múltiples métricas
        - Incluye boost por coincidencias exactas de palabras
        - Filtra resultados por umbral adaptativo de similitud
        - Registra costo y tokens utilizados
        
        **Modelos disponibles:**
        - `text-embedding-3-small`: Más económico, recomendado
        - `text-embedding-3-large`: Mayor precisión, más costoso
        - `text-embedding-ada-002`: Modelo anterior
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'texto': {
                        'type': 'string',
                        'description': 'Consulta en lenguaje natural',
                        'example': 'envíos entregados en Quito la semana pasada'
                    },
                    'limite': {
                        'type': 'integer',
                        'description': 'Número máximo de resultados (default: 20)',
                        'default': 20,
                        'minimum': 1,
                        'maximum': 100
                    },
                    'modeloEmbedding': {
                        'type': 'string',
                        'description': 'Modelo de embedding a usar',
                        'enum': ['text-embedding-3-small', 'text-embedding-3-large', 'text-embedding-ada-002'],
                        'default': 'text-embedding-3-small'
                    },
                    'filtrosAdicionales': {
                        'type': 'object',
                        'description': 'Filtros adicionales para la búsqueda',
                        'properties': {
                            'fechaDesde': {'type': 'string', 'format': 'date'},
                            'fechaHasta': {'type': 'string', 'format': 'date'},
                            'estado': {'type': 'string'},
                            'ciudadDestino': {'type': 'string'}
                        }
                    }
                },
                'required': ['texto']
            }
        },
        tags=['busqueda'],
        responses={
            200: {
                'description': 'Resultados de la búsqueda semántica',
                'examples': {
                    'application/json': {
                        'consulta': 'envíos entregados en Quito',
                        'resultados': [],
                        'totalEncontrados': 5,
                        'tiempoRespuesta': 1234,
                        'modeloUtilizado': 'text-embedding-3-small',
                        'costoConsulta': 0.0001,
                        'tokensUtilizados': 10,
                        'busquedaId': 123
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['post'], url_path='semantica', throttle_classes=[BusquedaSemanticaRateThrottle])
    def busqueda_semantica(self, request):
        """
        Búsqueda semántica de envíos usando OpenAI embeddings.
        Delegado al servicio BusquedaSemanticaService.
        Rate limited: 30 búsquedas/minuto debido al costo de OpenAI.
        """
        consulta_texto = request.data.get('texto', '').strip()
        limite = request.data.get('limite', 20)
        filtros = request.data.get('filtrosAdicionales', {})
        modelo = request.data.get('modeloEmbedding')
        metrica_ordenamiento = request.data.get('metricaOrdenamiento', 'score_combinado')
        
        if not consulta_texto:
            return Response(
                {'error': 'El campo "texto" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            resultado = BusquedaSemanticaService.buscar(
                    consulta=consulta_texto,
                usuario=request.user,
                filtros=filtros,
                limite=limite,
                modelo_embedding=modelo,
                metrica_ordenamiento=metrica_ordenamiento
            )
            return Response(resultado)
            
        except Exception as e:
            return Response(
                {'error': f'Error procesando búsqueda semántica: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Obtener sugerencias para búsqueda semántica",
        description="Retorna sugerencias predefinidas para mejorar las búsquedas semánticas",
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Término de búsqueda para filtrar sugerencias',
            ),
        ],
        tags=['busqueda'],
    )
    @action(detail=False, methods=['get'], url_path='semantica/sugerencias')
    def sugerencias_semanticas(self, request):
        """Obtiene sugerencias para búsqueda semántica"""
        query = request.query_params.get('q', '').lower()
        sugerencias = BusquedaSemanticaService.obtener_sugerencias(query)
        return Response(sugerencias)

    @action(detail=False, methods=['get', 'post', 'delete'], url_path='semantica/historial')
    def historial_semantico(self, request):
        """
        Gestiona el historial de búsquedas semánticas.
        
        GET: Obtiene el historial
        POST: Guarda una búsqueda (aunque esto se hace automáticamente)
        DELETE: Limpia el historial
        """
        # GET - Obtener historial
        if request.method == 'GET':
            try:
                historial = BusquedaSemanticaService.obtener_historial(request.user)
                return Response(historial)
            except Exception as e:
                return Response(
                    {'error': f'Error obteniendo historial: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # POST - Guardar búsqueda (aunque el servicio ya lo hace automáticamente)
        elif request.method == 'POST':
            consulta = request.data.get('consulta', '')
            total_resultados = request.data.get('totalResultados', 0)
            
            if not consulta:
                return Response(
                    {'error': 'Consulta requerida'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            busqueda = embedding_busqueda_repository.crear(
                usuario=request.user,
                consulta=consulta,
                resultados_encontrados=total_resultados
            )
            
            serializer = EmbeddingBusquedaSerializer(busqueda)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # DELETE - Limpiar historial
        elif request.method == 'DELETE':
            BusquedaSemanticaService.limpiar_historial(request.user)
            return Response({'message': 'Historial semántico limpiado correctamente'})

    @extend_schema(
        summary="Obtener métricas de búsquedas semánticas",
        description="""
        Obtiene estadísticas y métricas sobre las búsquedas semánticas del usuario.
        
        Incluye:
        - Total de búsquedas realizadas
        - Tiempo promedio de respuesta
        - Feedback positivo/negativo
        - Total de embeddings generados
        """,
        tags=['busqueda'],
    )
    @action(detail=False, methods=['get'], url_path='semantica/metricas')
    def metricas_semanticas(self, request):
        """Obtiene métricas de búsquedas semánticas"""
        metricas = BusquedaSemanticaService.obtener_metricas(request.user)
        return Response(metricas)
    
    @extend_schema(
        summary="Obtener estadísticas de embeddings",
        description="""
        Obtiene estadísticas sobre embeddings de envíos.
        
        Retorna:
        - Total de envíos
        - Total de envíos con embedding
        - Total de envíos sin embedding
        - Porcentaje de cobertura
        """,
        tags=['busqueda'],
    )
    @action(detail=False, methods=['get'], url_path='semantica/estadisticas-embeddings')
    def estadisticas_embeddings(self, request):
        """Obtiene estadísticas de embeddings de envíos"""
        try:
            estadisticas = BusquedaSemanticaService.obtener_estadisticas_embeddings(request.user)
            return Response(estadisticas)
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo estadísticas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Generar embeddings pendientes",
        description="""
        Genera embeddings para envíos que no tienen embedding o necesitan actualización.
        
        Esta operación puede tardar varios minutos dependiendo de la cantidad de envíos.
        Se procesa de forma asíncrona para no bloquear la respuesta.
        
        **Parámetros:**
        - `forzarRegeneracion`: Si True, regenera todos los embeddings (default: False)
        - `modelo`: Modelo de embedding a usar (default: text-embedding-3-small)
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'forzarRegeneracion': {
                        'type': 'boolean',
                        'default': False,
                        'description': 'Si True, regenera todos los embeddings'
                    },
                    'modelo': {
                        'type': 'string',
                        'enum': ['text-embedding-3-small', 'text-embedding-3-large', 'text-embedding-ada-002'],
                        'description': 'Modelo de embedding a usar'
                    }
                }
            }
        },
        tags=['busqueda'],
    )
    @action(detail=False, methods=['post'], url_path='semantica/generar-embeddings')
    def generar_embeddings_pendientes(self, request):
        """Genera embeddings para envíos pendientes"""
        try:
            forzar_regeneracion = request.data.get('forzarRegeneracion', False)
            modelo = request.data.get('modelo')
            
            # Ejecutar en un thread para no bloquear
            import threading
            resultado = {'mensaje': 'Proceso iniciado', 'procesando': True}
            
            def procesar():
                try:
                    resultado_final = BusquedaSemanticaService.generar_embeddings_pendientes(
                        usuario=request.user,
                        modelo=modelo,
                        forzar_regeneracion=forzar_regeneracion
                    )
                    resultado.update(resultado_final)
                    resultado['procesando'] = False
                except Exception as e:
                    resultado['error'] = str(e)
                    resultado['procesando'] = False
            
            thread = threading.Thread(target=procesar, daemon=True)
            thread.start()
            
            return Response(resultado, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            return Response(
                {'error': f'Error iniciando generación de embeddings: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    #
    @extend_schema(
        summary="Análisis comparativo de métricas de similitud",
        description="""
        Muestra un análisis comparativo detallado de las diferentes métricas de similitud
        utilizadas en la búsqueda semántica, justificando la elección de cosine similarity.
        
        Este endpoint es útil para:
        - Documentación académica
        - Análisis de resultados
        - Justificación técnica de la elección de métricas
        - Ejemplos educativos
        
        Retorna un ejemplo de análisis con valores típicos y explicaciones detalladas.
        """,
        tags=['busqueda'],
        responses={
            200: {
                'description': 'Análisis comparativo de métricas',
            }
        }
    )
    @action(detail=False, methods=['get'], url_path='semantica/analisis-metricas')
    def analisis_comparativo_metricas(self, request):
        """
        Retorna un análisis comparativo resumido de las métricas de similitud.
        Muestra las 4 métricas principales (cosine, dot product, euclidean, manhattan) 
        y el score combinado con justificación breve de por qué cosine similarity es la mejor.
        """
        # Ejemplo de resultado con valores típicos
        ejemplo_resultado = {
            'cosine_similarity': 0.85,
            'dot_product': 12.5,
            'euclidean_distance': 0.45,
            'manhattan_distance': 2.1,
            'score_combinado': 0.92,
            'boost_exactas': 0.07,
            'boost_productos': 0.0,
            'coincidencias_exactas': 0.5
        }
        
        # Usar método resumido para mostrar métricas de forma clara
        analisis = BusquedaSemanticaService._generar_analisis_metricas_resumido(ejemplo_resultado)
        
        return Response(analisis)


    # ==================== DESCARGAR PDF ====================

    @extend_schema(
        summary="Descargar PDF de búsqueda tradicional",
        description="Genera y descarga un PDF con los resultados de una búsqueda tradicional específica",
        tags=['busqueda'],
    )
    @action(detail=True, methods=['get'], url_path='descargar-pdf')
    def descargar_pdf_tradicional(self, request, pk=None):
        """Descarga PDF de una búsqueda tradicional"""
        try:
            # Obtener la búsqueda
            busqueda = busqueda_tradicional_repository.obtener_por_id(pk)
            
            if not busqueda:
                return Response(
                    {'error': 'Búsqueda no encontrada'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que pertenece al usuario
            if busqueda.usuario != request.user and not request.user.is_staff:
                return Response(
                    {'error': 'No tiene permiso para acceder a esta búsqueda'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Preparar datos para PDF
            busqueda_data = {
                'termino_busqueda': busqueda.termino_busqueda,
                'tipo_busqueda': busqueda.tipo_busqueda,
                'fecha_busqueda': busqueda.fecha_busqueda.strftime('%Y-%m-%d %H:%M:%S'),
                'resultados_encontrados': busqueda.resultados_encontrados,
                'usuario_nombre': busqueda.usuario.get_full_name() or busqueda.usuario.username,
                'resultados_json': busqueda.resultados_json or {}
            }
            
            # Generar PDF
            pdf_buffer = PDFBusquedaService.generar_pdf_busqueda_tradicional(busqueda_data)
            
            # Crear respuesta HTTP
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            filename = f"busqueda_tradicional_{pk}_{busqueda.fecha_busqueda.strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error generando PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Descargar PDF de búsqueda semántica",
        description="Genera y descarga un PDF con los resultados y métricas de una búsqueda semántica específica",
        tags=['busqueda'],
    )
    @action(detail=False, methods=['get'], url_path='semantica/(?P<busqueda_id>[^/.]+)/descargar-pdf')
    def descargar_pdf_semantica(self, request, busqueda_id=None):
        """Descarga PDF de una búsqueda semántica"""
        try:
            # Obtener la búsqueda
            busqueda = embedding_busqueda_repository.obtener_por_id(busqueda_id)
            
            if not busqueda:
                return Response(
                    {'error': 'Búsqueda semántica no encontrada'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que pertenece al usuario
            if busqueda.usuario != request.user and not request.user.is_staff:
                return Response(
                    {'error': 'No tiene permiso para acceder a esta búsqueda'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Preparar datos para PDF
            busqueda_data = {
                'consulta': busqueda.consulta,
                'modelo_utilizado': busqueda.modelo_utilizado,
                'fecha_busqueda': busqueda.fecha_busqueda.strftime('%Y-%m-%d %H:%M:%S'),
                'resultados_encontrados': busqueda.resultados_encontrados,
                'tiempo_respuesta': busqueda.tiempo_respuesta,
                'tokens_utilizados': busqueda.tokens_utilizados,
                'costo_consulta': float(busqueda.costo_consulta) if busqueda.costo_consulta else 0,
                'usuario_nombre': busqueda.usuario.get_full_name() or busqueda.usuario.username,
                'resultados_json': busqueda.resultados_json or []
            }
            
            # Generar PDF
            pdf_buffer = PDFBusquedaService.generar_pdf_busqueda_semantica(busqueda_data)
            
            # Crear respuesta HTTP
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            filename = f"busqueda_semantica_{busqueda_id}_{busqueda.fecha_busqueda.strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error generando PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

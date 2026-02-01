"""
Views para la app de archivos
Usan la arquitectura en capas (servicios y repositorios)
"""
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from django.core.exceptions import ValidationError
from datetime import datetime
from django.db import models

from .models import Envio, Producto, Tarifa, ImportacionExcel
from .serializers import (
    EnvioSerializer, EnvioListSerializer, EnvioCreateSerializer,
    ProductoSerializer, ProductoListSerializer, TarifaSerializer,
    ImportacionExcelSerializer, ImportacionExcelCreateSerializer,
    PreviewExcelSerializer, ProcesarExcelSerializer
)
from .services import EnvioService, ProductoService, TarifaService
from apps.core.exceptions import TransicionEstadoInvalidaError
from .repositories import (
    envio_repository, 
    producto_repository, 
    tarifa_repository,
    importacion_repository
)
from .utils_exportacion import (
    exportar_envios_excel,
    exportar_envios_csv,
    exportar_envios_pdf,
    generar_comprobante_envio
)
from .utils_importacion import (
    ProcesadorExcel,
    generar_reporte_errores
)


@extend_schema_view(
    list=extend_schema(
        summary="Listar envíos",
        description="Obtiene la lista de envíos según los permisos del usuario",
        tags=['envios']
    ),
    create=extend_schema(
        summary="Crear envío",
        description="""
        Crea un nuevo envío con productos asociados.
        
        **Validaciones:**
        - HAWB debe ser único
        - Validación de cupo anual del comprador
        - Cálculo automático de costo del servicio
        - Generación automática de embedding para búsqueda semántica
        """,
        tags=['envios']
    ),
    retrieve=extend_schema(
        summary="Obtener envío por ID",
        description="Obtiene los detalles completos de un envío específico",
        tags=['envios']
    ),
    update=extend_schema(
        summary="Actualizar envío completo",
        tags=['envios']
    ),
    partial_update=extend_schema(
        summary="Actualizar envío parcialmente",
        tags=['envios']
    ),
    destroy=extend_schema(
        summary="Eliminar envío",
        tags=['envios']
    ),
)
class EnvioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de envíos.
    
    **Arquitectura**: Usa servicios y repositorios.
    
    **Permisos:**
    - **Admin/Gerente/Digitador**: Pueden ver y gestionar todos los envíos
    - **Comprador**: Solo puede ver sus propios envíos
    """
    queryset = Envio.objects.all()
    serializer_class = EnvioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'comprador']
    search_fields = ['hawb', 'comprador__nombre']
    ordering_fields = ['fecha_emision', 'valor_total', 'peso_total']
    ordering = ['-fecha_emision']

    def get_serializer_class(self):
        if self.action == 'list':
            return EnvioListSerializer
        elif self.action == 'create':
            return EnvioCreateSerializer
        return EnvioSerializer

    def get_queryset(self):
        """
        Usa repositorio para filtrar por permisos.
        No se filtra por fecha_emision: todos los envíos (incluidos años atípicos)
        aparecen en el listado para que puedan verse y corregirse.
        """
        return envio_repository.filtrar_por_permisos_usuario(self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Crear envío - delegado al servicio"""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Formatear errores de manera más clara
            errores_formateados = {}
            for campo, mensajes in serializer.errors.items():
                if isinstance(mensajes, list):
                    errores_formateados[campo] = mensajes[0] if len(mensajes) == 1 else mensajes
                else:
                    errores_formateados[campo] = mensajes
            
            return Response({
                'error': 'Datos inválidos',
                'detalles': errores_formateados,
                'errores': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            envio = EnvioService.crear_envio(
                data=serializer.validated_data,
                usuario_creador=request.user
            )
            response_serializer = EnvioSerializer(envio)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Manejar errores de validación de Django
            if hasattr(e, 'error_dict'):
                errores = {}
                for campo, mensajes in e.error_dict.items():
                    errores[campo] = [str(msg) for msg in mensajes]
                return Response({
                    'error': 'Error de validación',
                    'detalles': errores
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'error': 'Error de validación',
                    'detalle': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            return Response({
                'error': 'Error al crear el envío',
                'detalle': str(e),
                'tipo': type(e).__name__
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Actualizar envío - delegado al servicio"""
        try:
            envio = EnvioService.actualizar_envio(
                envio_id=kwargs.get('pk'),
                data=request.data,
                usuario_actual=request.user
            )
            serializer = EnvioSerializer(envio)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Cambiar estado de envío",
        description="""
        Cambia el estado de un envío aplicando validaciones de transición.
        
        **Transiciones válidas:**
        - `pendiente` → `en_transito` o `cancelado`
        - `en_transito` → `entregado` o `cancelado`
        - `entregado` → (estado final)
        - `cancelado` → (estado final)
        
        Genera notificación automática al comprador si cambia el estado.
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'estado': {
                        'type': 'string',
                        'enum': ['pendiente', 'en_transito', 'entregado', 'cancelado'],
                        'description': 'Nuevo estado del envío'
                    }
                },
                'required': ['estado']
            }
        },
        tags=['envios'],
    )
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambia el estado - delegado al servicio"""
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response({
                'error': 'El campo "estado" es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            envio = EnvioService.cambiar_estado(
                envio_id=pk,
                nuevo_estado=nuevo_estado,
                usuario_actual=request.user
            )
            serializer = EnvioSerializer(envio)
            return Response({
                'message': f'Estado cambiado a {nuevo_estado}',
                'envio': serializer.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            # Manejar errores de validación de Django
            if hasattr(e, 'error_dict'):
                errores = {}
                for campo, mensajes in e.error_dict.items():
                    errores[campo] = [str(msg) for msg in mensajes]
                return Response({
                    'error': 'Error de validación',
                    'detalles': errores
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'error': 'Error de validación',
                    'detalle': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        except TransicionEstadoInvalidaError as e:
            return Response({
                'error': f'Transición de estado inválida: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            return Response({
                'error': 'Error al cambiar el estado',
                'detalle': str(e),
                'tipo': type(e).__name__
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def mis_envios(self, request):
        """Obtiene envíos del usuario actual"""
        if not request.user.es_comprador:
            return Response(
                {'error': 'Solo compradores pueden acceder'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        envios = envio_repository.filtrar_por_comprador(request.user.id)
        page = self.paginate_queryset(envios)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(envios, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """Obtiene envíos filtrados por estado"""
        estado = request.query_params.get('estado')
        if estado:
            envios = envio_repository.filtrar_por_estado(estado, request.user)
            page = self.paginate_queryset(envios)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(envios, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Parámetro estado requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas - usa repositorio"""
        if not (request.user.es_admin or request.user.es_gerente or request.user.es_digitador):
            return Response(
                {'error': 'No tienes permisos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = envio_repository.obtener_estadisticas(request.user)
        
        return Response({
            'total_envios': stats['total_envios'],
            'envios_pendientes': stats['envios_pendientes'],
            'envios_en_transito': stats['envios_en_transito'],
            'envios_entregados': stats['envios_entregados'],
            'total_peso': stats['total_peso'],
            'total_valor': stats['total_valor'],
            'por_estado': {
                'Pendiente': stats['envios_pendientes'],
                'En tránsito': stats['envios_en_transito'],
                'Entregado': stats['envios_entregados'],
                'Cancelado': stats['envios_cancelados']
            }
        })
    
    @staticmethod
    def _normalizar_decimal(valor):
        """Normaliza valores decimales: convierte coma a punto"""
        if valor is None:
            return None
        if isinstance(valor, (int, float)):
            return valor
        # Convertir a string y reemplazar coma por punto
        valor_str = str(valor).strip()
        # Si tiene coma y punto, asumir formato europeo (1.234,56 -> 1234.56)
        if '.' in valor_str and ',' in valor_str:
            # Eliminar puntos (separadores de miles) y convertir coma a punto
            valor_str = valor_str.replace('.', '').replace(',', '.')
        # Si solo tiene coma, convertir a punto
        elif ',' in valor_str:
            valor_str = valor_str.replace(',', '.')
        return valor_str
    
    @action(detail=False, methods=['post'])
    def calcular_costo(self, request):
        """Calcula el costo de envío con desglose detallado de tarifas"""
        productos_data = request.data.get('productos', [])
        
        if not productos_data:
            return Response({
                'error': 'Se requiere al menos un producto'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        detalles = []
        costo_total = 0
        
        for producto in productos_data:
            categoria = producto.get('categoria')
            # Normalizar peso (aceptar coma o punto como separador decimal)
            peso_str = EnvioViewSet._normalizar_decimal(producto.get('peso', 0))
            peso = float(peso_str) if peso_str else 0
            cantidad = int(producto.get('cantidad', 1))
            
            resultado = TarifaService.buscar_tarifa(categoria, peso)
            
            if resultado:
                tarifa = resultado['tarifa']
                costo_unitario = resultado['costo_calculado']
                costo_producto = costo_unitario * cantidad
                costo_total += costo_producto
                
                detalles.append({
                    'descripcion': producto.get('descripcion', 'Producto'),
                    'categoria': categoria,
                    'peso': peso,
                    'cantidad': cantidad,
                    'costo_unitario': round(costo_unitario, 2),
                    'costo_total': round(costo_producto, 2),
                    'tarifa': {
                        'id': tarifa.id,
                        'cargo_base': float(tarifa.cargo_base),
                        'precio_por_kg': float(tarifa.precio_por_kg),
                        'peso_minimo': float(tarifa.peso_minimo),
                        'peso_maximo': float(tarifa.peso_maximo),
                        'formula': f"${tarifa.cargo_base} + (${tarifa.precio_por_kg}/kg × {peso}kg) = ${costo_unitario:.2f}"
                    }
                })
            else:
                detalles.append({
                    'descripcion': producto.get('descripcion', 'Producto'),
                    'categoria': categoria,
                    'peso': peso,
                    'cantidad': cantidad,
                    'costo_unitario': 0,
                    'costo_total': 0,
                    'error': 'No hay tarifa disponible para esta categoría y peso'
                })
        
        return Response({
            'costo_total': round(costo_total, 2),
            'detalles': detalles
        })
    
    @extend_schema(
        summary="Exportar envíos",
        description="""
        Exporta los envíos filtrados a diferentes formatos.
        
        **Formatos disponibles:**
        - `excel`: Archivo Excel (.xlsx)
        - `csv`: Archivo CSV
        - `pdf`: Documento PDF
        
        Los filtros aplicados en la lista se mantienen para la exportación.
        """,
        parameters=[
            OpenApiParameter(
                name='formato',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Formato de exportación',
                enum=['excel', 'csv', 'pdf'],
            ),
        ],
        tags=['envios'],
    )
    @action(detail=False, methods=['get'])
    def exportar(self, request):
        """Exporta los envíos filtrados a Excel, CSV o PDF"""
        formato = request.query_params.get('formato', '').lower()
        
        if formato not in ['excel', 'csv', 'pdf']:
            return Response({
                'error': 'Formato inválido. Use: excel, csv o pdf'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.filter_queryset(self.get_queryset())
        
        if not queryset.exists():
            return Response({
                'error': 'No hay envíos para exportar con los filtros aplicados'
            }, status=status.HTTP_404_NOT_FOUND)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            if formato == 'excel':
                return exportar_envios_excel(queryset, f'envios_{timestamp}.xlsx')
            elif formato == 'csv':
                return exportar_envios_csv(queryset, f'envios_{timestamp}.csv')
            elif formato == 'pdf':
                return exportar_envios_pdf(queryset, f'envios_{timestamp}.pdf')
        except Exception as e:
            return Response({
                'error': f'Error al generar el archivo: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def comprobante(self, request, pk=None):
        """Genera comprobante de un envío"""
        try:
            envio = self.get_object()
            filename = f'comprobante_{envio.hawb}.pdf'
            return generar_comprobante_envio(envio, filename)
        except Envio.DoesNotExist:
            return Response({
                'error': 'Envío no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error al generar el comprobante: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductoViewSet(viewsets.ModelViewSet):
    """ViewSet para Producto - usa servicios y repositorios"""
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'envio']
    search_fields = ['descripcion', 'envio__hawb']
    ordering_fields = ['descripcion', 'valor', 'peso']
    ordering = ['-fecha_creacion']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoSerializer

    def get_queryset(self):
        """Usa repositorio para filtrar por permisos"""
        return producto_repository.filtrar_por_permisos_usuario(self.request.user)

    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """Obtiene productos por categoría"""
        categoria = request.query_params.get('categoria')
        if categoria:
            productos = producto_repository.filtrar_por_categoria(categoria, request.user)
            page = self.paginate_queryset(productos)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(productos, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Parámetro categoria requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas - usa repositorio"""
        if not (request.user.es_admin or request.user.es_gerente or request.user.es_digitador):
            return Response(
                {'error': 'No tienes permisos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = producto_repository.obtener_estadisticas(request.user)
        return Response(stats)


class TarifaViewSet(viewsets.ModelViewSet):
    """ViewSet para Tarifa"""
    queryset = Tarifa.objects.all()
    serializer_class = TarifaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['categoria', 'activa']
    ordering_fields = ['categoria', 'peso_minimo', 'precio_por_kg']
    ordering = ['categoria', 'peso_minimo']

    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """Obtiene tarifas de una categoría - usa repositorio"""
        categoria = request.query_params.get('categoria')
        if categoria:
            tarifas = tarifa_repository.obtener_tarifas_por_categoria(categoria)
            serializer = self.get_serializer(tarifas, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Parámetro categoria requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'])
    def buscar_tarifa(self, request):
        """Busca tarifa aplicable - usa servicio"""
        categoria = request.data.get('categoria')
        peso = request.data.get('peso')
        
        if not categoria or peso is None:
            return Response({
                'error': 'Se requieren los parámetros categoria y peso'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            peso = float(peso)
        except ValueError:
            return Response({
                'error': 'El peso debe ser un número válido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = TarifaService.buscar_tarifa(categoria, peso)
        
        if resultado:
            serializer = TarifaSerializer(resultado['tarifa'])
            return Response({
                'tarifa': serializer.data,
                'costo_calculado': resultado['costo_calculado']
            })
        else:
            return Response({
                'error': f'No se encontró tarifa activa para {categoria} con peso {peso}kg'
            }, status=status.HTTP_404_NOT_FOUND)


class ImportacionExcelViewSet(viewsets.ModelViewSet):
    """ViewSet para importaciones de Excel"""
    queryset = ImportacionExcel.objects.all()
    serializer_class = ImportacionExcelSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado', 'usuario']
    ordering_fields = ['fecha_creacion', 'fecha_completado']
    ordering = ['-fecha_creacion']
    
    def get_queryset(self):
        """Usa repositorio para filtrar por permisos"""
        return importacion_repository.filtrar_por_permisos_usuario(self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ImportacionExcelCreateSerializer
        return ImportacionExcelSerializer
    
    def create(self, request, *args, **kwargs):
        """Sube archivo Excel y crea importación"""
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            importacion = serializer.save(usuario=request.user)
            
            procesador = ProcesadorExcel(importacion.archivo.path)
            exito, mensaje = procesador.leer_archivo()
            
            if not exito:
                importacion.estado = 'error'
                importacion.mensaje_resultado = mensaje
                importacion.save()
                return Response({'error': mensaje}, status=status.HTTP_400_BAD_REQUEST)
            
            importacion.estado = 'validando'
            importacion.save()
            
            response_serializer = ImportacionExcelSerializer(importacion)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Error al procesar el archivo: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Obtiene vista previa de los datos"""
        try:
            importacion = self.get_object()
            limite = int(request.query_params.get('limite', 50))
            
            procesador = ProcesadorExcel(importacion.archivo.path)
            exito, mensaje = procesador.leer_archivo()
            
            if not exito:
                return Response({'error': mensaje}, status=status.HTTP_400_BAD_REQUEST)
            
            preview_data = procesador.obtener_preview(limite=limite)
            
            columnas = preview_data['columnas']
            if 'HAWB' in columnas or 'hawb' in columnas:
                columna_hawb = 'HAWB' if 'HAWB' in columnas else 'hawb'
                duplicados = procesador.detectar_duplicados(columna_hawb)
                preview_data['duplicados'] = duplicados
                
                importacion.registros_duplicados = len(set(duplicados))
                importacion.save()
            
            return Response(preview_data)
            
        except Exception as e:
            return Response({
                'error': f'Error al obtener vista previa: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def validar(self, request, pk=None):
        """Valida los datos del archivo Excel"""
        try:
            importacion = self.get_object()
            mapeo_columnas = request.data.get('columnas_mapeadas', {})
            
            if not mapeo_columnas:
                return Response({
                    'error': 'El mapeo de columnas es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            importacion.columnas_mapeadas = mapeo_columnas
            importacion.estado = 'validando'
            importacion.save()
            
            procesador = ProcesadorExcel(importacion.archivo.path)
            exito, mensaje = procesador.leer_archivo()
            
            if not exito:
                return Response({'error': mensaje}, status=status.HTTP_400_BAD_REQUEST)
            
            resultado_validacion = procesador.validar_datos(mapeo_columnas)
            
            errores_dict = {}
            for error in resultado_validacion.get('errores', []):
                fila_key = f"fila_{error['fila']}"
                if fila_key not in errores_dict:
                    errores_dict[fila_key] = []
                errores_dict[fila_key].append({
                    'columna': error['columna'],
                    'mensaje': error['error']
                })
            
            importacion.errores_validacion = errores_dict
            importacion.registros_errores = resultado_validacion.get('filas_con_errores', 0)
            importacion.total_registros = len(procesador.df) if procesador.df is not None else 0
            importacion.registros_validos = importacion.total_registros - importacion.registros_errores
            importacion.estado = 'validado'
            importacion.save()
            
            return Response({
                'mensaje': '✅ Validación completada',
                'estadisticas': {
                    'total_registros': importacion.total_registros,
                    'registros_validos': importacion.registros_validos,
                    'registros_errores': importacion.registros_errores,
                    'registros_duplicados': importacion.registros_duplicados
                },
                'errores': resultado_validacion['errores']
            })
            
        except Exception as e:
            try:
                importacion = self.get_object()
                importacion.estado = 'error'
                importacion.mensaje_resultado = f'Error en validación: {str(e)}'
                importacion.save()
            except Exception:
                pass
            
            return Response({
                'error': f'Error al validar: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def procesar(self, request, pk=None):
        """Procesa e importa los datos del archivo Excel"""
        try:
            importacion = self.get_object()
            
            if importacion.estado not in ['validado', 'error']:
                return Response({
                    'error': 'La importación debe estar validada antes de procesar'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            registros_seleccionados = request.data.get('registros_seleccionados', None)
            comprador_id = request.data.get('comprador_id')
            datos_actualizados = request.data.get('datos_actualizados', None)
            
            if datos_actualizados and not isinstance(datos_actualizados, list):
                return Response({
                    'error': 'El formato de datos_actualizados es inválido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if registros_seleccionados:
                importacion.registros_seleccionados = registros_seleccionados
                importacion.save()
            
            procesador = ProcesadorExcel(importacion.archivo.path)
            exito, mensaje = procesador.leer_archivo()
            
            if not exito:
                return Response({'error': mensaje}, status=status.HTTP_400_BAD_REQUEST)
            
            exito, mensaje, extras = procesador.procesar_e_importar(
                importacion=importacion,
                mapeo_columnas=importacion.columnas_mapeadas,
                indices_seleccionados=registros_seleccionados,
                comprador_id=comprador_id,
                actualizaciones=datos_actualizados
            )
            
            if exito:
                respuesta = {
                    'mensaje': mensaje,
                    'estadisticas': {
                        'total_registros': importacion.total_registros,
                        'registros_procesados': importacion.registros_procesados,
                        'registros_errores': importacion.registros_errores
                    }
                }
                if extras:
                    respuesta.update(extras)
                return Response(respuesta)
            else:
                respuesta = {
                    'error': mensaje,
                    'estadisticas': {
                        'total_registros': importacion.total_registros,
                        'registros_procesados': importacion.registros_procesados,
                        'registros_errores': importacion.registros_errores
                    }
                }
                if extras:
                    respuesta.update(extras)
                return Response(respuesta, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': f'Error al procesar: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def reporte_errores(self, request, pk=None):
        """Genera reporte de errores de la importación"""
        try:
            importacion = self.get_object()
            reporte = generar_reporte_errores(importacion)
            return Response(reporte)
        except Exception as e:
            return Response({
                'error': f'Error al generar reporte: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de importaciones"""
        stats = importacion_repository.obtener_estadisticas()
        return Response(stats)

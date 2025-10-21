from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.db import models
from datetime import datetime
from django.http import HttpResponse
import os
from .models import Envio, Producto, Tarifa, ImportacionExcel
from .serializers import (
    EnvioSerializer, EnvioListSerializer, EnvioCreateSerializer,
    ProductoSerializer, ProductoListSerializer, TarifaSerializer,
    ImportacionExcelSerializer, ImportacionExcelCreateSerializer,
    PreviewExcelSerializer, ProcesarExcelSerializer
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

# Create your views here.

class EnvioViewSet(viewsets.ModelViewSet):
    """ViewSet para el modelo Envío"""
    queryset = Envio.objects.all()
    serializer_class = EnvioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'comprador']
    search_fields = ['hawb', 'comprador__nombre']
    ordering_fields = ['fecha_emision', 'valor_total', 'peso_total']
    ordering = ['-fecha_emision']

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return EnvioListSerializer
        elif self.action == 'create':
            return EnvioCreateSerializer
        return EnvioSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear envío con mejor manejo de errores"""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Retornar errores detallados
            return Response({
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({
                'error': 'Error al crear el envío',
                'detalle': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """Filtra el queryset según el usuario y su rol"""
        user = self.request.user
        
        # Admins y gerentes pueden ver todos los envíos
        if user.es_admin or user.es_gerente:
            return Envio.objects.all()
        
        # Digitadores pueden ver todos los envíos
        if user.es_digitador:
            return Envio.objects.all()
        
        # Compradores solo pueden ver sus propios envíos
        if user.es_comprador:
            return Envio.objects.filter(comprador=user)
        
        return Envio.objects.none()

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambia el estado del envío"""
        envio = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado not in dict(Envio._meta.get_field('estado').choices):
            return Response({'error': 'Estado inválido'}, status=status.HTTP_400_BAD_REQUEST)
        
        envio.estado = nuevo_estado
        envio.save()
        
        return Response({'message': f'Estado cambiado a {nuevo_estado}'})

    @action(detail=False, methods=['get'])
    def mis_envios(self, request):
        """Obtiene solo los envíos del usuario actual (si es comprador)"""
        if not request.user.es_comprador:
            return Response({'error': 'Solo compradores pueden acceder'}, status=status.HTTP_403_FORBIDDEN)
        
        envios = self.get_queryset().filter(comprador=request.user)
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
            envios = self.get_queryset().filter(estado=estado)
            page = self.paginate_queryset(envios)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(envios, many=True)
            return Response(serializer.data)
        return Response({'error': 'Parámetro estado requerido'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de envíos"""
        if not (request.user.es_admin or request.user.es_gerente or request.user.es_digitador):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        
        # Estadísticas generales
        total_envios = queryset.count()
        envios_pendientes = queryset.filter(estado='pendiente').count()
        envios_en_transito = queryset.filter(estado='en_transito').count()
        envios_entregados = queryset.filter(estado='entregado').count()
        envios_cancelados = queryset.filter(estado='cancelado').count()
        
        # Totales
        total_peso = queryset.aggregate(total=models.Sum('peso_total'))['total'] or 0
        total_valor = queryset.aggregate(total=models.Sum('valor_total'))['total'] or 0
        
        return Response({
            'total_envios': total_envios,
            'envios_pendientes': envios_pendientes,
            'envios_en_transito': envios_en_transito,
            'envios_entregados': envios_entregados,
            'total_peso': float(total_peso),
            'total_valor': float(total_valor),
            'por_estado': {
                'Pendiente': envios_pendientes,
                'En tránsito': envios_en_transito,
                'Entregado': envios_entregados,
                'Cancelado': envios_cancelados
            }
        })
    
    @action(detail=False, methods=['post'])
    def calcular_costo(self, request):
        """Calcula el costo de envío sin crear el envío"""
        productos_data = request.data.get('productos', [])
        
        if not productos_data:
            return Response({
                'error': 'Se requiere al menos un producto'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        costo_total = 0
        detalles = []
        
        for producto in productos_data:
            categoria = producto.get('categoria')
            peso = float(producto.get('peso', 0))
            cantidad = int(producto.get('cantidad', 1))
            
            # Buscar tarifa aplicable
            tarifa = Tarifa.objects.filter(
                categoria=categoria,
                peso_minimo__lte=peso,
                peso_maximo__gte=peso,
                activa=True
            ).first()
            
            if tarifa:
                costo_producto = tarifa.calcular_costo(peso) * cantidad
                costo_total += costo_producto
                detalles.append({
                    'descripcion': producto.get('descripcion', 'Producto'),
                    'categoria': categoria,
                    'peso': peso,
                    'cantidad': cantidad,
                    'costo_unitario': round(tarifa.calcular_costo(peso), 2),
                    'costo_total': round(costo_producto, 2),
                    'tarifa': {
                        'precio_por_kg': float(tarifa.precio_por_kg),
                        'cargo_base': float(tarifa.cargo_base)
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
    
    @action(detail=False, methods=['get'])
    def exportar(self, request):
        """
        Exporta los envíos filtrados a Excel, CSV o PDF
        
        Parámetros de query:
        - formato: 'excel', 'csv' o 'pdf' (requerido)
        - Todos los parámetros de filtrado disponibles (hawb, estado, comprador, etc.)
        
        Ejemplo: /api/envios/envios/exportar/?formato=excel&estado=pendiente
        """
        formato = request.query_params.get('formato', '').lower()
        
        if formato not in ['excel', 'csv', 'pdf']:
            return Response({
                'error': 'Formato inválido. Use: excel, csv o pdf'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener queryset filtrado (usa los mismos filtros que list)
        queryset = self.filter_queryset(self.get_queryset())
        
        # Verificar que haya resultados
        if not queryset.exists():
            return Response({
                'error': 'No hay envíos para exportar con los filtros aplicados'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Exportar según el formato solicitado
        try:
            if formato == 'excel':
                filename = f'envios_{timestamp}.xlsx'
                return exportar_envios_excel(queryset, filename)
            elif formato == 'csv':
                filename = f'envios_{timestamp}.csv'
                return exportar_envios_csv(queryset, filename)
            elif formato == 'pdf':
                filename = f'envios_{timestamp}.pdf'
                return exportar_envios_pdf(queryset, filename)
        except Exception as e:
            return Response({
                'error': f'Error al generar el archivo: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def comprobante(self, request, pk=None):
        """
        Genera y descarga el comprobante de un envío específico en PDF
        
        Ejemplo: /api/envios/envios/123/comprobante/
        """
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
    """ViewSet para el modelo Producto"""
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'envio']
    search_fields = ['descripcion', 'envio__hawb']
    ordering_fields = ['descripcion', 'valor', 'peso']
    ordering = ['-fecha_creacion']

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoSerializer

    def get_queryset(self):
        """Filtra el queryset según el usuario y su rol"""
        user = self.request.user
        
        # Admins, gerentes y digitadores pueden ver todos los productos
        if user.es_admin or user.es_gerente or user.es_digitador:
            return Producto.objects.all()
        
        # Compradores solo pueden ver productos de sus envíos
        if user.es_comprador:
            return Producto.objects.filter(envio__comprador=user)
        
        return Producto.objects.none()

    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """Obtiene productos filtrados por categoría"""
        categoria = request.query_params.get('categoria')
        if categoria:
            productos = self.get_queryset().filter(categoria=categoria)
            page = self.paginate_queryset(productos)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(productos, many=True)
            return Response(serializer.data)
        return Response({'error': 'Parámetro categoria requerido'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de productos"""
        if not (request.user.es_admin or request.user.es_gerente or request.user.es_digitador):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        
        # Estadísticas por categoría
        stats_por_categoria = {}
        for categoria_id, categoria_nombre in Producto._meta.get_field('categoria').choices:
            count = queryset.filter(categoria=categoria_id).count()
            if count > 0:
                stats_por_categoria[categoria_nombre] = count
        
        # Totales
        total_productos = queryset.count()
        total_peso = queryset.aggregate(total=models.Sum('peso'))['total'] or 0
        total_valor = queryset.aggregate(total=models.Sum('valor'))['total'] or 0
        
        return Response({
            'total_productos': total_productos,
            'total_peso': float(total_peso),
            'total_valor': float(total_valor),
            'por_categoria': stats_por_categoria
        })

class TarifaViewSet(viewsets.ModelViewSet):
    """ViewSet para el modelo Tarifa"""
    queryset = Tarifa.objects.all()
    serializer_class = TarifaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['categoria', 'activa']
    ordering_fields = ['categoria', 'peso_minimo', 'precio_por_kg']
    ordering = ['categoria', 'peso_minimo']

    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """Obtiene tarifas activas de una categoría específica"""
        categoria = request.query_params.get('categoria')
        if categoria:
            tarifas = Tarifa.objects.filter(categoria=categoria, activa=True).order_by('peso_minimo')
            serializer = self.get_serializer(tarifas, many=True)
            return Response(serializer.data)
        return Response({'error': 'Parámetro categoria requerido'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def buscar_tarifa(self, request):
        """Busca la tarifa aplicable para una categoría y peso específico"""
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
        
        tarifa = Tarifa.objects.filter(
            categoria=categoria,
            peso_minimo__lte=peso,
            peso_maximo__gte=peso,
            activa=True
        ).first()
        
        if tarifa:
            serializer = self.get_serializer(tarifa)
            costo = tarifa.calcular_costo(peso)
            return Response({
                'tarifa': serializer.data,
                'costo_calculado': round(costo, 2)
            })
        else:
            return Response({
                'error': f'No se encontró tarifa activa para {categoria} con peso {peso}kg',
                'sugerencia': 'Verifique las tarifas disponibles o contacte al administrador'
            }, status=status.HTTP_404_NOT_FOUND)

class ImportacionExcelViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar importaciones de archivos Excel"""
    queryset = ImportacionExcel.objects.all()
    serializer_class = ImportacionExcelSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado', 'usuario']
    ordering_fields = ['fecha_creacion', 'fecha_completado']
    ordering = ['-fecha_creacion']
    
    def get_queryset(self):
        """Filtra las importaciones según el usuario y rol"""
        user = self.request.user
        
        # Admins y gerentes pueden ver todas las importaciones
        if user.es_admin or user.es_gerente:
            return ImportacionExcel.objects.all()
        
        # Digitadores y compradores solo ven sus propias importaciones
        return ImportacionExcel.objects.filter(usuario=user)
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'create':
            return ImportacionExcelCreateSerializer
        return ImportacionExcelSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Sube un archivo Excel y crea una importación
        
        POST /api/importaciones-excel/
        Body (multipart/form-data):
            - archivo: archivo Excel (.xlsx o .xls)
            - nombre_original: nombre del archivo (opcional)
        """
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Crear la importación
            importacion = serializer.save(usuario=request.user)
            
            # Procesar el archivo para obtener preview
            procesador = ProcesadorExcel(importacion.archivo.path)
            exito, mensaje = procesador.leer_archivo()
            
            if not exito:
                importacion.estado = 'error'
                importacion.mensaje_resultado = mensaje
                importacion.save()
                return Response({
                    'error': mensaje
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualizar estado
            importacion.estado = 'validando'
            importacion.save()
            
            # Retornar la importación creada
            response_serializer = ImportacionExcelSerializer(importacion)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Error al procesar el archivo: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        Obtiene una vista previa de los datos del archivo Excel
        
        GET /api/importaciones-excel/{id}/preview/
        Query params:
            - limite: número máximo de filas a retornar (default: 50)
        """
        try:
            importacion = self.get_object()
            limite = int(request.query_params.get('limite', 50))
            
            # Procesar el archivo
            procesador = ProcesadorExcel(importacion.archivo.path)
            exito, mensaje = procesador.leer_archivo()
            
            if not exito:
                return Response({
                    'error': mensaje
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener preview
            preview_data = procesador.obtener_preview(limite=limite)
            
            # Detectar duplicados si existe columna HAWB
            columnas = preview_data['columnas']
            if 'HAWB' in columnas or 'hawb' in columnas:
                columna_hawb = 'HAWB' if 'HAWB' in columnas else 'hawb'
                duplicados = procesador.detectar_duplicados(columna_hawb)
                preview_data['duplicados'] = duplicados
                
                # Actualizar estadísticas
                importacion.registros_duplicados = len(set(duplicados))
                importacion.save()
            
            return Response(preview_data)
            
        except Exception as e:
            return Response({
                'error': f'Error al obtener vista previa: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def validar(self, request, pk=None):
        """
        Valida los datos del archivo Excel según el mapeo de columnas
        
        POST /api/importaciones-excel/{id}/validar/
        Body:
            {
                "columnas_mapeadas": {
                    "HAWB": "hawb",
                    "Peso Total": "peso_total",
                    "Cantidad": "cantidad_total",
                    "Valor": "valor_total",
                    "Estado": "estado",
                    "Descripción": "descripcion",
                    "Peso": "peso",
                    "Cantidad Producto": "cantidad",
                    "Valor Producto": "valor",
                    "Categoría": "categoria"
                }
            }
        """
        try:
            importacion = self.get_object()
            mapeo_columnas = request.data.get('columnas_mapeadas', {})
            
            if not mapeo_columnas:
                return Response({
                    'error': 'El mapeo de columnas es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Guardar el mapeo
            importacion.columnas_mapeadas = mapeo_columnas
            importacion.estado = 'validando'
            importacion.save()
            
            # Procesar el archivo
            procesador = ProcesadorExcel(importacion.archivo.path)
            exito, mensaje = procesador.leer_archivo()
            
            if not exito:
                return Response({
                    'error': mensaje
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar datos
            resultado_validacion = procesador.validar_datos(mapeo_columnas)
            
            # Actualizar estadísticas
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
            except:
                pass
            
            import traceback
            traceback.print_exc()
            
            return Response({
                'error': f'Error al validar: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def procesar(self, request, pk=None):
        """
        Procesa e importa los datos del archivo Excel a la base de datos
        
        POST /api/importaciones-excel/{id}/procesar/
        Body:
            {
                "registros_seleccionados": [0, 1, 2, 3],  // opcional, vacío = todos
                "comprador_id": 123  // ID del comprador para asignar a los envíos
            }
        """
        try:
            importacion = self.get_object()
            
            # Validar que esté en estado correcto
            if importacion.estado not in ['validado', 'error']:
                return Response({
                    'error': 'La importación debe estar validada antes de procesar'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            registros_seleccionados = request.data.get('registros_seleccionados', None)
            comprador_id = request.data.get('comprador_id')
            
            if not comprador_id:
                return Response({
                    'error': 'El ID del comprador es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Guardar registros seleccionados
            if registros_seleccionados:
                importacion.registros_seleccionados = registros_seleccionados
                importacion.save()
            
            # Procesar el archivo
            procesador = ProcesadorExcel(importacion.archivo.path)
            exito, mensaje = procesador.leer_archivo()
            
            if not exito:
                return Response({
                    'error': mensaje
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Importar datos
            exito, mensaje = procesador.procesar_e_importar(
                importacion=importacion,
                mapeo_columnas=importacion.columnas_mapeadas,
                indices_seleccionados=registros_seleccionados,
                comprador_id=comprador_id
            )
            
            if exito:
                return Response({
                    'mensaje': mensaje,
                    'estadisticas': {
                        'total_registros': importacion.total_registros,
                        'registros_procesados': importacion.registros_procesados,
                        'registros_errores': importacion.registros_errores
                    }
                })
            else:
                return Response({
                    'error': mensaje,
                    'estadisticas': {
                        'total_registros': importacion.total_registros,
                        'registros_procesados': importacion.registros_procesados,
                        'registros_errores': importacion.registros_errores
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': f'Error al procesar: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def reporte_errores(self, request, pk=None):
        """
        Genera y descarga un reporte de errores de la importación
        
        GET /api/importaciones-excel/{id}/reporte_errores/
        """
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
        """
        Obtiene estadísticas generales de las importaciones
        
        GET /api/importaciones-excel/estadisticas/
        """
        queryset = self.get_queryset()
        
        total_importaciones = queryset.count()
        importaciones_completadas = queryset.filter(estado='completado').count()
        importaciones_error = queryset.filter(estado='error').count()
        importaciones_pendientes = queryset.filter(estado__in=['pendiente', 'validando', 'validado', 'procesando']).count()
        
        total_registros_procesados = sum(imp.registros_procesados for imp in queryset)
        total_registros_error = sum(imp.registros_errores for imp in queryset)
        
        return Response({
            'total_importaciones': total_importaciones,
            'importaciones_completadas': importaciones_completadas,
            'importaciones_error': importaciones_error,
            'importaciones_pendientes': importaciones_pendientes,
            'total_registros_procesados': total_registros_procesados,
            'total_registros_error': total_registros_error
        })

from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.db import models
from .models import Envio, Producto
from .serializers import (
    EnvioSerializer, EnvioListSerializer, EnvioCreateSerializer,
    ProductoSerializer, ProductoListSerializer
)

# Create your views here.

class EnvioViewSet(viewsets.ModelViewSet):
    """ViewSet para el modelo Envío"""
    queryset = Envio.objects.all()
    serializer_class = EnvioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'comprador', 'archivado', 'marcado']
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

    @action(detail=True, methods=['post'])
    def marcar(self, request, pk=None):
        """Marca o desmarca un envío"""
        envio = self.get_object()
        marcado = request.data.get('marcado')
        if marcado is None:
            envio.marcado = not envio.marcado
        else:
            envio.marcado = bool(marcado)
        envio.save(update_fields=['marcado'])
        return Response({'message': f'Envío {"marcado" if envio.marcado else "desmarcado"}'})

    @action(detail=True, methods=['post'])
    def archivar(self, request, pk=None):
        """Archiva un envío"""
        envio = self.get_object()
        envio.archivar()
        return Response({'message': 'Envío archivado'})

    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        """Restaura un envío archivado"""
        envio = self.get_object()
        envio.restaurar()
        return Response({'message': 'Envío restaurado'})

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
        
        # Totales
        total_peso = queryset.aggregate(total=models.Sum('peso_total'))['total'] or 0
        total_valor = queryset.aggregate(total=models.Sum('valor_total'))['total'] or 0
        
        return Response({
            'total_envios': total_envios,
            'envios_pendientes': envios_pendientes,
            'envios_en_transito': envios_en_transito,
            'envios_entregados': envios_entregados,
            'total_peso': float(total_peso),
            'total_valor': float(total_valor)
        })

    @action(detail=False, methods=['post'])
    def import_json(self, request):
        """Importar envíos desde archivo JSON"""
        if 'file' not in request.FILES:
            return Response(
                {'error': 'Se requiere un archivo JSON'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        json_file = request.FILES['file']
        
        try:
            import json
            from django.contrib.auth import get_user_model
            
            Usuario = get_user_model()
            
            # Leer y procesar archivo JSON
            raw = json_file.read().decode('utf-8')
            data = json.loads(raw)
            
            # Validar estructura de datos
            if not isinstance(data, list):
                return Response(
                    {'error': 'El archivo debe contener una lista de envíos'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            created_envios = []
            errors = []
            
            for i, envio_data in enumerate(data):
                try:
                    # Limpieza y normalización de datos
                    envio_data = self._clean_envio_payload(envio_data)
                    # Procesar productos si existen
                    productos_data = envio_data.pop('productos', [])
                    
                    # Buscar comprador por cédula o email
                    comprador_info = envio_data.get('comprador')
                    if isinstance(comprador_info, dict):
                        comprador = Usuario.objects.filter(
                            Q(cedula=comprador_info.get('cedula')) |
                            Q(correo=comprador_info.get('correo'))
                        ).first()
                        
                        if not comprador:
                            errors.append(f'Línea {i+1}: Comprador no encontrado')
                            continue
                        
                        envio_data['comprador'] = comprador.id
                    
                    # Crear envío
                    serializer = EnvioCreateSerializer(data=envio_data)
                    if serializer.is_valid():
                        envio = serializer.save()
                        
                        # Crear productos asociados
                        for producto_data in productos_data:
                            producto_data = self._clean_producto_payload(producto_data)
                            producto_data['envio'] = envio.id
                            prod_serializer = ProductoSerializer(data=producto_data)
                            if prod_serializer.is_valid():
                                prod_serializer.save()
                            else:
                                errors.append(f'Línea {i+1}, producto: {prod_serializer.errors}')
                        
                        # Recalcular totales del envío
                        envio.calcular_totales()
                        created_envios.append(envio)
                        
                    else:
                        errors.append(f'Línea {i+1}: {serializer.errors}')
                        
                except Exception as e:
                    errors.append(f'Línea {i+1}: {str(e)}')
            
            # Registrar actividad
            try:
                from dashboard.views import log_user_activity
                log_user_activity(
                    request.user, 'import_data',
                    f'Importados {len(created_envios)} envíos desde JSON',
                    'Envio', None,
                    {'total_imported': len(created_envios), 'errors': len(errors)},
                    request
                )
            except:
                pass  # No fallar si no se puede registrar actividad
            
            return Response({
                'message': f'Importación completada',
                'created': len(created_envios),
                'errors': errors,
                'envios': EnvioListSerializer(created_envios, many=True).data
            })
            
        except json.JSONDecodeError:
            return Response(
                {'error': 'Archivo JSON inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error procesando archivo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _to_decimal(self, value):
        """Convierte valores a decimal seguro, limpiando cadenas con comas/puntos"""
        from decimal import Decimal, InvalidOperation
        if value is None:
            return Decimal('0')
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        s = str(value).strip().replace(',', '.')
        try:
            return Decimal(s)
        except InvalidOperation:
            return Decimal('0')

    def _clean_envio_payload(self, payload: dict) -> dict:
        """Normaliza y limpia el dict de un envío importado"""
        payload = dict(payload or {})
        if 'hawb' in payload:
            payload['hawb'] = str(payload['hawb']).strip()
        if 'estado' in payload:
            payload['estado'] = str(payload['estado'] or '').strip() or 'pendiente'
        if 'observaciones' in payload:
            payload['observaciones'] = str(payload.get('observaciones', '') or '').strip()
        # Remover campos no permitidos
        for key in ['marcado', 'archivado', 'fecha_archivo', 'fecha_creacion', 'fecha_actualizacion']:
            payload.pop(key, None)
        return payload

    def _clean_producto_payload(self, payload: dict) -> dict:
        """Normaliza y limpia el dict de un producto importado"""
        payload = dict(payload or {})
        if 'descripcion' in payload:
            payload['descripcion'] = str(payload['descripcion']).strip()
        if 'categoria' in payload:
            payload['categoria'] = str(payload['categoria'] or 'otros').strip() or 'otros'
        if 'peso' in payload:
            payload['peso'] = float(self._to_decimal(payload['peso']))
        if 'valor' in payload:
            payload['valor'] = float(self._to_decimal(payload['valor']))
        if 'cantidad' in payload:
            try:
                payload['cantidad'] = int(payload['cantidad'])
            except Exception:
                payload['cantidad'] = 1
        return payload

    @action(detail=False, methods=['post'])
    def import_excel(self, request):
        """Importar envíos desde archivo Excel"""
        if 'file' not in request.FILES:
            return Response(
                {'error': 'Se requiere un archivo Excel'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        excel_file = request.FILES['file']
        
        try:
            import pandas as pd
            from django.contrib.auth import get_user_model
            
            Usuario = get_user_model()
            
            # Leer archivo Excel
            df = pd.read_excel(excel_file)
            # Limpieza de columnas: normalizar nombres y valores
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # Validar columnas requeridas
            required_columns = ['hawb', 'comprador_cedula', 'peso_total', 'valor_total']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return Response(
                    {'error': f'Columnas faltantes: {missing_columns}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            created_envios = []
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Limpieza por fila
                    hawb = str(row['hawb']).strip()
                    if not hawb:
                        errors.append(f'Fila {index+2}: HAWB vacío')
                        continue
                    # Buscar comprador
                    comprador = Usuario.objects.filter(
                        cedula=str(row['comprador_cedula']).strip()
                    ).first()
                    
                    if not comprador:
                        errors.append(f'Fila {index+2}: Comprador con cédula {row["comprador_cedula"]} no encontrado')
                        continue
                    
                    # Crear envío
                    envio_data = {
                        'hawb': hawb,
                        'comprador': comprador.id,
                        'peso_total': self._to_decimal(row.get('peso_total', 0)),
                        'valor_total': self._to_decimal(row.get('valor_total', 0)),
                        'cantidad_total': int(row.get('cantidad_total', 1) or 1),
                        'estado': str(row.get('estado', 'pendiente')).strip() or 'pendiente',
                        'observaciones': str(row.get('observaciones', '') or '').strip()
                    }
                    
                    serializer = EnvioCreateSerializer(data=envio_data)
                    if serializer.is_valid():
                        envio = serializer.save()
                        created_envios.append(envio)
                    else:
                        errors.append(f'Fila {index+2}: {serializer.errors}')
                        
                except Exception as e:
                    errors.append(f'Fila {index+2}: {str(e)}')
            
            # Registrar actividad
            try:
                from dashboard.views import log_user_activity
                log_user_activity(
                    request.user, 'import_data',
                    f'Importados {len(created_envios)} envíos desde Excel',
                    'Envio', None,
                    {'total_imported': len(created_envios), 'errors': len(errors)},
                    request
                )
            except:
                pass  # No fallar si no se puede registrar actividad
            
            return Response({
                'message': f'Importación completada',
                'created': len(created_envios),
                'errors': errors,
                'envios': EnvioListSerializer(created_envios, many=True).data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error procesando archivo Excel: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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

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

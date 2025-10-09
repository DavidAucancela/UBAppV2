from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import HistorialBusqueda
from .serializers import HistorialBusquedaSerializer, HistorialBusquedaListSerializer
from archivos.models import Envio, Producto
from django.utils import timezone
from django.db import models

Usuario = get_user_model()

class BusquedaViewSet(viewsets.ModelViewSet):
    """ViewSet para búsquedas y historial"""
    queryset = HistorialBusqueda.objects.all()
    serializer_class = HistorialBusquedaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['termino_busqueda']
    ordering_fields = ['fecha_busqueda', 'terminos_busqueda']
    ordering = ['-fecha_busqueda']

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return HistorialBusquedaListSerializer
        return HistorialBusquedaSerializer

    def get_queryset(self):
        """Filtra el queryset según el usuario"""
        return HistorialBusqueda.objects.filter(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """Realiza una búsqueda en usuarios, envíos y productos"""
        query = request.query_params.get('q', '')
        tipo = request.query_params.get('tipo', 'general')
        
        if not query:
            return Response({'error': 'Término de búsqueda requerido'}, status=status.HTTP_400_BAD_REQUEST)

        # Realizar búsqueda según el tipo
        resultados = {}
        
        if tipo in ['general', 'usuarios']:
            usuarios = Usuario.objects.filter(
                Q(nombre__icontains=query) | 
                Q(correo__icontains=query) |
                Q(cedula__icontains=query) |
                Q(username__icontains=query)
            )
            
            # Filtrar por permisos del usuario
            user = request.user
            if user.es_comprador:
                usuarios = usuarios.filter(id=user.id)
            elif user.es_digitador:
                usuarios = usuarios.filter(rol__in=[3, 4])
            elif user.es_gerente:
                usuarios = usuarios.exclude(rol=1)
            
            from usuarios.serializers import UsuarioListSerializer
            usuarios_serializer = UsuarioListSerializer(usuarios, many=True)
            resultados['usuarios'] = usuarios_serializer.data

        if tipo in ['general', 'envios']:
            envios = Envio.objects.filter(
                Q(hawb__icontains=query) | 
                Q(comprador__nombre__icontains=query) |
                Q(estado__icontains=query)
            )
            
            # Filtrar por permisos del usuario
            user = request.user
            if user.es_comprador:
                envios = envios.filter(comprador=user)
            
            from archivos.serializers import EnvioListSerializer
            envios_serializer = EnvioListSerializer(envios, many=True)
            resultados['envios'] = envios_serializer.data

        if tipo in ['general', 'productos']:
            productos = Producto.objects.filter(
                Q(descripcion__icontains=query) | 
                Q(categoria__icontains=query) |
                Q(envio__hawb__icontains=query)
            )
            
            # Filtrar por permisos del usuario
            user = request.user
            if user.es_comprador:
                productos = productos.filter(envio__comprador=user)
            
            from archivos.serializers import ProductoListSerializer
            productos_serializer = ProductoListSerializer(productos, many=True)
            resultados['productos'] = productos_serializer.data

        # Guardar en historial
        total_resultados = sum(len(resultados.get(key, [])) for key in resultados)
        HistorialBusqueda.objects.create(
            usuario=request.user,
            termino_busqueda=query,
            tipo_busqueda=tipo,
            resultados_encontrados=total_resultados
        )

        return Response({
            'query': query,
            'tipo': tipo,
            'total_resultados': total_resultados,
            'resultados': resultados
        })

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
        self.get_queryset().delete()
        return Response({'message': 'Historial limpiado correctamente'})

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de búsquedas del usuario"""
        user = request.user
        total_busquedas = HistorialBusqueda.objects.filter(usuario=user).count()
        busquedas_hoy = HistorialBusqueda.objects.filter(
            usuario=user,
            fecha_busqueda__date=timezone.now().date()
        ).count()
        
        # Búsquedas más populares
        busquedas_populares = HistorialBusqueda.objects.filter(
            usuario=user
        ).values('termino_busqueda').annotate(
            count=models.Count('termino_busqueda')
        ).order_by('-count')[:5]

        return Response({
            'total_busquedas': total_busquedas,
            'busquedas_hoy': busquedas_hoy,
            'busquedas_populares': busquedas_populares
        })

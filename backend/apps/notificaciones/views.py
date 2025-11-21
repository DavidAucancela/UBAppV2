from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Notificacion
from .serializers import NotificacionSerializer, NotificacionCountSerializer


class NotificacionViewSet(viewsets.ModelViewSet):
    """ViewSet para el modelo Notificación"""
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra las notificaciones por usuario autenticado"""
        return Notificacion.objects.filter(usuario=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """Lista las notificaciones del usuario autenticado"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'next': None,
            'previous': None,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def contador(self, request):
        """Obtiene el contador de notificaciones no leídas"""
        queryset = self.get_queryset()
        total = queryset.count()
        no_leidas = queryset.filter(leida=False).count()
        
        return Response({
            'total': total,
            'no_leidas': no_leidas
        })
    
    @action(detail=True, methods=['patch'], url_path='marcar-leida')
    def marcar_leida(self, request, pk=None):
        """Marca una notificación como leída"""
        notificacion = self.get_object()
        
        # Verificar que la notificación pertenece al usuario
        if notificacion.usuario != request.user:
            return Response(
                {'error': 'No tienes permiso para acceder a esta notificación'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notificacion.marcar_como_leida()
        serializer = self.get_serializer(notificacion)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='marcar-todas-leidas')
    def marcar_todas_leidas(self, request):
        """Marca todas las notificaciones del usuario como leídas"""
        queryset = self.get_queryset().filter(leida=False)
        
        # Actualizar todas las no leídas
        ahora = timezone.now()
        actualizadas = queryset.update(leida=True, fecha_lectura=ahora)
        
        return Response({
            'mensaje': f'Se marcaron {actualizadas} notificaciones como leídas',
            'actualizadas': actualizadas
        })
    
    def destroy(self, request, *args, **kwargs):
        """Elimina una notificación"""
        notificacion = self.get_object()
        
        # Verificar que la notificación pertenece al usuario
        if notificacion.usuario != request.user:
            return Response(
                {'error': 'No tienes permiso para eliminar esta notificación'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        self.perform_destroy(notificacion)
        return Response(status=status.HTTP_204_NO_CONTENT)

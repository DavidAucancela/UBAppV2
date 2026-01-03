"""
Repositorios para la app de notificaciones
Implementa el patrón Repository para acceso a datos de notificaciones
"""
from typing import Optional, List, Dict, Any
from django.db.models import QuerySet, Q, Count
from django.utils import timezone

from apps.core.base.base_repository import BaseRepository
from .models import Notificacion


class NotificacionRepository(BaseRepository):
    """
    Repositorio para operaciones de Notificacion.
    """
    
    @property
    def model(self):
        return Notificacion
    
    @property
    def select_related_fields(self) -> List[str]:
        return ['usuario']
    
    # ==================== CONSULTAS ESPECÍFICAS ====================
    
    def filtrar_por_usuario(self, usuario) -> QuerySet:
        """Obtiene notificaciones de un usuario"""
        return self._get_optimized_queryset().filter(usuario=usuario)
    
    def obtener_no_leidas(self, usuario) -> QuerySet:
        """Obtiene notificaciones no leídas de un usuario"""
        return self.filtrar_por_usuario(usuario).filter(leida=False)
    
    def obtener_recientes(self, usuario, limite: int = 10) -> QuerySet:
        """Obtiene las notificaciones más recientes"""
        return self.filtrar_por_usuario(usuario).order_by('-fecha_creacion')[:limite]
    
    # ==================== OPERACIONES ====================
    
    def marcar_como_leida(self, notificacion_id: int) -> Optional[Notificacion]:
        """Marca una notificación como leída"""
        try:
            notificacion = self.model.objects.get(id=notificacion_id)
            if not notificacion.leida:
                notificacion.leida = True
                notificacion.fecha_lectura = timezone.now()
                notificacion.save(update_fields=['leida', 'fecha_lectura'])
            return notificacion
        except self.model.DoesNotExist:
            return None
    
    def marcar_todas_como_leidas(self, usuario) -> int:
        """Marca todas las notificaciones del usuario como leídas"""
        return self.model.objects.filter(
            usuario=usuario,
            leida=False
        ).update(leida=True, fecha_lectura=timezone.now())
    
    # ==================== ESTADÍSTICAS ====================
    
    def contar_no_leidas(self, usuario) -> int:
        """Cuenta notificaciones no leídas"""
        return self.model.objects.filter(usuario=usuario, leida=False).count()
    
    def obtener_estadisticas(self, usuario) -> Dict[str, Any]:
        """Obtiene estadísticas de notificaciones"""
        notificaciones = self.model.objects.filter(usuario=usuario)
        
        return {
            'total': notificaciones.count(),
            'no_leidas': notificaciones.filter(leida=False).count(),
            'por_tipo': dict(
                notificaciones.values('tipo').annotate(count=Count('tipo')).values_list('tipo', 'count')
            )
        }
    
    # ==================== CREACIÓN ESPECÍFICA ====================
    
    def crear_notificacion_envio_asignado(self, envio) -> Optional[Notificacion]:
        """Crea notificación cuando se asigna un envío"""
        if not envio.comprador:
            return None
        
        return self.crear(
            usuario=envio.comprador,
            tipo='envio_asignado',
            titulo=f'Nuevo envío asignado: {envio.hawb}',
            mensaje=f'Se te ha asignado un nuevo envío con HAWB {envio.hawb}. '
                    f'Peso total: {envio.peso_total} kg, Valor total: ${envio.valor_total:.2f}',
            enlace=f'/envios/{envio.id}',
            metadata={
                'envio_id': envio.id,
                'hawb': envio.hawb,
                'peso_total': float(envio.peso_total),
                'valor_total': float(envio.valor_total),
                'estado': envio.estado,
            }
        )
    
    def crear_notificacion_estado_cambiado(
        self,
        envio,
        estado_anterior: str
    ) -> Optional[Notificacion]:
        """Crea notificación cuando cambia el estado de un envío"""
        if not envio.comprador:
            return None
        
        return self.crear(
            usuario=envio.comprador,
            tipo='estado_cambiado',
            titulo=f'Estado actualizado: {envio.hawb}',
            mensaje=f'El estado de tu envío {envio.hawb} ha cambiado de '
                    f'{dict(envio._meta.get_field("estado").choices).get(estado_anterior, estado_anterior)} '
                    f'a {envio.get_estado_display()}.',
            enlace=f'/envios/{envio.id}',
            metadata={
                'envio_id': envio.id,
                'hawb': envio.hawb,
                'estado_anterior': estado_anterior,
                'estado_nuevo': envio.estado,
            }
        )


# Instancia singleton para uso en servicios
notificacion_repository = NotificacionRepository()


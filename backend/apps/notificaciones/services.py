"""
Servicios para la app de notificaciones
Implementa la lógica de negocio relacionada con notificaciones
"""
from typing import Dict, Any, List
from django.db.models import QuerySet

from apps.core.base.base_service import BaseService
from .repositories import notificacion_repository
from .models import Notificacion


class NotificacionService(BaseService):
    """
    Servicio para operaciones de notificaciones.
    """
    
    # ==================== CONSULTAS ====================
    
    @staticmethod
    def obtener_notificaciones_usuario(usuario, limite: int = 50) -> QuerySet:
        """Obtiene notificaciones de un usuario"""
        return notificacion_repository.filtrar_por_usuario(usuario)[:limite]
    
    @staticmethod
    def obtener_no_leidas(usuario) -> QuerySet:
        """Obtiene notificaciones no leídas"""
        return notificacion_repository.obtener_no_leidas(usuario)
    
    @staticmethod
    def contar_no_leidas(usuario) -> int:
        """Cuenta notificaciones no leídas"""
        return notificacion_repository.contar_no_leidas(usuario)
    
    # ==================== OPERACIONES ====================
    
    @staticmethod
    def marcar_como_leida(notificacion_id: int, usuario) -> Notificacion:
        """
        Marca una notificación como leída.
        Valida que pertenece al usuario.
        """
        notificacion = notificacion_repository.obtener_por_id(notificacion_id)
        
        if notificacion.usuario_id != usuario.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes acceso a esta notificación")
        
        notificacion_repository.marcar_como_leida(notificacion_id)
        return notificacion
    
    @staticmethod
    def marcar_todas_como_leidas(usuario) -> int:
        """Marca todas las notificaciones del usuario como leídas"""
        return notificacion_repository.marcar_todas_como_leidas(usuario)
    
    @staticmethod
    def eliminar_notificacion(notificacion_id: int, usuario):
        """Elimina una notificación"""
        notificacion = notificacion_repository.obtener_por_id(notificacion_id)
        
        if notificacion.usuario_id != usuario.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes acceso a esta notificación")
        
        notificacion_repository.eliminar(notificacion)
    
    # ==================== CREACIÓN DE NOTIFICACIONES ====================
    
    @staticmethod
    def enviar_notificacion_envio_creado(envio) -> Notificacion:
        """Envía notificación de envío creado/asignado"""
        return notificacion_repository.crear_notificacion_envio_asignado(envio)
    
    @staticmethod
    def enviar_notificacion_cambio_estado(envio, estado_anterior: str) -> Notificacion:
        """Envía notificación de cambio de estado"""
        return notificacion_repository.crear_notificacion_estado_cambiado(
            envio, estado_anterior
        )
    
    @staticmethod
    def crear_notificacion_general(
        usuario,
        titulo: str,
        mensaje: str,
        enlace: str = None,
        metadata: Dict = None
    ) -> Notificacion:
        """Crea una notificación general"""
        return notificacion_repository.crear(
            usuario=usuario,
            tipo='general',
            titulo=titulo,
            mensaje=mensaje,
            enlace=enlace,
            metadata=metadata or {}
        )
    
    # ==================== ESTADÍSTICAS ====================
    
    @staticmethod
    def obtener_estadisticas(usuario) -> Dict[str, Any]:
        """Obtiene estadísticas de notificaciones"""
        return notificacion_repository.obtener_estadisticas(usuario)


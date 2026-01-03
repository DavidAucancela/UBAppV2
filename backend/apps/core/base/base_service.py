"""
Base Service - Clase base para todos los servicios del sistema
Implementa el patrón Service Layer para centralizar lógica de negocio
"""
from abc import ABC
from typing import Optional, Dict, Any
import logging
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """
    Clase base para servicios de dominio.
    
    Responsabilidades:
    - Implementar lógica de negocio
    - Orquestar operaciones entre múltiples repositorios
    - Validar reglas de dominio
    
    NO debe:
    - Conocer detalles de HTTP (request, response)
    - Acceder directamente a modelos (usar repositorios)
    """
    
    # ==================== VALIDACIÓN DE PERMISOS ====================
    
    @staticmethod
    def validar_es_admin(usuario) -> None:
        """
        Valida que el usuario sea administrador.
        
        Args:
            usuario: Instancia del usuario
            
        Raises:
            PermissionDenied: Si no es admin
        """
        if not usuario.es_admin:
            raise PermissionDenied("Solo administradores pueden realizar esta acción")
    
    @staticmethod
    def validar_es_admin_o_gerente(usuario) -> None:
        """
        Valida que el usuario sea admin o gerente.
        
        Args:
            usuario: Instancia del usuario
            
        Raises:
            PermissionDenied: Si no es admin ni gerente
        """
        if not (usuario.es_admin or usuario.es_gerente):
            raise PermissionDenied("Solo administradores y gerentes pueden realizar esta acción")
    
    @staticmethod
    def validar_puede_gestionar_envios(usuario) -> None:
        """
        Valida que el usuario puede gestionar envíos.
        
        Args:
            usuario: Instancia del usuario
            
        Raises:
            PermissionDenied: Si no tiene permisos
        """
        if not (usuario.es_admin or usuario.es_gerente or usuario.es_digitador):
            raise PermissionDenied("No tienes permisos para gestionar envíos")
    
    @staticmethod
    def validar_puede_ver_usuario(usuario_actual, usuario_objetivo) -> None:
        """
        Valida que el usuario actual puede ver el usuario objetivo.
        
        Args:
            usuario_actual: Usuario que realiza la acción
            usuario_objetivo: Usuario que se quiere ver
            
        Raises:
            PermissionDenied: Si no tiene permisos
        """
        # Admin puede ver a todos
        if usuario_actual.es_admin:
            return
        
        # Gerente puede ver a todos excepto admin
        if usuario_actual.es_gerente and not usuario_objetivo.es_admin:
            return
        
        # Digitador puede ver digitadores y compradores
        if usuario_actual.es_digitador and usuario_objetivo.rol in [3, 4]:
            return
        
        # Comprador solo puede verse a sí mismo
        if usuario_actual.id == usuario_objetivo.id:
            return
        
        raise PermissionDenied("No tienes permisos para ver este usuario")
    
    # ==================== LOGGING ====================
    
    @staticmethod
    def log_info(mensaje: str, extra: Dict[str, Any] = None, usuario_id: int = None):
        """
        Log de información con contexto adicional.
        
        Args:
            mensaje: Mensaje a registrar
            extra: Información adicional
            usuario_id: ID del usuario relacionado (opcional)
        """
        context = extra or {}
        if usuario_id:
            context['usuario_id'] = usuario_id
        context['tipo'] = 'info'
        logger.info(mensaje, extra=context)
    
    @staticmethod
    def log_warning(mensaje: str, extra: Dict[str, Any] = None, usuario_id: int = None):
        """
        Log de advertencia con contexto adicional.
        
        Args:
            mensaje: Mensaje a registrar
            extra: Información adicional
            usuario_id: ID del usuario relacionado (opcional)
        """
        context = extra or {}
        if usuario_id:
            context['usuario_id'] = usuario_id
        context['tipo'] = 'warning'
        logger.warning(mensaje, extra=context)
    
    @staticmethod
    def log_error(error: Exception, contexto: str, extra: Dict[str, Any] = None, usuario_id: int = None):
        """
        Log de errores con contexto detallado.
        
        Args:
            error: Excepción capturada
            contexto: Descripción del contexto donde ocurrió
            extra: Información adicional
            usuario_id: ID del usuario relacionado (opcional)
        """
        context = extra or {}
        if usuario_id:
            context['usuario_id'] = usuario_id
        context['tipo'] = 'error'
        context['excepcion'] = type(error).__name__
        context['mensaje_error'] = str(error)
        
        logger.error(
            f"{contexto}: {type(error).__name__}: {str(error)}",
            exc_info=True,
            extra=context
        )
    
    @staticmethod
    def log_operacion(operacion: str, entidad: str, entidad_id: int = None, 
                     usuario_id: int = None, detalles: Dict[str, Any] = None):
        """
        Log estructurado para operaciones de negocio.
        
        Args:
            operacion: Nombre de la operación (crear, actualizar, eliminar, etc.)
            entidad: Tipo de entidad (Usuario, Envio, etc.)
            entidad_id: ID de la entidad afectada (opcional)
            usuario_id: ID del usuario que realiza la operación (opcional)
            detalles: Información adicional sobre la operación
        """
        context = {
            'operacion': operacion,
            'entidad': entidad,
            'tipo': 'operacion'
        }
        
        if entidad_id:
            context['entidad_id'] = entidad_id
        if usuario_id:
            context['usuario_id'] = usuario_id
        if detalles:
            context.update(detalles)
        
        mensaje = f"{operacion.title()} {entidad}"
        if entidad_id:
            mensaje += f" (ID: {entidad_id})"
        if usuario_id:
            mensaje += f" por usuario {usuario_id}"
        
        logger.info(mensaje, extra=context)
    
    @staticmethod
    def log_metrica(metrica: str, valor: Any, unidad: str = None, 
                   usuario_id: int = None, contexto: Dict[str, Any] = None):
        """
        Log de métricas del sistema.
        
        Args:
            metrica: Nombre de la métrica
            valor: Valor de la métrica
            unidad: Unidad de medida (opcional)
            usuario_id: ID del usuario relacionado (opcional)
            contexto: Contexto adicional
        """
        context = {
            'metrica': metrica,
            'valor': valor,
            'tipo': 'metrica'
        }
        
        if unidad:
            context['unidad'] = unidad
        if usuario_id:
            context['usuario_id'] = usuario_id
        if contexto:
            context.update(contexto)
        
        mensaje = f"Métrica {metrica}: {valor}"
        if unidad:
            mensaje += f" {unidad}"
        
        logger.info(mensaje, extra=context)
    
    # ==================== TRANSACCIONES ====================
    
    @staticmethod
    def ejecutar_en_transaccion(func, *args, **kwargs):
        """
        Ejecuta una función dentro de una transacción atómica.
        
        Args:
            func: Función a ejecutar
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            Resultado de la función
        """
        with transaction.atomic():
            return func(*args, **kwargs)
    
    # ==================== VALIDACIONES DE DOMINIO ====================
    
    @staticmethod
    def validar_no_vacio(valor: Any, campo: str) -> None:
        """
        Valida que un valor no esté vacío.
        
        Args:
            valor: Valor a validar
            campo: Nombre del campo para el mensaje de error
            
        Raises:
            ValidationError: Si el valor está vacío
        """
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ValidationError({campo: f"El campo {campo} es requerido"})
    
    @staticmethod
    def validar_positivo(valor: float, campo: str) -> None:
        """
        Valida que un valor numérico sea positivo.
        
        Args:
            valor: Valor a validar
            campo: Nombre del campo para el mensaje de error
            
        Raises:
            ValidationError: Si el valor no es positivo
        """
        if valor is None or float(valor) <= 0:
            raise ValidationError({campo: f"El campo {campo} debe ser mayor a 0"})
    
    @staticmethod
    def validar_no_negativo(valor: float, campo: str) -> None:
        """
        Valida que un valor numérico no sea negativo.
        
        Args:
            valor: Valor a validar
            campo: Nombre del campo para el mensaje de error
            
        Raises:
            ValidationError: Si el valor es negativo
        """
        if valor is not None and float(valor) < 0:
            raise ValidationError({campo: f"El campo {campo} no puede ser negativo"})


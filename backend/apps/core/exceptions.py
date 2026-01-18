"""
Excepciones personalizadas y manejo centralizado de errores
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
import logging

logger = logging.getLogger(__name__)


# ==================== EXCEPCIONES DE DOMINIO ====================

class DomainException(Exception):
    """Excepción base para errores de dominio"""
    
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or 'domain_error'
        super().__init__(self.message)


class EntityNotFoundError(DomainException):
    """Excepción cuando no se encuentra una entidad"""
    
    def __init__(self, entity_name: str, identifier: str = None):
        message = f"{entity_name} no encontrado"
        if identifier:
            message = f"{entity_name} con identificador '{identifier}' no encontrado"
        super().__init__(message, 'not_found')
        self.entity_name = entity_name
        self.identifier = identifier


class UsuarioNoEncontradoError(EntityNotFoundError):
    """Excepción cuando no se encuentra un usuario"""
    
    def __init__(self, identifier: str = None):
        super().__init__("Usuario", identifier)


class EnvioNoEncontradoError(EntityNotFoundError):
    """Excepción cuando no se encuentra un envío"""
    
    def __init__(self, identifier: str = None):
        super().__init__("Envío", identifier)


class ProductoNoEncontradoError(EntityNotFoundError):
    """Excepción cuando no se encuentra un producto"""
    
    def __init__(self, identifier: str = None):
        super().__init__("Producto", identifier)


class TarifaNoEncontradaError(EntityNotFoundError):
    """Excepción cuando no se encuentra una tarifa"""
    
    def __init__(self, identifier: str = None):
        super().__init__("Tarifa", identifier)


class EmbeddingNoEncontradoError(EntityNotFoundError):
    """Excepción cuando no se encuentra un embedding"""
    
    def __init__(self, identifier: str = None):
        super().__init__("Embedding", identifier)


class BusinessRuleViolationError(DomainException):
    """Excepción cuando se viola una regla de negocio"""
    
    def __init__(self, message: str, rule: str = None):
        super().__init__(message, 'business_rule_violation')
        self.rule = rule


class CupoExcedidoError(BusinessRuleViolationError):
    """Excepción cuando se excede el cupo anual"""
    
    def __init__(self, cupo_disponible: float, peso_solicitado: float):
        message = f"Cupo excedido. Disponible: {cupo_disponible}kg, Solicitado: {peso_solicitado}kg"
        super().__init__(message, 'cupo_excedido')
        self.cupo_disponible = cupo_disponible
        self.peso_solicitado = peso_solicitado


class TransicionEstadoInvalidaError(BusinessRuleViolationError):
    """Excepción cuando una transición de estado no es válida"""
    
    def __init__(self, estado_actual: str, estado_nuevo: str, transiciones_validas: list = None):
        # Definir transiciones válidas si no se proporcionan
        if transiciones_validas is None:
            from apps.archivos.services import EnvioService
            transiciones_validas = EnvioService.TRANSICIONES_VALIDAS.get(estado_actual, [])
        
        # Construir mensaje con las transiciones válidas
        if transiciones_validas:
            estados_validos_str = " o ".join(transiciones_validas)
            message = (
                f"Transición de estado inválida: {estado_actual} -> {estado_nuevo}. "
                f"Desde el estado '{estado_actual}' solo puede cambiar a: {estados_validos_str}"
            )
        else:
            message = (
                f"Transición de estado inválida: {estado_actual} -> {estado_nuevo}. "
                f"El estado '{estado_actual}' es un estado final y no puede cambiar a otro estado."
            )
        
        super().__init__(message, 'transicion_invalida')
        self.estado_actual = estado_actual
        self.estado_nuevo = estado_nuevo
        self.transiciones_validas = transiciones_validas


class ExternalServiceError(DomainException):
    """Excepción para errores de servicios externos"""
    
    def __init__(self, service_name: str, message: str):
        full_message = f"Error en servicio {service_name}: {message}"
        super().__init__(full_message, 'external_service_error')
        self.service_name = service_name


class OpenAIServiceError(ExternalServiceError):
    """Excepción para errores del servicio de OpenAI"""
    
    def __init__(self, message: str):
        super().__init__("OpenAI", message)


class ConfigurationError(DomainException):
    """Excepción para errores de configuración"""
    
    def __init__(self, message: str):
        super().__init__(message, 'configuration_error')


class OpenAINotConfiguredError(ConfigurationError):
    """Excepción cuando OpenAI no está configurado"""
    
    def __init__(self):
        super().__init__(
            "OpenAI API key no configurada. "
            "Configure OPENAI_API_KEY en el archivo .env"
        )


# ==================== EXCEPCIONES API ====================

class DomainAPIException(APIException):
    """Excepción API para errores de dominio"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Ha ocurrido un error en la operación'
    default_code = 'domain_error'


class NotFoundAPIException(APIException):
    """Excepción API para recursos no encontrados"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Recurso no encontrado'
    default_code = 'not_found'


class BusinessRuleAPIException(APIException):
    """Excepción API para violaciones de reglas de negocio"""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'La operación viola una regla de negocio'
    default_code = 'business_rule_violation'


class ExternalServiceAPIException(APIException):
    """Excepción API para errores de servicios externos"""
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'Error en servicio externo'
    default_code = 'external_service_error'


# ==================== MANEJADOR CENTRALIZADO ====================

def custom_exception_handler(exc, context):
    """
    Manejador personalizado de excepciones para respuestas consistentes.
    
    Convierte excepciones de dominio a respuestas HTTP apropiadas.
    """
    # Manejar excepciones de dominio
    if isinstance(exc, EntityNotFoundError):
        logger.warning(f"Entidad no encontrada: {exc.message}")
        return Response(
            {
                'error': True,
                'code': exc.code,
                'message': exc.message,
                'entity': exc.entity_name,
                'identifier': exc.identifier
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if isinstance(exc, BusinessRuleViolationError):
        logger.warning(f"Violación de regla de negocio: {exc.message}")
        response_data = {
            'error': True,
            'code': exc.code,
            'message': exc.message,
            'rule': getattr(exc, 'rule', None)
        }
        # Agregar información adicional para TransicionEstadoInvalidaError
        if isinstance(exc, TransicionEstadoInvalidaError):
            response_data['estado_actual'] = exc.estado_actual
            response_data['estado_nuevo'] = exc.estado_nuevo
            response_data['transiciones_validas'] = exc.transiciones_validas
        return Response(
            response_data,
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    if isinstance(exc, ExternalServiceError):
        logger.error(f"Error de servicio externo: {exc.message}")
        return Response(
            {
                'error': True,
                'code': exc.code,
                'message': exc.message,
                'service': exc.service_name
            },
            status=status.HTTP_502_BAD_GATEWAY
        )
    
    if isinstance(exc, ConfigurationError):
        logger.error(f"Error de configuración: {exc.message}")
        return Response(
            {
                'error': True,
                'code': exc.code,
                'message': exc.message
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    if isinstance(exc, DomainException):
        logger.warning(f"Error de dominio: {exc.message}")
        return Response(
            {
                'error': True,
                'code': exc.code,
                'message': exc.message
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Obtener el handler estándar de DRF
    response = exception_handler(exc, context)
    
    # Si DRF no maneja la excepción, crear respuesta genérica
    if response is None:
        logger.exception(f"Excepción no manejada: {type(exc).__name__}: {str(exc)}")
        return Response(
            {
                'error': True,
                'code': 'internal_error',
                'message': 'Ha ocurrido un error en el servidor'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Personalizar respuesta de DRF para consistencia
    if hasattr(response, 'data'):
        original_data = response.data
        
        # Si es un dict con 'detail', normalizarlo
        if isinstance(original_data, dict):
            if 'detail' in original_data:
                response.data = {
                    'error': True,
                    'code': original_data.get('code', 'api_error'),
                    'message': str(original_data['detail']),
                    'details': {k: v for k, v in original_data.items() if k != 'detail'}
                }
            else:
                response.data = {
                    'error': True,
                    'code': 'validation_error',
                    'message': 'Error de validación',
                    'details': original_data
                }
        elif isinstance(original_data, list):
            response.data = {
                'error': True,
                'code': 'validation_error',
                'message': 'Errores de validación',
                'details': original_data
            }
    
    return response


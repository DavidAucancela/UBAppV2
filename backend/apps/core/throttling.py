"""
Clases de Rate Limiting (Throttling) personalizadas para UBApp.
Proporciona control granular sobre las tasas de solicitud por tipo de endpoint.
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class BusquedaRateThrottle(UserRateThrottle):
    """
    Throttling específico para endpoints de búsqueda.
    Limita a 60 búsquedas por minuto por usuario autenticado.
    """
    scope = 'busqueda'
    cache = 'throttle' if 'throttle' in __import__('django.conf', fromlist=['settings']).settings.CACHES else 'default'


class BusquedaSemanticaRateThrottle(UserRateThrottle):
    """
    Throttling específico para búsqueda semántica.
    Más restrictivo debido al costo de las llamadas a OpenAI.
    Limita a 30 búsquedas semánticas por minuto.
    """
    scope = 'busqueda_semantica'
    rate = '30/minute'


class LoginRateThrottle(AnonRateThrottle):
    """
    Throttling para intentos de login.
    Protege contra ataques de fuerza bruta.
    Limita a 5 intentos por minuto por IP.
    """
    scope = 'login'
    

class RegistroRateThrottle(AnonRateThrottle):
    """
    Throttling para registro de usuarios.
    Previene creación masiva de cuentas.
    Limita a 3 registros por hora por IP.
    """
    scope = 'registro'
    rate = '3/hour'


class ImportacionRateThrottle(UserRateThrottle):
    """
    Throttling para importación de archivos Excel.
    Limita operaciones intensivas en recursos.
    """
    scope = 'importacion'
    rate = '10/hour'


class ExportacionRateThrottle(UserRateThrottle):
    """
    Throttling para exportación de archivos (PDF, Excel).
    Limita operaciones intensivas.
    """
    scope = 'exportacion'
    rate = '30/hour'


class APIBurstThrottle(UserRateThrottle):
    """
    Throttling para ráfagas de solicitudes API.
    Permite ráfagas cortas pero limita el uso sostenido.
    """
    scope = 'burst'
    rate = '60/minute'


class APISustainedThrottle(UserRateThrottle):
    """
    Throttling para uso sostenido de la API.
    Limita el uso total por día.
    """
    scope = 'sustained'
    rate = '10000/day'








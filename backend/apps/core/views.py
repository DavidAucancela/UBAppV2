"""
Vistas core del sistema
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import redis


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint de health check para verificar el estado del sistema.
    Útil para monitoreo y health checks de Docker/Kubernetes.
    """
    health_status = {
        'status': 'healthy',
        'database': 'unknown',
        'cache': 'unknown',
        'version': '2.0.0'
    }
    http_status = status.HTTP_200_OK
    
    # Verificar base de datos
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['database'] = 'connected'
    except Exception as e:
        health_status['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    
    # Verificar cache (Redis si está configurado)
    try:
        if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
            # Intentar conectar a Redis
            cache.set('health_check', 'ok', 10)
            result = cache.get('health_check')
            if result == 'ok':
                health_status['cache'] = 'connected'
            else:
                health_status['cache'] = 'error'
                health_status['status'] = 'degraded'
        else:
            health_status['cache'] = 'not_configured'
    except Exception as e:
        health_status['cache'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'
    
    return Response(health_status, status=http_status)

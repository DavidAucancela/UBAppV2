from django.contrib.auth import get_user_model
from .models import Notificacion

Usuario = get_user_model()


def crear_notificacion_envio_asignado(envio):
    """
    Crea una notificación cuando se asigna un envío a un comprador
    
    Args:
        envio: Instancia del modelo Envio
    """
    if not envio.comprador:
        return None
    
    # Crear la notificación
    notificacion = Notificacion.objects.create(
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
    
    return notificacion


def crear_notificacion_estado_cambiado(envio, estado_anterior):
    """
    Crea una notificación cuando cambia el estado de un envío
    
    Args:
        envio: Instancia del modelo Envio
        estado_anterior: Estado anterior del envío
    """
    if not envio.comprador:
        return None
    
    # Crear la notificación
    notificacion = Notificacion.objects.create(
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
    
    return notificacion


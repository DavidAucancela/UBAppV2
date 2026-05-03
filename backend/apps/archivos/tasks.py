"""
Tareas Celery asíncronas para el módulo de archivos.
Reemplazan el uso de threading para operaciones post-transacción.
"""
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=2)
def generar_embedding_envio(self, envio_id: int, forzar_regeneracion: bool = False):
    """Genera el embedding semántico de un envío."""
    from apps.archivos.repositories import envio_repository
    from apps.core.exceptions import EnvioNoEncontradoError

    try:
        envio = envio_repository.obtener_por_id(envio_id)
    except EnvioNoEncontradoError as exc:
        raise self.retry(exc=exc)

    try:
        from apps.busqueda.semantic.embedding_service import EmbeddingService
        EmbeddingService.generar_embedding_envio(envio, forzar_regeneracion=forzar_regeneracion)
    except Exception as exc:
        logger.error(f"Error generando embedding para envio {envio_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=2)
def notificar_envio_creado(self, envio_id: int):
    """Notifica al comprador que se creó un envío."""
    from apps.archivos.repositories import envio_repository
    from apps.core.exceptions import EnvioNoEncontradoError

    try:
        envio = envio_repository.obtener_por_id(envio_id)
    except EnvioNoEncontradoError as exc:
        raise self.retry(exc=exc)

    try:
        if envio.comprador and envio.comprador.es_comprador:
            from apps.notificaciones.repositories import notificacion_repository
            notificacion_repository.crear_notificacion_envio_asignado(envio)
    except Exception as exc:
        logger.error(f"Error notificando envio creado {envio_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=2)
def notificar_cambio_estado(self, envio_id: int, estado_anterior: str):
    """Notifica al comprador el cambio de estado de un envío."""
    from apps.archivos.repositories import envio_repository
    from apps.core.exceptions import EnvioNoEncontradoError

    try:
        envio = envio_repository.obtener_por_id(envio_id)
    except EnvioNoEncontradoError as exc:
        raise self.retry(exc=exc)

    try:
        if envio.comprador and envio.comprador.es_comprador:
            from apps.notificaciones.repositories import notificacion_repository
            notificacion_repository.crear_notificacion_estado_cambiado(envio, estado_anterior)
    except Exception as exc:
        logger.error(f"Error notificando cambio estado envio {envio_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task
def log_creacion_envio(envio_id: int, usuario_id: int, hawb: str,
                       peso_total: float, valor_total: float,
                       estado: str, comprador_id):
    """Registra métricas y log de auditoría de la creación de un envío."""
    from apps.core.base.base_service import BaseService
    try:
        BaseService.log_operacion(
            operacion='crear',
            entidad='Envio',
            entidad_id=envio_id,
            usuario_id=usuario_id,
            detalles={
                'hawb': hawb,
                'peso_total': peso_total,
                'valor_total': valor_total,
                'estado': estado,
                'comprador_id': comprador_id,
            }
        )
        BaseService.log_metrica(
            metrica='envio_creado',
            valor=1,
            unidad='unidad',
            usuario_id=usuario_id,
            contexto={'hawb': hawb}
        )
    except Exception as exc:
        logger.warning(f"Error en log de creación de envio {envio_id}: {exc}")

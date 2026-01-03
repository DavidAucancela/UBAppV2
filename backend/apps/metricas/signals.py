"""
Signals para registro automático de generación de embeddings.
"""
import time
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from apps.archivos.models import Envio
from apps.busqueda.models import EnvioEmbedding
from apps.busqueda.semantic.embedding_service import EmbeddingService
from .services import RegistroEmbeddingService
from .models import RegistroGeneracionEmbedding

logger = logging.getLogger(__name__)


@receiver(post_save, sender=EnvioEmbedding)
def registrar_generacion_embedding(sender, instance, created, **kwargs):
    """
    Registra automáticamente la generación de un embedding.
    Se ejecuta cuando se crea o actualiza un EnvioEmbedding.
    """
    if created:
        # Embedding recién creado
        try:
            # Obtener el tiempo de generación (aproximado)
            # Nota: El tiempo real debería medirse en el servicio de generación
            tiempo_generacion_ms = 0  # Se actualizará desde el servicio
            
            RegistroEmbeddingService.registrar_generacion(
                envio=instance.envio,
                estado='generado',
                tiempo_generacion_ms=tiempo_generacion_ms,
                modelo_usado=instance.modelo_usado,
                tipo_proceso='automatico',
                embedding=instance
            )
        except Exception as e:
            logger.error(f"Error registrando generación de embedding: {str(e)}", exc_info=True)


def registrar_generacion_embedding_manual(
    envio: Envio,
    estado: str,
    tiempo_generacion_ms: int,
    modelo_usado: str = 'text-embedding-3-small',
    tipo_proceso: str = 'manual',
    mensaje_error: str = None,
    embedding: EnvioEmbedding = None
):
    """
    Función auxiliar para registrar generación de embedding manualmente.
    Se llama desde los servicios de generación de embeddings.
    
    Args:
        envio: Instancia del envío
        estado: Estado de la generación
        tiempo_generacion_ms: Tiempo de generación en milisegundos
        modelo_usado: Modelo utilizado
        tipo_proceso: Tipo de proceso ('automatico', 'manual', 'masivo')
        mensaje_error: Mensaje de error si hubo fallo
        embedding: Instancia del embedding generado (opcional)
    """
    try:
        RegistroEmbeddingService.registrar_generacion(
            envio=envio,
            estado=estado,
            tiempo_generacion_ms=tiempo_generacion_ms,
            modelo_usado=modelo_usado,
            tipo_proceso=tipo_proceso,
            mensaje_error=mensaje_error,
            embedding=embedding
        )
    except Exception as e:
        logger.error(f"Error registrando generación de embedding manual: {str(e)}", exc_info=True)


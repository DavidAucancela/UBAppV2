from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
Usuario = get_user_model()


@receiver(post_save, sender=Usuario)
def log_usuario_creado(sender, instance, created, **kwargs):
    """Registra cuando se crea un usuario."""
    if created:
        try:
            rol_nombre = instance.get_rol_display_name()
        except Exception:
            rol_nombre = str(getattr(instance, 'rol', ''))
        logger.info(
            f"Usuario creado: username={instance.username} id={instance.id} rol={rol_nombre} activo={instance.es_activo}"
        )


@receiver(pre_save, sender=Usuario)
def log_cambio_rol(sender, instance, **kwargs):
    """Registra cambios sensibles como rol o estado de actividad."""
    if not instance.pk:
        return
    try:
        anterior = Usuario.objects.get(pk=instance.pk)
    except Usuario.DoesNotExist:
        return

    if anterior.rol != instance.rol:
        try:
            anterior_rol = anterior.get_rol_display_name()
            nuevo_rol = instance.get_rol_display_name()
        except Exception:
            anterior_rol = str(anterior.rol)
            nuevo_rol = str(instance.rol)
        logger.warning(
            f"Cambio de rol: username={instance.username} {anterior_rol} -> {nuevo_rol}"
        )

    if anterior.es_activo != instance.es_activo:
        logger.warning(
            f"Cambio de estado activo: username={instance.username} {anterior.es_activo} -> {instance.es_activo}"
        )



"""
Signals para registrar auditoría automáticamente en Envio y Usuario.
"""
import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict

from .middleware import get_current_user, get_current_ip

logger = logging.getLogger(__name__)


def _serialize(instance):
    """Convierte una instancia de modelo a dict serializable."""
    try:
        data = {}
        for field in instance._meta.fields:
            val = getattr(instance, field.attname)
            if hasattr(val, 'isoformat'):
                val = val.isoformat()
            elif hasattr(val, '__str__') and not isinstance(val, (str, int, float, bool, type(None))):
                val = str(val)
            data[field.attname] = val
        return data
    except Exception:
        return {}


def _log(tabla, objeto_id, accion, datos_anteriores=None, datos_nuevos=None):
    from .models import AuditLog
    try:
        AuditLog.objects.create(
            tabla=tabla,
            objeto_id=str(objeto_id),
            accion=accion,
            usuario=get_current_user(),
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address=get_current_ip(),
        )
    except Exception as e:
        logger.error(f"Error creando AuditLog para {tabla}({objeto_id}): {e}")


def connect_audit_signals():
    """Conecta los signals de auditoría para los modelos principales."""
    from apps.archivos.models import Envio
    from apps.usuarios.models import Usuario

    # ----- Envio -----
    @receiver(post_save, sender=Envio, dispatch_uid='audit_envio_save')
    def audit_envio_save(sender, instance, created, **kwargs):
        accion = AuditLog.CREAR if created else AuditLog.ACTUALIZAR
        _log('envio', instance.pk, accion, datos_nuevos=_serialize(instance))

    @receiver(pre_delete, sender=Envio, dispatch_uid='audit_envio_delete')
    def audit_envio_delete(sender, instance, **kwargs):
        _log('envio', instance.pk, AuditLog.ELIMINAR, datos_anteriores=_serialize(instance))

    # ----- Usuario -----
    @receiver(post_save, sender=Usuario, dispatch_uid='audit_usuario_save')
    def audit_usuario_save(sender, instance, created, **kwargs):
        accion = AuditLog.CREAR if created else AuditLog.ACTUALIZAR
        data = _serialize(instance)
        data.pop('password', None)  # nunca loggear contraseñas
        _log('usuarios', instance.pk, accion, datos_nuevos=data)

    @receiver(pre_delete, sender=Usuario, dispatch_uid='audit_usuario_delete')
    def audit_usuario_delete(sender, instance, **kwargs):
        data = _serialize(instance)
        data.pop('password', None)
        _log('usuarios', instance.pk, AuditLog.ELIMINAR, datos_anteriores=data)

    from .models import AuditLog  # noqa: F811 — needed for accion constants above

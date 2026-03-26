"""
Modelos base reutilizables para todo el proyecto.
- SoftDeleteModel: borrado lógico
- AuditLog: registro de auditoría
"""
import json
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


# ==================== SOFT DELETE ====================

class SoftDeleteManager(models.Manager):
    """Manager que excluye registros eliminados lógicamente."""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager):
    """Manager que devuelve todos los registros, incluidos los eliminados."""
    pass


class SoftDeleteModel(models.Model):
    """
    Mixin de borrado lógico. En lugar de eliminar el registro de la BD,
    marca deleted_at con la fecha actual.
    """
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def hard_delete(self):
        """Elimina el registro físicamente de la BD."""
        super().delete()

    def restore(self):
        """Restaura un registro eliminado lógicamente."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    @property
    def esta_eliminado(self):
        return self.deleted_at is not None


# ==================== AUDIT LOG ====================

class AuditLog(models.Model):
    CREAR = 'CREATE'
    ACTUALIZAR = 'UPDATE'
    ELIMINAR = 'DELETE'
    RESTAURAR = 'RESTORE'

    ACCION_CHOICES = [
        (CREAR, 'Crear'),
        (ACTUALIZAR, 'Actualizar'),
        (ELIMINAR, 'Eliminar'),
        (RESTAURAR, 'Restaurar'),
    ]

    tabla = models.CharField(max_length=100)
    objeto_id = models.CharField(max_length=50)
    accion = models.CharField(max_length=10, choices=ACCION_CHOICES)
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
    )
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'audit_log'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['tabla', 'objeto_id']),
            models.Index(fields=['usuario', 'fecha']),
        ]

    def __str__(self):
        return f"{self.accion} {self.tabla}({self.objeto_id}) by {self.usuario_id} at {self.fecha}"

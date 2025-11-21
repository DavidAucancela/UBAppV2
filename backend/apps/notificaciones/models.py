from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

Usuario = get_user_model()


class Notificacion(models.Model):
    """Modelo para gestionar notificaciones de usuarios"""
    
    TIPO_CHOICES = [
        ('nuevo_envio', 'Nuevo Envío'),
        ('envio_asignado', 'Envío Asignado'),
        ('estado_cambiado', 'Estado Cambiado'),
        ('general', 'General'),
    ]
    
    # Usuario destinatario de la notificación
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name="Usuario"
    )
    
    # Tipo de notificación
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='general',
        verbose_name="Tipo"
    )
    
    # Contenido de la notificación
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título"
    )
    
    mensaje = models.TextField(
        verbose_name="Mensaje"
    )
    
    # Estado de lectura
    leida = models.BooleanField(
        default=False,
        verbose_name="Leída"
    )
    
    fecha_lectura = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Lectura"
    )
    
    # Enlace opcional (ej: a un envío específico)
    enlace = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Enlace"
    )
    
    # Metadata adicional en formato JSON
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadata",
        help_text="Información adicional en formato JSON (envio_id, estado_anterior, etc.)"
    )
    
    # Fechas
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'leida']),
            models.Index(fields=['fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.nombre}"
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save(update_fields=['leida', 'fecha_lectura'])

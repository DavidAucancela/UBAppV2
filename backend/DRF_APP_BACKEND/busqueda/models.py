from django.db import models
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class HistorialBusqueda(models.Model):
    """Modelo para almacenar historial de búsquedas"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    termino_busqueda = models.CharField(max_length=255)
    tipo_busqueda = models.CharField(max_length=50, default='general')
    fecha_busqueda = models.DateTimeField(auto_now_add=True)
    resultados_encontrados = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Historial de Búsqueda'
        verbose_name_plural = 'Historial de Búsquedas'
        ordering = ['-fecha_busqueda']

    def __str__(self):
        return f"{self.usuario.username} - {self.termino_busqueda}"

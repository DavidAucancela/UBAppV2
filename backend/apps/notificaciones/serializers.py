from rest_framework import serializers
from .models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Notificación"""
    tipo_nombre = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Notificacion
        fields = [
            'id', 'tipo', 'tipo_nombre', 'titulo', 'mensaje', 'leida',
            'fecha_creacion', 'fecha_lectura', 'enlace', 'metadata'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']


class NotificacionCountSerializer(serializers.Serializer):
    """Serializer para el contador de notificaciones"""
    total = serializers.IntegerField()
    no_leidas = serializers.IntegerField()


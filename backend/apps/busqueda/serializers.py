from rest_framework import serializers
from .models import HistorialBusqueda

class HistorialBusquedaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo HistorialBusqueda"""
    class Meta:
        model = HistorialBusqueda
        fields = ['id', 'usuario', 'termino_busqueda', 'tipo_busqueda', 'fecha_busqueda', 'resultados_encontrados']
        read_only_fields = ['id', 'usuario', 'fecha_busqueda']

    def create(self, validated_data):
        """Asigna automáticamente el usuario actual"""
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)

class HistorialBusquedaListSerializer(serializers.ModelSerializer):
    """Serializer para listar historial de búsquedas"""
    class Meta:
        model = HistorialBusqueda
        fields = ['id', 'termino_busqueda', 'tipo_busqueda', 'fecha_busqueda', 'resultados_encontrados']
        read_only_fields = ['id', 'fecha_busqueda'] 
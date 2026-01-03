from rest_framework import serializers
from .models import (
    BusquedaTradicional, 
    EmbeddingBusqueda, 
    HistorialSemantica,
    EnvioEmbedding
)

class BusquedaTradicionalSerializer(serializers.ModelSerializer):
    """Serializer para el modelo BusquedaTradicional"""
    class Meta:
        model = BusquedaTradicional
        fields = ['id', 'usuario', 'termino_busqueda', 'tipo_busqueda', 'fecha_busqueda', 'resultados_encontrados', 'resultados_json']
        read_only_fields = ['id', 'usuario', 'fecha_busqueda']

    def create(self, validated_data):
        """Asigna automáticamente el usuario actual"""
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)

class BusquedaTradicionalListSerializer(serializers.ModelSerializer):
    """Serializer para listar historial de búsquedas tradicionales"""
    class Meta:
        model = BusquedaTradicional
        fields = ['id', 'termino_busqueda', 'tipo_busqueda', 'fecha_busqueda', 'resultados_encontrados']
        read_only_fields = ['id', 'fecha_busqueda']


class EmbeddingBusquedaSerializer(serializers.ModelSerializer):
    """Serializer para búsquedas semánticas con embeddings"""
    class Meta:
        model = EmbeddingBusqueda
        fields = [
            'id', 'usuario', 'consulta', 'resultados_encontrados',
            'tiempo_respuesta', 'fecha_busqueda', 'filtros_aplicados',
            'modelo_utilizado', 'costo_consulta', 'tokens_utilizados', 'resultados_json'
        ]
        read_only_fields = ['id', 'usuario', 'fecha_busqueda']


class HistorialSemanticaSerializer(serializers.ModelSerializer):
    """Serializer para historial semántico (sugerencias)"""
    class Meta:
        model = HistorialSemantica
        fields = [
            'id', 'texto', 'categoria', 'icono', 'orden', 'activa', 'fecha_creacion', 'veces_usada'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'veces_usada']


class EnvioEmbeddingSerializer(serializers.ModelSerializer):
    """Serializer para embeddings de envíos"""
    class Meta:
        model = EnvioEmbedding
        fields = [
            'id', 'envio', 'texto_indexado', 'fecha_generacion', 'modelo_usado'
        ]
        read_only_fields = ['id', 'fecha_generacion'] 
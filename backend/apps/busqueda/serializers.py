from rest_framework import serializers
from .models import (
    HistorialBusqueda, 
    BusquedaSemantica, 
    FeedbackSemantico, 
    SugerenciaSemantica,
    EnvioEmbedding
)

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


class BusquedaSemanticaSerializer(serializers.ModelSerializer):
    """Serializer para búsquedas semánticas"""
    class Meta:
        model = BusquedaSemantica
        fields = [
            'id', 'usuario', 'consulta', 'resultados_encontrados',
            'tiempo_respuesta', 'fecha_busqueda', 'filtros_aplicados'
        ]
        read_only_fields = ['id', 'usuario', 'fecha_busqueda']


class FeedbackSemanticoSerializer(serializers.ModelSerializer):
    """Serializer para feedback semántico"""
    class Meta:
        model = FeedbackSemantico
        fields = [
            'id', 'usuario', 'busqueda', 'envio', 'es_relevante',
            'puntuacion_similitud', 'fecha_feedback'
        ]
        read_only_fields = ['id', 'usuario', 'fecha_feedback']


class SugerenciaSemanticaSerializer(serializers.ModelSerializer):
    """Serializer para sugerencias semánticas"""
    class Meta:
        model = SugerenciaSemantica
        fields = [
            'id', 'texto', 'categoria', 'icono', 'orden', 'activa', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion']


class EnvioEmbeddingSerializer(serializers.ModelSerializer):
    """Serializer para embeddings de envíos"""
    class Meta:
        model = EnvioEmbedding
        fields = [
            'id', 'envio', 'texto_indexado', 'fecha_generacion', 'modelo_usado'
        ]
        read_only_fields = ['id', 'fecha_generacion'] 
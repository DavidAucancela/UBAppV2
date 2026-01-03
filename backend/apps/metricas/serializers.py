"""
Serializers para la app de métricas.
"""
from rest_framework import serializers
from .models import (
    PruebaControladaSemantica,
    MetricaSemantica,
    RegistroGeneracionEmbedding,
    PruebaCarga,
    MetricaRendimiento,
    RegistroManualEnvio
)


class PruebaControladaSemanticaSerializer(serializers.ModelSerializer):
    """Serializer para PruebaControladaSemantica"""
    creado_por_username = serializers.CharField(source='creado_por.username', read_only=True)
    
    class Meta:
        model = PruebaControladaSemantica
        fields = [
            'id', 'nombre', 'descripcion', 'consulta', 'resultados_relevantes',
            'fecha_creacion', 'fecha_ejecucion', 'activa', 'creado_por', 'creado_por_username'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_ejecucion']


class MetricaSemanticaSerializer(serializers.ModelSerializer):
    """Serializer para MetricaSemantica"""
    busqueda_semantica_id = serializers.IntegerField(source='busqueda_semantica.id', read_only=True)
    prueba_controlada_nombre = serializers.CharField(source='prueba_controlada.nombre', read_only=True)
    
    class Meta:
        model = MetricaSemantica
        fields = [
            'id', 'busqueda_semantica', 'busqueda_semantica_id', 'prueba_controlada',
            'prueba_controlada_nombre', 'consulta', 'fecha_calculo', 'resultados_rankeados',
            'mrr', 'ndcg_10', 'precision_5', 'total_resultados', 'total_relevantes_encontrados',
            'tiempo_procesamiento_ms', 'logs_pipeline', 'modelo_embedding', 'metrica_ordenamiento'
        ]
        read_only_fields = ['id', 'fecha_calculo']


class RegistroGeneracionEmbeddingSerializer(serializers.ModelSerializer):
    """Serializer para RegistroGeneracionEmbedding"""
    envio_hawb = serializers.CharField(source='envio.hawb', read_only=True)
    embedding_id = serializers.IntegerField(source='embedding.id', read_only=True, allow_null=True)
    
    class Meta:
        model = RegistroGeneracionEmbedding
        fields = [
            'id', 'envio', 'envio_hawb', 'estado', 'dimension_embedding',
            'fecha_generacion', 'tiempo_generacion_ms', 'modelo_usado',
            'mensaje_error', 'tipo_proceso', 'embedding', 'embedding_id'
        ]
        read_only_fields = ['id', 'fecha_generacion']


class PruebaCargaSerializer(serializers.ModelSerializer):
    """Serializer para PruebaCarga"""
    ejecutado_por_username = serializers.CharField(source='ejecutado_por.username', read_only=True)
    
    class Meta:
        model = PruebaCarga
        fields = [
            'id', 'nombre', 'tipo_prueba', 'nivel_carga', 'tipo_registro',
            'fecha_ejecucion', 'ejecutado_por', 'ejecutado_por_username',
            'tiempo_promedio_ms', 'tiempo_minimo_ms', 'tiempo_maximo_ms',
            'cpu_promedio', 'cpu_maximo', 'ram_promedio_mb', 'ram_maximo_mb',
            'total_exitosos', 'total_errores', 'datos_prueba'
        ]
        read_only_fields = ['id', 'fecha_ejecucion']


class MetricaRendimientoSerializer(serializers.ModelSerializer):
    """Serializer para MetricaRendimiento"""
    prueba_carga_nombre = serializers.CharField(source='prueba_carga.nombre', read_only=True)
    
    class Meta:
        model = MetricaRendimiento
        fields = [
            'id', 'prueba_carga', 'prueba_carga_nombre', 'proceso',
            'tiempo_respuesta_ms', 'uso_cpu', 'uso_ram_mb',
            'fecha_medicion', 'nivel_carga', 'exito', 'detalles'
        ]
        read_only_fields = ['id', 'fecha_medicion']


class RegistroManualEnvioSerializer(serializers.ModelSerializer):
    """Serializer para RegistroManualEnvio"""
    registrado_por_username = serializers.CharField(source='registrado_por.username', read_only=True)
    
    class Meta:
        model = RegistroManualEnvio
        fields = [
            'id', 'hawb', 'tiempo_registro_segundos', 'fecha_registro',
            'registrado_por', 'registrado_por_username', 'datos_envio', 'notas'
        ]
        read_only_fields = ['id', 'fecha_registro']


class EjecutarPruebaControladaSerializer(serializers.Serializer):
    """Serializer para ejecutar prueba controlada"""
    prueba_id = serializers.IntegerField()
    filtros = serializers.DictField(required=False, allow_null=True)
    limite = serializers.IntegerField(default=20, min_value=1, max_value=100)


class EjecutarPruebaCargaSerializer(serializers.Serializer):
    """Serializer para ejecutar prueba de carga"""
    nivel_carga = serializers.IntegerField(min_value=1, max_value=100)
    consultas = serializers.ListField(
        child=serializers.CharField(),
        min_length=1
    )
    nombre_prueba = serializers.CharField(required=False, allow_blank=True)


class RegistrarEnvioManualSerializer(serializers.Serializer):
    """Serializer para registrar envío manual"""
    hawb = serializers.CharField(max_length=50)
    tiempo_registro_segundos = serializers.FloatField(min_value=0.0)
    datos_envio = serializers.DictField(required=False, allow_null=True)
    notas = serializers.CharField(required=False, allow_blank=True)


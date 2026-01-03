"""
Admin para la app de métricas.
"""
from django.contrib import admin
from .models import (
    PruebaControladaSemantica,
    MetricaSemantica,
    RegistroGeneracionEmbedding,
    PruebaCarga,
    MetricaRendimiento,
    RegistroManualEnvio
)


@admin.register(PruebaControladaSemantica)
class PruebaControladaSemanticaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'consulta', 'activa', 'fecha_creacion', 'fecha_ejecucion', 'creado_por']
    list_filter = ['activa', 'fecha_creacion']
    search_fields = ['nombre', 'consulta']
    readonly_fields = ['fecha_creacion', 'fecha_ejecucion']


@admin.register(MetricaSemantica)
class MetricaSemanticaAdmin(admin.ModelAdmin):
    list_display = ['id', 'consulta', 'mrr', 'ndcg_10', 'precision_5', 'fecha_calculo']
    list_filter = ['fecha_calculo', 'modelo_embedding']
    search_fields = ['consulta']
    readonly_fields = ['fecha_calculo']


@admin.register(RegistroGeneracionEmbedding)
class RegistroGeneracionEmbeddingAdmin(admin.ModelAdmin):
    list_display = ['id', 'envio', 'estado', 'tiempo_generacion_ms', 'tipo_proceso', 'fecha_generacion']
    list_filter = ['estado', 'tipo_proceso', 'fecha_generacion']
    search_fields = ['envio__hawb']
    readonly_fields = ['fecha_generacion']


@admin.register(PruebaCarga)
class PruebaCargaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_prueba', 'nivel_carga', 'tiempo_promedio_ms', 'fecha_ejecucion']
    list_filter = ['tipo_prueba', 'nivel_carga', 'fecha_ejecucion']
    search_fields = ['nombre']
    readonly_fields = ['fecha_ejecucion']


@admin.register(MetricaRendimiento)
class MetricaRendimientoAdmin(admin.ModelAdmin):
    list_display = ['id', 'proceso', 'tiempo_respuesta_ms', 'uso_cpu', 'nivel_carga', 'exito', 'fecha_medicion']
    list_filter = ['proceso', 'nivel_carga', 'exito', 'fecha_medicion']
    readonly_fields = ['fecha_medicion']


@admin.register(RegistroManualEnvio)
class RegistroManualEnvioAdmin(admin.ModelAdmin):
    list_display = ['hawb', 'tiempo_registro_segundos', 'registrado_por', 'fecha_registro']
    list_filter = ['fecha_registro']
    search_fields = ['hawb']
    readonly_fields = ['fecha_registro']

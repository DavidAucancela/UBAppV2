from django.contrib import admin
from .models import (
    HistorialBusqueda,
    BusquedaSemantica,
    FeedbackSemantico,
    SugerenciaSemantica,
    EnvioEmbedding
)


@admin.register(HistorialBusqueda)
class HistorialBusquedaAdmin(admin.ModelAdmin):
    """Admin para el modelo HistorialBusqueda"""
    list_display = ['usuario', 'termino_busqueda', 'tipo_busqueda', 'resultados_encontrados', 'fecha_busqueda']
    list_filter = ['tipo_busqueda', 'fecha_busqueda', 'usuario']
    search_fields = ['termino_busqueda', 'usuario__username']
    ordering = ['-fecha_busqueda']
    readonly_fields = ['fecha_busqueda']
    
    fieldsets = (
        ('Información de Búsqueda', {
            'fields': ('usuario', 'termino_busqueda', 'tipo_busqueda')
        }),
        ('Resultados', {
            'fields': ('resultados_encontrados', 'fecha_busqueda')
        }),
    )


@admin.register(BusquedaSemantica)
class BusquedaSemanticaAdmin(admin.ModelAdmin):
    """Admin para búsquedas semánticas"""
    list_display = ['usuario', 'consulta_truncada', 'resultados_encontrados', 'tiempo_respuesta', 'fecha_busqueda']
    list_filter = ['fecha_busqueda', 'usuario']
    search_fields = ['consulta', 'usuario__username']
    ordering = ['-fecha_busqueda']
    readonly_fields = ['fecha_busqueda']
    
    def consulta_truncada(self, obj):
        return obj.consulta[:50] + '...' if len(obj.consulta) > 50 else obj.consulta
    consulta_truncada.short_description = 'Consulta'


@admin.register(FeedbackSemantico)
class FeedbackSemanticoAdmin(admin.ModelAdmin):
    """Admin para feedback semántico"""
    list_display = ['usuario', 'envio', 'es_relevante', 'puntuacion_similitud', 'fecha_feedback']
    list_filter = ['es_relevante', 'fecha_feedback', 'usuario']
    search_fields = ['usuario__username', 'envio__hawb']
    ordering = ['-fecha_feedback']
    readonly_fields = ['fecha_feedback']


@admin.register(SugerenciaSemantica)
class SugerenciaSemanticaAdmin(admin.ModelAdmin):
    """Admin para sugerencias semánticas"""
    list_display = ['texto', 'categoria', 'icono', 'orden', 'activa', 'fecha_creacion']
    list_filter = ['categoria', 'activa', 'fecha_creacion']
    search_fields = ['texto']
    ordering = ['orden', '-fecha_creacion']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información de Sugerencia', {
            'fields': ('texto', 'categoria', 'icono', 'orden')
        }),
        ('Estado', {
            'fields': ('activa', 'fecha_creacion')
        }),
    )


@admin.register(EnvioEmbedding)
class EnvioEmbeddingAdmin(admin.ModelAdmin):
    """Admin para embeddings de envíos"""
    list_display = ['envio', 'modelo_usado', 'fecha_generacion', 'texto_truncado']
    list_filter = ['modelo_usado', 'fecha_generacion']
    search_fields = ['envio__hawb', 'texto_indexado']
    ordering = ['-fecha_generacion']
    readonly_fields = ['fecha_generacion', 'embedding_vector']
    
    def texto_truncado(self, obj):
        return obj.texto_indexado[:100] + '...' if len(obj.texto_indexado) > 100 else obj.texto_indexado
    texto_truncado.short_description = 'Texto Indexado'
    
    fieldsets = (
        ('Información del Embedding', {
            'fields': ('envio', 'modelo_usado', 'fecha_generacion')
        }),
        ('Datos de Indexación', {
            'fields': ('texto_indexado',),
            'classes': ('collapse',)
        }),
        ('Vector de Embedding', {
            'fields': ('embedding_vector',),
            'classes': ('collapse',),
            'description': 'Vector de embedding serializado (JSON)'
        }),
    )

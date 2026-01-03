from django.contrib import admin
from .models import (
    BusquedaTradicional,
    EmbeddingBusqueda,
    HistorialSemantica,
    EnvioEmbedding
)


@admin.register(BusquedaTradicional)
class BusquedaTradicionalAdmin(admin.ModelAdmin):
    """Admin para el modelo BusquedaTradicional"""
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
        ('Resultados JSON', {
            'fields': ('resultados_json',),
            'classes': ('collapse',),
            'description': 'Resultados completos en formato JSON para generación de PDF'
        }),
    )


@admin.register(EmbeddingBusqueda)
class EmbeddingBusquedaAdmin(admin.ModelAdmin):
    """Admin para búsquedas semánticas con embeddings"""
    list_display = ['usuario', 'consulta_truncada', 'resultados_encontrados', 'tiempo_respuesta', 'costo_consulta', 'fecha_busqueda']
    list_filter = ['fecha_busqueda', 'usuario', 'modelo_utilizado']
    search_fields = ['consulta', 'usuario__username']
    ordering = ['-fecha_busqueda']
    readonly_fields = ['fecha_busqueda', 'embedding_vector']
    
    def consulta_truncada(self, obj):
        return obj.consulta[:50] + '...' if len(obj.consulta) > 50 else obj.consulta
    consulta_truncada.short_description = 'Consulta'
    
    fieldsets = (
        ('Información de Búsqueda', {
            'fields': ('usuario', 'consulta', 'modelo_utilizado')
        }),
        ('Resultados', {
            'fields': ('resultados_encontrados', 'tiempo_respuesta', 'tokens_utilizados', 'costo_consulta', 'fecha_busqueda')
        }),
        ('Filtros Aplicados', {
            'fields': ('filtros_aplicados',),
            'classes': ('collapse',)
        }),
        ('Resultados JSON', {
            'fields': ('resultados_json',),
            'classes': ('collapse',),
            'description': 'Resultados completos en formato JSON para generación de PDF'
        }),
        ('Vector de Embedding', {
            'fields': ('embedding_vector',),
            'classes': ('collapse',),
            'description': 'Vector de embedding de la consulta'
        }),
    )


@admin.register(HistorialSemantica)
class HistorialSemanticaAdmin(admin.ModelAdmin):
    """Admin para historial semántico (sugerencias)"""
    list_display = ['texto', 'categoria', 'icono', 'orden', 'veces_usada', 'activa', 'fecha_creacion']
    list_filter = ['categoria', 'activa', 'fecha_creacion']
    search_fields = ['texto']
    ordering = ['orden', '-veces_usada', '-fecha_creacion']
    readonly_fields = ['fecha_creacion', 'veces_usada']
    
    fieldsets = (
        ('Información de Sugerencia', {
            'fields': ('texto', 'categoria', 'icono', 'orden')
        }),
        ('Estadísticas', {
            'fields': ('veces_usada',)
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

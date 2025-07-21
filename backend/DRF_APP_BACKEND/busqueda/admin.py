from django.contrib import admin
from .models import HistorialBusqueda

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

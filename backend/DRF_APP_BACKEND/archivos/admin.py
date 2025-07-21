from django.contrib import admin
from .models import Envio, Producto

class ProductoInline(admin.TabularInline):
    """Inline para productos en envíos"""
    model = Producto
    extra = 1
    fields = ['descripcion', 'peso', 'cantidad', 'valor', 'categoria']

@admin.register(Envio)
class EnvioAdmin(admin.ModelAdmin):
    """Admin para el modelo Envío"""
    list_display = ['hawb', 'comprador', 'estado', 'peso_total', 'cantidad_total', 'valor_total', 'fecha_emision']
    list_filter = ['estado', 'fecha_emision', 'comprador']
    search_fields = ['hawb', 'comprador__nombre', 'comprador__cedula']
    ordering = ['-fecha_emision']
    readonly_fields = ['fecha_emision', 'fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('hawb', 'comprador', 'estado')
        }),
        ('Totales', {
            'fields': ('peso_total', 'cantidad_total', 'valor_total'),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': ('observaciones', 'fecha_emision', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductoInline]

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Admin para el modelo Producto"""
    list_display = ['descripcion', 'envio', 'categoria', 'peso', 'cantidad', 'valor']
    list_filter = ['categoria', 'fecha_creacion', 'envio__estado']
    search_fields = ['descripcion', 'envio__hawb']
    ordering = ['-fecha_creacion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información del Producto', {
            'fields': ('descripcion', 'peso', 'cantidad', 'valor', 'categoria')
        }),
        ('Envío', {
            'fields': ('envio',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

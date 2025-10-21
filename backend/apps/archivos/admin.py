from django.contrib import admin
from .models import Envio, Producto, Tarifa, ImportacionExcel

class ProductoInline(admin.TabularInline):
    """Inline para productos en envíos"""
    model = Producto
    extra = 1
    fields = ['descripcion', 'peso', 'cantidad', 'valor', 'categoria', 'costo_envio']
    readonly_fields = ['costo_envio']

@admin.register(Envio)
class EnvioAdmin(admin.ModelAdmin):
    """Admin para el modelo Envío"""
    list_display = ['hawb', 'comprador', 'estado', 'peso_total', 'cantidad_total', 'valor_total', 'costo_servicio', 'fecha_emision']
    list_filter = ['estado', 'fecha_emision', 'comprador']
    search_fields = ['hawb', 'comprador__nombre', 'comprador__cedula']
    ordering = ['-fecha_emision']
    readonly_fields = ['fecha_emision', 'fecha_creacion', 'fecha_actualizacion', 'costo_servicio']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('hawb', 'comprador', 'estado')
        }),
        ('Totales', {
            'fields': ('peso_total', 'cantidad_total', 'valor_total', 'costo_servicio'),
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
    list_display = ['descripcion', 'envio', 'categoria', 'peso', 'cantidad', 'valor', 'costo_envio']
    list_filter = ['categoria', 'fecha_creacion', 'envio__estado']
    search_fields = ['descripcion', 'envio__hawb']
    ordering = ['-fecha_creacion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'costo_envio']
    
    fieldsets = (
        ('Información del Producto', {
            'fields': ('descripcion', 'peso', 'cantidad', 'valor', 'categoria', 'costo_envio')
        }),
        ('Envío', {
            'fields': ('envio',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    """Admin para el modelo Tarifa"""
    list_display = ['categoria', 'peso_minimo', 'peso_maximo', 'precio_por_kg', 'cargo_base', 'activa']
    list_filter = ['categoria', 'activa', 'fecha_creacion']
    search_fields = ['categoria']
    ordering = ['categoria', 'peso_minimo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Configuración de Tarifa', {
            'fields': ('categoria', 'peso_minimo', 'peso_maximo', 'precio_por_kg', 'cargo_base', 'activa')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ImportacionExcel)
class ImportacionExcelAdmin(admin.ModelAdmin):
    """Admin para el modelo ImportacionExcel"""
    list_display = ['nombre_original', 'usuario', 'estado', 'total_registros', 'registros_validos', 'registros_errores', 'fecha_creacion']
    list_filter = ['estado', 'fecha_creacion', 'usuario']
    search_fields = ['nombre_original', 'usuario__nombre', 'usuario__cedula']
    ordering = ['-fecha_creacion']
    readonly_fields = [
        'nombre_original', 'usuario', 'estado', 'total_registros', 'registros_validos',
        'registros_errores', 'registros_duplicados', 'registros_procesados',
        'errores_validacion', 'mensaje_resultado', 'fecha_creacion', 'fecha_actualizacion', 'fecha_completado'
    ]
    
    fieldsets = (
        ('Información del Archivo', {
            'fields': ('archivo', 'nombre_original', 'usuario', 'estado')
        }),
        ('Estadísticas', {
            'fields': ('total_registros', 'registros_validos', 'registros_errores', 'registros_duplicados', 'registros_procesados'),
        }),
        ('Configuración', {
            'fields': ('columnas_mapeadas', 'registros_seleccionados'),
            'classes': ('collapse',)
        }),
        ('Resultados', {
            'fields': ('mensaje_resultado', 'errores_validacion'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion', 'fecha_completado'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """No permitir crear importaciones desde el admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Solo permitir ver, no editar"""
        return False

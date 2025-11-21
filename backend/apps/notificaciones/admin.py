from django.contrib import admin
from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    """Admin para el modelo Notificación"""
    list_display = ['titulo', 'usuario', 'tipo', 'leida', 'fecha_creacion']
    list_filter = ['tipo', 'leida', 'fecha_creacion']
    search_fields = ['titulo', 'mensaje', 'usuario__nombre', 'usuario__cedula']
    ordering = ['-fecha_creacion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'fecha_lectura']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('usuario', 'tipo', 'titulo', 'mensaje')
        }),
        ('Estado', {
            'fields': ('leida', 'fecha_lectura')
        }),
        ('Información Adicional', {
            'fields': ('enlace', 'metadata', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        qs = super().get_queryset(request)
        return qs.select_related('usuario')

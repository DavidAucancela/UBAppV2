from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin personalizado para el modelo Usuario"""
    # Usar is_active (campo heredado de AbstractUser) en lugar de es_activo (propiedad)
    list_display = ['username', 'nombre', 'correo', 'cedula', 'rol', 'is_active', 'fecha_creacion']
    list_filter = ['is_active', 'rol', 'fecha_creacion']
    search_fields = ['username', 'nombre', 'correo', 'cedula']
    ordering = ['-fecha_creacion']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Personal', {
            'fields': ('nombre', 'correo', 'cedula', 'rol', 'telefono', 'fecha_nacimiento', 'direccion')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Personal', {
            'fields': ('nombre', 'correo', 'cedula', 'rol', 'telefono', 'fecha_nacimiento', 'direccion')
        }),
    )

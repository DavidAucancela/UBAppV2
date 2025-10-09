from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin personalizado para el modelo Usuario"""
    list_display = ['username', 'nombre', 'correo', 'cedula', 'rol', 'es_activo', 'fecha_creacion']
    list_filter = ['es_activo', 'rol', 'fecha_creacion']
    search_fields = ['username', 'nombre', 'correo', 'cedula']
    ordering = ['-fecha_creacion']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Personal', {
            'fields': ('nombre', 'correo', 'cedula', 'rol', 'telefono', 'fecha_nacimiento', 'direccion', 'es_activo')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Personal', {
            'fields': ('nombre', 'correo', 'cedula', 'rol', 'telefono', 'fecha_nacimiento', 'direccion', 'es_activo')
        }),
    )

#!/usr/bin/env python
"""
Script para actualizar el superusuario con los nuevos campos
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DRF_APP_BACKEND.settings')
django.setup()

from django.contrib.auth import get_user_model

Usuario = get_user_model()

def update_superuser():
    """Actualiza el superusuario existente"""
    try:
        # Buscar el superusuario existente
        superuser = Usuario.objects.filter(is_superuser=True).first()
        
        if superuser:
            # Actualizar campos requeridos
            superuser.nombre = "David Admin"
            superuser.correo = "david102002@hotmail.com"
            superuser.cedula = "1234567890"
            superuser.rol = 1  # Admin
            superuser.save()
            
            print(f"✅ Superusuario actualizado:")
            print(f"   Username: {superuser.username}")
            print(f"   Nombre: {superuser.nombre}")
            print(f"   Correo: {superuser.correo}")
            print(f"   Cédula: {superuser.cedula}")
            print(f"   Rol: {superuser.get_rol_display_name()}")
        else:
            print("❌ No se encontró superusuario")
            
    except Exception as e:
        print(f"❌ Error actualizando superusuario: {e}")

if __name__ == "__main__":
    update_superuser() 
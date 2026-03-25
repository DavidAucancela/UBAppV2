#!/usr/bin/env python
"""
Crea el superusuario inicial desde variables de entorno.
Solo crea si no existe. Seguro para ejecutar en cada deploy.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from apps.usuarios.models import Usuario  # noqa: E402

username = os.environ.get('ADMIN_USER')
password = os.environ.get('ADMIN_PASSWORD')
correo   = os.environ.get('ADMIN_EMAIL', '')
nombre   = os.environ.get('ADMIN_NOMBRE', username or 'Admin')

if not username or not password:
    print('ADMIN_USER/ADMIN_PASSWORD no configurados — saltando creación de admin')
else:
    if not Usuario.objects.filter(username=username).exists():
        Usuario.objects.create_superuser(
            username=username,
            correo=correo,
            password=password,
            nombre=nombre,
        )
        print(f'✓ Superusuario "{username}" creado')
    else:
        print(f'✓ Superusuario "{username}" ya existe')

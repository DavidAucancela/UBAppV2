#!/usr/bin/env python
"""
Script de arranque para Render. Ejecuta migraciones y arranca Gunicorn.
Evita problemas con shell/CRLF en Windows.
"""
import os
import subprocess
import sys

def run(cmd, check=True):
    """Ejecuta un comando y retorna el código de salida."""
    print(f">>> {cmd}")
    result = subprocess.run(cmd, shell=True)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result.returncode

def create_superuser_if_needed():
    """Crea superusuario inicial desde variables de entorno si no existe."""
    username = os.environ.get("ADMIN_USER")
    password = os.environ.get("ADMIN_PASSWORD")
    correo   = os.environ.get("ADMIN_EMAIL", "")
    nombre   = os.environ.get("ADMIN_NOMBRE", username or "Admin")

    if not username or not password:
        return  # Variables no configuradas, saltar

    import django
    django.setup()
    from apps.usuarios.models import Usuario

    if not Usuario.objects.filter(username=username).exists():
        Usuario.objects.create_superuser(
            username=username,
            correo=correo,
            password=password,
            nombre=nombre,
        )
        print(f"✓ Superusuario '{username}' creado")
    else:
        print(f"✓ Superusuario '{username}' ya existe")


def main():
    run("python wait_for_db.py")
    run("python rename_backup_tables.py", check=False)
    run("python manage.py migrate --noinput")
    run("python manage.py collectstatic --noinput")
    create_superuser_if_needed()
    
    port = os.environ.get("PORT", "8000")
    # Reemplazar este proceso con gunicorn (recibe señales correctamente)
    os.execvp("gunicorn", [
        "gunicorn", "wsgi:application",
        "--bind", f"0.0.0.0:{port}",
        "--workers", "1",
        "--timeout", "120",
        "--access-logfile", "-",
        "--error-logfile", "-",
    ])

if __name__ == "__main__":
    main()

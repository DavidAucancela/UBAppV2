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

def main():
    run("python wait_for_db.py")
    run("python rename_backup_tables.py", check=False)
    run("python manage.py migrate --noinput")
    run("python manage.py collectstatic --noinput")
    run("python create_admin.py", check=False)
    
    port = os.environ.get("PORT", "8000")
    workers = os.environ.get("WEB_CONCURRENCY", str(os.cpu_count() * 2 + 1))
    timeout = os.environ.get("GUNICORN_TIMEOUT", "120")
    # Reemplazar este proceso con gunicorn (recibe señales correctamente)
    os.execvp("gunicorn", [
        "gunicorn", "wsgi:application",
        "--bind", f"0.0.0.0:{port}",
        "--workers", workers,
        "--timeout", timeout,
        "--access-logfile", "-",
        "--error-logfile", "-",
    ])

if __name__ == "__main__":
    main()

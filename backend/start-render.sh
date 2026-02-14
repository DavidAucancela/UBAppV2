#!/bin/sh
set -e

echo "Esperando base de datos..."
python wait_for_db.py

echo "Renombrando tablas de backup (si aplica)..."
python rename_backup_tables.py || true

echo "Ejecutando migraciones..."
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor..."
exec gunicorn wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --timeout 120 --access-logfile - --error-logfile -

# Dockerfile para Backend Django
FROM python:3.11-slim

# Metadatos
LABEL maintainer="Equipo UBApp"
LABEL description="Backend Django para UBApp"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn  # Servidor WSGI para producción

# Copiar el código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Script para esperar a que la base de datos esté lista
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
host="$1"\n\
shift\n\
cmd="$@"\n\
\n\
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1" > /dev/null 2>&1; do\n\
  >&2 echo "PostgreSQL no está disponible - esperando..."\n\
  sleep 1\n\
done\n\
\n\
>&2 echo "PostgreSQL está disponible - ejecutando comando"\n\
exec $cmd' > /usr/local/bin/wait_for_db.sh && \
    chmod +x /usr/local/bin/wait_for_db.sh

# Copiar script de espera para la base de datos
COPY wait_for_db.py .
RUN chmod +x wait_for_db.py

# Exponer puerto
EXPOSE 8000

# Comando por defecto (puede ser sobrescrito en docker-compose)
CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

#!/usr/bin/env python
"""
Script para esperar a que la base de datos esté disponible.
"""
import sys
import time
import os
import psycopg2
from psycopg2 import OperationalError

def wait_for_db():
    max_attempts = 30
    attempt = 0

    db_config = {
        "host": os.getenv("DB_HOST", "postgres"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME", "UBAppDB"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "admin")
    }

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        from urllib.parse import urlparse
        # Limpiar brackets IPv6 que rompen el parser
        clean_url = database_url.strip()
        parsed = urlparse(clean_url)
        host = parsed.hostname or "postgres"
        # Remover brackets si quedaron
        host = host.strip("[]")
        db_config = {
            "host": host,
            "port": parsed.port or 5432,
            "dbname": (parsed.path or "/UBAppDB").lstrip("/") or "UBAppDB",
            "user": parsed.username or "postgres",
            "password": parsed.password or "admin"
        }

    print(f"Esperando conexión a PostgreSQL en {db_config['host']}:{db_config['port']}...")

    while attempt < max_attempts:
        try:
            conn = psycopg2.connect(**db_config)
            conn.close()
            print("✓ Base de datos disponible")
            return True
        except OperationalError as e:
            attempt += 1
            print(f"Intento {attempt}/{max_attempts}: {str(e)}")
            time.sleep(2)

    print("✗ No se pudo conectar a la base de datos después de 30 intentos")
    sys.exit(1)

if __name__ == "__main__":
    wait_for_db()

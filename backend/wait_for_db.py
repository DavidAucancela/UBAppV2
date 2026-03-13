#!/usr/bin/env python
"""
Script para esperar a que la base de datos esté disponible.
Útil para Docker Compose y despliegues.
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
    
    # Si hay DATABASE_URL, parsearla (Render, Supabase, etc.)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        import re
        from urllib.parse import urlparse
        # Supabase wraps hostnames in brackets (e.g. [host.supabase.com]) which Python 3.11+
        # rejects unless it's a valid IPv6 address. Strip brackets from hostnames
        # (hostnames have no colons; IPv6 addresses do, so this is safe).
        database_url = re.sub(r'\[([a-zA-Z0-9._-]+)\]', r'\1', database_url)
        parsed = urlparse(database_url)
        db_config = {
            "host": parsed.hostname or "postgres",
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

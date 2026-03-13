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
    
    # Si hay DATABASE_URL, usarla directo como DSN (psycopg2 soporta URLs de postgres)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # psycopg2 parsea la URL internamente sin usar urlparse de Python,
        # evitando el bug de Python 3.11 con hostnames entre corchetes (Supabase).
        print(f"Esperando conexión a PostgreSQL (via DATABASE_URL)...")
        while attempt < max_attempts:
            try:
                conn = psycopg2.connect(database_url)
                conn.close()
                print("✓ Base de datos disponible")
                return True
            except OperationalError as e:
                attempt += 1
                print(f"Intento {attempt}/{max_attempts}: {str(e)}")
                time.sleep(2)
        print("✗ No se pudo conectar a la base de datos después de 30 intentos")
        sys.exit(1)
    
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

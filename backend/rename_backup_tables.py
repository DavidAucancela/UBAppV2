#!/usr/bin/env python
"""
Renombra tablas del backup local al nombre que espera Django.
Se ejecuta al arrancar el backend (antes de migrate) para que el restore funcione sin pasos manuales.
Idempotente: si las tablas ya tienen el nombre correcto, no hace nada.
"""
import os
import sys

def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return 0

    try:
        import psycopg2
        from urllib.parse import urlparse
    except ImportError:
        print("rename_backup_tables: psycopg2 no disponible, omitiendo renombrado.")
        return 0

    parsed = urlparse(database_url)
    conn_params = {
        "host": parsed.hostname or "postgres",
        "port": parsed.port or 5432,
        "dbname": (parsed.path or "/UBAppDB").lstrip("/") or "UBAppDB",
        "user": parsed.username or "postgres",
        "password": parsed.password or "admin",
    }
    if parsed.query:
        conn_params["options"] = parsed.query

    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cur = conn.cursor()

        # tipo_contenido -> django_content_type (backup local)
        cur.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tipo_contenido'"
        )
        if cur.fetchone():
            cur.execute('ALTER TABLE public.tipo_contenido RENAME TO django_content_type')
            print("rename_backup_tables: tipo_contenido -> django_content_type")

        # logs -> django_admin_log (backup local)
        cur.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'logs'"
        )
        if cur.fetchone():
            cur.execute('ALTER TABLE public.logs RENAME TO django_admin_log')
            print("rename_backup_tables: logs -> django_admin_log")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"rename_backup_tables: error (no crítico): {e}", file=sys.stderr)
        # No salir con error para no bloquear el arranque

    return 0

if __name__ == "__main__":
    sys.exit(main())

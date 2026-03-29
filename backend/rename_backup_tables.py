#!/usr/bin/env python
"""
Renombra tablas al nombre que espera Django (custom db_table).
Se ejecuta al arrancar el backend (antes de migrate).
Idempotente: si las tablas ya tienen el nombre correcto, no hace nada.

Cubre dos escenarios:
  A) Restore de backup local (tablas ya renombradas → revertir a nombre Django estándar)
  B) Producción Railway (tabla creada con nombre Django por defecto → renombrar a nombre custom)
"""
import os
import sys


# (viejo, nuevo) — se renombra solo si viejo existe y nuevo NO existe
RENOMBRES = [
    # ── A) Backup local → nombres estándar Django (para que migrate arranque limpio)
    ('tipo_contenido',  'django_content_type'),
    ('logs',            'django_admin_log'),
    ('sesiones_key',    'django_session'),

    # ── B) Railway: nombre Django por defecto → nombre custom (db_table en Meta)
    ('usuarios_usuario',                    'usuarios'),
    ('usuarios_usuario_groups',             'usuarios_groups'),
    ('usuarios_usuario_user_permissions',   'usuarios_user_permissions'),
    ('archivos_tarifa',                     'tarifa'),
    ('archivos_envio',                      'envio'),
    ('archivos_producto',                   'producto'),
    ('archivos_archivo',                    'archivo'),
    ('notificaciones_notificacion',         'notificaciones'),
    ('busqueda_busquedastradicional',        'busqueda_tradicional'),
    ('busqueda_embeddingenvio',             'embedding_envio'),
    ('busqueda_embeddingbusqueda',          'embedding_busqueda'),
    ('busqueda_sugerenciasemantica',        'historial_semantica'),
    ('core_auditlog',                       'audit_log'),
]


def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return 0

    try:
        import psycopg2
        from urllib.parse import urlparse
    except ImportError:
        print("rename_backup_tables: psycopg2 no disponible, omitiendo.")
        return 0

    parsed = urlparse(database_url)
    conn_params = {
        "host":     parsed.hostname or "postgres",
        "port":     parsed.port or 5432,
        "dbname":   (parsed.path or "/UBAppDB").lstrip("/") or "UBAppDB",
        "user":     parsed.username or "postgres",
        "password": parsed.password or "admin",
    }

    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cur = conn.cursor()

        for vieja, nueva in RENOMBRES:
            cur.execute(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name=%s",
                [vieja]
            )
            existe_vieja = cur.fetchone()

            cur.execute(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name=%s",
                [nueva]
            )
            existe_nueva = cur.fetchone()

            if existe_vieja and not existe_nueva:
                cur.execute(f'ALTER TABLE public."{vieja}" RENAME TO "{nueva}"')
                print(f"rename_backup_tables: {vieja} -> {nueva}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"rename_backup_tables: error (no crítico): {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())

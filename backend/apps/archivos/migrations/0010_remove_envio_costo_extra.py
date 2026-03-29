# Generated manually to remove costo_extra column

from django.db import migrations


def drop_costo_extra(apps, schema_editor):
    """Elimina la columna costo_extra si existe (compatible con PostgreSQL y SQLite)."""
    vendor = schema_editor.connection.vendor
    if vendor == 'postgresql':
        schema_editor.execute("ALTER TABLE envio DROP COLUMN IF EXISTS costo_extra;")
    elif vendor == 'sqlite':
        # SQLite no soporta DROP COLUMN IF EXISTS — verificar primero
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(envio)")
            columns = [row[1] for row in cursor.fetchall()]
        if 'costo_extra' in columns:
            schema_editor.execute("ALTER TABLE envio DROP COLUMN costo_extra;")


def restore_costo_extra(apps, schema_editor):
    schema_editor.execute(
        "ALTER TABLE envio ADD COLUMN costo_extra NUMERIC(12, 2) DEFAULT 0 NOT NULL;"
    )


class Migration(migrations.Migration):

    dependencies = [
        ('archivos', '0009_alter_envio_cantidad_total_alter_envio_peso_total_and_more'),
    ]

    operations = [
        migrations.RunPython(drop_costo_extra, restore_costo_extra),
    ]

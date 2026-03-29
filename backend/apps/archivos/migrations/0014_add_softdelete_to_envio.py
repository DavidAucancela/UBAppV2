from django.db import migrations, models


def add_deleted_at(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == 'postgresql':
        schema_editor.execute(
            "ALTER TABLE envio ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE NULL;"
        )
        schema_editor.execute(
            "CREATE INDEX IF NOT EXISTS archivos_envio_deleted_at ON envio (deleted_at);"
        )
    elif vendor == 'sqlite':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(envio)")
            columns = [row[1] for row in cursor.fetchall()]
        if 'deleted_at' not in columns:
            schema_editor.execute("ALTER TABLE envio ADD COLUMN deleted_at DATETIME NULL;")
        schema_editor.execute(
            "CREATE INDEX IF NOT EXISTS archivos_envio_deleted_at ON envio (deleted_at);"
        )


def remove_deleted_at(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == 'postgresql':
        schema_editor.execute("DROP INDEX IF EXISTS archivos_envio_deleted_at;")
        schema_editor.execute("ALTER TABLE envio DROP COLUMN IF EXISTS deleted_at;")
    elif vendor == 'sqlite':
        schema_editor.execute("DROP INDEX IF EXISTS archivos_envio_deleted_at;")
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(envio)")
            columns = [row[1] for row in cursor.fetchall()]
        if 'deleted_at' in columns:
            schema_editor.execute("ALTER TABLE envio DROP COLUMN deleted_at;")


class Migration(migrations.Migration):

    dependencies = [
        ('archivos', '0013_aumentar_decimales_envio_totales'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_deleted_at, remove_deleted_at),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='envio',
                    name='deleted_at',
                    field=models.DateTimeField(blank=True, db_index=True, null=True),
                ),
            ],
        ),
    ]

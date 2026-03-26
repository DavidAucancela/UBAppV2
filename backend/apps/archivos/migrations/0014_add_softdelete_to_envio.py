from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archivos', '0013_aumentar_decimales_envio_totales'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="ALTER TABLE envio ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE NULL;",
                    reverse_sql="ALTER TABLE envio DROP COLUMN IF EXISTS deleted_at;",
                ),
                migrations.RunSQL(
                    sql="CREATE INDEX IF NOT EXISTS archivos_envio_deleted_at ON envio (deleted_at);",
                    reverse_sql="DROP INDEX IF EXISTS archivos_envio_deleted_at;",
                ),
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

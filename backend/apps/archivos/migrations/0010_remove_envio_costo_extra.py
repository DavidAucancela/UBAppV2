# Generated manually to remove costo_extra column

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archivos', '0009_alter_envio_cantidad_total_alter_envio_peso_total_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            # Eliminar la columna costo_extra si existe
            sql="ALTER TABLE envio DROP COLUMN IF EXISTS costo_extra;",
            reverse_sql="ALTER TABLE envio ADD COLUMN costo_extra NUMERIC(12, 2) DEFAULT 0 NOT NULL;"
        ),
    ]

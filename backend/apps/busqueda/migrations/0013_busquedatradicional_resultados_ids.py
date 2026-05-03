from django.db import migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('busqueda', '0012_fix_rename_historial_semantica'),
    ]

    operations = [
        migrations.AddField(
            model_name='busquedatradicional',
            name='resultados_ids',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=django.db.models.IntegerField(),
                blank=True,
                default=list,
                help_text='IDs de los envíos encontrados. Usar para re-consultar en PDF.',
                size=None,
                verbose_name='IDs de Resultados',
            ),
        ),
    ]

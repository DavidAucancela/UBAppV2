from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0011_fix_rename_tabla_usuarios'),
    ]

    operations = [
        # Primero rellenar nulls existentes antes de aplicar NOT NULL
        migrations.RunSQL(
            sql="UPDATE usuarios SET nombre = '' WHERE nombre IS NULL;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="""
                UPDATE usuarios
                SET correo = CONCAT('sin_correo_', id::text, '@placeholder.invalid')
                WHERE correo IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='usuario',
            name='nombre',
            field=models.CharField(
                default='',
                max_length=100,
                validators=[],
            ),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='correo',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]

from django.db import migrations


class Migration(migrations.Migration):
    """
    Fix idempotente: asegura que la tabla de usuarios se llame 'usuarios'.
    Caso Railway: si 0007 ya estaba marcada como aplicada pero el rename nunca ocurrió.
    """

    dependencies = [
        ('usuarios', '0010_alter_usuario_managers'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'usuarios_usuario'
                ) AND NOT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'usuarios'
                ) THEN
                    ALTER TABLE usuarios_usuario RENAME TO usuarios;
                    RAISE NOTICE 'Tabla renombrada: usuarios_usuario -> usuarios';
                ELSE
                    RAISE NOTICE 'Tabla usuarios ya existe o usuarios_usuario no existe, sin cambios.';
                END IF;

                -- M2M groups
                IF EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'usuarios_usuario_groups'
                ) AND NOT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'usuarios_groups'
                ) THEN
                    ALTER TABLE usuarios_usuario_groups RENAME TO usuarios_groups;
                END IF;

                -- M2M user_permissions
                IF EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'usuarios_usuario_user_permissions'
                ) AND NOT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'usuarios_user_permissions'
                ) THEN
                    ALTER TABLE usuarios_usuario_user_permissions RENAME TO usuarios_user_permissions;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

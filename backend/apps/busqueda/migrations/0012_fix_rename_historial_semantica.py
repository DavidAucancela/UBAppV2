"""
Migración correctiva: renombrar la tabla busqueda_sugerenciasemantica → historial_semantica
en la base de datos de producción.

La migración 0009 PASO 8 usó SeparateDatabaseAndState con database_operations=[]
asumiendo que la tabla ya existía con el nombre nuevo, pero en Railway nunca
se ejecutó ese renombrado físico.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('busqueda', '0011_crear_tabla_busqueda_tradicional_si_no_existe'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    -- Si la tabla vieja existe y la nueva no, renombrarla
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_schema = 'public'
                          AND table_name = 'busqueda_sugerenciasemantica'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_schema = 'public'
                          AND table_name = 'historial_semantica'
                    ) THEN
                        ALTER TABLE busqueda_sugerenciasemantica RENAME TO historial_semantica;
                        RAISE NOTICE 'Tabla renombrada: busqueda_sugerenciasemantica → historial_semantica';

                    -- Si no existe ninguna de las dos, crear historial_semantica desde cero
                    ELSIF NOT EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_schema = 'public'
                          AND table_name = 'historial_semantica'
                    ) THEN
                        CREATE TABLE historial_semantica (
                            id         BIGSERIAL PRIMARY KEY,
                            texto      VARCHAR(200) NOT NULL,
                            categoria  VARCHAR(50)  NOT NULL DEFAULT 'general',
                            icono      VARCHAR(50)  NOT NULL DEFAULT 'fa-search',
                            orden      INTEGER      NOT NULL DEFAULT 0,
                            activa     BOOLEAN      NOT NULL DEFAULT TRUE,
                            fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            veces_usada    INTEGER   NOT NULL DEFAULT 0
                        );
                        RAISE NOTICE 'Tabla historial_semantica creada desde cero';

                    ELSE
                        RAISE NOTICE 'Tabla historial_semantica ya existe, sin cambios';
                    END IF;
                END $$;
            """,
            reverse_sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_schema = 'public'
                          AND table_name = 'historial_semantica'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_schema = 'public'
                          AND table_name = 'busqueda_sugerenciasemantica'
                    ) THEN
                        ALTER TABLE historial_semantica RENAME TO busqueda_sugerenciasemantica;
                    END IF;
                END $$;
            """
        ),
    ]

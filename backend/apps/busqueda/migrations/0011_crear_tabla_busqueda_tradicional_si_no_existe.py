# Generated migration to create busqueda_tradicional table if it doesn't exist
# This fixes the error when deleting users: relation "busqueda_tradicional" does not exist

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('busqueda', '0010_rename_embedding_b_usuario_idx_embedding_b_usuario_275ca3_idx_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Crear la tabla busqueda_tradicional si no existe
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    -- Si la tabla no existe, crearla
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'busqueda_tradicional'
                    ) THEN
                        CREATE TABLE busqueda_tradicional (
                            id BIGSERIAL PRIMARY KEY,
                            usuario_id BIGINT NOT NULL,
                            termino_busqueda VARCHAR(255) NOT NULL,
                            tipo_busqueda VARCHAR(50) NOT NULL DEFAULT 'general',
                            fecha_busqueda TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            resultados_encontrados INTEGER NOT NULL DEFAULT 0,
                            resultados_json JSONB NULL,
                            CONSTRAINT busqueda_tradicional_usuario_id_fk 
                                FOREIGN KEY (usuario_id) 
                                REFERENCES usuarios(id) 
                                ON DELETE CASCADE
                        );
                        
                        -- Crear índice para mejorar consultas por usuario
                        CREATE INDEX IF NOT EXISTS busqueda_tradicional_usuario_id_idx 
                        ON busqueda_tradicional (usuario_id);
                        
                        -- Crear índice para ordenar por fecha
                        CREATE INDEX IF NOT EXISTS busqueda_tradicional_fecha_busqueda_idx 
                        ON busqueda_tradicional (fecha_busqueda DESC);
                    END IF;
                END $$;
            """,
            reverse_sql="""
                -- No revertir automáticamente para evitar pérdida de datos
                -- Si necesitas eliminar la tabla, hazlo manualmente
            """
        ),
    ]

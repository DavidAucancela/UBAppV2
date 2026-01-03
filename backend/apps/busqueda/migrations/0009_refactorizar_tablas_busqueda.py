# Generated migration for refactoring busqueda tables
# Las tablas ya están renombradas en la base de datos, solo actualizamos el estado de Django

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from pgvector.django import VectorField


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('busqueda', '0008_rename_busqueda_en_modelo__81e0a9_idx_busqueda_en_modelo__08fb29_idx_and_more'),
    ]

    operations = [
        # PASO 1: Renombrar modelo HistorialBusqueda a BusquedaTradicional
        # La tabla ya se llama busqueda_tradicional, solo actualizamos el estado
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameModel(
                    old_name='HistorialBusqueda',
                    new_name='BusquedaTradicional',
                ),
                migrations.AlterModelTable(
                    name='busquedatradicional',
                    table='busqueda_tradicional',
                ),
            ]
        ),
        
        # PASO 2: Agregar campo resultados_json (solo si la tabla existe y el campo no existe)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'busqueda_tradicional'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'busqueda_tradicional' AND column_name = 'resultados_json'
                    ) THEN
                        ALTER TABLE busqueda_tradicional 
                        ADD COLUMN resultados_json JSONB NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                ALTER TABLE busqueda_tradicional DROP COLUMN IF EXISTS resultados_json;
            """
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # No hacer nada, el campo ya existe o fue agregado por RunSQL
            state_operations=[
                migrations.AddField(
                    model_name='busquedatradicional',
                    name='resultados_json',
                    field=models.JSONField(blank=True, help_text='Resultados completos para generación de PDF', null=True, verbose_name='Resultados en JSON'),
                ),
            ]
        ),
        
        # PASO 3: Renombrar modelo BusquedaSemantica a EmbeddingBusqueda
        # La tabla ya se llama embedding_busqueda, solo actualizamos el estado
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameModel(
                    old_name='BusquedaSemantica',
                    new_name='EmbeddingBusqueda',
                ),
                migrations.AlterModelTable(
                    name='embeddingbusqueda',
                    table='embedding_busqueda',
                ),
            ]
        ),
        
        # PASO 4: Agregar campo embedding_vector (solo si la tabla existe y el campo no existe)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'embedding_busqueda'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'embedding_busqueda' AND column_name = 'embedding_vector'
                    ) THEN
                        ALTER TABLE embedding_busqueda 
                        ADD COLUMN embedding_vector vector(1536) NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                ALTER TABLE embedding_busqueda DROP COLUMN IF EXISTS embedding_vector;
            """
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # No hacer nada, el campo ya existe o fue agregado por RunSQL
            state_operations=[
                migrations.AddField(
                    model_name='embeddingbusqueda',
                    name='embedding_vector',
                    field=VectorField(blank=True, dimensions=1536, help_text='Vector embedding de la consulta para reutilización', null=True, verbose_name='Vector de Embedding de la Consulta'),
                ),
            ]
        ),
        
        # PASO 5: Agregar campo resultados_json a EmbeddingBusqueda (solo si la tabla existe y el campo no existe)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'embedding_busqueda'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'embedding_busqueda' AND column_name = 'resultados_json'
                    ) THEN
                        ALTER TABLE embedding_busqueda 
                        ADD COLUMN resultados_json JSONB NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                ALTER TABLE embedding_busqueda DROP COLUMN IF EXISTS resultados_json;
            """
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # No hacer nada, el campo ya existe o fue agregado por RunSQL
            state_operations=[
                migrations.AddField(
                    model_name='embeddingbusqueda',
                    name='resultados_json',
                    field=models.JSONField(blank=True, help_text='Resultados completos con métricas para generación de PDF', null=True, verbose_name='Resultados en JSON'),
                ),
            ]
        ),
        
        # PASO 6: Agregar índices (solo si la tabla existe y el índice no existe)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'embedding_busqueda'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM pg_indexes 
                        WHERE indexname = 'embedding_b_usuario_idx'
                    ) THEN
                        CREATE INDEX embedding_b_usuario_idx 
                        ON embedding_busqueda (usuario_id, fecha_busqueda DESC);
                    END IF;
                END $$;
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS embedding_b_usuario_idx;
            """
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # No hacer nada, el índice ya existe o fue creado por RunSQL
            state_operations=[
                migrations.AddIndex(
                    model_name='embeddingbusqueda',
                    index=models.Index(fields=['usuario', '-fecha_busqueda'], name='embedding_b_usuario_idx'),
                ),
            ]
        ),
        
        # PASO 7: Eliminar FeedbackSemantico (solo si existe en la base de datos)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'busqueda_feedbacksemantico') THEN
                        DROP TABLE busqueda_feedbacksemantico CASCADE;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'feed_semantica') THEN
                        DROP TABLE feed_semantica CASCADE;
                    END IF;
                END $$;
            """,
            reverse_sql="-- No se puede revertir automáticamente"
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # No hacer nada, la tabla ya fue eliminada
            state_operations=[
                migrations.DeleteModel(
                    name='FeedbackSemantico',
                ),
            ]
        ),
        
        # PASO 8: Renombrar modelo SugerenciaSemantica a HistorialSemantica
        # La tabla ya se llama historial_semantica, solo actualizamos el estado
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameModel(
                    old_name='SugerenciaSemantica',
                    new_name='HistorialSemantica',
                ),
                migrations.AlterModelTable(
                    name='historialsemantica',
                    table='historial_semantica',
                ),
            ]
        ),
        
        # PASO 9: Agregar campo veces_usada (solo si la tabla existe y el campo no existe)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'historial_semantica'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'historial_semantica' AND column_name = 'veces_usada'
                    ) THEN
                        ALTER TABLE historial_semantica 
                        ADD COLUMN veces_usada INTEGER DEFAULT 0 NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                ALTER TABLE historial_semantica DROP COLUMN IF EXISTS veces_usada;
            """
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # No hacer nada, el campo ya existe o fue agregado por RunSQL
            state_operations=[
                migrations.AddField(
                    model_name='historialsemantica',
                    name='veces_usada',
                    field=models.PositiveIntegerField(default=0, help_text='Contador de veces que se ha usado esta sugerencia', verbose_name='Veces Usada'),
                ),
            ]
        ),
        
        # PASO 10: Actualizar opciones de modelos
        migrations.AlterModelOptions(
            name='historialsemantica',
            options={'ordering': ['orden', '-veces_usada', '-fecha_creacion'], 'verbose_name': 'Historial Semántico', 'verbose_name_plural': 'Historial Semántico'},
        ),
        migrations.AlterModelOptions(
            name='embeddingbusqueda',
            options={'ordering': ['-fecha_busqueda'], 'verbose_name': 'Búsqueda Semántica (Embedding)', 'verbose_name_plural': 'Búsquedas Semánticas (Embeddings)'},
        ),
        migrations.AlterModelOptions(
            name='busquedatradicional',
            options={'ordering': ['-fecha_busqueda'], 'verbose_name': 'Búsqueda Tradicional', 'verbose_name_plural': 'Búsquedas Tradicionales'},
        ),
    ]

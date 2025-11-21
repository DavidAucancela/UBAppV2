# Generated migration for EnvioEmbedding with pgvector support

from django.db import migrations, models
import pgvector.django


class Migration(migrations.Migration):
    """Actualiza EnvioEmbedding para usar VectorField nativo de pgvector"""

    dependencies = [
        ('busqueda', '0006_habilitar_pgvector'),
    ]

    operations = [
        # Agregar nuevo campo vectorial
        migrations.AddField(
            model_name='envioembedding',
            name='embedding_vector_new',
            field=pgvector.django.VectorField(
                dimensions=1536,
                blank=True,
                help_text='Vector de embedding nativo de pgvector',
                null=True,
                verbose_name='Vector de Embedding'
            ),
        ),
        # Agregar campo de similitud coseno promedio
        migrations.AddField(
            model_name='envioembedding',
            name='cosine_similarity_avg',
            field=models.FloatField(
                default=0.0,
                help_text='Similitud coseno promedio con otros embeddings',
                verbose_name='Similitud Coseno Promedio'
            ),
        ),
        # Agregar índices
        migrations.AddIndex(
            model_name='envioembedding',
            index=models.Index(fields=['modelo_usado'], name='busqueda_en_modelo__81e0a9_idx'),
        ),
        migrations.AddIndex(
            model_name='envioembedding',
            index=models.Index(fields=['fecha_generacion'], name='busqueda_en_fecha_g_6f5e42_idx'),
        ),
    ]


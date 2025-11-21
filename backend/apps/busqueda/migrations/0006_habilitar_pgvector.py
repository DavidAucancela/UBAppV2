from django.db import migrations
from pgvector.django import VectorExtension


class Migration(migrations.Migration):
    """Migración para habilitar la extensión pgvector en PostgreSQL"""
    
    dependencies = [
        ('busqueda', '0005_agregar_costo_y_modelo_busqueda_semantica'),
    ]

    operations = [
        VectorExtension(),
    ]


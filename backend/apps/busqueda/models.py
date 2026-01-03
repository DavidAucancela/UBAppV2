from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField
import json

Usuario = get_user_model()

class BusquedaTradicional(models.Model):
    """Modelo para almacenar historial de búsquedas tradicionales"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    termino_busqueda = models.CharField(max_length=255)
    tipo_busqueda = models.CharField(max_length=50, default='general')
    fecha_busqueda = models.DateTimeField(auto_now_add=True)
    resultados_encontrados = models.PositiveIntegerField(default=0)
    resultados_json = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Resultados en JSON",
        help_text="Resultados completos para generación de PDF"
    )

    class Meta:
        db_table = 'busqueda_tradicional'
        verbose_name = 'Búsqueda Tradicional'
        verbose_name_plural = 'Búsquedas Tradicionales'
        ordering = ['-fecha_busqueda']

    def __str__(self):
        return f"{self.usuario.username} - {self.termino_busqueda}"


class EnvioEmbedding(models.Model):
    """Modelo para almacenar embeddings de envíos generados con OpenAI"""
    envio = models.OneToOneField(
        'archivos.Envio',
        on_delete=models.CASCADE,
        related_name='embedding',
        verbose_name="Envío"
    )
    # Campo vectorial nativo de pgvector (1536 dimensiones para text-embedding-3-small)
    embedding_vector = VectorField(
        dimensions=1536,
        verbose_name="Vector de Embedding",
        help_text="Vector de embedding nativo de pgvector",
        null=True,
        blank=True
    )
    texto_indexado = models.TextField(
        verbose_name="Texto Indexado",
        help_text="Texto que fue usado para generar el embedding"
    )
    fecha_generacion = models.DateTimeField(auto_now=True)
    modelo_usado = models.CharField(max_length=100, default='text-embedding-3-small')
    
    # Métricas de similitud precalculadas
    cosine_similarity_avg = models.FloatField(
        default=0.0,
        verbose_name="Similitud Coseno Promedio",
        help_text="Similitud coseno promedio con otros embeddings"
    )

    class Meta:
        db_table = 'embedding_envio'
        verbose_name = 'Embedding de Envío'
        verbose_name_plural = 'Embeddings de Envíos'
        ordering = ['-fecha_generacion']
        indexes = [
            models.Index(fields=['modelo_usado']),
            models.Index(fields=['fecha_generacion']),
        ]

    def __str__(self):
        return f"Embedding: {self.envio.hawb}"

    def set_vector(self, vector_list):
        """Guarda el vector (compatible con pgvector)"""
        self.embedding_vector = vector_list

    def get_vector(self):
        """Obtiene el vector como lista de Python"""
        if self.embedding_vector is None:
            return []
        # pgvector devuelve el vector directamente como lista
        return list(self.embedding_vector) if hasattr(self.embedding_vector, '__iter__') else []


class EmbeddingBusqueda(models.Model):
    """Modelo para almacenar historial de búsquedas semánticas con sus embeddings"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    consulta = models.TextField(verbose_name="Consulta")
    
    # Campo vectorial para almacenar el embedding de la consulta
    embedding_vector = VectorField(
        dimensions=1536,
        verbose_name="Vector de Embedding de la Consulta",
        help_text="Vector embedding de la consulta para reutilización",
        null=True,
        blank=True
    )
    
    resultados_encontrados = models.PositiveIntegerField(default=0)
    tiempo_respuesta = models.IntegerField(
        help_text="Tiempo de respuesta en milisegundos",
        default=0
    )
    fecha_busqueda = models.DateTimeField(auto_now_add=True)
    filtros_aplicados = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Filtros Aplicados"
    )
    modelo_utilizado = models.CharField(
        max_length=100,
        default='text-embedding-3-small',
        verbose_name="Modelo de Embedding Utilizado"
    )
    costo_consulta = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        default=0.0,
        verbose_name="Costo de la Consulta (USD)",
        help_text="Costo en USD de la consulta según tokens utilizados"
    )
    tokens_utilizados = models.PositiveIntegerField(
        default=0,
        verbose_name="Tokens Utilizados"
    )
    resultados_json = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Resultados en JSON",
        help_text="Resultados completos con métricas para generación de PDF"
    )

    class Meta:
        db_table = 'embedding_busqueda'
        verbose_name = 'Búsqueda Semántica (Embedding)'
        verbose_name_plural = 'Búsquedas Semánticas (Embeddings)'
        ordering = ['-fecha_busqueda']
        indexes = [
            models.Index(fields=['usuario', '-fecha_busqueda']),
            models.Index(fields=['modelo_utilizado']),
        ]

    def __str__(self):
        return f"{self.usuario.username} - {self.consulta[:50]}"
    
    def set_vector(self, vector_list):
        """Guarda el vector de embedding de la consulta"""
        self.embedding_vector = vector_list

    def get_vector(self):
        """Obtiene el vector como lista de Python"""
        if self.embedding_vector is None:
            return []
        return list(self.embedding_vector) if hasattr(self.embedding_vector, '__iter__') else []


class HistorialSemantica(models.Model):
    """Modelo para sugerencias y historial de búsquedas semánticas populares"""
    texto = models.CharField(max_length=200, verbose_name="Texto de Sugerencia")
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('estado', 'Estado'),
            ('ciudad', 'Ciudad'),
            ('fecha', 'Fecha'),
            ('comprador', 'Comprador'),
            ('general', 'General'),
        ],
        default='general'
    )
    icono = models.CharField(
        max_length=50,
        default='fa-search',
        help_text="Clase de icono FontAwesome"
    )
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    veces_usada = models.PositiveIntegerField(
        default=0,
        verbose_name="Veces Usada",
        help_text="Contador de veces que se ha usado esta sugerencia"
    )

    class Meta:
        db_table = 'historial_semantica'
        verbose_name = 'Historial Semántico'
        verbose_name_plural = 'Historial Semántico'
        ordering = ['orden', '-veces_usada', '-fecha_creacion']

    def __str__(self):
        return f"{self.texto} ({self.categoria})"

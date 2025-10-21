from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
import json

Usuario = get_user_model()

class HistorialBusqueda(models.Model):
    """Modelo para almacenar historial de búsquedas"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    termino_busqueda = models.CharField(max_length=255)
    tipo_busqueda = models.CharField(max_length=50, default='general')
    fecha_busqueda = models.DateTimeField(auto_now_add=True)
    resultados_encontrados = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Historial de Búsqueda'
        verbose_name_plural = 'Historial de Búsquedas'
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
    embedding_vector = models.TextField(
        verbose_name="Vector de Embedding",
        help_text="Vector de embedding serializado como JSON"
    )
    texto_indexado = models.TextField(
        verbose_name="Texto Indexado",
        help_text="Texto que fue usado para generar el embedding"
    )
    fecha_generacion = models.DateTimeField(auto_now=True)
    modelo_usado = models.CharField(max_length=100, default='text-embedding-3-small')

    class Meta:
        verbose_name = 'Embedding de Envío'
        verbose_name_plural = 'Embeddings de Envíos'
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"Embedding: {self.envio.hawb}"

    def set_vector(self, vector_list):
        """Guarda el vector como JSON"""
        self.embedding_vector = json.dumps(vector_list)

    def get_vector(self):
        """Obtiene el vector como lista de Python"""
        return json.loads(self.embedding_vector)


class BusquedaSemantica(models.Model):
    """Modelo para almacenar historial de búsquedas semánticas"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    consulta = models.TextField(verbose_name="Consulta")
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

    class Meta:
        verbose_name = 'Búsqueda Semántica'
        verbose_name_plural = 'Búsquedas Semánticas'
        ordering = ['-fecha_busqueda']

    def __str__(self):
        return f"{self.usuario.username} - {self.consulta[:50]}"


class FeedbackSemantico(models.Model):
    """Modelo para almacenar feedback de resultados semánticos"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    busqueda = models.ForeignKey(
        BusquedaSemantica,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        null=True,
        blank=True
    )
    envio = models.ForeignKey(
        'archivos.Envio',
        on_delete=models.CASCADE,
        verbose_name="Envío"
    )
    es_relevante = models.BooleanField(
        verbose_name="Es Relevante",
        help_text="Indica si el usuario consideró relevante este resultado"
    )
    puntuacion_similitud = models.FloatField(
        verbose_name="Puntuación de Similitud",
        help_text="Puntuación de similitud original del resultado"
    )
    fecha_feedback = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Feedback Semántico'
        verbose_name_plural = 'Feedbacks Semánticos'
        ordering = ['-fecha_feedback']
        unique_together = [['usuario', 'envio', 'busqueda']]

    def __str__(self):
        relevancia = "Relevante" if self.es_relevante else "No relevante"
        return f"{self.usuario.username} - {self.envio.hawb} - {relevancia}"


class SugerenciaSemantica(models.Model):
    """Modelo para sugerencias predefinidas de búsqueda semántica"""
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

    class Meta:
        verbose_name = 'Sugerencia Semántica'
        verbose_name_plural = 'Sugerencias Semánticas'
        ordering = ['orden', '-fecha_creacion']

    def __str__(self):
        return f"{self.texto} ({self.categoria})"

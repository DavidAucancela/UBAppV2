"""
Modelos para el Dashboard de Pruebas y Métricas.
Almacena métricas de evaluación experimental del sistema y módulo de búsqueda semántica.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import json

Usuario = get_user_model()


# ==================== MÉTRICAS SEMÁNTICAS ====================

class PruebaControladaSemantica(models.Model):
    """
    Modelo para almacenar pruebas controladas de búsqueda semántica.
    Permite evaluar métricas offline con datos predefinidos.
    """
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre de la Prueba",
        help_text="Nombre descriptivo de la prueba controlada"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
        help_text="Descripción detallada de la prueba"
    )
    consulta = models.TextField(
        verbose_name="Consulta de Prueba",
        help_text="Texto de la consulta a evaluar"
    )
    resultados_relevantes = models.JSONField(
        verbose_name="Resultados Relevantes",
        help_text="Lista de IDs de envíos que son relevantes para esta consulta"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ejecucion = models.DateTimeField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pruebas_semanticas_creadas'
    )

    class Meta:
        db_table = 'prueba_controlada_semantica'
        verbose_name = 'Prueba Controlada Semántica'
        verbose_name_plural = 'Pruebas Controladas Semánticas'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - {self.consulta[:50]}"


class MetricaSemantica(models.Model):
    """
    Modelo para almacenar métricas de evaluación de búsqueda semántica.
    Calculadas offline sobre pruebas controladas o búsquedas reales.
    """
    # Relación con búsqueda semántica real (opcional)
    busqueda_semantica = models.ForeignKey(
        'busqueda.EmbeddingBusqueda',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='metricas',
        verbose_name="Búsqueda Semántica"
    )
    
    # Relación con prueba controlada (opcional)
    prueba_controlada = models.ForeignKey(
        PruebaControladaSemantica,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='metricas',
        verbose_name="Prueba Controlada"
    )
    
    # Datos de la consulta
    consulta = models.TextField(verbose_name="Consulta")
    fecha_calculo = models.DateTimeField(auto_now_add=True)
    
    # Resultados rankeados (JSON con estructura completa)
    resultados_rankeados = models.JSONField(
        verbose_name="Resultados Rankeados",
        help_text="Lista de resultados con scores y posiciones"
    )
    
    # Métricas calculadas
    mrr = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="MRR (Mean Reciprocal Rank)",
        help_text="MRR calculado sobre los resultados"
    )
    
    ndcg_10 = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="nDCG@10",
        help_text="Normalized Discounted Cumulative Gain@10"
    )
    
    precision_5 = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Precision@5",
        help_text="Precisión en los primeros 5 resultados"
    )
    
    # Información adicional
    total_resultados = models.PositiveIntegerField(default=0)
    total_relevantes_encontrados = models.PositiveIntegerField(default=0)
    tiempo_procesamiento_ms = models.IntegerField(
        default=0,
        verbose_name="Tiempo de Procesamiento (ms)"
    )
    
    # Logs detallados del pipeline
    logs_pipeline = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Logs del Pipeline",
        help_text="Logs detallados de cada etapa del proceso semántico"
    )
    
    # Metadata
    modelo_embedding = models.CharField(
        max_length=100,
        default='text-embedding-3-small',
        verbose_name="Modelo de Embedding Utilizado"
    )
    metrica_ordenamiento = models.CharField(
        max_length=50,
        default='score_combinado',
        verbose_name="Métrica de Ordenamiento"
    )

    class Meta:
        db_table = 'metrica_semantica'
        verbose_name = 'Métrica Semántica'
        verbose_name_plural = 'Métricas Semánticas'
        ordering = ['-fecha_calculo']
        indexes = [
            models.Index(fields=['-fecha_calculo']),
            models.Index(fields=['mrr']),
            models.Index(fields=['ndcg_10']),
            models.Index(fields=['precision_5']),
        ]

    def __str__(self):
        return f"Métrica Semántica - {self.consulta[:50]} - {self.fecha_calculo}"


class RegistroGeneracionEmbedding(models.Model):
    """
    Modelo para registrar cada generación de embedding de un envío.
    Se registra automáticamente cuando se crea o actualiza un envío.
    """
    envio = models.ForeignKey(
        'archivos.Envio',
        on_delete=models.CASCADE,
        related_name='registros_embedding',
        verbose_name="Envío"
    )
    
    estado = models.CharField(
        max_length=20,
        choices=[
            ('generado', 'Generado Exitosamente'),
            ('error', 'Error en Generación'),
            ('omitido', 'Omitido (ya existía)'),
        ],
        default='generado',
        verbose_name="Estado"
    )
    
    dimension_embedding = models.PositiveIntegerField(
        default=1536,
        verbose_name="Dimensión del Embedding"
    )
    
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    tiempo_generacion_ms = models.IntegerField(
        default=0,
        verbose_name="Tiempo de Generación (ms)"
    )
    
    modelo_usado = models.CharField(
        max_length=100,
        default='text-embedding-3-small',
        verbose_name="Modelo Utilizado"
    )
    
    # Información del error si hubo
    mensaje_error = models.TextField(
        null=True,
        blank=True,
        verbose_name="Mensaje de Error"
    )
    
    # Tipo de proceso
    tipo_proceso = models.CharField(
        max_length=50,
        choices=[
            ('automatico', 'Automático (creación de envío)'),
            ('manual', 'Manual (comando de gestión)'),
            ('masivo', 'Masivo (importación)'),
        ],
        default='automatico',
        verbose_name="Tipo de Proceso"
    )
    
    # Relación con embedding generado (si fue exitoso)
    embedding = models.OneToOneField(
        'busqueda.EnvioEmbedding',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registro_generacion',
        verbose_name="Embedding Generado"
    )

    class Meta:
        db_table = 'registro_generacion_embedding'
        verbose_name = 'Registro de Generación de Embedding'
        verbose_name_plural = 'Registros de Generación de Embeddings'
        ordering = ['-fecha_generacion']
        indexes = [
            models.Index(fields=['-fecha_generacion']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_proceso']),
            models.Index(fields=['envio', '-fecha_generacion']),
        ]

    def __str__(self):
        return f"Embedding {self.envio.hawb} - {self.estado} - {self.fecha_generacion}"


# ==================== MÉTRICAS DE EFICIENCIA Y RENDIMIENTO ====================

class PruebaCarga(models.Model):
    """
    Modelo para almacenar pruebas de carga del sistema.
    Permite ejecutar pruebas con diferentes niveles de carga (1, 10, 30 búsquedas).
    """
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre de la Prueba",
        help_text="Nombre descriptivo de la prueba de carga"
    )
    
    tipo_prueba = models.CharField(
        max_length=50,
        choices=[
            ('busqueda_semantica', 'Búsqueda Semántica'),
            ('registro_envio', 'Registro de Envío'),
        ],
        verbose_name="Tipo de Prueba"
    )
    
    nivel_carga = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Nivel de Carga",
        help_text="Cantidad de operaciones a ejecutar (1, 10, 30)"
    )
    
    tipo_registro = models.CharField(
        max_length=50,
        choices=[
            ('manual', 'Manual (simulado)'),
            ('automatico', 'Automático'),
        ],
        null=True,
        blank=True,
        verbose_name="Tipo de Registro",
        help_text="Solo aplica para pruebas de registro de envío"
    )
    
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)
    ejecutado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pruebas_carga_ejecutadas'
    )
    
    # Resultados agregados
    tiempo_promedio_ms = models.FloatField(
        default=0.0,
        verbose_name="Tiempo Promedio (ms)"
    )
    tiempo_minimo_ms = models.IntegerField(
        default=0,
        verbose_name="Tiempo Mínimo (ms)"
    )
    tiempo_maximo_ms = models.IntegerField(
        default=0,
        verbose_name="Tiempo Máximo (ms)"
    )
    
    # Recursos promedio
    cpu_promedio = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="CPU Promedio (%)"
    )
    cpu_maximo = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="CPU Máximo (%)"
    )
    ram_promedio_mb = models.FloatField(
        default=0.0,
        verbose_name="RAM Promedio (MB)"
    )
    ram_maximo_mb = models.FloatField(
        default=0.0,
        verbose_name="RAM Máximo (MB)"
    )
    
    # Estadísticas
    total_exitosos = models.PositiveIntegerField(default=0)
    total_errores = models.PositiveIntegerField(default=0)
    
    # Datos de prueba (JSON con consultas o datos usados)
    datos_prueba = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Datos de Prueba",
        help_text="Consultas o datos utilizados en la prueba"
    )

    class Meta:
        db_table = 'prueba_carga'
        verbose_name = 'Prueba de Carga'
        verbose_name_plural = 'Pruebas de Carga'
        ordering = ['-fecha_ejecucion']
        indexes = [
            models.Index(fields=['-fecha_ejecucion']),
            models.Index(fields=['tipo_prueba', 'nivel_carga']),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.tipo_prueba} - Carga: {self.nivel_carga}"


class MetricaRendimiento(models.Model):
    """
    Modelo para almacenar métricas individuales de rendimiento.
    Cada registro representa una medición de tiempo y recursos para una operación específica.
    """
    # Relación con prueba de carga (opcional)
    prueba_carga = models.ForeignKey(
        PruebaCarga,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='metricas_individuales',
        verbose_name="Prueba de Carga"
    )
    
    # Tipo de proceso
    proceso = models.CharField(
        max_length=50,
        choices=[
            ('registro_envio_manual', 'Registro de Envío Manual'),
            ('registro_envio_automatico', 'Registro de Envío Automático'),
            ('busqueda_semantica', 'Búsqueda Semántica'),
        ],
        verbose_name="Proceso"
    )
    
    # Tiempos
    tiempo_respuesta_ms = models.IntegerField(
        default=0,
        verbose_name="Tiempo de Respuesta (ms)"
    )
    
    # Recursos del sistema
    uso_cpu = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="Uso de CPU (%)"
    )
    uso_ram_mb = models.FloatField(
        default=0.0,
        verbose_name="Uso de RAM (MB)"
    )
    
    # Momento de la medición
    fecha_medicion = models.DateTimeField(auto_now_add=True)
    
    # Nivel de carga asociado
    nivel_carga = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Nivel de Carga",
        help_text="Cantidad de operaciones simultáneas (1, 10, 30)"
    )
    
    # Estado
    exito = models.BooleanField(
        default=True,
        verbose_name="Éxito",
        help_text="Indica si la operación fue exitosa"
    )
    
    # Información adicional
    detalles = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Detalles Adicionales",
        help_text="Información adicional sobre la operación"
    )

    class Meta:
        db_table = 'metrica_rendimiento'
        verbose_name = 'Métrica de Rendimiento'
        verbose_name_plural = 'Métricas de Rendimiento'
        ordering = ['-fecha_medicion']
        indexes = [
            models.Index(fields=['-fecha_medicion']),
            models.Index(fields=['proceso', 'nivel_carga']),
            models.Index(fields=['exito']),
        ]

    def __str__(self):
        return f"{self.proceso} - {self.tiempo_respuesta_ms}ms - {self.fecha_medicion}"


class RegistroManualEnvio(models.Model):
    """
    Modelo para simular y registrar tiempos de registro manual de envíos.
    Permite comparar tiempos manuales vs automáticos.
    """
    hawb = models.CharField(
        max_length=50,
        verbose_name="HAWB",
        help_text="Número de envío simulado"
    )
    
    tiempo_registro_segundos = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        verbose_name="Tiempo de Registro (segundos)",
        help_text="Tiempo medido con cronómetro para registro manual"
    )
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registros_manuales_envios'
    )
    
    # Información del envío simulado
    datos_envio = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Datos del Envío",
        help_text="Datos del envío que se registró manualmente"
    )
    
    # Notas
    notas = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notas",
        help_text="Observaciones sobre el registro manual"
    )

    class Meta:
        db_table = 'registro_manual_envio'
        verbose_name = 'Registro Manual de Envío'
        verbose_name_plural = 'Registros Manuales de Envíos'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['-fecha_registro']),
            models.Index(fields=['registrado_por']),
        ]

    def __str__(self):
        return f"Registro Manual {self.hawb} - {self.tiempo_registro_segundos}s"

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

Usuario = get_user_model()

class DashboardMetric(models.Model):
    """Modelo para métricas del dashboard"""
    
    METRIC_TYPES = [
        ('envios_count', 'Cantidad de Envíos'),
        ('envios_value', 'Valor Total de Envíos'),
        ('envios_weight', 'Peso Total de Envíos'),
        ('productos_count', 'Cantidad de Productos'),
        ('usuarios_activos', 'Usuarios Activos'),
        ('compradores_activos', 'Compradores Activos'),
    ]
    
    PERIOD_TYPES = [
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
        ('yearly', 'Anual'),
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES)
    date = models.DateField()
    value = models.DecimalField(max_digits=15, decimal_places=2)
    count = models.IntegerField(default=0)
    
    # Campos adicionales para análisis
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Métrica del Dashboard'
        verbose_name_plural = 'Métricas del Dashboard'
        unique_together = ['metric_type', 'period_type', 'date']
        ordering = ['-date', 'metric_type']
    
    def __str__(self):
        return f"{self.get_metric_type_display()} - {self.date} ({self.get_period_type_display()})"


class Report(models.Model):
    """Modelo para reportes generados"""
    
    REPORT_TYPES = [
        ('envios_summary', 'Resumen de Envíos'),
        ('productos_analysis', 'Análisis de Productos'),
        ('usuarios_activity', 'Actividad de Usuarios'),
        ('financial_summary', 'Resumen Financiero'),
        ('custom', 'Reporte Personalizado'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    
    # Usuario que solicitó el reporte
    requested_by = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='requested_reports')
    
    # Parámetros del reporte
    parameters = models.JSONField(default=dict, blank=True)
    
    # Estado y resultados
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_data = models.JSONField(default=dict, blank=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Fechas
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    def mark_as_completed(self):
        """Marca el reporte como completado"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_as_failed(self):
        """Marca el reporte como fallido"""
        self.status = 'failed'
        self.save()


class UserActivity(models.Model):
    """Modelo para rastrear actividad de usuarios"""
    
    ACTION_TYPES = [
        ('login', 'Inicio de Sesión'),
        ('logout', 'Cierre de Sesión'),
        ('create_envio', 'Crear Envío'),
        ('update_envio', 'Actualizar Envío'),
        ('delete_envio', 'Eliminar Envío'),
        ('create_producto', 'Crear Producto'),
        ('update_producto', 'Actualizar Producto'),
        ('delete_producto', 'Eliminar Producto'),
        ('search', 'Búsqueda'),
        ('export_data', 'Exportar Datos'),
        ('import_data', 'Importar Datos'),
        ('generate_report', 'Generar Reporte'),
    ]
    
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField(blank=True)
    
    # Información adicional sobre la acción
    object_type = models.CharField(max_length=50, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    
    # Metadatos adicionales
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Actividad de Usuario'
        verbose_name_plural = 'Actividades de Usuarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.nombre} - {self.get_action_display()} - {self.created_at}"

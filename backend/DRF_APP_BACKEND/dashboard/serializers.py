from rest_framework import serializers
from .models import DashboardMetric, Report, UserActivity
from usuarios.serializers import UsuarioListSerializer


class DashboardMetricSerializer(serializers.ModelSerializer):
    """Serializer para métricas del dashboard"""
    
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    period_type_display = serializers.CharField(source='get_period_type_display', read_only=True)
    
    class Meta:
        model = DashboardMetric
        fields = [
            'id', 'metric_type', 'metric_type_display', 
            'period_type', 'period_type_display',
            'date', 'value', 'count', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ReportSerializer(serializers.ModelSerializer):
    """Serializer para reportes"""
    
    requested_by_info = UsuarioListSerializer(source='requested_by', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'report_type', 'report_type_display',
            'description', 'requested_by', 'requested_by_info',
            'parameters', 'status', 'status_display',
            'result_data', 'file_path', 'date_from', 'date_to',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'completed_at', 'result_data', 'file_path']
    
    def create(self, validated_data):
        """Asigna el usuario actual al crear un reporte"""
        validated_data['requested_by'] = self.context['request'].user
        return super().create(validated_data)


class ReportListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar reportes"""
    
    requested_by_name = serializers.CharField(source='requested_by.nombre', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'report_type_display', 'requested_by_name',
            'status', 'status_display', 'created_at', 'completed_at'
        ]


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer para actividades de usuario"""
    
    user_info = UsuarioListSerializer(source='user', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'user_info', 'action', 'action_display',
            'description', 'object_type', 'object_id', 'metadata',
            'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['created_at']


class UserActivityListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar actividades"""
    
    user_name = serializers.CharField(source='user.nombre', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user_name', 'action_display', 'description', 'created_at'
        ]


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas generales del dashboard"""
    
    total_envios = serializers.IntegerField()
    total_productos = serializers.IntegerField()
    total_usuarios = serializers.IntegerField()
    total_compradores = serializers.IntegerField()
    
    # Valores totales
    valor_total_envios = serializers.DecimalField(max_digits=15, decimal_places=2)
    peso_total_envios = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Estadísticas del período actual
    envios_mes_actual = serializers.IntegerField()
    productos_mes_actual = serializers.IntegerField()
    valor_mes_actual = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Comparaciones con período anterior
    cambio_envios_mes = serializers.DecimalField(max_digits=5, decimal_places=2)
    cambio_productos_mes = serializers.DecimalField(max_digits=5, decimal_places=2)
    cambio_valor_mes = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Distribución por estado
    envios_por_estado = serializers.DictField()
    productos_por_categoria = serializers.DictField()
    
    # Actividad reciente
    actividad_reciente = UserActivityListSerializer(many=True)


class ChartDataSerializer(serializers.Serializer):
    """Serializer para datos de gráficos"""
    
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField(child=serializers.DictField())
    
    
class MetricsSummarySerializer(serializers.Serializer):
    """Serializer para resumen de métricas"""
    
    period = serializers.CharField()
    envios_data = ChartDataSerializer()
    productos_data = ChartDataSerializer()
    usuarios_data = ChartDataSerializer()
    financial_data = ChartDataSerializer()
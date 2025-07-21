from django.contrib import admin
from .models import DashboardMetric, Report, UserActivity


@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'period_type', 'date', 'value', 'count', 'created_at']
    list_filter = ['metric_type', 'period_type', 'date', 'created_at']
    search_fields = ['metric_type']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date', 'metric_type']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'requested_by', 'status', 'created_at', 'completed_at']
    list_filter = ['report_type', 'status', 'created_at', 'completed_at']
    search_fields = ['name', 'description', 'requested_by__nombre']
    readonly_fields = ['created_at', 'updated_at', 'completed_at', 'result_data']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'report_type', 'description', 'requested_by')
        }),
        ('Parámetros', {
            'fields': ('parameters', 'date_from', 'date_to')
        }),
        ('Estado y Resultados', {
            'fields': ('status', 'result_data', 'file_path')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'description', 'object_type', 'created_at']
    list_filter = ['action', 'object_type', 'created_at']
    search_fields = ['user__nombre', 'description', 'user__correo']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Usuario y Acción', {
            'fields': ('user', 'action', 'description')
        }),
        ('Objeto Relacionado', {
            'fields': ('object_type', 'object_id')
        }),
        ('Información Técnica', {
            'fields': ('metadata', 'ip_address', 'user_agent')
        }),
        ('Fecha', {
            'fields': ('created_at',)
        }),
    )

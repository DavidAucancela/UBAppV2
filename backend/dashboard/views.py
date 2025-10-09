from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg, Max, Min
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek, TruncYear
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import json
import os
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import DashboardMetric, Report, UserActivity
from .serializers import (
    DashboardMetricSerializer, ReportSerializer, ReportListSerializer,
    UserActivitySerializer, UserActivityListSerializer,
    DashboardStatsSerializer, ChartDataSerializer, MetricsSummarySerializer
)
from archivos.models import Envio, Producto
from usuarios.models import Usuario

Usuario = get_user_model()


class DashboardMetricViewSet(viewsets.ModelViewSet):
    """ViewSet para métricas del dashboard"""
    queryset = DashboardMetric.objects.all()
    serializer_class = DashboardMetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['metric_type', 'period_type', 'date']
    ordering_fields = ['date', 'value', 'count']
    ordering = ['-date']

    def get_queryset(self):
        """Filtra métricas según permisos del usuario"""
        user = self.request.user
        queryset = DashboardMetric.objects.all()
        
        # Solo admins y gerentes pueden ver todas las métricas
        if not (user.es_admin or user.es_gerente):
            # Otros usuarios pueden ver métricas limitadas
            queryset = queryset.filter(
                metric_type__in=['envios_count', 'productos_count']
            )
        
        return queryset


class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet para reportes"""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'status', 'requested_by']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'completed_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ReportListSerializer
        return ReportSerializer

    def get_queryset(self):
        """Filtra reportes según permisos del usuario"""
        user = self.request.user
        
        # Admins y gerentes pueden ver todos los reportes
        if user.es_admin or user.es_gerente:
            return Report.objects.all()
        
        # Otros usuarios solo ven sus propios reportes
        return Report.objects.filter(requested_by=user)

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Genera un reporte específico"""
        report = self.get_object()
        
        if report.status != 'pending':
            return Response(
                {'error': 'El reporte ya ha sido procesado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            report.status = 'processing'
            report.save()
            
            # Generar reporte según tipo
            result_data = self._generate_report_data(report)
            
            report.result_data = result_data
            report.mark_as_completed()
            
            serializer = self.get_serializer(report)
            return Response(serializer.data)
            
        except Exception as e:
            report.mark_as_failed()
            return Response(
                {'error': f'Error generando reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _generate_report_data(self, report):
        """Genera los datos del reporte según su tipo"""
        if report.report_type == 'envios_summary':
            return self._generate_envios_summary(report)
        elif report.report_type == 'productos_analysis':
            return self._generate_productos_analysis(report)
        elif report.report_type == 'usuarios_activity':
            return self._generate_usuarios_activity(report)
        elif report.report_type == 'financial_summary':
            return self._generate_financial_summary(report)
        else:
            return {'message': 'Tipo de reporte no implementado'}

    def _generate_envios_summary(self, report):
        """Genera resumen de envíos"""
        queryset = Envio.objects.all()
        
        if report.date_from:
            queryset = queryset.filter(fecha_emision__gte=report.date_from)
        if report.date_to:
            queryset = queryset.filter(fecha_emision__lte=report.date_to)
        
        summary = queryset.aggregate(
            total_envios=Count('id'),
            valor_total=Sum('valor_total'),
            peso_total=Sum('peso_total'),
            cantidad_total=Sum('cantidad_total'),
            valor_promedio=Avg('valor_total'),
            peso_promedio=Avg('peso_total')
        )
        
        # Distribución por estado
        por_estado = queryset.values('estado').annotate(
            count=Count('id'),
            valor=Sum('valor_total')
        ).order_by('estado')
        
        # Distribución por comprador
        por_comprador = queryset.values(
            'comprador__nombre'
        ).annotate(
            count=Count('id'),
            valor=Sum('valor_total')
        ).order_by('-valor')[:10]
        
        return {
            'resumen_general': summary,
            'por_estado': list(por_estado),
            'top_compradores': list(por_comprador),
            'periodo': {
                'desde': report.date_from,
                'hasta': report.date_to
            }
        }

    def _generate_productos_analysis(self, report):
        """Genera análisis de productos"""
        queryset = Producto.objects.all()
        
        if report.date_from:
            queryset = queryset.filter(fecha_creacion__gte=report.date_from)
        if report.date_to:
            queryset = queryset.filter(fecha_creacion__lte=report.date_to)
        
        summary = queryset.aggregate(
            total_productos=Count('id'),
            valor_total=Sum('valor'),
            peso_total=Sum('peso'),
            cantidad_total=Sum('cantidad'),
            valor_promedio=Avg('valor'),
            peso_promedio=Avg('peso')
        )
        
        # Distribución por categoría
        por_categoria = queryset.values('categoria').annotate(
            count=Count('id'),
            valor=Sum('valor'),
            peso=Sum('peso')
        ).order_by('-count')
        
        # Productos más valiosos
        mas_valiosos = queryset.order_by('-valor')[:10].values(
            'descripcion', 'valor', 'peso', 'cantidad', 'categoria'
        )
        
        return {
            'resumen_general': summary,
            'por_categoria': list(por_categoria),
            'productos_mas_valiosos': list(mas_valiosos),
            'periodo': {
                'desde': report.date_from,
                'hasta': report.date_to
            }
        }

    def _generate_usuarios_activity(self, report):
        """Genera reporte de actividad de usuarios"""
        queryset = UserActivity.objects.all()
        
        if report.date_from:
            queryset = queryset.filter(created_at__gte=report.date_from)
        if report.date_to:
            queryset = queryset.filter(created_at__lte=report.date_to)
        
        # Actividad por usuario
        por_usuario = queryset.values(
            'user__nombre', 'user__rol'
        ).annotate(
            total_acciones=Count('id')
        ).order_by('-total_acciones')
        
        # Actividad por tipo de acción
        por_accion = queryset.values('action').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Actividad por día
        por_dia = queryset.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        return {
            'actividad_por_usuario': list(por_usuario),
            'actividad_por_accion': list(por_accion),
            'actividad_por_dia': list(por_dia),
            'periodo': {
                'desde': report.date_from,
                'hasta': report.date_to
            }
        }

    def _generate_financial_summary(self, report):
        """Genera resumen financiero"""
        queryset = Envio.objects.all()
        
        if report.date_from:
            queryset = queryset.filter(fecha_emision__gte=report.date_from)
        if report.date_to:
            queryset = queryset.filter(fecha_emision__lte=report.date_to)
        
        # Resumen financiero general
        summary = queryset.aggregate(
            ingresos_totales=Sum('valor_total'),
            envios_count=Count('id'),
            ticket_promedio=Avg('valor_total'),
            ingreso_maximo=Max('valor_total'),
            ingreso_minimo=Min('valor_total')
        )
        
        # Ingresos por mes
        por_mes = queryset.annotate(
            mes=TruncMonth('fecha_emision')
        ).values('mes').annotate(
            ingresos=Sum('valor_total'),
            envios=Count('id')
        ).order_by('mes')
        
        # Top compradores por valor
        top_compradores = queryset.values(
            'comprador__nombre'
        ).annotate(
            ingresos=Sum('valor_total'),
            envios=Count('id')
        ).order_by('-ingresos')[:10]
        
        return {
            'resumen_financiero': summary,
            'ingresos_por_mes': list(por_mes),
            'top_compradores': list(top_compradores),
            'periodo': {
                'desde': report.date_from,
                'hasta': report.date_to
            }
        }


class UserActivityViewSet(viewsets.ModelViewSet):
    """ViewSet para actividades de usuario"""
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'action', 'object_type']
    search_fields = ['description', 'user__nombre']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return UserActivityListSerializer
        return UserActivitySerializer

    def get_queryset(self):
        """Filtra actividades según permisos del usuario"""
        user = self.request.user
        
        # Admins y gerentes pueden ver todas las actividades
        if user.es_admin or user.es_gerente:
            return UserActivity.objects.all()
        
        # Otros usuarios solo ven sus propias actividades
        return UserActivity.objects.filter(user=user)


class DashboardStatsView(APIView):
    """Vista para estadísticas generales del dashboard"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Obtiene estadísticas generales del dashboard"""
        now = timezone.now()
        mes_actual = now.replace(day=1)
        mes_anterior = mes_actual - relativedelta(months=1)
        
        # Estadísticas generales
        total_envios = Envio.objects.count()
        total_productos = Producto.objects.count()
        total_usuarios = Usuario.objects.count()
        total_compradores = Usuario.objects.filter(rol=4).count()
        
        # Valores totales
        valor_total_envios = Envio.objects.aggregate(
            total=Sum('valor_total')
        )['total'] or 0
        
        peso_total_envios = Envio.objects.aggregate(
            total=Sum('peso_total')
        )['total'] or 0
        
        # Estadísticas del mes actual
        envios_mes_actual = Envio.objects.filter(
            fecha_emision__gte=mes_actual
        ).count()
        
        productos_mes_actual = Producto.objects.filter(
            fecha_creacion__gte=mes_actual
        ).count()
        
        valor_mes_actual = Envio.objects.filter(
            fecha_emision__gte=mes_actual
        ).aggregate(total=Sum('valor_total'))['total'] or 0
        
        # Estadísticas del mes anterior para comparación
        envios_mes_anterior = Envio.objects.filter(
            fecha_emision__gte=mes_anterior,
            fecha_emision__lt=mes_actual
        ).count()
        
        productos_mes_anterior = Producto.objects.filter(
            fecha_creacion__gte=mes_anterior,
            fecha_creacion__lt=mes_actual
        ).count()
        
        valor_mes_anterior = Envio.objects.filter(
            fecha_emision__gte=mes_anterior,
            fecha_emision__lt=mes_actual
        ).aggregate(total=Sum('valor_total'))['total'] or 0
        
        # Calcular cambios porcentuales
        def calcular_cambio_porcentual(actual, anterior):
            if anterior == 0:
                return 100 if actual > 0 else 0
            return ((actual - anterior) / anterior) * 100
        
        cambio_envios_mes = calcular_cambio_porcentual(envios_mes_actual, envios_mes_anterior)
        cambio_productos_mes = calcular_cambio_porcentual(productos_mes_actual, productos_mes_anterior)
        cambio_valor_mes = calcular_cambio_porcentual(float(valor_mes_actual), float(valor_mes_anterior))
        
        # Distribución por estado
        envios_por_estado = dict(
            Envio.objects.values('estado').annotate(
                count=Count('id')
            ).values_list('estado', 'count')
        )
        
        # Distribución por categoría de productos
        productos_por_categoria = dict(
            Producto.objects.values('categoria').annotate(
                count=Count('id')
            ).values_list('categoria', 'count')
        )
        
        # Actividad reciente
        actividad_reciente = UserActivity.objects.select_related('user')[:10]
        
        stats = {
            'total_envios': total_envios,
            'total_productos': total_productos,
            'total_usuarios': total_usuarios,
            'total_compradores': total_compradores,
            'valor_total_envios': valor_total_envios,
            'peso_total_envios': peso_total_envios,
            'envios_mes_actual': envios_mes_actual,
            'productos_mes_actual': productos_mes_actual,
            'valor_mes_actual': valor_mes_actual,
            'cambio_envios_mes': round(cambio_envios_mes, 2),
            'cambio_productos_mes': round(cambio_productos_mes, 2),
            'cambio_valor_mes': round(cambio_valor_mes, 2),
            'envios_por_estado': envios_por_estado,
            'productos_por_categoria': productos_por_categoria,
            'actividad_reciente': actividad_reciente
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)


class MetricsSummaryView(APIView):
    """Vista para resumen de métricas con datos para gráficos"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Obtiene datos de métricas para gráficos"""
        period = request.query_params.get('period', 'monthly')  # daily, weekly, monthly, yearly
        
        # Determinar el rango de fechas según el período
        now = timezone.now()
        if period == 'daily':
            start_date = now - timedelta(days=30)
            trunc_func = TruncDate
        elif period == 'weekly':
            start_date = now - timedelta(weeks=12)
            trunc_func = TruncWeek
        elif period == 'yearly':
            start_date = now - relativedelta(years=2)
            trunc_func = TruncYear
        else:  # monthly
            start_date = now - relativedelta(months=12)
            trunc_func = TruncMonth
        
        # Datos de envíos
        envios_data = self._get_envios_chart_data(start_date, trunc_func)
        
        # Datos de productos
        productos_data = self._get_productos_chart_data(start_date, trunc_func)
        
        # Datos de usuarios (actividad)
        usuarios_data = self._get_usuarios_chart_data(start_date, trunc_func)
        
        # Datos financieros
        financial_data = self._get_financial_chart_data(start_date, trunc_func)
        
        summary = {
            'period': period,
            'envios_data': envios_data,
            'productos_data': productos_data,
            'usuarios_data': usuarios_data,
            'financial_data': financial_data
        }
        
        serializer = MetricsSummarySerializer(summary)
        return Response(serializer.data)

    def _get_envios_chart_data(self, start_date, trunc_func):
        """Obtiene datos de envíos para gráficos"""
        data = Envio.objects.filter(
            fecha_emision__gte=start_date
        ).annotate(
            period=trunc_func('fecha_emision')
        ).values('period').annotate(
            count=Count('id'),
            valor=Sum('valor_total'),
            peso=Sum('peso_total')
        ).order_by('period')
        
        labels = [item['period'].strftime('%Y-%m-%d') for item in data]
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Cantidad de Envíos',
                    'data': [item['count'] for item in data],
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                },
                {
                    'label': 'Valor Total',
                    'data': [float(item['valor'] or 0) for item in data],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                }
            ]
        }

    def _get_productos_chart_data(self, start_date, trunc_func):
        """Obtiene datos de productos para gráficos"""
        data = Producto.objects.filter(
            fecha_creacion__gte=start_date
        ).annotate(
            period=trunc_func('fecha_creacion')
        ).values('period').annotate(
            count=Count('id'),
            valor=Sum('valor'),
            peso=Sum('peso')
        ).order_by('period')
        
        labels = [item['period'].strftime('%Y-%m-%d') for item in data]
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Cantidad de Productos',
                    'data': [item['count'] for item in data],
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                }
            ]
        }

    def _get_usuarios_chart_data(self, start_date, trunc_func):
        """Obtiene datos de actividad de usuarios para gráficos"""
        data = UserActivity.objects.filter(
            created_at__gte=start_date
        ).annotate(
            period=trunc_func('created_at')
        ).values('period').annotate(
            count=Count('id'),
            usuarios=Count('user', distinct=True)
        ).order_by('period')
        
        labels = [item['period'].strftime('%Y-%m-%d') for item in data]
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Actividades',
                    'data': [item['count'] for item in data],
                    'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                    'borderColor': 'rgba(153, 102, 255, 1)',
                },
                {
                    'label': 'Usuarios Activos',
                    'data': [item['usuarios'] for item in data],
                    'backgroundColor': 'rgba(255, 159, 64, 0.2)',
                    'borderColor': 'rgba(255, 159, 64, 1)',
                }
            ]
        }

    def _get_financial_chart_data(self, start_date, trunc_func):
        """Obtiene datos financieros para gráficos"""
        data = Envio.objects.filter(
            fecha_emision__gte=start_date
        ).annotate(
            period=trunc_func('fecha_emision')
        ).values('period').annotate(
            ingresos=Sum('valor_total'),
            envios=Count('id'),
            ticket_promedio=Avg('valor_total')
        ).order_by('period')
        
        labels = [item['period'].strftime('%Y-%m-%d') for item in data]
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Ingresos Totales',
                    'data': [float(item['ingresos'] or 0) for item in data],
                    'backgroundColor': 'rgba(255, 206, 86, 0.2)',
                    'borderColor': 'rgba(255, 206, 86, 1)',
                },
                {
                    'label': 'Ticket Promedio',
                    'data': [float(item['ticket_promedio'] or 0) for item in data],
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                }
            ]
        }


def log_user_activity(user, action, description='', object_type=None, object_id=None, metadata=None, request=None):
    """Función helper para registrar actividad de usuario"""
    activity_data = {
        'user': user,
        'action': action,
        'description': description,
        'object_type': object_type,
        'object_id': object_id,
        'metadata': metadata or {}
    }
    
    if request:
        activity_data['ip_address'] = request.META.get('REMOTE_ADDR')
        activity_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
    
    UserActivity.objects.create(**activity_data)

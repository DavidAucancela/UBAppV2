"""
Repositorios para la app de métricas.
Implementa el patrón Repository para acceso a datos de métricas y pruebas.
"""
from typing import Optional, List, Dict, Any
from django.db.models import QuerySet, Avg, Max, Min, Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.core.base.base_repository import BaseRepository
from .models import (
    PruebaControladaSemantica,
    MetricaSemantica,
    RegistroGeneracionEmbedding,
    PruebaCarga,
    MetricaRendimiento,
    RegistroManualEnvio
)


class PruebaControladaSemanticaRepository(BaseRepository):
    """Repositorio para PruebaControladaSemantica"""
    
    @property
    def model(self):
        return PruebaControladaSemantica
    
    def obtener_activas(self) -> QuerySet:
        """Obtiene pruebas controladas activas"""
        return self._get_optimized_queryset().filter(activa=True)
    
    def ejecutar_prueba(self, prueba_id: int) -> PruebaControladaSemantica:
        """Marca una prueba como ejecutada"""
        prueba = self.obtener_por_id(prueba_id)
        prueba.fecha_ejecucion = timezone.now()
        prueba.save()
        return prueba


class MetricaSemanticaRepository(BaseRepository):
    """Repositorio para MetricaSemantica"""
    
    @property
    def model(self):
        return MetricaSemantica
    
    @property
    def select_related_fields(self) -> List[str]:
        return ['busqueda_semantica', 'prueba_controlada']
    
    def filtrar_por_fecha(self, fecha_desde=None, fecha_hasta=None) -> QuerySet:
        """Filtra métricas por rango de fechas"""
        queryset = self._get_optimized_queryset()
        if fecha_desde:
            queryset = queryset.filter(fecha_calculo__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_calculo__lte=fecha_hasta)
        return queryset
    
    def obtener_estadisticas(self, fecha_desde=None, fecha_hasta=None) -> Dict[str, Any]:
        """Obtiene estadísticas agregadas de métricas semánticas"""
        queryset = self.filtrar_por_fecha(fecha_desde, fecha_hasta)
        
        return {
            'total_metricas': queryset.count(),
            'mrr_promedio': queryset.aggregate(avg=Avg('mrr'))['avg'] or 0.0,
            'mrr_maximo': queryset.aggregate(max=Max('mrr'))['max'] or 0.0,
            'mrr_minimo': queryset.aggregate(min=Min('mrr'))['min'] or 0.0,
            'ndcg_10_promedio': queryset.aggregate(avg=Avg('ndcg_10'))['avg'] or 0.0,
            'precision_5_promedio': queryset.aggregate(avg=Avg('precision_5'))['avg'] or 0.0,
        }


class RegistroGeneracionEmbeddingRepository(BaseRepository):
    """Repositorio para RegistroGeneracionEmbedding"""
    
    @property
    def model(self):
        return RegistroGeneracionEmbedding
    
    @property
    def select_related_fields(self) -> List[str]:
        return ['envio', 'embedding']
    
    def filtrar_por_estado(self, estado: str) -> QuerySet:
        """Filtra registros por estado"""
        return self._get_optimized_queryset().filter(estado=estado)
    
    def filtrar_por_tipo_proceso(self, tipo_proceso: str) -> QuerySet:
        """Filtra registros por tipo de proceso"""
        return self._get_optimized_queryset().filter(tipo_proceso=tipo_proceso)
    
    def obtener_estadisticas_generacion(self) -> Dict[str, Any]:
        """Obtiene estadísticas de generación de embeddings"""
        queryset = self._get_optimized_queryset()
        
        return {
            'total_registros': queryset.count(),
            'exitosos': queryset.filter(estado='generado').count(),
            'errores': queryset.filter(estado='error').count(),
            'omitidos': queryset.filter(estado='omitido').count(),
            'tiempo_promedio_ms': queryset.aggregate(avg=Avg('tiempo_generacion_ms'))['avg'] or 0.0,
            'tiempo_maximo_ms': queryset.aggregate(max=Max('tiempo_generacion_ms'))['max'] or 0,
        }


class PruebaCargaRepository(BaseRepository):
    """Repositorio para PruebaCarga"""
    
    @property
    def model(self):
        return PruebaCarga
    
    @property
    def select_related_fields(self) -> List[str]:
        return ['ejecutado_por']
    
    def filtrar_por_tipo(self, tipo_prueba: str) -> QuerySet:
        """Filtra pruebas por tipo"""
        return self._get_optimized_queryset().filter(tipo_prueba=tipo_prueba)
    
    def filtrar_por_nivel_carga(self, nivel_carga: int) -> QuerySet:
        """Filtra pruebas por nivel de carga"""
        return self._get_optimized_queryset().filter(nivel_carga=nivel_carga)


class MetricaRendimientoRepository(BaseRepository):
    """Repositorio para MetricaRendimiento"""
    
    @property
    def model(self):
        return MetricaRendimiento
    
    @property
    def select_related_fields(self) -> List[str]:
        return ['prueba_carga']
    
    def filtrar_por_proceso(self, proceso: str) -> QuerySet:
        """Filtra métricas por proceso"""
        return self._get_optimized_queryset().filter(proceso=proceso)
    
    def filtrar_por_nivel_carga(self, nivel_carga: int) -> QuerySet:
        """Filtra métricas por nivel de carga"""
        return self._get_optimized_queryset().filter(nivel_carga=nivel_carga)
    
    def obtener_estadisticas_por_proceso(self, proceso: str, nivel_carga: int = None) -> Dict[str, Any]:
        """Obtiene estadísticas agregadas por proceso"""
        queryset = self.filtrar_por_proceso(proceso)
        if nivel_carga:
            queryset = queryset.filter(nivel_carga=nivel_carga)
        
        return {
            'total_mediciones': queryset.count(),
            'tiempo_promedio_ms': queryset.aggregate(avg=Avg('tiempo_respuesta_ms'))['avg'] or 0.0,
            'tiempo_minimo_ms': queryset.aggregate(min=Min('tiempo_respuesta_ms'))['min'] or 0,
            'tiempo_maximo_ms': queryset.aggregate(max=Max('tiempo_respuesta_ms'))['max'] or 0,
            'cpu_promedio': queryset.aggregate(avg=Avg('uso_cpu'))['avg'] or 0.0,
            'cpu_maximo': queryset.aggregate(max=Max('uso_cpu'))['max'] or 0.0,
            'ram_promedio_mb': queryset.aggregate(avg=Avg('uso_ram_mb'))['avg'] or 0.0,
            'ram_maximo_mb': queryset.aggregate(max=Max('uso_ram_mb'))['max'] or 0.0,
            'total_exitosos': queryset.filter(exito=True).count(),
            'total_errores': queryset.filter(exito=False).count(),
        }
    
    def obtener_estadisticas_generales(self, nivel_carga: int = None) -> Dict[str, Any]:
        """Obtiene estadísticas generales de todas las métricas"""
        queryset = self._get_optimized_queryset()
        if nivel_carga:
            queryset = queryset.filter(nivel_carga=nivel_carga)
        
        return {
            'total_mediciones': queryset.count(),
            'tiempo_promedio_ms': queryset.aggregate(avg=Avg('tiempo_respuesta_ms'))['avg'] or 0.0,
            'tiempo_minimo_ms': queryset.aggregate(min=Min('tiempo_respuesta_ms'))['min'] or 0,
            'tiempo_maximo_ms': queryset.aggregate(max=Max('tiempo_respuesta_ms'))['max'] or 0,
            'cpu_promedio': queryset.aggregate(avg=Avg('uso_cpu'))['avg'] or 0.0,
            'cpu_maximo': queryset.aggregate(max=Max('uso_cpu'))['max'] or 0.0,
            'ram_promedio_mb': queryset.aggregate(avg=Avg('uso_ram_mb'))['avg'] or 0.0,
            'ram_maximo_mb': queryset.aggregate(max=Max('uso_ram_mb'))['max'] or 0.0,
            'total_exitosos': queryset.filter(exito=True).count(),
            'total_errores': queryset.filter(exito=False).count(),
        }


class RegistroManualEnvioRepository(BaseRepository):
    """Repositorio para RegistroManualEnvio"""
    
    @property
    def model(self):
        return RegistroManualEnvio
    
    @property
    def select_related_fields(self) -> List[str]:
        return ['registrado_por']
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de registros manuales"""
        queryset = self._get_optimized_queryset()
        
        return {
            'total_registros': queryset.count(),
            'tiempo_promedio_segundos': queryset.aggregate(avg=Avg('tiempo_registro_segundos'))['avg'] or 0.0,
            'tiempo_minimo_segundos': queryset.aggregate(min=Min('tiempo_registro_segundos'))['min'] or 0.0,
            'tiempo_maximo_segundos': queryset.aggregate(max=Max('tiempo_registro_segundos'))['max'] or 0.0,
        }


# Instancias singleton de repositorios
prueba_controlada_repository = PruebaControladaSemanticaRepository()
metrica_semantica_repository = MetricaSemanticaRepository()
registro_embedding_repository = RegistroGeneracionEmbeddingRepository()
prueba_carga_repository = PruebaCargaRepository()
metrica_rendimiento_repository = MetricaRendimientoRepository()
registro_manual_repository = RegistroManualEnvioRepository()


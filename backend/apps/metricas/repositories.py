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

    def obtener_reporte_comparativo(self, fecha_desde=None, fecha_hasta=None) -> Dict[str, Any]:
        """
        Obtiene reporte comparativo de eficiencia del panel semántico.
        Incluye filas por evaluación e interpretación (MRR, NDCG@10, Precision@5).
        """
        from .utils import interpretar_metrica

        queryset = self.filtrar_por_fecha(fecha_desde, fecha_hasta).order_by('-fecha_calculo')
        stats = self.obtener_estadisticas(fecha_desde, fecha_hasta)

        filas = []
        for m in queryset:
            consulta_truncada = (m.consulta[:80] + '...') if m.consulta and len(m.consulta) > 80 else (m.consulta or '')
            filas.append({
                'id': m.id,
                'consulta': consulta_truncada,
                'consulta_completa': m.consulta,
                'fecha_calculo': m.fecha_calculo.isoformat() if m.fecha_calculo else None,
                'mrr': round(m.mrr, 4) if m.mrr is not None else None,
                'ndcg_10': round(m.ndcg_10, 4) if m.ndcg_10 is not None else None,
                'precision_5': round(m.precision_5, 4) if m.precision_5 is not None else None,
                'total_resultados': m.total_resultados,
                'total_relevantes_encontrados': m.total_relevantes_encontrados,
                'interpretacion_mrr': interpretar_metrica(m.mrr, 'mrr'),
                'interpretacion_ndcg': interpretar_metrica(m.ndcg_10, 'ndcg_10'),
                'interpretacion_precision': interpretar_metrica(m.precision_5, 'precision_5'),
            })

        # Interpretación global según promedios (media de las 3 métricas)
        mrr_avg = stats.get('mrr_promedio') or 0.0
        ndcg_avg = stats.get('ndcg_10_promedio') or 0.0
        prec_avg = stats.get('precision_5_promedio') or 0.0
        media = (mrr_avg + ndcg_avg + prec_avg) / 3.0 if stats['total_metricas'] else None
        if media is not None:
            if media >= 0.6:
                interpretacion_global = {'nivel': 'bueno', 'etiqueta': 'Eficiente', 'descripcion': 'El panel semántico tiene buena eficiencia global'}
            elif media >= 0.4:
                interpretacion_global = {'nivel': 'regular', 'etiqueta': 'Aceptable', 'descripcion': 'Eficiencia aceptable; hay margen de mejora'}
            else:
                interpretacion_global = {'nivel': 'mejorable', 'etiqueta': 'Mejorable', 'descripcion': 'Revisar consultas de prueba y relevancia del ranking'}
        else:
            interpretacion_global = {'nivel': 'sin_dato', 'etiqueta': '-', 'descripcion': 'Sin evaluaciones en el período'}

        return {
            'filas': filas,
            'resumen': {
                'total_evaluaciones': stats['total_metricas'],
                'mrr_promedio': round(mrr_avg, 4),
                'mrr_maximo': round(stats.get('mrr_maximo') or 0.0, 4),
                'mrr_minimo': round(stats.get('mrr_minimo') or 0.0, 4),
                'ndcg_10_promedio': round(ndcg_avg, 4),
                'precision_5_promedio': round(prec_avg, 4),
                'interpretacion_global': interpretacion_global,
            },
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


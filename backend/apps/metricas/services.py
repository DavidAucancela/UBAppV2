"""
Servicios para la app de métricas.
Implementa la lógica de negocio para cálculo y gestión de métricas experimentales.
"""
from typing import Dict, Any, List, Optional
import time
import logging
import psutil
import os
from django.db import transaction
from django.utils import timezone

from apps.core.base.base_service import BaseService
from apps.busqueda.services import BusquedaSemanticaService
from apps.busqueda.models import EmbeddingBusqueda
from apps.archivos.models import Envio
from .repositories import (
    prueba_controlada_repository,
    metrica_semantica_repository,
    registro_embedding_repository,
    prueba_carga_repository,
    metrica_rendimiento_repository,
    registro_manual_repository
)
from .utils import calcular_metricas_completas
from .models import (
    PruebaControladaSemantica,
    MetricaSemantica,
    RegistroGeneracionEmbedding,
    PruebaCarga,
    MetricaRendimiento,
    RegistroManualEnvio
)

logger = logging.getLogger(__name__)


class MetricaSemanticaService(BaseService):
    """Servicio para gestión de métricas semánticas"""
    
    @staticmethod
    def calcular_metricas_busqueda(
        busqueda_semantica: EmbeddingBusqueda,
        resultados_relevantes: List[int],
        logs_pipeline: Dict[str, Any] = None
    ) -> MetricaSemantica:
        """
        Calcula métricas semánticas (MRR, nDCG@10, Precision@5) para una búsqueda.
        
        Args:
            busqueda_semantica: Instancia de EmbeddingBusqueda
            resultados_relevantes: Lista de IDs de envíos relevantes
            logs_pipeline: Logs detallados del pipeline (opcional)
        
        Returns:
            MetricaSemantica: Instancia con métricas calculadas
        """
        tiempo_inicio = time.time()
        
        # Obtener resultados rankeados de la búsqueda
        resultados_json = busqueda_semantica.resultados_json or []
        
        # Calcular métricas
        metricas = calcular_metricas_completas(
            resultados_rankeados=resultados_json,
            resultados_relevantes=resultados_relevantes
        )
        
        tiempo_procesamiento = int((time.time() - tiempo_inicio) * 1000)
        
        # Crear registro de métrica
        metrica = metrica_semantica_repository.crear(
            busqueda_semantica=busqueda_semantica,
            consulta=busqueda_semantica.consulta,
            resultados_rankeados=resultados_json,
            mrr=metricas['mrr'],
            ndcg_10=metricas['ndcg_10'],
            precision_5=metricas['precision_5'],
            total_resultados=metricas['total_resultados'],
            total_relevantes_encontrados=metricas['total_relevantes_encontrados'],
            tiempo_procesamiento_ms=tiempo_procesamiento,
            logs_pipeline=logs_pipeline,
            modelo_embedding=busqueda_semantica.modelo_utilizado,
            metrica_ordenamiento='score_combinado'  # Por defecto
        )
        
        BaseService.log_info(
            f"Métricas semánticas calculadas: MRR={metricas['mrr']:.4f}, "
            f"nDCG@10={metricas['ndcg_10']:.4f}, Precision@5={metricas['precision_5']:.4f}",
            extra={'metrica_id': metrica.id, 'busqueda_id': busqueda_semantica.id}
        )
        
        return metrica
    
    @staticmethod
    def ejecutar_prueba_controlada(
        prueba: PruebaControladaSemantica,
        usuario,
        filtros: Dict[str, Any] = None,
        limite: int = 20
    ) -> MetricaSemantica:
        """
        Ejecuta una prueba controlada y calcula métricas.
        
        Args:
            prueba: Instancia de PruebaControladaSemantica
            usuario: Usuario que ejecuta la prueba
            filtros: Filtros adicionales para la búsqueda
            limite: Límite de resultados
        
        Returns:
            MetricaSemantica: Métricas calculadas
        """
        tiempo_inicio = time.time()
        
        # Ejecutar búsqueda semántica
        resultado_busqueda = BusquedaSemanticaService.buscar(
            consulta=prueba.consulta,
            usuario=usuario,
            filtros=filtros or {},
            limite=limite
        )
        
        # Obtener la búsqueda guardada
        busqueda_semantica = EmbeddingBusqueda.objects.get(id=resultado_busqueda['busquedaId'])
        
        # Calcular métricas
        metrica = MetricaSemanticaService.calcular_metricas_busqueda(
            busqueda_semantica=busqueda_semantica,
            resultados_relevantes=prueba.resultados_relevantes,
            logs_pipeline={
                'consulta': prueba.consulta,
                'filtros_aplicados': filtros,
                'limite': limite,
                'tiempo_busqueda_ms': resultado_busqueda['tiempoRespuesta']
            }
        )
        
        # Asociar con prueba controlada
        metrica.prueba_controlada = prueba
        metrica.save()
        
        # Marcar prueba como ejecutada
        prueba_controlada_repository.ejecutar_prueba(prueba.id)
        
        return metrica
    
    @staticmethod
    def obtener_estadisticas(fecha_desde=None, fecha_hasta=None) -> Dict[str, Any]:
        """Obtiene estadísticas agregadas de métricas semánticas"""
        return metrica_semantica_repository.obtener_estadisticas(fecha_desde, fecha_hasta)


class RegistroEmbeddingService(BaseService):
    """Servicio para registro de generación de embeddings"""
    
    @staticmethod
    def registrar_generacion(
        envio: Envio,
        estado: str,
        tiempo_generacion_ms: int,
        modelo_usado: str = 'text-embedding-3-small',
        tipo_proceso: str = 'automatico',
        mensaje_error: str = None,
        embedding=None
    ) -> RegistroGeneracionEmbedding:
        """
        Registra la generación de un embedding.
        
        Args:
            envio: Instancia del envío
            estado: Estado de la generación ('generado', 'error', 'omitido')
            tiempo_generacion_ms: Tiempo de generación en milisegundos
            modelo_usado: Modelo de embedding utilizado
            tipo_proceso: Tipo de proceso ('automatico', 'manual', 'masivo')
            mensaje_error: Mensaje de error si hubo fallo
            embedding: Instancia del embedding generado (opcional)
        
        Returns:
            RegistroGeneracionEmbedding: Registro creado
        """
        dimension = 1536  # Por defecto para text-embedding-3-small
        if modelo_usado == 'text-embedding-3-large':
            dimension = 3072
        
        registro = registro_embedding_repository.crear(
            envio=envio,
            estado=estado,
            dimension_embedding=dimension,
            tiempo_generacion_ms=tiempo_generacion_ms,
            modelo_usado=modelo_usado,
            tipo_proceso=tipo_proceso,
            mensaje_error=mensaje_error,
            embedding=embedding
        )
        
        BaseService.log_info(
            f"Registro de generación de embedding: {envio.hawb} - {estado}",
            extra={'registro_id': registro.id, 'envio_id': envio.id}
        )
        
        return registro
    
    @staticmethod
    def obtener_estadisticas() -> Dict[str, Any]:
        """Obtiene estadísticas de generación de embeddings"""
        return registro_embedding_repository.obtener_estadisticas_generacion()


class MetricaRendimientoService(BaseService):
    """Servicio para métricas de rendimiento y eficiencia"""
    
    @staticmethod
    def medir_recursos() -> Dict[str, float]:
        """
        Mide el uso actual de recursos del sistema.
        
        Returns:
            Dict con uso de CPU (%) y RAM (MB)
        """
        proceso = psutil.Process(os.getpid())
        
        # CPU: promedio en el último intervalo
        cpu_percent = proceso.cpu_percent(interval=0.1)
        
        # RAM: memoria usada en MB
        memoria_info = proceso.memory_info()
        ram_mb = memoria_info.rss / (1024 * 1024)  # Convertir bytes a MB
        
        return {
            'cpu': cpu_percent,
            'ram_mb': ram_mb
        }
    
    @staticmethod
    def registrar_metrica_rendimiento(
        proceso: str,
        tiempo_respuesta_ms: int,
        nivel_carga: int = None,
        exito: bool = True,
        detalles: Dict[str, Any] = None,
        prueba_carga: PruebaCarga = None
    ) -> MetricaRendimiento:
        """
        Registra una métrica de rendimiento individual.
        
        Args:
            proceso: Tipo de proceso
            tiempo_respuesta_ms: Tiempo de respuesta en milisegundos
            nivel_carga: Nivel de carga (1, 10, 30)
            exito: Si la operación fue exitosa
            detalles: Detalles adicionales
            prueba_carga: Prueba de carga asociada (opcional)
        
        Returns:
            MetricaRendimiento: Métrica registrada
        """
        recursos = MetricaRendimientoService.medir_recursos()
        
        metrica = metrica_rendimiento_repository.crear(
            prueba_carga=prueba_carga,
            proceso=proceso,
            tiempo_respuesta_ms=tiempo_respuesta_ms,
            uso_cpu=recursos['cpu'],
            uso_ram_mb=recursos['ram_mb'],
            nivel_carga=nivel_carga,
            exito=exito,
            detalles=detalles or {}
        )
        
        return metrica
    
    @staticmethod
    def ejecutar_prueba_carga_busqueda(
        nivel_carga: int,
        consultas: List[str],
        usuario,
        nombre_prueba: str = None
    ) -> PruebaCarga:
        """
        Ejecuta una prueba de carga de búsqueda semántica.
        
        Args:
            nivel_carga: Nivel de carga (1, 10, 30)
            consultas: Lista de consultas a ejecutar
            usuario: Usuario que ejecuta la prueba
            nombre_prueba: Nombre de la prueba (opcional)
        
        Returns:
            PruebaCarga: Prueba ejecutada con resultados agregados
        """
        tiempo_inicio_total = time.time()
        
        # Crear prueba de carga
        prueba = prueba_carga_repository.crear(
            nombre=nombre_prueba or f"Prueba Búsqueda Semántica - Carga {nivel_carga}",
            tipo_prueba='busqueda_semantica',
            nivel_carga=nivel_carga,
            ejecutado_por=usuario,
            datos_prueba={'consultas': consultas}
        )
        
        tiempos = []
        recursos_cpu = []
        recursos_ram = []
        exitosos = 0
        errores = 0
        
        # Ejecutar búsquedas secuencialmente
        for i, consulta in enumerate(consultas[:nivel_carga]):
            tiempo_inicio_busqueda = time.time()
            
            try:
                # Medir recursos antes
                recursos_antes = MetricaRendimientoService.medir_recursos()
                
                # Ejecutar búsqueda
                resultado = BusquedaSemanticaService.buscar(
                    consulta=consulta,
                    usuario=usuario,
                    limite=20
                )
                
                tiempo_busqueda = int((time.time() - tiempo_inicio_busqueda) * 1000)
                tiempos.append(tiempo_busqueda)
                
                # Medir recursos después
                recursos_despues = MetricaRendimientoService.medir_recursos()
                recursos_cpu.append((recursos_antes['cpu'] + recursos_despues['cpu']) / 2)
                recursos_ram.append((recursos_antes['ram_mb'] + recursos_despues['ram_mb']) / 2)
                
                # Registrar métrica individual
                MetricaRendimientoService.registrar_metrica_rendimiento(
                    proceso='busqueda_semantica',
                    tiempo_respuesta_ms=tiempo_busqueda,
                    nivel_carga=nivel_carga,
                    exito=True,
                    detalles={'consulta': consulta, 'resultados': resultado.get('totalEncontrados', 0)},
                    prueba_carga=prueba
                )
                
                exitosos += 1
                
            except Exception as e:
                tiempo_busqueda = int((time.time() - tiempo_inicio_busqueda) * 1000)
                tiempos.append(tiempo_busqueda)
                errores += 1
                
                MetricaRendimientoService.registrar_metrica_rendimiento(
                    proceso='busqueda_semantica',
                    tiempo_respuesta_ms=tiempo_busqueda,
                    nivel_carga=nivel_carga,
                    exito=False,
                    detalles={'consulta': consulta, 'error': str(e)},
                    prueba_carga=prueba
                )
                
                logger.error(f"Error en prueba de carga: {str(e)}", exc_info=True)
        
        # Calcular estadísticas agregadas
        tiempo_total = int((time.time() - tiempo_inicio_total) * 1000)
        
        prueba.tiempo_promedio_ms = sum(tiempos) / len(tiempos) if tiempos else 0.0
        prueba.tiempo_minimo_ms = min(tiempos) if tiempos else 0
        prueba.tiempo_maximo_ms = max(tiempos) if tiempos else 0
        prueba.cpu_promedio = sum(recursos_cpu) / len(recursos_cpu) if recursos_cpu else 0.0
        prueba.cpu_maximo = max(recursos_cpu) if recursos_cpu else 0.0
        prueba.ram_promedio_mb = sum(recursos_ram) / len(recursos_ram) if recursos_ram else 0.0
        prueba.ram_maximo_mb = max(recursos_ram) if recursos_ram else 0.0
        prueba.total_exitosos = exitosos
        prueba.total_errores = errores
        prueba.save()
        
        BaseService.log_info(
            f"Prueba de carga completada: {prueba.nombre} - "
            f"Tiempo promedio: {prueba.tiempo_promedio_ms:.2f}ms",
            extra={'prueba_id': prueba.id}
        )
        
        return prueba
    
    @staticmethod
    def registrar_envio_manual(
        hawb: str,
        tiempo_registro_segundos: float,
        usuario,
        datos_envio: Dict[str, Any] = None,
        notas: str = None
    ) -> RegistroManualEnvio:
        """
        Registra un tiempo de registro manual de envío.
        
        Args:
            hawb: Número de envío
            tiempo_registro_segundos: Tiempo medido con cronómetro
            usuario: Usuario que registra
            datos_envio: Datos del envío (opcional)
            notas: Notas adicionales (opcional)
        
        Returns:
            RegistroManualEnvio: Registro creado
        """
        registro = registro_manual_repository.crear(
            hawb=hawb,
            tiempo_registro_segundos=tiempo_registro_segundos,
            registrado_por=usuario,
            datos_envio=datos_envio,
            notas=notas
        )
        
        # También registrar como métrica de rendimiento
        MetricaRendimientoService.registrar_metrica_rendimiento(
            proceso='registro_envio_manual',
            tiempo_respuesta_ms=int(tiempo_registro_segundos * 1000),
            exito=True,
            detalles={'hawb': hawb, 'datos_envio': datos_envio}
        )
        
        return registro
    
    @staticmethod
    def obtener_estadisticas_rendimiento(proceso: str = None, nivel_carga: int = None) -> Dict[str, Any]:
        """Obtiene estadísticas de rendimiento"""
        if proceso:
            return metrica_rendimiento_repository.obtener_estadisticas_por_proceso(proceso, nivel_carga)
        return {}


class ExportacionMetricasService(BaseService):
    """Servicio para exportación de métricas a CSV"""
    
    @staticmethod
    def exportar_metricas_semanticas_csv(fecha_desde=None, fecha_hasta=None) -> str:
        """
        Exporta métricas semánticas a formato CSV.
        
        Returns:
            str: Contenido del CSV
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Encabezados
        writer.writerow([
            'ID', 'Fecha Cálculo', 'Consulta', 'MRR', 'nDCG@10', 'Precision@5',
            'Total Resultados', 'Relevantes Encontrados', 'Tiempo Procesamiento (ms)',
            'Modelo Embedding', 'Métrica Ordenamiento'
        ])
        
        # Datos
        metricas = metrica_semantica_repository.filtrar_por_fecha(fecha_desde, fecha_hasta)
        for metrica in metricas:
            writer.writerow([
                metrica.id,
                metrica.fecha_calculo.isoformat(),
                metrica.consulta[:100],  # Limitar longitud
                f"{metrica.mrr:.4f}" if metrica.mrr else '',
                f"{metrica.ndcg_10:.4f}" if metrica.ndcg_10 else '',
                f"{metrica.precision_5:.4f}" if metrica.precision_5 else '',
                metrica.total_resultados,
                metrica.total_relevantes_encontrados,
                metrica.tiempo_procesamiento_ms,
                metrica.modelo_embedding,
                metrica.metrica_ordenamiento
            ])
        
        return output.getvalue()
    
    @staticmethod
    def exportar_metricas_rendimiento_csv(fecha_desde=None, fecha_hasta=None) -> str:
        """
        Exporta métricas de rendimiento a formato CSV.
        
        Returns:
            str: Contenido del CSV
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Encabezados
        writer.writerow([
            'ID', 'Fecha Medición', 'Proceso', 'Tiempo Respuesta (ms)',
            'CPU (%)', 'RAM (MB)', 'Nivel Carga', 'Éxito'
        ])
        
        # Datos
        metricas = metrica_rendimiento_repository.listar()
        if fecha_desde:
            metricas = metricas.filter(fecha_medicion__gte=fecha_desde)
        if fecha_hasta:
            metricas = metricas.filter(fecha_medicion__lte=fecha_hasta)
        
        for metrica in metricas:
            writer.writerow([
                metrica.id,
                metrica.fecha_medicion.isoformat(),
                metrica.proceso,
                metrica.tiempo_respuesta_ms,
                f"{metrica.uso_cpu:.2f}",
                f"{metrica.uso_ram_mb:.2f}",
                metrica.nivel_carga or '',
                'Sí' if metrica.exito else 'No'
            ])
        
        return output.getvalue()


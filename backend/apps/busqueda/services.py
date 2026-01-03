"""
Servicios para la app de búsqueda
Implementa la lógica de negocio para búsquedas tradicionales y semánticas
"""
from typing import Dict, Any, List, Optional
import time
import logging
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.conf import settings

from apps.core.base.base_service import BaseService
from apps.core.exceptions import OpenAINotConfiguredError
from .repositories import (
    busqueda_tradicional_repository,
    embedding_busqueda_repository,
    historial_semantica_repository,
    embedding_repository
)
from .semantic import EmbeddingService, VectorSearchService, TextProcessor
from apps.archivos.repositories import envio_repository, producto_repository
from apps.usuarios.repositories import usuario_repository
from apps.archivos.serializers import EnvioSerializer

# Logger específico para búsqueda semántica con métricas detalladas
logger = logging.getLogger('apps.busqueda.semantic')

Usuario = get_user_model()

# Caché para búsquedas semánticas
def get_semantic_cache():
    """Obtiene el caché para búsquedas semánticas"""
    try:
        return caches['embeddings']
    except Exception:
        return caches['default']


class BusquedaTradicionalService(BaseService):
    """
    Servicio para búsquedas tradicionales (texto).
    """
    
    @staticmethod
    def buscar(
        query: str,
        tipo: str,
        usuario
    ) -> Dict[str, Any]:
        """
        Realiza una búsqueda tradicional en usuarios, envíos y productos.
        
        Args:
            query: Término de búsqueda
            tipo: Tipo de búsqueda ('general', 'usuarios', 'envios', 'productos')
            usuario: Usuario que realiza la búsqueda
            
        Returns:
            Dict con resultados de búsqueda
        """
        resultados = {}
        
        if tipo in ['general', 'usuarios']:
            usuarios = usuario_repository.buscar(query)
            # Filtrar por permisos
            usuarios = BusquedaTradicionalService._filtrar_usuarios_por_permisos(
                usuarios, usuario
            )
            from apps.usuarios.serializers import UsuarioListSerializer
            resultados['usuarios'] = UsuarioListSerializer(usuarios, many=True).data
        
        if tipo in ['general', 'envios']:
            envios = envio_repository.buscar(query, usuario)
            from apps.archivos.serializers import EnvioListSerializer
            resultados['envios'] = EnvioListSerializer(envios, many=True).data
        
        if tipo in ['general', 'productos']:
            productos = producto_repository.buscar(query, usuario)
            from apps.archivos.serializers import ProductoListSerializer
            resultados['productos'] = ProductoListSerializer(productos, many=True).data
        
        # Calcular total
        total_resultados = sum(len(resultados.get(key, [])) for key in resultados)
        
        # Guardar en historial
        busqueda_tradicional_repository.crear(
            usuario=usuario,
            termino_busqueda=query,
            tipo_busqueda=tipo,
            resultados_encontrados=total_resultados,
            resultados_json=resultados
        )
        
        # Log de la búsqueda
        from apps.core.base.base_service import BaseService
        BaseService.log_operacion(
            operacion='buscar',
            entidad='BusquedaTradicional',
            usuario_id=usuario.id,
            detalles={
                'query': query,
                'tipo': tipo,
                'total_resultados': total_resultados
            }
        )
        
        BaseService.log_metrica(
            metrica='busqueda_tradicional',
            valor=1,
            unidad='busqueda',
            usuario_id=usuario.id,
            contexto={'tipo': tipo, 'resultados': total_resultados}
        )
        
        return {
            'query': query,
            'tipo': tipo,
            'total_resultados': total_resultados,
            'resultados': resultados
        }
    
    @staticmethod
    def _filtrar_usuarios_por_permisos(usuarios, usuario_actual):
        """Filtra usuarios según permisos del usuario actual"""
        if usuario_actual.es_comprador:
            return usuarios.filter(id=usuario_actual.id)
        elif usuario_actual.es_digitador:
            return usuarios.filter(rol__in=[3, 4])
        elif usuario_actual.es_gerente:
            return usuarios.exclude(rol=1)
        return usuarios


class BusquedaSemanticaService(BaseService):
    """
    Servicio para búsquedas semánticas usando embeddings.
    Orquesta la generación de embeddings, búsqueda vectorial y formateo de resultados.
    """
    
    @staticmethod
    def buscar(
        consulta: str,
        usuario,
        filtros: Dict[str, Any] = None,
        limite: int = 20,
        modelo_embedding: str = None,
        metrica_ordenamiento: str = 'score_combinado'
    ) -> Dict[str, Any]:
        """
        Realiza una búsqueda semántica de envíos.
        
        Args:
            consulta: Texto de la consulta
            usuario: Usuario que realiza la búsqueda
            filtros: Filtros adicionales (fechaDesde, fechaHasta, estado, ciudadDestino)
            limite: Cantidad máxima de resultados
            modelo_embedding: Modelo de embedding a usar
            metrica_ordenamiento: Métrica para ordenar resultados. Opciones:
                - 'score_combinado' (default): Score combinado (recomendado)
                - 'cosine_similarity': Similitud coseno
                - 'dot_product': Producto punto
                - 'euclidean_distance': Distancia euclidiana (menor es mejor)
                - 'manhattan_distance': Distancia Manhattan (menor es mejor)
            
        Returns:
            Dict con resultados, métricas y costos
        """
        tiempo_inicio = time.time()
        
        # Validar modelo
        if modelo_embedding is None:
            modelo_embedding = EmbeddingService.get_modelo_default()
        else:
            modelo_embedding = EmbeddingService.validar_modelo(modelo_embedding)
        
        # 1. Obtener envíos filtrados
        envios_queryset = BusquedaSemanticaService._obtener_envios_filtrados(
            usuario, filtros or {}
        )
        
        # Procesar consulta: aplicar limpieza y normalización
        consulta_procesada = TextProcessor.procesar_texto(consulta)
        
        if envios_queryset.count() == 0:
            # Generar embedding para calcular costo incluso sin resultados
            try:
                embedding_resultado = EmbeddingService.generar_embedding(
                    consulta_procesada, modelo_embedding
                )
                costo = embedding_resultado['costo']
                tokens = embedding_resultado['tokens']
            except OpenAINotConfiguredError:
                costo = 0
                tokens = 0
            
            tiempo_respuesta = int((time.time() - tiempo_inicio) * 1000)
            
            # Guardar búsqueda (incluso sin resultados)
            # Guardar consulta original para el historial
            busqueda = embedding_busqueda_repository.crear(
                usuario=usuario,
                consulta=consulta,  # Consulta original sin procesar
                resultados_encontrados=0,
                tiempo_respuesta=tiempo_respuesta,
                filtros_aplicados=filtros,
                modelo_utilizado=modelo_embedding,
                costo_consulta=costo,
                tokens_utilizados=tokens,
                resultados_json=[]
            )
            
            # Guardar el embedding si se generó
            if 'embedding' in embedding_resultado:
                busqueda.set_vector(embedding_resultado['embedding'])
                busqueda.save()
            
            return {
                'consulta': consulta,  # Retornar consulta original
                'resultados': [],
                'totalEncontrados': 0,
                'tiempoRespuesta': tiempo_respuesta,
                'modeloUtilizado': modelo_embedding,
                'costoConsulta': float(costo),
                'tokensUtilizados': tokens,
                'busquedaId': busqueda.id
            }
        
        # 2. Generar embedding de la consulta (usando consulta procesada)
        embedding_resultado = EmbeddingService.generar_embedding(consulta_procesada, modelo_embedding)
        embedding_consulta = embedding_resultado['embedding']
        tokens_consulta = embedding_resultado['tokens']
        costo_consulta = embedding_resultado['costo']
        
        # 3. Buscar envíos similares (usar consulta procesada para comparaciones)
        resultados = BusquedaSemanticaService._buscar_envios_similares(
            envios_queryset,
            embedding_consulta,
            consulta_procesada,  # Usar consulta procesada
            limite,
            modelo_embedding,
            metrica_ordenamiento
        )
        
        # 4. Calcular tiempo de respuesta
        tiempo_respuesta = int((time.time() - tiempo_inicio) * 1000)
        
        # 5. Guardar en historial con embedding y resultados
        # Guardar consulta original para el historial
        busqueda = embedding_busqueda_repository.crear(
            usuario=usuario,
            consulta=consulta,  # Consulta original sin procesar
            resultados_encontrados=len(resultados),
            tiempo_respuesta=tiempo_respuesta,
            filtros_aplicados=filtros,
            modelo_utilizado=modelo_embedding,
            costo_consulta=costo_consulta,
            tokens_utilizados=tokens_consulta,
            resultados_json=resultados  # Guardar resultados para PDF
        )
        
        # Guardar el embedding de la consulta
        if embedding_consulta:
            busqueda.set_vector(embedding_consulta)
            busqueda.save()
        
        # Log detallado de la búsqueda semántica
        from apps.core.base.base_service import BaseService
        BaseService.log_operacion(
            operacion='buscar_semantica',
            entidad='BusquedaSemantica',
            usuario_id=usuario.id,
            detalles={
                'consulta': consulta[:100],  # Limitar longitud
                'resultados_encontrados': len(resultados),
                'tiempo_respuesta_ms': tiempo_respuesta,
                'modelo': modelo_embedding,
                'costo': float(costo_consulta),
                'tokens': tokens_consulta
            }
        )
        
        BaseService.log_metrica(
            metrica='busqueda_semantica_tiempo',
            valor=tiempo_respuesta,
            unidad='ms',
            usuario_id=usuario.id,
            contexto={'modelo': modelo_embedding, 'resultados': len(resultados)}
        )
        
        BaseService.log_metrica(
            metrica='busqueda_semantica_costo',
            valor=float(costo_consulta),
            unidad='USD',
            usuario_id=usuario.id,
            contexto={'modelo': modelo_embedding}
        )
        
        return {
            'consulta': consulta,
            'resultados': resultados,
            'totalEncontrados': len(resultados),
            'tiempoRespuesta': tiempo_respuesta,
            'modeloUtilizado': modelo_embedding,
            'costoConsulta': float(costo_consulta),
            'tokensUtilizados': tokens_consulta,
            'busquedaId': busqueda.id,
            'metricaOrdenamiento': metrica_ordenamiento or 'score_combinado'
        }
    
    @staticmethod
    def _obtener_envios_filtrados(usuario, filtros: Dict) -> Any:
        """Obtiene envíos filtrados según permisos y criterios adicionales"""
        return envio_repository.filtrar_por_criterios_multiples(
            usuario=usuario,
            estado=filtros.get('estado'),
            fecha_desde=filtros.get('fechaDesde'),
            fecha_hasta=filtros.get('fechaHasta'),
            ciudad_destino=filtros.get('ciudadDestino')
        )
    
    @staticmethod
    def _buscar_envios_similares(
        envios_queryset,
        embedding_consulta: List[float],
        texto_consulta: str,
        limite: int,
        modelo_embedding: str,
        metrica_ordenamiento: str = 'score_combinado'
    ) -> List[Dict]:
        """
        Busca envíos similares usando búsqueda vectorial.
        OPTIMIZADO: Solo usa embeddings existentes, no genera en tiempo real.
        """
        tiempo_inicio_busqueda = time.time()
        
        # LIMITAR envíos a procesar para mejorar rendimiento
        # Aumentado a 300 para mejor cobertura (mejora para productos)
        MAX_ENVIOS_A_PROCESAR = 300
        
        # Limitar el queryset antes de procesar
        envios_limitados = envios_queryset[:MAX_ENVIOS_A_PROCESAR]
        total_envios_disponibles = envios_queryset.count()
        
        logger.info(
            f"Búsqueda semántica iniciada: consulta='{texto_consulta[:50]}...', "
            f"envios_disponibles={total_envios_disponibles}, limite={limite}"
        )
        
        # Obtener embeddings de envíos EXISTENTES únicamente
        # No generar embeddings en tiempo real para evitar demoras
        try:
            embeddings_envios = embedding_repository.obtener_embeddings_para_busqueda(
                envios_limitados,
                modelo=modelo_embedding,
                limite=MAX_ENVIOS_A_PROCESAR
            )
        except Exception as e:
            logger.error(
                f"Error al obtener embeddings: {str(e)}", 
                exc_info=True,
                extra={
                    'consulta': texto_consulta[:100],
                    'modelo': modelo_embedding,
                    'total_envios': total_envios_disponibles
                }
            )
            raise
        
        # OPTIMIZACIÓN: No generar embeddings faltantes en tiempo real
        # Esto evita llamadas a API que causan demoras de 10+ minutos
        # Los embeddings deben generarse previamente con el comando de gestión
        
        if not embeddings_envios:
            logger.warning(
                f"No se encontraron embeddings para la búsqueda. "
                f"Modelo: {modelo_embedding}, Envíos disponibles: {total_envios_disponibles}. "
                f"Ejecute 'python manage.py generar_embeddings' para generarlos."
            )
            BaseService.log_info(
                f"No se encontraron embeddings existentes. "
                f"Ejecute 'python manage.py generar_embeddings' para generarlos."
            )
            return []
        
        logger.debug(f"Embeddings encontrados: {len(embeddings_envios)} de {total_envios_disponibles} envíos")
        
        # Obtener textos indexados en batch
        envio_ids = [e[0] for e in embeddings_envios]
        textos_indexados = embedding_repository.obtener_textos_indexados(envio_ids)
        
        # Calcular similitudes
        vector_search = VectorSearchService()
        resultados_similitud = vector_search.calcular_similitudes(
            embedding_consulta,
            embeddings_envios,
            texto_consulta=texto_consulta,
            textos_indexados=textos_indexados
        )
        
        # Aplicar umbral y ordenar (MEJORADO para productos)
        # Detectar si es consulta sobre productos para usar umbral más bajo
        es_consulta_productos = BusquedaSemanticaService._es_consulta_productos(texto_consulta)
        
        # Umbral más bajo para consultas de productos (0.30 vs 0.35)
        # Esto permite encontrar más resultados relevantes para productos
        umbral_base = 0.30 if es_consulta_productos else 0.35
        
        resultados_filtrados = vector_search.aplicar_umbral(
            resultados_similitud,
            umbral_base=umbral_base,
            usar_adaptativo=True
        )
        
        # Validar métrica de ordenamiento
        metricas_validas = [
            'score_combinado', 'cosine_similarity', 'dot_product',
            'euclidean_distance', 'manhattan_distance'
        ]
        if metrica_ordenamiento not in metricas_validas:
            metrica_ordenamiento = 'score_combinado'
        
        resultados_ordenados = vector_search.ordenar_por_metrica(
            resultados_filtrados,
            metrica=metrica_ordenamiento,
            limite=limite
        )
        
        # Formatear resultados
        resultados_formateados = BusquedaSemanticaService._formatear_resultados(
            resultados_ordenados,
            texto_consulta,
            textos_indexados
        )
        
        # Log métricas de rendimiento
        tiempo_total_busqueda = (time.time() - tiempo_inicio_busqueda) * 1000
        logger.info(
            f"Búsqueda semántica completada: "
            f"tiempo={tiempo_total_busqueda:.2f}ms, "
            f"resultados_similitud={len(resultados_similitud)}, "
            f"resultados_filtrados={len(resultados_filtrados)}, "
            f"resultados_finales={len(resultados_formateados)}"
        )
        
        # Log detallado si hay pocos resultados
        if len(resultados_formateados) < 3 and len(embeddings_envios) > 10:
            logger.warning(
                f"Pocos resultados para consulta '{texto_consulta[:50]}': "
                f"{len(resultados_formateados)} de {len(embeddings_envios)} embeddings. "
                f"Umbral: {umbral_base}, Es consulta productos: {es_consulta_productos}"
            )
        
        return resultados_formateados
    
    @staticmethod
    def _formatear_resultados(
        resultados: List[Dict],
        texto_consulta: str,
        textos_indexados: Dict[int, str]
    ) -> List[Dict]:
        """Formatea resultados para el frontend"""
        resultados_finales = []
        
        for resultado in resultados:
            envio = resultado['envio']
            texto_indexado = textos_indexados.get(envio.id, "")
            
            # Extraer fragmentos relevantes
            fragmentos = TextProcessor.extraer_fragmentos(texto_consulta, texto_indexado)
            
            # Generar razón de relevancia
            razon = TextProcessor.generar_razon_relevancia(
                texto_consulta, envio, resultado['score_combinado']
            )
            
            # Serializar envío
            envio_data = EnvioSerializer(envio).data
            
            # Obtener dot_product real (puede ser igual a cosine si los vectores están normalizados)
            dot_product = resultado.get('dot_product', 0)
            norma_envio = resultado.get('norma_envio', 1.0)
            norma_consulta = resultado.get('norma_consulta', 1.0)
            
            # Si los vectores están normalizados (norma ≈ 1), dot_product ≈ cosine
            # Mostrar ambos valores para claridad
            dot_product_real = dot_product  # Valor real del producto punto
            
            resultados_finales.append({
                'envio': envio_data,
                'puntuacionSimilitud': round(resultado['score_combinado'], 4),
                'cosineSimilarity': round(resultado['cosine_similarity'], 4),
                'dotProduct': round(dot_product_real, 4),
                'euclideanDistance': round(resultado['euclidean_distance'], 4),
                'manhattanDistance': round(resultado['manhattan_distance'], 4),
                'scoreCombinado': round(resultado['score_combinado'], 4),
                'boostExactas': round(resultado.get('boost_exactas', 0), 4),
                'fragmentosRelevantes': fragmentos,
                'razonRelevancia': razon,
                'textoIndexado': texto_indexado[:200] + "..." if len(texto_indexado) > 200 else texto_indexado,
                # Información adicional para análisis
                'normaEnvio': round(norma_envio, 4),
                'normaConsulta': round(norma_consulta, 4)
            })
        
        return resultados_finales
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    @staticmethod
    def generar_embedding_envio(envio, modelo: str = None):
        """Genera embedding para un envío (delegado a EmbeddingService)"""
        return EmbeddingService.generar_embedding_envio(envio, modelo)
    
    @staticmethod
    def obtener_sugerencias(query: str = None, limite: int = 10) -> List[Dict]:
        """Obtiene sugerencias para búsqueda semántica"""
        sugerencias = historial_semantica_repository.obtener_activas(query, limite)
        from .serializers import HistorialSemanticaSerializer
        return HistorialSemanticaSerializer(sugerencias, many=True).data
    
    @staticmethod
    def obtener_historial(usuario, limite: int = 10) -> List[Dict]:
        """Obtiene historial de búsquedas semánticas del usuario"""
        historial = embedding_busqueda_repository.filtrar_por_usuario(usuario, limite)
        
        # Formatear para frontend
        datos_formateados = []
        for item in historial:
            costo_consulta = item.costo_consulta
            if costo_consulta is None:
                costo_consulta = 0.0
            else:
                try:
                    costo_consulta = float(costo_consulta)
                except (ValueError, TypeError):
                    costo_consulta = 0.0
            
            datos_formateados.append({
                'id': item.id,
                'consulta': item.consulta,
                'fecha': item.fecha_busqueda.isoformat(),
                'totalResultados': item.resultados_encontrados,
                'tiempoRespuesta': item.tiempo_respuesta,
                'modeloUtilizado': item.modelo_utilizado,
                'costoConsulta': costo_consulta,
                'tokensUtilizados': item.tokens_utilizados,
                'filtrosAplicados': item.filtros_aplicados
            })
        
        return datos_formateados
    
    @staticmethod
    def limpiar_historial(usuario) -> int:
        """Limpia el historial semántico del usuario"""
        return embedding_busqueda_repository.limpiar_historial_usuario(usuario)
    
    
    @staticmethod
    def obtener_metricas(usuario) -> Dict[str, Any]:
        """Obtiene métricas de búsquedas semánticas"""
        metricas_busqueda = embedding_busqueda_repository.obtener_metricas(usuario)
        
        return {
            'totalBusquedas': metricas_busqueda['total_busquedas'],
            'tiempoPromedioRespuesta': round(metricas_busqueda['tiempo_promedio_respuesta'], 2),
            'totalEmbeddings': embedding_repository.contar_embeddings()
        }
    
    @staticmethod
    def _es_consulta_productos(texto_consulta: str) -> bool:
        """
        Detecta si una consulta es sobre productos.
        Reutiliza la lógica del VectorSearchService.
        
        Args:
            texto_consulta: Texto de la consulta
            
        Returns:
            bool: True si es consulta sobre productos
        """
        from .semantic.vector_search import VectorSearchService
        return VectorSearchService._es_consulta_productos(texto_consulta)


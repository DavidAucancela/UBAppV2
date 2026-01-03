"""
Vector Search Service - Servicio de búsqueda vectorial
"""
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
import numpy as np

from apps.core.base.base_service import BaseService


# ==================== ESTRATEGIAS DE SIMILITUD ====================

class SimilarityStrategy(ABC):
    """Estrategia base para cálculo de similitud"""
    
    @abstractmethod
    def calcular(
        self,
        embedding_consulta: List[float],
        embedding_envio: List[float]
    ) -> float:
        """Calcula similitud entre dos embeddings"""
        pass
    
    @property
    @abstractmethod
    def nombre(self) -> str:
        """Nombre de la estrategia"""
        pass
    
    @property
    def es_distancia(self) -> bool:
        """True si menor es mejor, False si mayor es mejor"""
        return False


class CosineSimilarityStrategy(SimilarityStrategy):
    """Estrategia de similitud coseno (mayor es mejor)"""
    
    def calcular(
        self,
        embedding_consulta: List[float],
        embedding_envio: List[float]
    ) -> float:
        vec1 = np.array(embedding_consulta)
        vec2 = np.array(embedding_envio)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    @property
    def nombre(self) -> str:
        return "cosine_similarity"


class EuclideanDistanceStrategy(SimilarityStrategy):
    """Estrategia de distancia euclidiana (menor es mejor)"""
    
    def calcular(
        self,
        embedding_consulta: List[float],
        embedding_envio: List[float]
    ) -> float:
        vec1 = np.array(embedding_consulta)
        vec2 = np.array(embedding_envio)
        
        return float(np.linalg.norm(vec1 - vec2))
    
    @property
    def nombre(self) -> str:
        return "euclidean_distance"
    
    @property
    def es_distancia(self) -> bool:
        return True


class ManhattanDistanceStrategy(SimilarityStrategy):
    """Estrategia de distancia Manhattan (menor es mejor)"""
    
    def calcular(
        self,
        embedding_consulta: List[float],
        embedding_envio: List[float]
    ) -> float:
        vec1 = np.array(embedding_consulta)
        vec2 = np.array(embedding_envio)
        
        return float(np.sum(np.abs(vec1 - vec2)))
    
    @property
    def nombre(self) -> str:
        return "manhattan_distance"
    
    @property
    def es_distancia(self) -> bool:
        return True


class DotProductStrategy(SimilarityStrategy):
    """Estrategia de producto punto (mayor es mejor)"""
    
    def calcular(
        self,
        embedding_consulta: List[float],
        embedding_envio: List[float]
    ) -> float:
        vec1 = np.array(embedding_consulta)
        vec2 = np.array(embedding_envio)
        
        return float(np.dot(vec1, vec2))
    
    @property
    def nombre(self) -> str:
        return "dot_product"


# ==================== SERVICIO DE BÚSQUEDA ====================

class VectorSearchService(BaseService):
    """
    Servicio de búsqueda vectorial con múltiples métricas de similitud.
    """
    
    def __init__(self, estrategia: SimilarityStrategy = None):
        """
        Inicializa el servicio con una estrategia de similitud.
        
        Args:
            estrategia: Estrategia de similitud (por defecto: cosine)
        """
        self.estrategia = estrategia or CosineSimilarityStrategy()
    
    def cambiar_estrategia(self, estrategia: SimilarityStrategy):
        """Cambia la estrategia de similitud"""
        self.estrategia = estrategia
    
    def calcular_similitudes(
        self,
        embedding_consulta: List[float],
        embeddings_envios: List[Tuple],
        texto_consulta: str = "",
        textos_indexados: Dict[int, str] = None
    ) -> List[Dict]:
        """
        Calcula múltiples métricas de similitud entre la consulta y los embeddings.
        OPTIMIZADO: Usa operaciones vectorizadas de NumPy para máximo rendimiento.
        
        Args:
            embedding_consulta: Vector de la consulta
            embeddings_envios: Lista de tuplas (envio_id, vector_embedding, envio_obj)
            texto_consulta: Texto de la consulta original (opcional, para boost)
            textos_indexados: Diccionario {envio_id: texto_indexado} (opcional)
        
        Returns:
            List[Dict]: Lista de resultados con métricas de similitud
        """
        if not embeddings_envios:
            return []
        
        # ==================== VECTORIZACIÓN MASIVA ====================
        # Extraer datos en listas separadas para procesamiento batch
        envio_ids = []
        envio_objs = []
        vectores_envios = []
        
        for envio_id, vector_envio, envio_obj in embeddings_envios:
            envio_ids.append(envio_id)
            envio_objs.append(envio_obj)
            vectores_envios.append(vector_envio)
        
        # Convertir a matrices NumPy de una sola vez (MUCHO más rápido)
        consulta_vec = np.array(embedding_consulta, dtype=np.float32)
        matriz_envios = np.array(vectores_envios, dtype=np.float32)
        
        # Pre-calcular norma de consulta (una sola vez)
        consulta_norm = np.linalg.norm(consulta_vec)
        
        # ==================== CÁLCULOS VECTORIZADOS ====================
        # Todas las operaciones se realizan en paralelo sobre la matriz completa
        
        # 1. Normas de todos los envíos (vectorizado)
        normas_envios = np.linalg.norm(matriz_envios, axis=1)
        
        # 2. Productos punto de todos los envíos con la consulta (vectorizado)
        dot_products = np.dot(matriz_envios, consulta_vec)
        
        # 3. Similitud Coseno vectorizada
        # Evitar división por cero
        denominadores = normas_envios * consulta_norm
        denominadores = np.where(denominadores == 0, 1e-10, denominadores)
        cosine_similarities = dot_products / denominadores
        
        # 4. Distancia Euclidiana vectorizada
        diferencias = matriz_envios - consulta_vec
        euclidean_distances = np.linalg.norm(diferencias, axis=1)
        
        # 5. Distancia Manhattan vectorizada
        manhattan_distances = np.sum(np.abs(diferencias), axis=1)
        
        # ==================== BOOST POR TEXTO (OPTIMIZADO) ====================
        # Pre-calcular boost para productos una sola vez
        es_consulta_productos = VectorSearchService._es_consulta_productos(texto_consulta) if texto_consulta else False
        boost_base = 0.25 if es_consulta_productos else 0.15
        
        # Pre-procesar consulta para coincidencias
        consulta_lower = texto_consulta.lower() if texto_consulta else ""
        palabras_consulta = set(consulta_lower.split()) if consulta_lower else set()
        
        # Palabras clave para boost de productos (pre-procesado)
        palabras_producto = {'producto', 'artículo', 'item', 'mercancía', 'bien'}
        tiene_palabras_producto = bool(palabras_consulta & palabras_producto) if es_consulta_productos else False
        
        # Palabras clave filtradas (pre-procesado)
        palabras_clave = [
            p for p in palabras_consulta 
            if len(p) > 3 and p not in {'producto', 'productos', 'artículo', 'artículos'}
        ] if tiene_palabras_producto else []
        
        # ==================== CONSTRUIR RESULTADOS ====================
        resultados = []
        
        for i in range(len(envio_ids)):
            envio_id = envio_ids[i]
            
            # Obtener métricas pre-calculadas (acceso directo, sin cálculo)
            cosine_similarity = float(cosine_similarities[i])
            dot_product = float(dot_products[i])
            euclidean_distance = float(euclidean_distances[i])
            manhattan_distance = float(manhattan_distances[i])
            
            # Calcular boost (optimizado: sin regex, lógica simplificada)
            boost_exactas = 0.0
            coincidencias_score = 0.0
            boost_productos = 0.0
            
            if texto_consulta and textos_indexados and envio_id in textos_indexados:
                texto_indexado = textos_indexados[envio_id].lower()
                
                # Coincidencias exactas simplificadas (sin regex)
                palabras_texto = set(texto_indexado.split())
                palabras_comunes = palabras_consulta & palabras_texto
                if palabras_consulta:
                    coincidencias_score = len(palabras_comunes) / len(palabras_consulta)
                
                # Boost para productos
                if tiene_palabras_producto:
                    if 'producto:' in texto_indexado or 'contiene:' in texto_indexado:
                        for palabra_clave in palabras_clave:
                            if palabra_clave in texto_indexado:
                                boost_productos = 0.05
                                break
                
                boost_exactas = coincidencias_score * boost_base + min(boost_productos, 0.10)
            
            # Score combinado
            cosine_normalizado = (cosine_similarity + 1) / 2
            score_combinado = min(cosine_normalizado + boost_exactas, 1.0)
            
            # Calcular normas para información adicional
            norma_envio = float(normas_envios[i])
            norma_consulta = float(consulta_norm)
            
            resultados.append({
                'envio_id': envio_id,
                'envio': envio_objs[i],
                'cosine_similarity': cosine_similarity,
                'dot_product': dot_product,
                'euclidean_distance': euclidean_distance,
                'manhattan_distance': manhattan_distance,
                'score_combinado': score_combinado,
                'boost_exactas': boost_exactas,
                'boost_productos': boost_productos,
                'coincidencias_exactas': coincidencias_score,
                # Información adicional para debugging/visualización
                'norma_envio': norma_envio,
                'norma_consulta': norma_consulta,
                'dot_product_normalizado': dot_product / (norma_envio * norma_consulta) if norma_envio > 0 and norma_consulta > 0 else 0.0
            })
        
        return resultados
    
    def ordenar_por_metrica(
        self,
        resultados: List[Dict],
        metrica: str = 'score_combinado',
        limite: int = 20
    ) -> List[Dict]:
        """
        Ordena resultados por la métrica especificada.
        
        Args:
            resultados: Lista de resultados con métricas
            metrica: Métrica a usar para ordenar
            limite: Cantidad máxima de resultados
        
        Returns:
            List[Dict]: Resultados ordenados y limitados
        """
        # Métricas donde mayor es mejor
        metricas_descendentes = ['cosine_similarity', 'dot_product', 'score_combinado']
        # Métricas donde menor es mejor
        metricas_ascendentes = ['euclidean_distance', 'manhattan_distance']
        
        if metrica in metricas_descendentes:
            resultados_ordenados = sorted(
                resultados,
                key=lambda x: x.get(metrica, 0),
                reverse=True
            )
        elif metrica in metricas_ascendentes:
            resultados_ordenados = sorted(
                resultados,
                key=lambda x: x.get(metrica, float('inf'))
            )
        else:
            # Por defecto usar score_combinado
            resultados_ordenados = sorted(
                resultados,
                key=lambda x: x.get('score_combinado', 0),
                reverse=True
            )
        
        return resultados_ordenados[:limite]
    
    def aplicar_umbral(
        self,
        resultados: List[Dict],
        umbral_base: float = 0.35,
        usar_adaptativo: bool = True
    ) -> List[Dict]:
        """
        Filtra resultados según umbral de similitud.
        
        Args:
            resultados: Lista de resultados con métricas
            umbral_base: Umbral mínimo absoluto
            usar_adaptativo: Si True, usa umbral adaptativo
        
        Returns:
            List[Dict]: Resultados filtrados
        """
        if not resultados:
            return []
        
        # Calcular umbral adaptativo si corresponde
        if usar_adaptativo and len(resultados) > 3:
            scores = [
                max(r.get('cosine_similarity', 0), r.get('score_combinado', 0))
                for r in resultados
            ]
            scores_ordenados = sorted(scores, reverse=True)
            
            # Usar percentil 75 como umbral adaptativo
            indice_percentil = max(0, int(len(scores_ordenados) * 0.25))
            if indice_percentil < len(scores_ordenados):
                umbral_adaptativo = max(scores_ordenados[indice_percentil], umbral_base)
            else:
                umbral_adaptativo = umbral_base
        else:
            umbral_adaptativo = umbral_base
        
        # Filtrar resultados
        resultados_filtrados = []
        for resultado in resultados:
            score = resultado.get('cosine_similarity', 0)
            score_combinado = resultado.get('score_combinado', score)
            score_final = max(score, score_combinado)
            
            if score_final >= umbral_adaptativo:
                resultados_filtrados.append(resultado)
        
        return resultados_filtrados
    
    @staticmethod
    def _es_consulta_productos(texto_consulta: str) -> bool:
        """
        Detecta si una consulta es sobre productos.
        
        Args:
            texto_consulta: Texto de la consulta
            
        Returns:
            bool: True si es consulta sobre productos
        """
        if not texto_consulta:
            return False
        
        texto_lower = texto_consulta.lower()
        
        # Palabras clave que indican consulta sobre productos
        palabras_clave_productos = [
            'producto', 'productos', 'artículo', 'artículos', 'item', 'items',
            'mercancía', 'mercancías', 'bien', 'bienes', 'contenido',
            'laptop', 'smartphone', 'tablet', 'computadora', 'celular',
            'ropa', 'vestimenta', 'prendas', 'camiseta', 'pantalón', 'zapatos',
            'electrónica', 'electrónicos', 'tecnología', 'dispositivos',
            'hogar', 'muebles', 'decoración', 'utensilios',
            'deportes', 'deportivo', 'fitness', 'equipamiento',
            'categoría', 'categorías', 'tipo de producto'
        ]
        
        # Verificar si contiene palabras clave de productos
        for palabra in palabras_clave_productos:
            if palabra in texto_lower:
                return True
        
        # Verificar patrones de preguntas sobre productos
        patrones_preguntas = [
            'qué productos', 'qué artículos', 'qué contiene',
            'muéstrame productos', 'muéstrame artículos',
            'envíos con productos', 'envíos que contienen'
        ]
        
        for patron in patrones_preguntas:
            if patron in texto_lower:
                return True
        
        return False


# Instancia singleton para uso directo
vector_search_service = VectorSearchService()


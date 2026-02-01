"""
Utilidades para cálculo de métricas de evaluación de búsqueda semántica.
Implementa MRR, nDCG@10 y Precision@5 según estándares de Information Retrieval.
"""
from typing import List, Dict, Any
import math
import logging

logger = logging.getLogger(__name__)


def calcular_mrr(resultados_rankeados: List[Dict], resultados_relevantes: List[int]) -> float:
    """
    Calcula Mean Reciprocal Rank (MRR).
    
    MRR = 1 / posición_del_primer_relevante
    Si no hay resultados relevantes, MRR = 0
    
    Args:
        resultados_rankeados: Lista de resultados ordenados con campo 'envio_id'
        resultados_relevantes: Lista de IDs de envíos que son relevantes
    
    Returns:
        float: Valor de MRR entre 0.0 y 1.0
    """
    if not resultados_rankeados or not resultados_relevantes:
        return 0.0
    
    # Buscar la posición del primer resultado relevante (1-indexed)
    for posicion, resultado in enumerate(resultados_rankeados, start=1):
        envio_id = resultado.get('envio_id') or resultado.get('envio', {}).get('id')
        if envio_id and envio_id in resultados_relevantes:
            return 1.0 / posicion
    
    # No se encontró ningún resultado relevante
    return 0.0


def calcular_ndcg_k(
    resultados_rankeados: List[Dict],
    resultados_relevantes: List[int],
    k: int = 10,
    niveles_relevancia: Dict[int, float] = None
) -> float:
    """
    Calcula Normalized Discounted Cumulative Gain@K (nDCG@K).
    
    DCG@K = Σ(i=1 to K) (relevancia_i / log2(i+1))
    nDCG@K = DCG@K / IDCG@K
    
    Args:
        resultados_rankeados: Lista de resultados ordenados con campo 'envio_id'
        resultados_relevantes: Lista de IDs de envíos relevantes
        k: Número de resultados a considerar (default: 10)
        niveles_relevancia: Dict con niveles de relevancia por ID (opcional)
                          Si no se proporciona, usa relevancia binaria (1 o 0)
    
    Returns:
        float: Valor de nDCG@K entre 0.0 y 1.0
    """
    if not resultados_rankeados or not resultados_relevantes:
        return 0.0
    
    # Función para obtener relevancia
    def obtener_relevancia(envio_id: int) -> float:
        if envio_id not in resultados_relevantes:
            return 0.0
        if niveles_relevancia and envio_id in niveles_relevancia:
            return niveles_relevancia[envio_id]
        return 1.0  # Relevancia binaria
    
    # Calcular DCG@K
    dcg = 0.0
    resultados_k = resultados_rankeados[:k]
    
    for posicion, resultado in enumerate(resultados_k, start=1):
        envio_id = resultado.get('envio_id') or resultado.get('envio', {}).get('id')
        if envio_id:
            relevancia = obtener_relevancia(envio_id)
            if relevancia > 0:
                # log2(posicion + 1) para el discount
                dcg += relevancia / math.log2(posicion + 1)
    
    # Calcular IDCG@K (DCG ideal)
    # Ordenar resultados relevantes por relevancia descendente
    niveles = niveles_relevancia or {}
    relevancias_ideales = []
    for envio_id in resultados_relevantes:
        relevancia = niveles.get(envio_id, 1.0)
        relevancias_ideales.append(relevancia)
    
    relevancias_ideales.sort(reverse=True)
    relevancias_ideales = relevancias_ideales[:k]
    
    idcg = 0.0
    for posicion, relevancia in enumerate(relevancias_ideales, start=1):
        if relevancia > 0:
            idcg += relevancia / math.log2(posicion + 1)
    
    # Calcular nDCG
    if idcg == 0.0:
        return 0.0
    
    return dcg / idcg


def calcular_precision_k(
    resultados_rankeados: List[Dict],
    resultados_relevantes: List[int],
    k: int = 5
) -> float:
    """
    Calcula Precision@K.
    
    Precision@K = (Resultados Relevantes en top K) / K
    
    Args:
        resultados_rankeados: Lista de resultados ordenados con campo 'envio_id'
        resultados_relevantes: Lista de IDs de envíos relevantes
        k: Número de resultados a considerar (default: 5)
    
    Returns:
        float: Valor de Precision@K entre 0.0 y 1.0
    """
    if not resultados_rankeados or not resultados_relevantes:
        return 0.0
    
    resultados_k = resultados_rankeados[:k]
    relevantes_encontrados = 0
    
    for resultado in resultados_k:
        envio_id = resultado.get('envio_id') or resultado.get('envio', {}).get('id')
        if envio_id and envio_id in resultados_relevantes:
            relevantes_encontrados += 1
    
    return relevantes_encontrados / k if k > 0 else 0.0


def interpretar_metrica(valor: float, metrica: str) -> Dict[str, Any]:
    """
    Interpreta un valor de métrica para el reporte comparativo.
    Umbrales según documentación: MRR>0.7 bueno, NDCG>0.6 bueno, Precision@5>0.5 bueno.
    
    Returns:
        Dict con 'nivel' ('bueno'|'regular'|'mejorable'), 'etiqueta', 'descripcion'
    """
    if valor is None:
        return {'nivel': 'sin_dato', 'etiqueta': '-', 'descripcion': 'Sin datos'}
    umbrales = {
        'mrr': (0.7, 0.4),      # (bueno, regular)
        'ndcg_10': (0.6, 0.4),
        'precision_5': (0.5, 0.3),
    }
    bueno, regular = umbrales.get(metrica, (0.5, 0.3))
    if valor >= bueno:
        return {'nivel': 'bueno', 'etiqueta': 'Bueno', 'descripcion': 'Eficiencia adecuada'}
    if valor >= regular:
        return {'nivel': 'regular', 'etiqueta': 'Regular', 'descripcion': 'Hay margen de mejora'}
    return {'nivel': 'mejorable', 'etiqueta': 'Mejorable', 'descripcion': 'Revisar ranking o relevancia'}


def calcular_metricas_completas(
    resultados_rankeados: List[Dict],
    resultados_relevantes: List[int],
    niveles_relevancia: Dict[int, float] = None
) -> Dict[str, float]:
    """
    Calcula todas las métricas de evaluación de una vez.
    
    Args:
        resultados_rankeados: Lista de resultados ordenados
        resultados_relevantes: Lista de IDs relevantes
        niveles_relevancia: Dict con niveles de relevancia (opcional)
    
    Returns:
        Dict con todas las métricas calculadas
    """
    return {
        'mrr': calcular_mrr(resultados_rankeados, resultados_relevantes),
        'ndcg_10': calcular_ndcg_k(resultados_rankeados, resultados_relevantes, k=10, niveles_relevancia=niveles_relevancia),
        'precision_5': calcular_precision_k(resultados_rankeados, resultados_relevantes, k=5),
        'total_resultados': len(resultados_rankeados),
        'total_relevantes_encontrados': sum(
            1 for r in resultados_rankeados
            if (r.get('envio_id') or r.get('envio', {}).get('id')) in resultados_relevantes
        ),
    }


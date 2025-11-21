"""
Utilidades para generación y gestión de embeddings con OpenAI
"""
from django.conf import settings
from openai import OpenAI
import numpy as np
from typing import Dict, List, Any, Tuple
from .models import EnvioEmbedding


def get_openai_client():
    """Obtiene el cliente de OpenAI, inicializándolo solo cuando se necesita"""
    try:
        api_key = settings.OPENAI_API_KEY
        if not api_key or api_key == 'sk-proj-temp-key-replace-with-your-key':
            return None
        return OpenAI(api_key=api_key)
    except Exception:
        return None


def generar_texto_envio(envio) -> str:
    """
    Genera texto descriptivo del envío para indexación semántica
    
    Args:
        envio: Instancia del modelo Envio
        
    Returns:
        str: Texto descriptivo completo del envío
    """
    partes = [
        f"HAWB: {envio.hawb}",
        f"Comprador: {envio.comprador.nombre}",
        f"Estado: {envio.get_estado_display()}",
        f"Fecha: {envio.fecha_emision.strftime('%Y-%m-%d')}",
        f"Peso: {envio.peso_total} kg",
        f"Valor: ${envio.valor_total}",
        f"Costo servicio: ${envio.costo_servicio}",
    ]
    
    # Agregar información del comprador
    if envio.comprador.ciudad:
        partes.append(f"Ciudad destino: {envio.comprador.ciudad}")
    if envio.comprador.provincia:
        partes.append(f"Provincia: {envio.comprador.provincia}")
    if envio.comprador.canton:
        partes.append(f"Cantón: {envio.comprador.canton}")
    
    # Agregar información de productos
    productos = envio.productos.all()
    if productos.exists():
        descripciones = []
        categorias = []
        for producto in productos[:5]:  # Limitar a 5 productos
            descripciones.append(producto.descripcion)
            if producto.categoria not in categorias:
                categorias.append(producto.get_categoria_display())
        
        partes.append(f"Productos: {', '.join(descripciones)}")
        partes.append(f"Categorías: {', '.join(categorias)}")
        partes.append(f"Cantidad total de productos: {envio.cantidad_total}")
    
    # Agregar observaciones si existen
    if envio.observaciones:
        partes.append(f"Observaciones: {envio.observaciones}")
    
    return " | ".join(partes)


def generar_embedding(texto: str, modelo: str = None) -> Dict[str, Any]:
    """
    Genera un embedding usando OpenAI y calcula el costo
    
    Args:
        texto: Texto para generar embedding
        modelo: Modelo de OpenAI a usar (por defecto text-embedding-3-small)
    
    Returns:
        dict: {
            'embedding': lista de floats,
            'tokens': int,
            'costo': float,
            'modelo': str
        }
    
    Raises:
        ValueError: Si no hay API key configurada
        Exception: Si falla la llamada a OpenAI
    """
    client = get_openai_client()
    if not client:
        raise ValueError("OpenAI API key no configurada. Configura OPENAI_API_KEY en .env")
    
    if modelo is None:
        modelo = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    
    # Precios por 1K tokens según modelo (USD) - Actualizados 2024
    precios_modelos = {
        'text-embedding-3-small': 0.00002,   # $0.02 / 1M tokens
        'text-embedding-3-large': 0.00013,   # $0.13 / 1M tokens
        'text-embedding-ada-002': 0.0001     # $0.10 / 1M tokens
    }
    
    precio_por_1k = precios_modelos.get(modelo, 0.00002)
    
    try:
        response = client.embeddings.create(
            model=modelo,
            input=texto,
            encoding_format="float"
        )
        
        embedding = response.data[0].embedding
        tokens_utilizados = response.usage.total_tokens
        
        # Calcular costo: (tokens / 1000) * precio_por_1k
        costo = (tokens_utilizados / 1000.0) * precio_por_1k
        
        return {
            'embedding': embedding,
            'tokens': tokens_utilizados,
            'costo': costo,
            'modelo': modelo
        }
    except Exception as e:
        print(f"Error generando embedding: {str(e)}")
        raise


def generar_embedding_envio(envio, modelo: str = None, forzar_regeneracion: bool = False) -> EnvioEmbedding:
    """
    Genera o actualiza el embedding de un envío
    
    Args:
        envio: Instancia del modelo Envio
        modelo: Modelo de OpenAI a usar
        forzar_regeneracion: Si True, regenera el embedding aunque ya exista
    
    Returns:
        EnvioEmbedding: Instancia del embedding generado o actualizado
    """
    if modelo is None:
        modelo = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    
    # Verificar si ya existe un embedding
    try:
        envio_embedding = EnvioEmbedding.objects.get(envio=envio, modelo_usado=modelo)
        if not forzar_regeneracion:
            # Ya existe y no se fuerza regeneración
            return envio_embedding
    except EnvioEmbedding.DoesNotExist:
        envio_embedding = None
    
    # Generar texto descriptivo
    texto_indexado = generar_texto_envio(envio)
    
    # Generar embedding
    resultado = generar_embedding(texto_indexado, modelo)
    
    # Guardar o actualizar embedding
    if envio_embedding:
        envio_embedding.texto_indexado = texto_indexado
        envio_embedding.set_vector(resultado['embedding'])
        envio_embedding.save()
    else:
        envio_embedding = EnvioEmbedding.objects.create(
            envio=envio,
            texto_indexado=texto_indexado,
            modelo_usado=modelo
        )
        envio_embedding.set_vector(resultado['embedding'])
        envio_embedding.save()
    
    return envio_embedding


def calcular_similitudes(embedding_consulta: List[float], embeddings_envios: List[Tuple]) -> List[Dict]:
    """
    Calcula múltiples métricas de similitud entre la consulta y los embeddings de envíos
    
    Args:
        embedding_consulta: Vector de la consulta
        embeddings_envios: Lista de tuplas (envio_id, vector_embedding, envio_obj)
    
    Returns:
        List[Dict]: Lista de resultados con múltiples métricas de similitud
    """
    consulta_vec = np.array(embedding_consulta)
    consulta_norm = np.linalg.norm(consulta_vec)
    
    resultados = []
    
    for envio_id, vector_envio, envio_obj in embeddings_envios:
        envio_vec = np.array(vector_envio)
        envio_norm = np.linalg.norm(envio_vec)
        
        # 1. Similitud Coseno: dot(A, B) / (||A|| * ||B||)
        # Rango: [-1, 1], 1 es idéntico, 0 es ortogonal, -1 es opuesto
        cosine_similarity = 0.0
        if consulta_norm > 0 and envio_norm > 0:
            cosine_similarity = float(np.dot(consulta_vec, envio_vec) / (consulta_norm * envio_norm))
        
        # 2. Dot Product (Producto Punto): dot(A, B)
        # Rango: [0, infinito], mayor es más similar
        dot_product = float(np.dot(consulta_vec, envio_vec))
        
        # 3. Distancia Euclidiana: sqrt(sum((A - B)^2))
        # Rango: [0, infinito], 0 es idéntico, mayor es más diferente
        euclidean_distance = float(np.linalg.norm(consulta_vec - envio_vec))
        
        # 4. Distancia Manhattan (L1): sum(|A - B|)
        manhattan_distance = float(np.sum(np.abs(consulta_vec - envio_vec)))
        
        resultados.append({
            'envio_id': envio_id,
            'envio': envio_obj,
            'cosine_similarity': cosine_similarity,
            'dot_product': dot_product,
            'euclidean_distance': euclidean_distance,
            'manhattan_distance': manhattan_distance,
            # Puntuación combinada (normalizada)
            'score_combinado': (cosine_similarity + 1) / 2  # Normalizar cosine a [0, 1]
        })
    
    return resultados


def ordenar_por_metrica(resultados: List[Dict], metrica: str = 'cosine_similarity', 
                        limite: int = 20) -> List[Dict]:
    """
    Ordena resultados por la métrica especificada
    
    Args:
        resultados: Lista de resultados con métricas
        metrica: Métrica a usar para ordenar (cosine_similarity, dot_product, euclidean_distance)
        limite: Cantidad máxima de resultados a retornar
    
    Returns:
        List[Dict]: Resultados ordenados y limitados
    """
    # Determinar si ordenar ascendente o descendente según la métrica
    metricas_descendentes = ['cosine_similarity', 'dot_product', 'score_combinado']
    metricas_ascendentes = ['euclidean_distance', 'manhattan_distance']
    
    if metrica in metricas_descendentes:
        # Mayor es mejor
        resultados_ordenados = sorted(resultados, key=lambda x: x.get(metrica, 0), reverse=True)
    elif metrica in metricas_ascendentes:
        # Menor es mejor
        resultados_ordenados = sorted(resultados, key=lambda x: x.get(metrica, float('inf')))
    else:
        # Por defecto usar cosine similarity
        resultados_ordenados = sorted(resultados, key=lambda x: x.get('cosine_similarity', 0), reverse=True)
    
    return resultados_ordenados[:limite]


def aplicar_umbral_similitud(resultados: List[Dict], umbral_cosine: float = 0.3,
                             umbral_euclidean: float = None) -> List[Dict]:
    """
    Filtra resultados según umbrales de similitud
    
    Args:
        resultados: Lista de resultados con métricas
        umbral_cosine: Umbral mínimo de similitud coseno (0.0 - 1.0)
        umbral_euclidean: Umbral máximo de distancia euclidiana (opcional)
    
    Returns:
        List[Dict]: Resultados filtrados
    """
    resultados_filtrados = []
    
    for resultado in resultados:
        # Aplicar umbral de cosine similarity
        if resultado.get('cosine_similarity', 0) >= umbral_cosine:
            # Aplicar umbral euclidiano si está definido
            if umbral_euclidean is None or resultado.get('euclidean_distance', float('inf')) <= umbral_euclidean:
                resultados_filtrados.append(resultado)
    
    return resultados_filtrados


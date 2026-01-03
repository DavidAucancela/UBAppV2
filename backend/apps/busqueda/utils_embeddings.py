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
    Versión mejorada con más contexto y repetición de información importante
    
    Args:
        envio: Instancia del modelo Envio
        
    Returns:
        str: Texto descriptivo completo del envío
    """
    # Información principal (ordenada por importancia semántica)
    estado_display = envio.get_estado_display()
    partes = [
        # Estado y código identificador primero (más importante para búsqueda)
        f"Envió {envio.hawb} con estado {estado_display}",
        f"Estado del envío: {estado_display}",
        f"Código HAWB: {envio.hawb}",
        f"Comprador: {envio.comprador.nombre}",
    ]
    
    # Información de ubicación (importante para búsquedas geográficas)
    if envio.comprador.ciudad:
        partes.append(f"Ciudad destino: {envio.comprador.ciudad}")
        partes.append(f"Ubicación: {envio.comprador.ciudad}")  # Repetir para más peso
    if envio.comprador.provincia:
        partes.append(f"Provincia: {envio.comprador.provincia}")
    if envio.comprador.canton:
        partes.append(f"Cantón: {envio.comprador.canton}")
    
    # Información temporal
    fecha_str = envio.fecha_emision.strftime('%Y-%m-%d')
    partes.append(f"Fecha de emisión: {fecha_str}")
    partes.append(f"Fecha: {fecha_str}")  # Variación para mejor matching
    
    # Información de envío
    partes.extend([
        f"Peso total: {envio.peso_total} kg",
        f"Peso: {envio.peso_total} kg",
        f"Valor total: ${envio.valor_total}",
        f"Valor: ${envio.valor_total}",
        f"Costo del servicio: ${envio.costo_servicio}",
    ])
    
    # Información de productos (muy importante para búsquedas de productos)
    productos = envio.productos.all()
    if productos.exists():
        descripciones = []
        categorias = []
        nombres_productos = []
        
        for producto in productos[:5]:  # Limitar a 5 productos
            descripciones.append(producto.descripcion)
            if producto.categoria not in categorias:
                categorias.append(producto.get_categoria_display())
            if hasattr(producto, 'nombre') and producto.nombre:
                nombres_productos.append(producto.nombre)
        
        if descripciones:
            partes.append(f"Productos incluidos: {', '.join(descripciones)}")
            partes.append(f"Contiene: {', '.join(descripciones[:3])}")  # Versión corta
        
        if categorias:
            partes.append(f"Categorías de productos: {', '.join(categorias)}")
        
        partes.append(f"Cantidad total de productos: {envio.cantidad_total}")
    
    # Observaciones (pueden contener información relevante)
    if envio.observaciones:
        partes.append(f"Observaciones: {envio.observaciones}")
        partes.append(envio.observaciones)  # También como texto libre
    
    # Resumen descriptivo al final
    resumen = f"Envío {envio.hawb} {estado_display} para {envio.comprador.nombre}"
    if envio.comprador.ciudad:
        resumen += f" en {envio.comprador.ciudad}"
    partes.append(resumen)
    
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


def calcular_coincidencias_exactas(texto_consulta: str, texto_indexado: str) -> float:
    """
    Calcula un score de coincidencias exactas entre consulta y texto indexado
    
    Args:
        texto_consulta: Texto de la consulta del usuario
        texto_indexado: Texto indexado del envío
        
    Returns:
        float: Score de coincidencias [0.0, 1.0]
    """
    consulta_lower = texto_consulta.lower()
    texto_lower = texto_indexado.lower()
    
    # Separar palabras significativas (más de 3 caracteres)
    palabras_consulta = [p for p in consulta_lower.split() if len(p) > 3]
    if not palabras_consulta:
        return 0.0
    
    coincidencias = 0
    total_palabras = len(palabras_consulta)
    
    for palabra in palabras_consulta:
        # Verificar coincidencia exacta
        if palabra in texto_lower:
            coincidencias += 1
        # Verificar coincidencia parcial (palabra contenida)
        elif any(palabra in p or p in palabra for p in texto_lower.split() if len(p) > 3):
            coincidencias += 0.5
    
    return min(coincidencias / total_palabras, 1.0) if total_palabras > 0 else 0.0


def calcular_similitudes(embedding_consulta: List[float], embeddings_envios: List[Tuple], 
                         texto_consulta: str = "", textos_indexados: Dict[int, str] = None) -> List[Dict]:
    """
    Calcula múltiples métricas de similitud entre la consulta y los embeddings de envíos
    Ahora incluye boost por coincidencias exactas
    
    Args:
        embedding_consulta: Vector de la consulta
        embeddings_envios: Lista de tuplas (envio_id, vector_embedding, envio_obj)
        texto_consulta: Texto de la consulta original (opcional, para boost)
        textos_indexados: Diccionario {envio_id: texto_indexado} (opcional)
    
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
        
        # 5. Boost por coincidencias exactas (si hay texto disponible)
        boost_exactas = 0.0
        coincidencias_score = 0.0
        if texto_consulta and textos_indexados and envio_id in textos_indexados:
            coincidencias_score = calcular_coincidencias_exactas(
                texto_consulta, 
                textos_indexados[envio_id]
            )
            # Boost: hasta 0.15 puntos adicionales para coincidencias exactas
            boost_exactas = coincidencias_score * 0.15
        
        # 6. Score combinado mejorado: cosine + boost de exactas
        # Normalizar cosine a [0, 1] y agregar boost
        cosine_normalizado = (cosine_similarity + 1) / 2
        score_combinado = min(cosine_normalizado + boost_exactas, 1.0)
        
        resultados.append({
            'envio_id': envio_id,
            'envio': envio_obj,
            'cosine_similarity': cosine_similarity,
            'dot_product': dot_product,
            'euclidean_distance': euclidean_distance,
            'manhattan_distance': manhattan_distance,
            'score_combinado': score_combinado,
            'boost_exactas': boost_exactas,
            'coincidencias_exactas': coincidencias_score
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


def aplicar_umbral_adaptativo(resultados: List[Dict], umbral_base: float = 0.3, 
                               percentil_minimo: float = 0.75) -> List[Dict]:
    """
    Filtra resultados usando umbral adaptativo basado en la distribución de scores
    
    Args:
        resultados: Lista de resultados con métricas
        umbral_base: Umbral mínimo absoluto (ej: 0.3)
        percentil_minimo: Percentil mínimo para considerar (ej: 0.75 = solo top 25%)
    
    Returns:
        List[Dict]: Resultados filtrados
    """
    if not resultados:
        return []
    
    # Obtener todos los scores de similitud (usar score_combinado si está disponible)
    scores = [max(r.get('cosine_similarity', 0), r.get('score_combinado', 0)) for r in resultados]
    
    # Calcular umbral adaptativo
    if len(scores) > 1:
        scores_ordenados = sorted(scores, reverse=True)
        # Umbral como percentil de los mejores resultados
        indice_percentil = max(0, int(len(scores_ordenados) * (1 - percentil_minimo)))
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
        
        # Usar el mayor entre cosine_similarity y score_combinado
        score_final = max(score, score_combinado)
        
        # Aplicar umbral (el mayor entre base y adaptativo)
        if score_final >= umbral_adaptativo:
            resultados_filtrados.append(resultado)
    
    return resultados_filtrados


def aplicar_umbral_similitud(resultados: List[Dict], umbral_cosine: float = 0.35,
                             umbral_euclidean: float = None, usar_adaptativo: bool = True) -> List[Dict]:
    """
    Filtra resultados según umbrales de similitud
    
    Args:
        resultados: Lista de resultados con métricas
        umbral_cosine: Umbral mínimo de similitud coseno (0.0 - 1.0)
                      Aumentado a 0.35 por defecto para mayor precisión
        umbral_euclidean: Umbral máximo de distancia euclidiana (opcional)
        usar_adaptativo: Si True, usa umbral adaptativo además del base
    
    Returns:
        List[Dict]: Resultados filtrados
    """
    if usar_adaptativo and len(resultados) > 3:
        # Usar umbral adaptativo para mejor filtrado
        return aplicar_umbral_adaptativo(resultados, umbral_base=umbral_cosine)
    
    # Filtrado tradicional
    resultados_filtrados = []
    for resultado in resultados:
        score = resultado.get('cosine_similarity', 0)
        score_combinado = resultado.get('score_combinado', score)
        score_final = max(score, score_combinado)
        
        if score_final >= umbral_cosine:
            if umbral_euclidean is None or resultado.get('euclidean_distance', float('inf')) <= umbral_euclidean:
                resultados_filtrados.append(resultado)
    
    return resultados_filtrados


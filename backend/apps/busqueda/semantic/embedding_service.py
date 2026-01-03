"""
Embedding Service - Servicio para generación de embeddings con OpenAI
"""
from typing import Dict, Any, List, Optional
from django.conf import settings
from openai import OpenAI

from apps.core.base.base_service import BaseService
from apps.core.exceptions import (
    OpenAINotConfiguredError,
    OpenAIServiceError
)
from apps.busqueda.repositories import embedding_repository
from .text_processor import TextProcessor


class OpenAIClient:
    """
    Singleton para el cliente de OpenAI.
    Evita crear múltiples instancias del cliente.
    """
    _instance: Optional[OpenAI] = None
    
    @classmethod
    def get_instance(cls) -> Optional[OpenAI]:
        """Obtiene la instancia única del cliente"""
        if cls._instance is None:
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if not api_key or api_key == 'sk-proj-temp-key-replace-with-your-key':
                return None
            
            cls._instance = OpenAI(api_key=api_key)
        
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Resetea la instancia (útil para testing)"""
        cls._instance = None


class EmbeddingService(BaseService):
    """
    Servicio para generación y gestión de embeddings.
    Centraliza toda la lógica relacionada con embeddings de OpenAI.
    """
    
    # Precios por 1K tokens según modelo (USD) - Actualizados 2024
    PRECIOS_MODELOS = {
        'text-embedding-3-small': 0.00002,   # $0.02 / 1M tokens
        'text-embedding-3-large': 0.00013,   # $0.13 / 1M tokens
        'text-embedding-ada-002': 0.0001     # $0.10 / 1M tokens
    }
    
    MODELOS_VALIDOS = list(PRECIOS_MODELOS.keys())
    
    @staticmethod
    def get_modelo_default() -> str:
        """Obtiene el modelo de embedding por defecto"""
        return getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    
    @staticmethod
    def validar_modelo(modelo: str) -> str:
        """Valida y retorna un modelo válido"""
        if modelo not in EmbeddingService.MODELOS_VALIDOS:
            return EmbeddingService.get_modelo_default()
        return modelo
    
    # ==================== GENERACIÓN DE EMBEDDINGS ====================
    
    @staticmethod
    def generar_embedding(texto: str, modelo: str = None) -> Dict[str, Any]:
        """
        Genera un embedding usando OpenAI y calcula el costo.
        
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
            OpenAINotConfiguredError: Si no hay API key configurada
            OpenAIServiceError: Si falla la llamada a OpenAI
        """
        client = OpenAIClient.get_instance()
        if not client:
            raise OpenAINotConfiguredError()
        
        if modelo is None:
            modelo = EmbeddingService.get_modelo_default()
        else:
            modelo = EmbeddingService.validar_modelo(modelo)
        
        precio_por_1k = EmbeddingService.PRECIOS_MODELOS.get(modelo, 0.00002)
        
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
            BaseService.log_error(e, "Error generando embedding")
            raise OpenAIServiceError(str(e))
    
    @staticmethod
    def generar_embedding_envio(
        envio,
        modelo: str = None,
        forzar_regeneracion: bool = False,
        tipo_proceso: str = 'automatico'
    ):
        """
        Genera o actualiza el embedding de un envío.
        
        Args:
            envio: Instancia del modelo Envio
            modelo: Modelo de OpenAI a usar
            forzar_regeneracion: Si True, regenera aunque ya exista
            tipo_proceso: Tipo de proceso ('automatico', 'manual', 'masivo')
        
        Returns:
            EnvioEmbedding: Instancia del embedding generado o actualizado
        """
        import time
        from apps.metricas.signals import registrar_generacion_embedding_manual
        
        tiempo_inicio = time.time()
        
        if modelo is None:
            modelo = EmbeddingService.get_modelo_default()
        
        # Verificar si ya existe y no se fuerza regeneración
        if not forzar_regeneracion:
            embedding_existente = embedding_repository.obtener_por_envio(envio, modelo)
            if embedding_existente:
                # Registrar como omitido
                tiempo_generacion_ms = int((time.time() - tiempo_inicio) * 1000)
                registrar_generacion_embedding_manual(
                    envio=envio,
                    estado='omitido',
                    tiempo_generacion_ms=tiempo_generacion_ms,
                    modelo_usado=modelo,
                    tipo_proceso=tipo_proceso,
                    embedding=embedding_existente
                )
                return embedding_existente
        
        try:
            # Generar texto descriptivo
            texto_indexado = TextProcessor.generar_texto_envio(envio)
            
            # Generar embedding
            resultado = EmbeddingService.generar_embedding(texto_indexado, modelo)
            
            # Guardar o actualizar embedding
            embedding = embedding_repository.crear_o_actualizar_embedding(
                envio=envio,
                texto_indexado=texto_indexado,
                vector=resultado['embedding'],
                modelo=modelo
            )
            
            # Registrar generación exitosa
            tiempo_generacion_ms = int((time.time() - tiempo_inicio) * 1000)
            registrar_generacion_embedding_manual(
                envio=envio,
                estado='generado',
                tiempo_generacion_ms=tiempo_generacion_ms,
                modelo_usado=modelo,
                tipo_proceso=tipo_proceso,
                embedding=embedding
            )
            
            return embedding
            
        except Exception as e:
            # Registrar error
            tiempo_generacion_ms = int((time.time() - tiempo_inicio) * 1000)
            registrar_generacion_embedding_manual(
                envio=envio,
                estado='error',
                tiempo_generacion_ms=tiempo_generacion_ms,
                modelo_usado=modelo,
                tipo_proceso=tipo_proceso,
                mensaje_error=str(e)
            )
            raise
    
    @staticmethod
    def generar_embeddings_masivo(
        envios,
        modelo: str = None,
        forzar_regeneracion: bool = False
    ) -> Dict[str, Any]:
        """
        Genera embeddings para múltiples envíos.
        
        Args:
            envios: QuerySet de envíos
            modelo: Modelo a usar
            forzar_regeneracion: Si True, regenera todos
            
        Returns:
            Dict con estadísticas de la operación
        """
        if modelo is None:
            modelo = EmbeddingService.get_modelo_default()
        
        total = envios.count()
        procesados = 0
        errores = 0
        tokens_total = 0
        costo_total = 0.0
        
        for envio in envios:
            try:
                # Verificar si ya existe
                if not forzar_regeneracion and embedding_repository.existe_embedding(envio, modelo):
                    continue
                
                # Generar texto y embedding
                texto = TextProcessor.generar_texto_envio(envio)
                resultado = EmbeddingService.generar_embedding(texto, modelo)
                
                # Guardar
                embedding_repository.crear_o_actualizar_embedding(
                    envio=envio,
                    texto_indexado=texto,
                    vector=resultado['embedding'],
                    modelo=modelo
                )
                
                procesados += 1
                tokens_total += resultado['tokens']
                costo_total += resultado['costo']
                
            except Exception as e:
                errores += 1
                BaseService.log_error(e, f"Error generando embedding para envío {envio.hawb}")
        
        return {
            'total': total,
            'procesados': procesados,
            'errores': errores,
            'omitidos': total - procesados - errores,
            'tokens_total': tokens_total,
            'costo_total': round(costo_total, 6),
            'modelo': modelo
        }


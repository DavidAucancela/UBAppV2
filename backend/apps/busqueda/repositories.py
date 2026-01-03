"""
Repositorios para la app de búsqueda
Implementa el patrón Repository para acceso a datos de búsqueda y embeddings
"""
from typing import Optional, List, Dict, Any
from django.db.models import QuerySet, Q, Avg, Count
from django.db import models

from apps.core.base.base_repository import BaseRepository
from apps.core.exceptions import EmbeddingNoEncontradoError
from .models import (
    BusquedaTradicional,
    EmbeddingBusqueda,
    HistorialSemantica,
    EnvioEmbedding
)


class BusquedaTradicionalRepository(BaseRepository):
    """
    Repositorio para operaciones de BusquedaTradicional.
    """
    
    @property
    def model(self):
        return BusquedaTradicional
    
    @property
    def select_related_fields(self) -> List[str]:
        return ['usuario']
    
    def filtrar_por_usuario(self, usuario) -> QuerySet:
        """Obtiene historial de un usuario"""
        return self._get_optimized_queryset().filter(usuario=usuario)
    
    def obtener_busquedas_populares(self, usuario, limite: int = 5) -> List[Dict]:
        """Obtiene las búsquedas más populares del usuario"""
        return list(
            self.model.objects.filter(usuario=usuario)
            .values('termino_busqueda')
            .annotate(count=Count('termino_busqueda'))
            .order_by('-count')[:limite]
        )
    
    def limpiar_historial_usuario(self, usuario) -> int:
        """Elimina todo el historial de un usuario"""
        count, _ = self.model.objects.filter(usuario=usuario).delete()
        return count


class EmbeddingBusquedaRepository(BaseRepository):
    """
    Repositorio para operaciones de EmbeddingBusqueda (búsquedas semánticas).
    """
    
    @property
    def model(self):
        return EmbeddingBusqueda
    
    @property
    def select_related_fields(self) -> List[str]:
        return ['usuario']
    
    def filtrar_por_usuario(self, usuario, limite: int = 10) -> QuerySet:
        """Obtiene historial semántico de un usuario"""
        return (
            self._get_optimized_queryset()
            .filter(usuario=usuario)
            .order_by('-fecha_busqueda')[:limite]
        )
    
    def obtener_metricas(self, usuario) -> Dict[str, Any]:
        """Obtiene métricas de búsquedas semánticas del usuario"""
        busquedas = self.model.objects.filter(usuario=usuario)
        
        return {
            'total_busquedas': busquedas.count(),
            'tiempo_promedio_respuesta': busquedas.aggregate(
                promedio=Avg('tiempo_respuesta')
            )['promedio'] or 0,
        }
    
    def limpiar_historial_usuario(self, usuario) -> int:
        """Elimina historial semántico de un usuario"""
        count, _ = self.model.objects.filter(usuario=usuario).delete()
        return count


class HistorialSemanticaRepository(BaseRepository):
    """
    Repositorio para operaciones de HistorialSemantica (sugerencias).
    """
    
    @property
    def model(self):
        return HistorialSemantica
    
    def obtener_activas(self, query: str = None, limite: int = 10) -> QuerySet:
        """
        Obtiene sugerencias activas, opcionalmente filtradas.
        
        Args:
            query: Término de búsqueda para filtrar (opcional)
            limite: Cantidad máxima de resultados
        """
        queryset = self.model.objects.filter(activa=True)
        
        if query and len(query) >= 2:
            queryset = queryset.filter(
                Q(texto__icontains=query) | Q(categoria__icontains=query)
            )
        
        return queryset.order_by('orden', '-fecha_creacion')[:limite]


class EnvioEmbeddingRepository(BaseRepository):
    """
    Repositorio para operaciones de EnvioEmbedding.
    Especializado en operaciones de embeddings y búsqueda vectorial.
    """
    
    @property
    def model(self):
        return EnvioEmbedding
    
    @property
    def select_related_fields(self) -> List[str]:
        return ['envio', 'envio__comprador']
    
    @property
    def prefetch_related_fields(self) -> List[str]:
        return ['envio__productos']
    
    # ==================== CONSULTAS ESPECÍFICAS ====================
    
    def obtener_por_envio(self, envio, modelo: str = None) -> Optional[EnvioEmbedding]:
        """
        Obtiene el embedding de un envío.
        
        Args:
            envio: Instancia o ID del envío
            modelo: Modelo de embedding específico (opcional)
        """
        filtros = {'envio': envio}
        if modelo:
            filtros['modelo_usado'] = modelo
        
        return self.model.objects.filter(**filtros).first()
    
    def obtener_por_envio_o_error(
        self,
        envio,
        modelo: str = None
    ) -> EnvioEmbedding:
        """
        Obtiene el embedding de un envío o lanza error.
        
        Raises:
            EmbeddingNoEncontradoError: Si no existe el embedding
        """
        embedding = self.obtener_por_envio(envio, modelo)
        if not embedding:
            raise EmbeddingNoEncontradoError(str(envio.hawb if hasattr(envio, 'hawb') else envio))
        return embedding
    
    # ==================== OPERACIONES DE EMBEDDINGS ====================
    
    def obtener_embeddings_para_busqueda(
        self,
        envios_queryset,
        modelo: str = None,
        limite: int = 500
    ) -> List[tuple]:
        """
        Obtiene embeddings para búsqueda vectorial.
        
        Args:
            envios_queryset: QuerySet de envíos
            modelo: Modelo de embedding
            limite: Máximo de embeddings a retornar
            
        Returns:
            Lista de tuplas (envio_id, vector, envio_obj)
        """
        filtros = {'envio__in': envios_queryset[:limite]}
        if modelo:
            filtros['modelo_usado'] = modelo
        
        embeddings = (
            self._get_optimized_queryset()
            .filter(**filtros)
        )
        
        resultado = []
        for emb in embeddings:
            vector = emb.get_vector()
            if vector:
                resultado.append((emb.envio_id, vector, emb.envio))
        
        return resultado
    
    def obtener_textos_indexados(
        self,
        envios_ids: List[int]
    ) -> Dict[int, str]:
        """
        Obtiene los textos indexados para un conjunto de envíos.
        
        Args:
            envios_ids: Lista de IDs de envíos
            
        Returns:
            Diccionario {envio_id: texto_indexado}
        """
        embeddings = self.model.objects.filter(
            envio_id__in=envios_ids
        ).values('envio_id', 'texto_indexado')
        
        return {emb['envio_id']: emb['texto_indexado'] for emb in embeddings}
    
    def crear_o_actualizar_embedding(
        self,
        envio,
        texto_indexado: str,
        vector: List[float],
        modelo: str
    ) -> EnvioEmbedding:
        """
        Crea o actualiza el embedding de un envío.
        
        Args:
            envio: Instancia del envío
            texto_indexado: Texto usado para generar el embedding
            vector: Vector de embedding
            modelo: Modelo usado
            
        Returns:
            Instancia del embedding
        """
        embedding, created = self.model.objects.get_or_create(
            envio=envio,
            modelo_usado=modelo,
            defaults={'texto_indexado': texto_indexado}
        )
        
        if not created:
            embedding.texto_indexado = texto_indexado
        
        embedding.set_vector(vector)
        embedding.save()
        
        return embedding
    
    def contar_embeddings(self, modelo: str = None) -> int:
        """Cuenta el total de embeddings"""
        if modelo:
            return self.model.objects.filter(modelo_usado=modelo).count()
        return self.model.objects.count()
    
    def existe_embedding(self, envio, modelo: str = None) -> bool:
        """Verifica si existe embedding para un envío"""
        filtros = {'envio': envio}
        if modelo:
            filtros['modelo_usado'] = modelo
        return self.model.objects.filter(**filtros).exists()


# Instancias singleton para uso en servicios
busqueda_tradicional_repository = BusquedaTradicionalRepository()
embedding_busqueda_repository = EmbeddingBusquedaRepository()
historial_semantica_repository = HistorialSemanticaRepository()
embedding_repository = EnvioEmbeddingRepository()


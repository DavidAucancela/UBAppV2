# 🎨 PATRONES DE DISEÑO - GUÍA DE IMPLEMENTACIÓN

**Fecha:** Enero 2025  
**Versión:** 1.0  
**Sistema:** UBApp

---

## 📋 TABLA DE CONTENIDOS

1. [Patrones Identificados](#patrones-identificados)
2. [Patrones a Implementar](#patrones-a-implementar)
3. [Ejemplos de Código](#ejemplos-de-código)
4. [Migración Gradual](#migración-gradual)

---

## 1. PATRONES IDENTIFICADOS

### 1.1 Patrones Actuales (Estado)

| Patrón | Estado | Ubicación | Calidad |
|--------|--------|-----------|---------|
| **Repository** | ⚠️ Parcial | Models Django | Media |
| **Service Layer** | ⚠️ Parcial | utils_*.py | Baja |
| **Serializer** | ✅ Completo | serializers.py | Alta |
| **ViewSet** | ✅ Completo | views.py | Alta |
| **Factory** | ❌ No existe | - | - |
| **Strategy** | ⚠️ Parcial | utils_embeddings.py | Media |
| **Observer** | ✅ Completo | signals.py | Alta |
| **Singleton** | ⚠️ Implícito | get_openai_client() | Baja |
| **Dependency Injection** | ❌ No existe | - | - |
| **Unit of Work** | ⚠️ Parcial | transaction.atomic() | Media |

---

## 2. PATRONES A IMPLEMENTAR

### 2.1 REPOSITORY PATTERN

**Objetivo**: Abstraer acceso a datos, facilitar testing, centralizar queries.

**Implementación**:

```python
# apps/core/base/base_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from django.db.models import Model, QuerySet

T = TypeVar('T', bound=Model)

class BaseRepository(ABC, Generic[T]):
    """Repositorio base con operaciones CRUD comunes"""
    
    @property
    @abstractmethod
    def model(self) -> type[T]:
        """Retorna el modelo Django"""
        pass
    
    def obtener_por_id(self, id: int) -> T:
        """Obtiene un objeto por ID"""
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist(f"{self.model.__name__} {id} no existe")
    
    def obtener_todos(self) -> QuerySet[T]:
        """Obtiene todos los objetos"""
        return self.model.objects.all()
    
    def crear(self, **kwargs) -> T:
        """Crea un nuevo objeto"""
        return self.model.objects.create(**kwargs)
    
    def actualizar(self, obj: T, **kwargs) -> T:
        """Actualiza un objeto existente"""
        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.save()
        return obj
    
    def eliminar(self, obj: T) -> None:
        """Elimina un objeto"""
        obj.delete()
    
    def existe(self, **filtros) -> bool:
        """Verifica si existe un objeto con los filtros"""
        return self.model.objects.filter(**filtros).exists()

# apps/archivos/repositories.py
from apps.core.base.base_repository import BaseRepository
from .models import Envio, Producto, Tarifa

class EnvioRepository(BaseRepository):
    """Repositorio para operaciones de Envío"""
    
    @property
    def model(self):
        return Envio
    
    def obtener_por_hawb(self, hawb: str) -> Envio:
        """Obtiene un envío por HAWB"""
        try:
            return self.model.objects.select_related(
                'comprador'
            ).prefetch_related(
                'productos'
            ).get(hawb=hawb)
        except Envio.DoesNotExist:
            raise Envio.DoesNotExist(f"Envío {hawb} no existe")
    
    def filtrar_por_usuario(self, usuario) -> QuerySet[Envio]:
        """Filtra envíos según permisos del usuario"""
        queryset = self.model.objects.select_related(
            'comprador'
        ).prefetch_related(
            'productos'
        )
        
        if usuario.es_comprador:
            return queryset.filter(comprador=usuario)
        elif usuario.es_digitador or usuario.es_gerente:
            return queryset
        else:
            return queryset.none()
    
    def filtrar_por_estado(self, estado: str, usuario) -> QuerySet[Envio]:
        """Filtra envíos por estado"""
        return self.filtrar_por_usuario(usuario).filter(estado=estado)
    
    def filtrar_por_fecha_rango(
        self, 
        fecha_desde, 
        fecha_hasta, 
        usuario
    ) -> QuerySet[Envio]:
        """Filtra envíos por rango de fechas"""
        return self.filtrar_por_usuario(usuario).filter(
            fecha_emision__gte=fecha_desde,
            fecha_emision__lte=fecha_hasta
        )

class ProductoRepository(BaseRepository):
    """Repositorio para operaciones de Producto"""
    
    @property
    def model(self):
        return Producto
    
    def obtener_por_envio(self, envio: Envio) -> QuerySet[Producto]:
        """Obtiene productos de un envío"""
        return self.model.objects.filter(envio=envio)
    
    def crear_multiples(self, productos_data: List[dict], envio: Envio) -> List[Producto]:
        """Crea múltiples productos para un envío"""
        productos = []
        for data in productos_data:
            data['envio'] = envio
            productos.append(self.crear(**data))
        return productos
```

**Uso**:
```python
# En servicios
from apps.archivos.repositories import EnvioRepository

class EnvioService:
    def obtener_envio(self, envio_id: int, usuario):
        envio = EnvioRepository().obtener_por_id(envio_id)
        # Validar permisos
        if usuario.es_comprador and envio.comprador != usuario:
            raise PermissionDenied()
        return envio
```

---

### 2.2 SERVICE LAYER PATTERN

**Objetivo**: Centralizar lógica de negocio, facilitar testing, reutilización.

**Implementación**:

```python
# apps/core/base/base_service.py
from abc import ABC
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class BaseService(ABC):
    """Clase base para servicios"""
    
    @staticmethod
    def validar_permisos(usuario, accion: str):
        """Valida permisos del usuario"""
        # Implementación base
        pass
    
    @staticmethod
    def log_error(error: Exception, contexto: str):
        """Log de errores"""
        logger.error(f"{contexto}: {str(error)}", exc_info=True)

# apps/archivos/services.py
from apps.core.base.base_service import BaseService
from apps.archivos.repositories import EnvioRepository, ProductoRepository
from apps.archivos.models import Envio
from apps.busqueda.semantic.embedding_service import EmbeddingService
from apps.notificaciones.services import NotificacionService
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied

class EnvioService(BaseService):
    """Servicio para operaciones de envíos"""
    
    @staticmethod
    def crear_envio(data: dict, usuario) -> Envio:
        """
        Crea un envío aplicando reglas de negocio
        
        Reglas:
        - Validar permisos
        - Validar cupo anual del comprador
        - Calcular costo automáticamente
        - Generar embedding
        - Enviar notificación
        """
        # Validar permisos
        if not (usuario.es_admin or usuario.es_digitador):
            raise PermissionDenied("Solo admins y digitadores pueden crear envíos")
        
        # Validar cupo anual (si es comprador)
        comprador_id = data.get('comprador')
        if comprador_id:
            from apps.usuarios.repositories import UsuarioRepository
            comprador = UsuarioRepository().obtener_por_id(comprador_id)
            
            if comprador.es_comprador:
                peso_total = float(data.get('peso_total', 0))
                if not EnvioService.validar_cupo_anual(comprador, peso_total):
                    raise ValidationError("El comprador ha excedido su cupo anual")
        
        # Calcular costo automáticamente
        productos_data = data.pop('productos', [])
        costo_servicio = EnvioService.calcular_costo_servicio(productos_data)
        data['costo_servicio'] = costo_servicio
        
        # Crear envío
        envio = EnvioRepository().crear(**data)
        
        # Crear productos
        if productos_data:
            ProductoRepository().crear_multiples(productos_data, envio)
        
        # Generar embedding (asíncrono recomendado)
        try:
            EmbeddingService().generar_embedding_envio(envio)
        except Exception as e:
            BaseService.log_error(e, "Error generando embedding")
            # No fallar la creación si falla el embedding
        
        # Enviar notificación
        if envio.comprador:
            NotificacionService.enviar_notificacion_envio_creado(envio)
        
        return envio
    
    @staticmethod
    def validar_cupo_anual(comprador, peso_nuevo: float) -> bool:
        """Valida si el comprador tiene cupo disponible"""
        from apps.usuarios.services import UsuarioService
        peso_usado = UsuarioService.obtener_peso_usado_anual(comprador)
        peso_disponible = float(comprador.cupo_anual) - peso_usado
        return peso_disponible >= peso_nuevo
    
    @staticmethod
    def calcular_costo_servicio(productos_data: List[dict]) -> float:
        """Calcula el costo total del servicio"""
        from apps.archivos.repositories import TarifaRepository
        
        costo_total = 0.0
        for producto in productos_data:
            categoria = producto.get('categoria')
            peso = float(producto.get('peso', 0))
            cantidad = int(producto.get('cantidad', 1))
            
            tarifa = TarifaRepository().buscar_tarifa(categoria, peso)
            if tarifa:
                costo_producto = tarifa.calcular_costo(peso) * cantidad
                costo_total += costo_producto
        
        return round(costo_total, 2)
    
    @staticmethod
    def actualizar_estado(envio: Envio, nuevo_estado: str, usuario) -> Envio:
        """Actualiza el estado de un envío"""
        # Validar permisos
        if not (usuario.es_admin or usuario.es_digitador):
            raise PermissionDenied()
        
        # Validar transición de estado
        estado_anterior = envio.estado
        if not EnvioService.es_transicion_valida(estado_anterior, nuevo_estado):
            raise ValidationError(
                f"Transición inválida: {estado_anterior} -> {nuevo_estado}"
            )
        
        # Actualizar
        envio = EnvioRepository().actualizar(envio, estado=nuevo_estado)
        
        # Notificar cambio
        if envio.comprador:
            NotificacionService.enviar_notificacion_cambio_estado(
                envio, estado_anterior
            )
        
        return envio
    
    @staticmethod
    def es_transicion_valida(estado_actual: str, nuevo_estado: str) -> bool:
        """Valida si una transición de estado es válida"""
        transiciones_validas = {
            'pendiente': ['en_transito', 'cancelado'],
            'en_transito': ['entregado', 'cancelado'],
            'entregado': [],  # Estado final
            'cancelado': []   # Estado final
        }
        return nuevo_estado in transiciones_validas.get(estado_actual, [])
```

---

### 2.3 FACTORY PATTERN

**Objetivo**: Simplificar creación de objetos complejos.

**Implementación**:

```python
# apps/archivos/factories.py
from apps.archivos.models import Envio, Producto
from apps.archivos.repositories import EnvioRepository, ProductoRepository
from apps.archivos.services import EnvioService

class EnvioFactory:
    """Factory para crear envíos"""
    
    @staticmethod
    def crear_desde_excel(
        datos_fila: dict,
        comprador,
        mapeo_columnas: dict
    ) -> Envio:
        """
        Crea un envío desde datos de Excel
        
        Args:
            datos_fila: Diccionario con datos de la fila
            comprador: Usuario comprador
            mapeo_columnas: Mapeo de columnas Excel -> campos modelo
        """
        # Mapear datos
        envio_data = {
            'hawb': datos_fila[mapeo_columnas.get('hawb', 'HAWB')],
            'peso_total': float(datos_fila[mapeo_columnas.get('peso_total', 'Peso Total')]),
            'cantidad_total': int(datos_fila[mapeo_columnas.get('cantidad_total', 'Cantidad')]),
            'valor_total': float(datos_fila[mapeo_columnas.get('valor_total', 'Valor')]),
            'comprador': comprador,
            'estado': datos_fila.get(mapeo_columnas.get('estado', 'Estado'), 'pendiente'),
        }
        
        # Extraer productos
        productos_data = ProductoFactory.extraer_productos_desde_excel(
            datos_fila, mapeo_columnas
        )
        
        # Crear envío usando servicio
        return EnvioService.crear_envio({
            **envio_data,
            'productos': productos_data
        }, comprador)

class ProductoFactory:
    """Factory para crear productos"""
    
    @staticmethod
    def extraer_productos_desde_excel(
        datos_fila: dict,
        mapeo_columnas: dict
    ) -> List[dict]:
        """Extrae datos de productos desde fila de Excel"""
        productos = []
        
        # Si hay múltiples productos en la misma fila
        if 'productos' in mapeo_columnas:
            productos_raw = datos_fila[mapeo_columnas['productos']]
            # Procesar productos...
        
        # Si hay un solo producto por fila
        producto_data = {
            'descripcion': datos_fila.get(mapeo_columnas.get('descripcion', 'Descripción'), ''),
            'categoria': datos_fila.get(mapeo_columnas.get('categoria', 'Categoría'), 'otros'),
            'peso': float(datos_fila.get(mapeo_columnas.get('peso', 'Peso'), 0)),
            'cantidad': int(datos_fila.get(mapeo_columnas.get('cantidad', 'Cantidad'), 1)),
            'valor': float(datos_fila.get(mapeo_columnas.get('valor', 'Valor'), 0)),
        }
        
        productos.append(producto_data)
        return productos
```

---

### 2.4 STRATEGY PATTERN

**Objetivo**: Intercambiar algoritmos de similitud dinámicamente.

**Implementación**:

```python
# apps/busqueda/semantic/strategies/similarity_strategy.py
from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np

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
    
    @abstractmethod
    def nombre(self) -> str:
        """Nombre de la estrategia"""
        pass

class CosineSimilarityStrategy(SimilarityStrategy):
    """Estrategia de similitud coseno"""
    
    def calcular(self, embedding_consulta: List[float], embedding_envio: List[float]) -> float:
        vec1 = np.array(embedding_consulta)
        vec2 = np.array(embedding_envio)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def nombre(self) -> str:
        return "cosine_similarity"

class EuclideanDistanceStrategy(SimilarityStrategy):
    """Estrategia de distancia euclidiana"""
    
    def calcular(self, embedding_consulta: List[float], embedding_envio: List[float]) -> float:
        vec1 = np.array(embedding_consulta)
        vec2 = np.array(embedding_envio)
        
        distance = np.linalg.norm(vec1 - vec2)
        # Normalizar a [0, 1] (invertir: menor distancia = mayor similitud)
        return 1.0 / (1.0 + distance)
    
    def nombre(self) -> str:
        return "euclidean_distance"

class DotProductStrategy(SimilarityStrategy):
    """Estrategia de producto punto"""
    
    def calcular(self, embedding_consulta: List[float], embedding_envio: List[float]) -> float:
        vec1 = np.array(embedding_consulta)
        vec2 = np.array(embedding_envio)
        
        return float(np.dot(vec1, vec2))
    
    def nombre(self) -> str:
        return "dot_product"

# apps/busqueda/semantic/vector_search.py
class VectorSearchService:
    """Servicio de búsqueda vectorial con estrategias"""
    
    def __init__(self, strategy: SimilarityStrategy = None):
        self.strategy = strategy or CosineSimilarityStrategy()
    
    def buscar_similares(
        self,
        embedding_consulta: List[float],
        embeddings_envios: List[tuple],
        limite: int = 20
    ) -> List[Dict]:
        """Busca envíos similares usando la estrategia configurada"""
        resultados = []
        
        for envio_id, embedding_envio, envio_obj in embeddings_envios:
            similitud = self.strategy.calcular(embedding_consulta, embedding_envio)
            
            resultados.append({
                'envio_id': envio_id,
                'envio': envio_obj,
                'similitud': similitud,
                'metrica': self.strategy.nombre()
            })
        
        # Ordenar por similitud
        resultados.sort(key=lambda x: x['similitud'], reverse=True)
        
        return resultados[:limite]
    
    def cambiar_estrategia(self, strategy: SimilarityStrategy):
        """Cambia la estrategia de similitud"""
        self.strategy = strategy
```

**Uso**:
```python
# Usar estrategia por defecto (coseno)
search_service = VectorSearchService()
resultados = search_service.buscar_similares(embedding, envios)

# Cambiar a distancia euclidiana
search_service.cambiar_estrategia(EuclideanDistanceStrategy())
resultados = search_service.buscar_similares(embedding, envios)
```

---

### 2.5 SINGLETON PATTERN

**Objetivo**: Asegurar una única instancia de clientes externos.

**Implementación**:

```python
# apps/busqueda/semantic/providers/openai_provider.py
from openai import OpenAI
from django.conf import settings
from typing import Optional

class OpenAIClientSingleton:
    """Singleton para cliente de OpenAI"""
    
    _instance: Optional[OpenAI] = None
    _api_key: Optional[str] = None
    
    @classmethod
    def get_instance(cls) -> Optional[OpenAI]:
        """Obtiene la instancia única del cliente"""
        if cls._instance is None:
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if not api_key or api_key == 'sk-proj-temp-key-replace-with-your-key':
                return None
            
            cls._api_key = api_key
            cls._instance = OpenAI(api_key=api_key)
        
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Resetea la instancia (útil para testing)"""
        cls._instance = None
        cls._api_key = None

# Uso
from apps.busqueda.semantic.providers.openai_provider import OpenAIClientSingleton

client = OpenAIClientSingleton.get_instance()
if client:
    response = client.embeddings.create(...)
```

---

### 2.6 DEPENDENCY INJECTION

**Objetivo**: Facilitar testing y desacoplar componentes.

**Implementación**:

```python
# apps/busqueda/services.py
class BusquedaSemanticaService:
    """Servicio de búsqueda semántica con inyección de dependencias"""
    
    def __init__(
        self,
        embedding_service=None,
        vector_search=None,
        semantic_repository=None
    ):
        # Inyección de dependencias con valores por defecto
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_search = vector_search or VectorSearchService()
        self.semantic_repository = semantic_repository or SemanticRepository()
    
    def buscar(
        self,
        consulta: str,
        usuario,
        filtros: dict = None,
        limite: int = 20
    ) -> dict:
        """Realiza búsqueda semántica"""
        # Generar embedding de consulta
        embedding_resultado = self.embedding_service.generar_embedding(consulta)
        embedding_consulta = embedding_resultado['embedding']
        
        # Obtener envíos filtrados
        from apps.archivos.repositories import EnvioRepository
        envios = EnvioRepository().filtrar_por_usuario(usuario)
        
        # Aplicar filtros adicionales
        if filtros:
            envios = self._aplicar_filtros(envios, filtros)
        
        # Obtener embeddings de envíos
        embeddings_envios = self.semantic_repository.obtener_embeddings_envios(
            envios, limite=500
        )
        
        # Buscar similares
        resultados = self.vector_search.buscar_similares(
            embedding_consulta,
            embeddings_envios,
            limite=limite
        )
        
        return {
            'resultados': resultados,
            'costo': embedding_resultado['costo'],
            'tokens': embedding_resultado['tokens']
        }

# En tests, inyectar mocks
def test_busqueda_semantica():
    mock_embedding = MockEmbeddingService()
    mock_vector = MockVectorSearch()
    
    service = BusquedaSemanticaService(
        embedding_service=mock_embedding,
        vector_search=mock_vector
    )
    
    resultado = service.buscar("test", usuario_mock)
    assert resultado is not None
```

---

## 3. MIGRACIÓN GRADUAL

### 3.1 Estrategia de Migración

**Principio**: Migrar gradualmente, mantener funcionalidad existente.

**Pasos**:

1. **Crear estructura nueva** (sin romper código existente)
2. **Migrar una funcionalidad a la vez**
3. **Mantener código antiguo hasta que nuevo esté probado**
4. **Eliminar código antiguo después de validación**

### 3.2 Ejemplo: Migración de Búsqueda Semántica

**Antes** (views.py):
```python
@action(detail=False, methods=['post'])
def busqueda_semantica(self, request):
    # 200+ líneas de lógica
    consulta_texto = request.data.get('texto', '').strip()
    # ... toda la lógica aquí ...
```

**Después** (migración gradual):

**Paso 1**: Crear servicio, mantener lógica en view
```python
# services.py - NUEVO
class BusquedaSemanticaService:
    @staticmethod
    def buscar(consulta, usuario, filtros, limite):
        # Mover lógica aquí gradualmente
        pass

# views.py - MODIFICADO
@action(detail=False, methods=['post'])
def busqueda_semantica(self, request):
    # Llamar servicio, pero mantener lógica antigua como fallback
    try:
        resultado = BusquedaSemanticaService.buscar(...)
    except NotImplementedError:
        # Fallback a lógica antigua
        resultado = self._busqueda_semantica_antigua(request)
    return Response(resultado)
```

**Paso 2**: Completar migración, eliminar fallback
```python
# views.py - FINAL
@action(detail=False, methods=['post'])
def busqueda_semantica(self, request):
    serializer = BusquedaSemanticaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    resultado = BusquedaSemanticaService.buscar(
        consulta=serializer.validated_data['texto'],
        usuario=request.user,
        filtros=serializer.validated_data.get('filtrosAdicionales', {}),
        limite=serializer.validated_data.get('limite', 20)
    )
    
    return Response(resultado)
```

---

## 4. CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: Repositorios
- [ ] Crear BaseRepository
- [ ] Implementar EnvioRepository
- [ ] Implementar ProductoRepository
- [ ] Implementar UsuarioRepository
- [ ] Implementar TarifaRepository
- [ ] Tests unitarios

### Fase 2: Servicios
- [ ] Crear BaseService
- [ ] Implementar EnvioService
- [ ] Implementar UsuarioService
- [ ] Implementar BusquedaSemanticaService
- [ ] Tests unitarios

### Fase 3: Factories
- [ ] Implementar EnvioFactory
- [ ] Implementar ProductoFactory
- [ ] Tests unitarios

### Fase 4: Strategies
- [ ] Crear SimilarityStrategy
- [ ] Implementar CosineSimilarityStrategy
- [ ] Implementar EuclideanDistanceStrategy
- [ ] Integrar en VectorSearchService
- [ ] Tests unitarios

### Fase 5: Singleton
- [ ] Implementar OpenAIClientSingleton
- [ ] Reemplazar get_openai_client()
- [ ] Tests unitarios

### Fase 6: Dependency Injection
- [ ] Refactorizar servicios para DI
- [ ] Crear contenedor de dependencias (opcional)
- [ ] Tests con mocks

---

**Documento creado:** Enero 2025  
**Última actualización:** Enero 2025  
**Versión:** 1.0


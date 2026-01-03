"""
Base Repository - Clase base para todos los repositorios del sistema
Implementa el patrón Repository para abstraer el acceso a datos
"""
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic, Dict, Any
from django.db.models import Model, QuerySet

T = TypeVar('T', bound=Model)


class BaseRepository(ABC, Generic[T]):
    """
    Repositorio base con operaciones CRUD comunes.
    
    Responsabilidades:
    - Encapsular acceso a base de datos
    - Proporcionar métodos CRUD reutilizables
    - Optimizar consultas con select_related/prefetch_related
    
    NO debe:
    - Contener lógica de negocio
    - Conocer detalles de HTTP
    """
    
    @property
    @abstractmethod
    def model(self) -> type:
        """
        Retorna la clase del modelo Django.
        Debe ser implementado por cada repositorio concreto.
        """
        pass
    
    @property
    def select_related_fields(self) -> List[str]:
        """
        Campos para select_related por defecto.
        Sobrescribir en repositorios concretos.
        """
        return []
    
    @property
    def prefetch_related_fields(self) -> List[str]:
        """
        Campos para prefetch_related por defecto.
        Sobrescribir en repositorios concretos.
        """
        return []
    
    def _get_optimized_queryset(self) -> QuerySet:
        """Retorna un queryset optimizado con select_related y prefetch_related"""
        queryset = self.model.objects.all()
        
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        
        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)
        
        return queryset
    
    # ==================== OPERACIONES DE LECTURA ====================
    
    def obtener_por_id(self, id: int) -> T:
        """
        Obtiene un objeto por su ID.
        
        Args:
            id: ID del objeto
            
        Returns:
            Instancia del modelo
            
        Raises:
            Model.DoesNotExist: Si no existe el objeto
        """
        return self._get_optimized_queryset().get(id=id)
    
    def obtener_por_ids(self, ids: List[int]) -> QuerySet:
        """
        Obtiene múltiples objetos por sus IDs.
        
        Args:
            ids: Lista de IDs
            
        Returns:
            QuerySet con los objetos encontrados
        """
        return self._get_optimized_queryset().filter(id__in=ids)
    
    def obtener_todos(self) -> QuerySet:
        """
        Obtiene todos los objetos.
        
        Returns:
            QuerySet con todos los objetos
        """
        return self._get_optimized_queryset()
    
    def filtrar(self, **kwargs) -> QuerySet:
        """
        Filtra objetos según criterios.
        
        Args:
            **kwargs: Criterios de filtrado
            
        Returns:
            QuerySet filtrado
        """
        return self._get_optimized_queryset().filter(**kwargs)
    
    def filtrar_por_criterios(self, criterios: Dict[str, Any]) -> QuerySet:
        """
        Filtra objetos según un diccionario de criterios.
        Ignora valores None.
        
        Args:
            criterios: Diccionario con criterios de filtrado
            
        Returns:
            QuerySet filtrado
        """
        filtros = {k: v for k, v in criterios.items() if v is not None}
        return self._get_optimized_queryset().filter(**filtros)
    
    def obtener_primero(self, **kwargs) -> Optional[T]:
        """
        Obtiene el primer objeto que coincida con los criterios.
        
        Args:
            **kwargs: Criterios de búsqueda
            
        Returns:
            Instancia del modelo o None
        """
        return self._get_optimized_queryset().filter(**kwargs).first()
    
    def existe(self, **kwargs) -> bool:
        """
        Verifica si existe un objeto con los criterios dados.
        
        Args:
            **kwargs: Criterios de búsqueda
            
        Returns:
            True si existe, False si no
        """
        return self.model.objects.filter(**kwargs).exists()
    
    def contar(self, **kwargs) -> int:
        """
        Cuenta objetos según criterios.
        
        Args:
            **kwargs: Criterios de filtrado (opcional)
            
        Returns:
            Cantidad de objetos
        """
        if kwargs:
            return self.model.objects.filter(**kwargs).count()
        return self.model.objects.count()
    
    # ==================== OPERACIONES DE ESCRITURA ====================
    
    def crear(self, **kwargs) -> T:
        """
        Crea un nuevo objeto.
        
        Args:
            **kwargs: Datos del objeto
            
        Returns:
            Instancia creada
        """
        return self.model.objects.create(**kwargs)
    
    def crear_multiple(self, objetos_data: List[Dict[str, Any]]) -> List[T]:
        """
        Crea múltiples objetos de forma eficiente.
        
        Args:
            objetos_data: Lista de diccionarios con datos
            
        Returns:
            Lista de instancias creadas
        """
        objetos = [self.model(**data) for data in objetos_data]
        return self.model.objects.bulk_create(objetos)
    
    def actualizar(self, obj: T, **kwargs) -> T:
        """
        Actualiza un objeto existente.
        
        Args:
            obj: Instancia a actualizar
            **kwargs: Datos a actualizar
            
        Returns:
            Instancia actualizada
        """
        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.save()
        return obj
    
    def actualizar_por_id(self, id: int, **kwargs) -> T:
        """
        Actualiza un objeto por su ID.
        
        Args:
            id: ID del objeto
            **kwargs: Datos a actualizar
            
        Returns:
            Instancia actualizada
        """
        obj = self.obtener_por_id(id)
        return self.actualizar(obj, **kwargs)
    
    def actualizar_multiple(self, queryset: QuerySet, **kwargs) -> int:
        """
        Actualiza múltiples objetos de forma eficiente.
        
        Args:
            queryset: QuerySet con objetos a actualizar
            **kwargs: Datos a actualizar
            
        Returns:
            Cantidad de objetos actualizados
        """
        return queryset.update(**kwargs)
    
    def eliminar(self, obj: T) -> None:
        """
        Elimina un objeto.
        
        Args:
            obj: Instancia a eliminar
        """
        obj.delete()
    
    def eliminar_por_id(self, id: int) -> None:
        """
        Elimina un objeto por su ID.
        
        Args:
            id: ID del objeto a eliminar
        """
        self.model.objects.filter(id=id).delete()
    
    def eliminar_multiple(self, queryset: QuerySet) -> int:
        """
        Elimina múltiples objetos.
        
        Args:
            queryset: QuerySet con objetos a eliminar
            
        Returns:
            Cantidad de objetos eliminados
        """
        count, _ = queryset.delete()
        return count
    
    # ==================== MÉTODOS DE UTILIDAD ====================
    
    def obtener_o_crear(self, defaults: Dict[str, Any] = None, **kwargs) -> tuple:
        """
        Obtiene un objeto existente o lo crea si no existe.
        
        Args:
            defaults: Datos para usar si se crea el objeto
            **kwargs: Criterios de búsqueda
            
        Returns:
            Tupla (instancia, creado)
        """
        return self.model.objects.get_or_create(defaults=defaults, **kwargs)
    
    def actualizar_o_crear(self, defaults: Dict[str, Any] = None, **kwargs) -> tuple:
        """
        Actualiza un objeto existente o lo crea si no existe.
        
        Args:
            defaults: Datos para actualizar o crear
            **kwargs: Criterios de búsqueda
            
        Returns:
            Tupla (instancia, creado)
        """
        return self.model.objects.update_or_create(defaults=defaults, **kwargs)


# 📘 GUÍA PRÁCTICA DE IMPLEMENTACIÓN - ARQUITECTURA EN CAPAS

**Fecha:** Enero 2025  
**Versión:** 1.0  
**Autor:** Documentación Técnica

---

## 📋 TABLA DE CONTENIDOS

1. [Plantillas de Código](#1-plantillas-de-código)
2. [Ejemplos de Refactorización](#2-ejemplos-de-refactorización)
3. [Checklist de Implementación](#3-checklist-de-implementación)
4. [Troubleshooting](#4-troubleshooting)

---

## 1. PLANTILLAS DE CÓDIGO

### 1.1 Plantilla: BaseRepository

```python
# backend/apps/core/base/base_repository.py
from abc import ABC, Generic, TypeVar
from typing import Optional, List, Dict, Any
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

T = TypeVar('T', bound=models.Model)

class BaseRepository(ABC, Generic[T]):
    """
    Clase base abstracta para todos los repositorios
    
    Proporciona métodos comunes para operaciones CRUD
    """
    
    @classmethod
    @abstractmethod
    def get_model(cls) -> type[T]:
        """Retorna el modelo asociado al repositorio"""
        pass
    
    @classmethod
    def obtener_por_id(cls, id: int) -> T:
        """
        Obtiene una instancia por ID
        
        Raises:
            ObjectDoesNotExist: Si no existe el objeto
        """
        try:
            return cls.get_model().objects.get(id=id)
        except cls.get_model().DoesNotExist:
            raise ObjectDoesNotExist(f"{cls.get_model().__name__} con id {id} no existe")
    
    @classmethod
    def obtener_todos(cls) -> models.QuerySet[T]:
        """Obtiene todas las instancias"""
        return cls.get_model().objects.all()
    
    @classmethod
    def crear(cls, data: Dict[str, Any]) -> T:
        """Crea una nueva instancia"""
        return cls.get_model().objects.create(**data)
    
    @classmethod
    def actualizar(cls, instancia: T, data: Dict[str, Any]) -> T:
        """Actualiza una instancia existente"""
        for key, value in data.items():
            setattr(instancia, key, value)
        instancia.save()
        return instancia
    
    @classmethod
    def eliminar(cls, instancia: T) -> None:
        """Elimina una instancia"""
        instancia.delete()
    
    @classmethod
    def existe(cls, **filtros) -> bool:
        """Verifica si existe una instancia con los filtros dados"""
        return cls.get_model().objects.filter(**filtros).exists()
    
    @classmethod
    def contar(cls, **filtros) -> int:
        """Cuenta instancias que cumplen los filtros"""
        return cls.get_model().objects.filter(**filtros).count()
```

### 1.2 Plantilla: BaseService

```python
# backend/apps/core/base/base_service.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from django.core.exceptions import PermissionDenied, ValidationError
from apps.usuarios.models import Usuario

class BaseService(ABC):
    """
    Clase base abstracta para todos los servicios
    
    Proporciona métodos comunes para validación y operaciones de negocio
    """
    
    @classmethod
    @abstractmethod
    def validate_permissions(cls, usuario: Usuario, action: str, **kwargs) -> bool:
        """
        Valida permisos del usuario para una acción
        
        Args:
            usuario: Usuario que realiza la acción
            action: Acción a validar (crear, actualizar, eliminar, etc.)
            **kwargs: Argumentos adicionales para validación
        
        Returns:
            True si tiene permisos
        
        Raises:
            PermissionDenied: Si no tiene permisos
        """
        pass
    
    @classmethod
    @abstractmethod
    def validate_business_rules(cls, data: Dict[str, Any], usuario: Usuario, **kwargs) -> bool:
        """
        Valida reglas de negocio
        
        Args:
            data: Datos a validar
            usuario: Usuario que realiza la acción
            **kwargs: Argumentos adicionales
        
        Returns:
            True si cumple las reglas
        
        Raises:
            ValidationError: Si no cumple las reglas
        """
        pass
    
    @classmethod
    def handle_exception(cls, exception: Exception, context: Dict[str, Any] = None):
        """
        Maneja excepciones de manera consistente
        
        Args:
            exception: Excepción a manejar
            context: Contexto adicional
        """
        # Logging, notificaciones, etc.
        raise exception
```

### 1.3 Plantilla: Repository Específico

```python
# backend/apps/archivos/repositories.py
from typing import Optional, List
from django.db.models import QuerySet
from apps.core.base.base_repository import BaseRepository
from apps.archivos.models import Envio
from apps.usuarios.models import Usuario

class EnvioRepository(BaseRepository[Envio]):
    """Repositorio para gestión de envíos"""
    
    @classmethod
    def get_model(cls):
        return Envio
    
    @classmethod
    def obtener_por_id(cls, envio_id: int) -> Envio:
        """
        Obtiene un envío por ID con relaciones optimizadas
        
        Args:
            envio_id: ID del envío
        
        Returns:
            Instancia de Envio
        
        Raises:
            EnvioNoEncontrado: Si no existe el envío
        """
        try:
            return Envio.objects.select_related(
                'comprador',
                'digitador'
            ).prefetch_related(
                'productos',
                'productos__categoria'
            ).get(id=envio_id)
        except Envio.DoesNotExist:
            from apps.archivos.exceptions import EnvioNoEncontrado
            raise EnvioNoEncontrado(f"Envío {envio_id} no existe")
    
    @classmethod
    def filtrar_por_usuario(cls, usuario: Usuario) -> QuerySet[Envio]:
        """
        Filtra envíos según permisos del usuario
        
        Args:
            usuario: Usuario que realiza la consulta
        
        Returns:
            QuerySet de envíos filtrados
        """
        queryset = Envio.objects.select_related('comprador', 'digitador')
        
        if usuario.es_comprador:
            return queryset.filter(comprador=usuario)
        elif usuario.es_digitador:
            return queryset.filter(digitador=usuario)
        elif usuario.es_gerente or usuario.es_admin:
            return queryset.all()
        else:
            return queryset.none()
    
    @classmethod
    def filtrar_por_estado(cls, estado: str) -> QuerySet[Envio]:
        """Filtra envíos por estado"""
        return Envio.objects.filter(estado=estado)
    
    @classmethod
    def filtrar_por_fecha_rango(
        cls,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None
    ) -> QuerySet[Envio]:
        """Filtra envíos por rango de fechas"""
        queryset = Envio.objects.all()
        
        if fecha_desde:
            queryset = queryset.filter(fecha_emision__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_emision__lte=fecha_hasta)
        
        return queryset
    
    @classmethod
    def existe_hawb(cls, hawb: str) -> bool:
        """Verifica si existe un envío con ese HAWB"""
        return Envio.objects.filter(hawb=hawb).exists()
```

### 1.4 Plantilla: Service Específico

```python
# backend/apps/archivos/services.py
from typing import Dict, Any
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from apps.core.base.base_service import BaseService
from apps.archivos.repositories import EnvioRepository, ProductoRepository
from apps.archivos.models import Envio
from apps.usuarios.models import Usuario
from apps.busqueda.semantic.embedding_service import EmbeddingService
from apps.notificaciones.services import NotificacionService

class EnvioService(BaseService):
    """Servicio para gestión de envíos"""
    
    @classmethod
    def validate_permissions(cls, usuario: Usuario, action: str, **kwargs) -> bool:
        """
        Valida permisos para operaciones de envíos
        
        Reglas:
        - Crear: Solo digitadores, gerentes y admins
        - Actualizar: Solo digitador del envío, gerentes y admins
        - Eliminar: Solo gerentes y admins
        - Ver: Según rol (compradores solo ven sus envíos)
        """
        if action == 'crear':
            if not (usuario.es_digitador or usuario.es_gerente or usuario.es_admin):
                raise PermissionDenied("No tienes permisos para crear envíos")
        
        elif action == 'actualizar':
            envio = kwargs.get('envio')
            if envio and envio.digitador != usuario:
                if not (usuario.es_gerente or usuario.es_admin):
                    raise PermissionDenied("No tienes permisos para actualizar este envío")
        
        elif action == 'eliminar':
            if not (usuario.es_gerente or usuario.es_admin):
                raise PermissionDenied("No tienes permisos para eliminar envíos")
        
        return True
    
    @classmethod
    def validate_business_rules(cls, data: Dict[str, Any], usuario: Usuario, **kwargs) -> bool:
        """
        Valida reglas de negocio para envíos
        
        Reglas:
        - HAWB debe ser único
        - Comprador debe existir
        - Fecha de emisión no puede ser futura
        """
        # Validar HAWB único
        hawb = data.get('hawb')
        if hawb and EnvioRepository.existe_hawb(hawb):
            # Si es actualización, permitir mismo HAWB
            envio_existente = kwargs.get('envio_existente')
            if not envio_existente or envio_existente.hawb != hawb:
                raise ValidationError("El HAWB ya está registrado")
        
        # Validar comprador existe
        comprador_id = data.get('comprador_id') or data.get('comprador')
        if comprador_id:
            from apps.usuarios.repositories import UsuarioRepository
            if not UsuarioRepository.existe(id=comprador_id):
                raise ValidationError("El comprador no existe")
        
        return True
    
    @classmethod
    @transaction.atomic
    def crear_envio(cls, data: Dict[str, Any], usuario: Usuario) -> Envio:
        """
        Crea un nuevo envío aplicando todas las validaciones y reglas
        
        Args:
            data: Datos del envío
            usuario: Usuario que crea el envío
        
        Returns:
            Instancia de Envio creada
        
        Raises:
            PermissionDenied: Si no tiene permisos
            ValidationError: Si no cumple reglas de negocio
        """
        # 1. Validar permisos
        cls.validate_permissions(usuario, 'crear')
        
        # 2. Preparar datos
        datos_envio = cls._preparar_datos_envio(data, usuario)
        
        # 3. Validar reglas de negocio
        cls.validate_business_rules(datos_envio, usuario)
        
        # 4. Crear envío
        envio = EnvioRepository.crear(datos_envio)
        
        # 5. Operaciones post-creación
        cls._post_creacion(envio, data)
        
        return envio
    
    @classmethod
    def _preparar_datos_envio(cls, data: Dict[str, Any], usuario: Usuario) -> Dict[str, Any]:
        """Prepara datos del envío antes de crear"""
        datos = data.copy()
        datos['digitador'] = usuario
        datos['fecha_emision'] = timezone.now()
        
        # Calcular campos derivados si es necesario
        # datos['costo_total'] = cls._calcular_costo_total(data)
        
        return datos
    
    @classmethod
    def _post_creacion(cls, envio: Envio, data: Dict[str, Any]):
        """Operaciones después de crear el envío"""
        # Generar embedding (asíncrono si es posible)
        try:
            EmbeddingService.generar_embedding_envio(envio)
        except Exception as e:
            # Log error pero no fallar la creación
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generando embedding para envío {envio.id}: {e}")
        
        # Enviar notificación
        try:
            NotificacionService.enviar_notificacion_creacion(envio)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error enviando notificación para envío {envio.id}: {e}")
    
    @classmethod
    @transaction.atomic
    def actualizar_envio(
        cls,
        envio: Envio,
        data: Dict[str, Any],
        usuario: Usuario
    ) -> Envio:
        """Actualiza un envío existente"""
        # 1. Validar permisos
        cls.validate_permissions(usuario, 'actualizar', envio=envio)
        
        # 2. Validar reglas de negocio
        cls.validate_business_rules(data, usuario, envio_existente=envio)
        
        # 3. Validar que no se pueda actualizar envío entregado
        if envio.estado == 'Entregado':
            raise ValidationError("No se puede actualizar un envío entregado")
        
        # 4. Actualizar envío
        envio_actualizado = EnvioRepository.actualizar(envio, data)
        
        # 5. Operaciones post-actualización
        cls._post_actualizacion(envio_actualizado, data)
        
        return envio_actualizado
    
    @classmethod
    def _post_actualizacion(cls, envio: Envio, data: Dict[str, Any]):
        """Operaciones después de actualizar el envío"""
        # Si cambió información relevante, regenerar embedding
        campos_relevantes = ['hawb', 'comprador', 'estado']
        if any(campo in data for campo in campos_relevantes):
            try:
                EmbeddingService.generar_embedding_envio(envio)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error regenerando embedding: {e}")
```

### 1.5 Plantilla: ViewSet Simplificada

```python
# backend/apps/archivos/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.archivos.models import Envio
from apps.archivos.serializers import EnvioSerializer
from apps.archivos.services import EnvioService
from apps.archivos.repositories import EnvioRepository
from apps.usuarios.permissions import EnvioPermission

class EnvioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de envíos
    
    Solo maneja HTTP, delega lógica a servicios
    """
    serializer_class = EnvioSerializer
    permission_classes = [IsAuthenticated, EnvioPermission]
    
    def get_queryset(self):
        """Obtiene queryset según permisos del usuario"""
        return EnvioRepository.filtrar_por_usuario(self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Crea un nuevo envío"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Delegar a servicio
        envio = EnvioService.crear_envio(
            data=serializer.validated_data,
            usuario=request.user
        )
        
        # Serializar respuesta
        response_serializer = EnvioSerializer(envio)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Actualiza un envío existente"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Delegar a servicio
        envio = EnvioService.actualizar_envio(
            envio=instance,
            data=serializer.validated_data,
            usuario=request.user
        )
        
        # Serializar respuesta
        response_serializer = EnvioSerializer(envio)
        return Response(response_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Elimina un envío"""
        instance = self.get_object()
        
        # Validar permisos
        EnvioService.validate_permissions(request.user, 'eliminar')
        
        # Eliminar
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Acción personalizada para cambiar estado"""
        envio = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'Estado requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delegar a servicio
        envio = EnvioService.actualizar_envio(
            envio=envio,
            data={'estado': nuevo_estado},
            usuario=request.user
        )
        
        return Response(EnvioSerializer(envio).data)
```

### 1.6 Plantilla: Excepciones de Dominio

```python
# backend/apps/archivos/exceptions.py
from apps.core.exceptions import DomainException

class EnvioNoEncontrado(DomainException):
    """Excepción cuando no se encuentra un envío"""
    pass

class EnvioYaExiste(DomainException):
    """Excepción cuando el envío ya existe"""
    pass

class EnvioNoPuedeEliminarse(DomainException):
    """Excepción cuando no se puede eliminar un envío"""
    pass

class CupoAnualExcedido(DomainException):
    """Excepción cuando se excede el cupo anual"""
    pass
```

---

## 2. EJEMPLOS DE REFACTORIZACIÓN

### 2.1 Ejemplo: Refactorizar View con Lógica de Negocio

#### ❌ ANTES - Lógica en View

```python
# apps/archivos/views.py (ANTES)
class EnvioViewSet(viewsets.ModelViewSet):
    def create(self, request):
        # ⚠️ 80+ líneas de lógica de negocio
        hawb = request.data.get('hawb')
        
        # Validar HAWB único
        if Envio.objects.filter(hawb=hawb).exists():
            return Response(
                {'error': 'HAWB ya existe'},
                status=400
            )
        
        # Validar permisos
        if not (request.user.es_digitador or request.user.es_admin):
            return Response(
                {'error': 'Sin permisos'},
                status=403
            )
        
        # Validar comprador
        comprador_id = request.data.get('comprador_id')
        if not Usuario.objects.filter(id=comprador_id).exists():
            return Response(
                {'error': 'Comprador no existe'},
                status=400
            )
        
        # Crear envío
        envio = Envio.objects.create(
            hawb=hawb,
            comprador_id=comprador_id,
            digitador=request.user,
            fecha_emision=timezone.now(),
            # ... más campos
        )
        
        # Generar embedding
        texto = f"{envio.hawb} {envio.comprador.nombre} ..."
        embedding = generar_embedding(texto)  # Función duplicada
        EnvioEmbedding.objects.create(
            envio=envio,
            embedding=embedding,
            texto_indexado=texto
        )
        
        # Enviar notificación
        Notificacion.objects.create(
            usuario=envio.comprador,
            mensaje=f"Nuevo envío {envio.hawb}"
        )
        
        return Response(EnvioSerializer(envio).data, status=201)
```

#### ✅ DESPUÉS - Lógica en Service

```python
# apps/archivos/views.py (DESPUÉS)
class EnvioViewSet(viewsets.ModelViewSet):
    serializer_class = EnvioSerializer
    permission_classes = [IsAuthenticated, EnvioPermission]
    
    def get_queryset(self):
        return EnvioRepository.filtrar_por_usuario(self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # ✅ Solo una línea - toda la lógica en el servicio
        envio = EnvioService.crear_envio(
            data=serializer.validated_data,
            usuario=request.user
        )
        
        return Response(
            EnvioSerializer(envio).data,
            status=status.HTTP_201_CREATED
        )

# apps/archivos/services.py
class EnvioService(BaseService):
    @classmethod
    @transaction.atomic
    def crear_envio(cls, data: Dict[str, Any], usuario: Usuario) -> Envio:
        # Validar permisos
        cls.validate_permissions(usuario, 'crear')
        
        # Validar reglas de negocio
        cls.validate_business_rules(data, usuario)
        
        # Preparar datos
        datos_envio = cls._preparar_datos_envio(data, usuario)
        
        # Crear envío
        envio = EnvioRepository.crear(datos_envio)
        
        # Operaciones post-creación
        cls._post_creacion(envio, data)
        
        return envio
```

### 2.2 Ejemplo: Refactorizar Acceso Directo a Modelos

#### ❌ ANTES - Acceso Directo

```python
# apps/archivos/services.py (ANTES)
class EnvioService:
    @staticmethod
    def obtener_envios_usuario(usuario):
        # ⚠️ Acceso directo a modelos
        if usuario.es_comprador:
            envios = Envio.objects.filter(comprador=usuario)
        elif usuario.es_digitador:
            envios = Envio.objects.filter(digitador=usuario)
        else:
            envios = Envio.objects.all()
        
        # ⚠️ N+1 queries
        resultados = []
        for envio in envios:
            resultados.append({
                'envio': envio,
                'comprador_nombre': envio.comprador.nombre,  # Query por cada iteración
                'productos': [p.nombre for p in envio.productos.all()]  # Query por cada iteración
            })
        
        return resultados
```

#### ✅ DESPUÉS - Uso de Repository

```python
# apps/archivos/repositories.py
class EnvioRepository(BaseRepository):
    @classmethod
    def filtrar_por_usuario(cls, usuario: Usuario) -> QuerySet[Envio]:
        """Filtra con queryset optimizado"""
        queryset = Envio.objects.select_related(
            'comprador',
            'digitador'
        ).prefetch_related(
            'productos',
            'productos__categoria'
        )
        
        if usuario.es_comprador:
            return queryset.filter(comprador=usuario)
        elif usuario.es_digitador:
            return queryset.filter(digitador=usuario)
        else:
            return queryset.all()

# apps/archivos/services.py (DESPUÉS)
class EnvioService:
    @staticmethod
    def obtener_envios_usuario(usuario):
        # ✅ Usa repositorio con queryset optimizado
        envios = EnvioRepository.filtrar_por_usuario(usuario)
        
        # ✅ Sin N+1 queries gracias a select_related/prefetch_related
        resultados = []
        for envio in envios:
            resultados.append({
                'envio': envio,
                'comprador_nombre': envio.comprador.nombre,  # Sin query adicional
                'productos': [p.nombre for p in envio.productos.all()]  # Sin query adicional
            })
        
        return resultados
```

---

## 3. CHECKLIST DE IMPLEMENTACIÓN

### 3.1 Checklist por Archivo

#### ✅ Repository (repositories.py)

- [ ] Hereda de `BaseRepository`
- [ ] Implementa `get_model()`
- [ ] Métodos usan `select_related()` y `prefetch_related()`
- [ ] No hay queries N+1
- [ ] Excepciones de dominio definidas
- [ ] Métodos documentados con docstrings
- [ ] Métodos estáticos o de clase

#### ✅ Service (services.py)

- [ ] Hereda de `BaseService`
- [ ] Implementa `validate_permissions()`
- [ ] Implementa `validate_business_rules()`
- [ ] No accede directamente a modelos (usa repositorios)
- [ ] No conoce detalles de HTTP
- [ ] Usa transacciones donde sea necesario
- [ ] Métodos documentados con reglas de negocio
- [ ] Manejo de errores consistente

#### ✅ ViewSet (views.py)

- [ ] Menos de 50 líneas por método
- [ ] No contiene lógica de negocio
- [ ] Delega a servicios
- [ ] Usa serializers para validación
- [ ] Permisos definidos
- [ ] Respuestas HTTP correctas
- [ ] Manejo de errores apropiado

#### ✅ Serializer (serializers.py)

- [ ] Valida formato de datos
- [ ] No contiene lógica de negocio
- [ ] Campos `read_only` definidos
- [ ] Validaciones personalizadas si es necesario
- [ ] Métodos `to_representation()` si es necesario

---

## 4. TROUBLESHOOTING

### 4.1 Problema: "No puedo acceder a modelos desde servicio"

**Síntoma:**
```python
# Error: No se puede importar Modelo directamente
from apps.archivos.models import Envio
envio = Envio.objects.get(id=1)  # ❌ No hacer esto
```

**Solución:**
```python
# ✅ Usar repositorio
from apps.archivos.repositories import EnvioRepository
envio = EnvioRepository.obtener_por_id(1)
```

---

### 4.2 Problema: "Queries N+1 en búsqueda"

**Síntoma:**
```python
# Muchas queries para pocos resultados
for envio in Envio.objects.all():
    print(envio.comprador.nombre)  # Query por cada iteración
```

**Solución:**
```python
# ✅ Usar select_related
for envio in Envio.objects.select_related('comprador').all():
    print(envio.comprador.nombre)  # Sin queries adicionales
```

---

### 4.3 Problema: "Lógica de negocio duplicada"

**Síntoma:**
```python
# Misma validación en múltiples lugares
if Envio.objects.filter(hawb=hawb).exists():
    raise ValidationError("HAWB existe")
```

**Solución:**
```python
# ✅ Centralizar en servicio
class EnvioService:
    @classmethod
    def validate_business_rules(cls, data, usuario):
        hawb = data.get('hawb')
        if hawb and EnvioRepository.existe_hawb(hawb):
            raise ValidationError("HAWB existe")
```

---

### 4.4 Problema: "View muy grande (>100 líneas)"

**Síntoma:**
```python
# View con mucha lógica
class EnvioViewSet:
    def create(self, request):
        # 100+ líneas de código
        ...
```

**Solución:**
```python
# ✅ Extraer a servicio
class EnvioViewSet:
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        envio = EnvioService.crear_envio(
            data=serializer.validated_data,
            usuario=request.user
        )
        
        return Response(EnvioSerializer(envio).data, status=201)
```

---

## 5. RECURSOS ADICIONALES

### 5.1 Comandos Útiles

```bash
# Buscar lógica de negocio en views
grep -r "if.*usuario\|if.*permiso" backend/apps/*/views.py

# Buscar acceso directo a modelos
grep -r "\.objects\." backend/apps/*/views.py
grep -r "\.objects\." backend/apps/*/services.py

# Contar líneas en views
wc -l backend/apps/*/views.py

# Analizar complejidad
radon cc backend/apps/*/views.py
radon cc backend/apps/*/services.py
```

### 5.2 Herramientas Recomendadas

- **Django Debug Toolbar**: Para detectar queries N+1
- **coverage**: Para medir cobertura de tests
- **pylint/flake8**: Para análisis estático
- **radon**: Para complejidad ciclomática

---

**Documento creado:** Enero 2025  
**Última actualización:** Enero 2025  
**Versión:** 1.0


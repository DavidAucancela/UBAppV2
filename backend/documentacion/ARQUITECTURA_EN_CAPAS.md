# 🏗️ ARQUITECTURA EN CAPAS - SISTEMA UBAPP

**Fecha:** Enero 2025  
**Versión:** 1.0  
**Autor:** Documentación Técnica

---

## 📋 TABLA DE CONTENIDOS

1. [Introducción](#introducción)
2. [Arquitectura Propuesta](#arquitectura-propuesta)
3. [Capas del Sistema](#capas-del-sistema)
4. [Patrones de Diseño Identificados](#patrones-de-diseño-identificados)
5. [Recomendaciones y Correcciones](#recomendaciones-y-correcciones)
6. [Plan de Implementación](#plan-de-implementación)
7. [Diagramas de Arquitectura](#diagramas-de-arquitectura)

---

## 1. INTRODUCCIÓN

### 1.1 Objetivo

Este documento describe la arquitectura en capas propuesta para el sistema UBApp, organizando el código en cuatro capas principales:

- **Capa de Presentación**: Manejo de peticiones HTTP y respuestas
- **Capa de Lógica de Negocio**: Reglas de negocio y orquestación
- **Capa de Datos**: Acceso a base de datos y persistencia
- **Capa Semántica**: Procesamiento de embeddings y búsqueda semántica

### 1.2 Estado Actual

El sistema actualmente está organizado por **apps Django** (usuarios, archivos, busqueda, notificaciones), pero la lógica de negocio está mezclada en las vistas (views), lo que dificulta:

- Mantenibilidad
- Testabilidad
- Reutilización de código
- Escalabilidad

---

## 2. ARQUITECTURA PROPUESTA

### 2.1 Visión General

```
┌─────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                 │
│  (Views, Serializers, Permissions, Validators)          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              CAPA DE LÓGICA DE NEGOCIO                   │
│  (Services, Business Logic, Orchestration)               │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌─────────▼──────────┐
│  CAPA DE DATOS │      │  CAPA SEMÁNTICA    │
│  (Repositories,│      │  (Embeddings,      │
│   Models, ORM) │      │   Vector Search)   │
└────────────────┘      └────────────────────┘
```

### 2.2 Principios de Diseño

1. **Separación de Responsabilidades**: Cada capa tiene una responsabilidad única
2. **Dependencia Unidireccional**: Las capas superiores dependen de las inferiores, no al revés
3. **Inversión de Dependencias**: Las capas superiores definen interfaces, las inferiores las implementan
4. **Testabilidad**: Cada capa puede ser testeada independientemente

---

## 3. CAPAS DEL SISTEMA

### 3.1 CAPA DE PRESENTACIÓN

**Responsabilidad**: Manejar la comunicación HTTP, validar entrada, serializar salida.

**Componentes**:
- **Views/ViewSets**: Endpoints REST
- **Serializers**: Serialización/deserialización de datos
- **Permissions**: Control de acceso
- **Validators**: Validación de entrada
- **Exception Handlers**: Manejo de errores HTTP

**Ubicación Propuesta**:
```
backend/apps/
├── usuarios/
│   ├── views.py          # ViewSets
│   ├── serializers.py    # Serializers
│   ├── permissions.py    # Permisos
│   └── validators.py     # Validadores
├── archivos/
│   └── ...
└── busqueda/
    └── ...
```

**Ejemplo de Estructura**:
```python
# apps/usuarios/views.py
class UsuarioViewSet(viewsets.ModelViewSet):
    """Solo maneja HTTP, delega lógica a servicios"""
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Validar entrada
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Delegar a servicio
        usuario = UsuarioService.crear_usuario(
            data=serializer.validated_data,
            usuario_creador=request.user
        )
        
        # Serializar salida
        return Response(
            UsuarioSerializer(usuario).data,
            status=status.HTTP_201_CREATED
        )
```

**Reglas**:
- ✅ NO debe contener lógica de negocio
- ✅ NO debe acceder directamente a modelos (excepto para filtros básicos)
- ✅ DEBE validar entrada y serializar salida
- ✅ DEBE delegar operaciones complejas a la capa de servicios

---

### 3.2 CAPA DE LÓGICA DE NEGOCIO

**Responsabilidad**: Implementar reglas de negocio, orquestar operaciones, validar reglas de dominio.

**Componentes**:
- **Services**: Servicios de dominio
- **Business Logic**: Reglas de negocio
- **Orchestration**: Coordinación entre múltiples operaciones
- **Domain Models**: Modelos de dominio (si se usa DDD)

**Ubicación Propuesta**:
```
backend/apps/
├── usuarios/
│   ├── services.py       # ⭐ NUEVO
│   │   ├── UsuarioService
│   │   ├── AutenticacionService
│   │   └── PermisosService
│   └── business_logic.py # ⭐ NUEVO (opcional)
├── archivos/
│   ├── services.py       # ⭐ NUEVO
│   │   ├── EnvioService
│   │   ├── ProductoService
│   │   └── TarifaService
│   └── business_logic.py
└── busqueda/
    ├── services.py       # ⭐ NUEVO
    │   ├── BusquedaService
    │   └── BusquedaSemanticaService
    └── ...
```

**Ejemplo de Estructura**:
```python
# apps/usuarios/services.py
class UsuarioService:
    """Servicio para operaciones de usuarios"""
    
    @staticmethod
    def crear_usuario(data: dict, usuario_creador) -> Usuario:
        """
        Crea un usuario aplicando reglas de negocio
        
        Reglas:
        - Solo admin puede crear usuarios
        - Validar cédula única
        - Validar correo único
        - Asignar rol según permisos
        """
        # Validar permisos
        if not usuario_creador.es_admin:
            raise PermissionDenied("Solo administradores pueden crear usuarios")
        
        # Validar reglas de negocio
        if UsuarioRepository.existe_cedula(data['cedula']):
            raise ValidationError("La cédula ya está registrada")
        
        if UsuarioRepository.existe_correo(data['correo']):
            raise ValidationError("El correo ya está registrado")
        
        # Crear usuario
        usuario = UsuarioRepository.crear(data)
        
        # Operaciones post-creación
        NotificacionService.enviar_bienvenida(usuario)
        
        return usuario
    
    @staticmethod
    def actualizar_perfil(usuario: Usuario, data: dict) -> Usuario:
        """Actualiza perfil con validaciones de negocio"""
        # Validar que no cambie rol (solo admin puede)
        if 'rol' in data and not usuario.es_admin:
            raise PermissionDenied("No puedes cambiar tu rol")
        
        # Actualizar
        return UsuarioRepository.actualizar(usuario, data)
```

**Reglas**:
- ✅ DEBE contener toda la lógica de negocio
- ✅ NO debe conocer detalles de HTTP (request, response)
- ✅ PUEDE usar múltiples repositorios
- ✅ PUEDE orquestar múltiples operaciones
- ✅ DEBE validar reglas de dominio

---

### 3.3 CAPA DE DATOS

**Responsabilidad**: Acceso a datos, persistencia, consultas a base de datos.

**Componentes**:
- **Repositories**: Abstracción de acceso a datos
- **Models**: Modelos de Django ORM
- **Querysets**: Consultas optimizadas
- **Migrations**: Migraciones de base de datos

**Ubicación Propuesta**:
```
backend/apps/
├── usuarios/
│   ├── repositories.py   # ⭐ NUEVO
│   │   ├── UsuarioRepository
│   │   └── CompradorRepository
│   ├── models.py        # Existente
│   └── querysets.py     # ⭐ NUEVO (opcional)
├── archivos/
│   ├── repositories.py
│   ├── models.py
│   └── querysets.py
└── busqueda/
    ├── repositories.py
    └── models.py
```

**Ejemplo de Estructura**:
```python
# apps/usuarios/repositories.py
class UsuarioRepository:
    """Repositorio para acceso a datos de usuarios"""
    
    @staticmethod
    def obtener_por_id(usuario_id: int) -> Usuario:
        """Obtiene un usuario por ID"""
        try:
            return Usuario.objects.select_related().get(id=usuario_id)
        except Usuario.DoesNotExist:
            raise UsuarioNoEncontrado(f"Usuario {usuario_id} no existe")
    
    @staticmethod
    def crear(data: dict) -> Usuario:
        """Crea un nuevo usuario"""
        return Usuario.objects.create(**data)
    
    @staticmethod
    def actualizar(usuario: Usuario, data: dict) -> Usuario:
        """Actualiza un usuario"""
        for key, value in data.items():
            setattr(usuario, key, value)
        usuario.save()
        return usuario
    
    @staticmethod
    def existe_cedula(cedula: str) -> bool:
        """Verifica si existe un usuario con esa cédula"""
        return Usuario.objects.filter(cedula=cedula).exists()
    
    @staticmethod
    def existe_correo(correo: str) -> bool:
        """Verifica si existe un usuario con ese correo"""
        return Usuario.objects.filter(correo=correo).exists()
    
    @staticmethod
    def filtrar_por_rol(rol: int, usuario_actual: Usuario):
        """Filtra usuarios según permisos del usuario actual"""
        queryset = Usuario.objects.all()
        
        if usuario_actual.es_admin:
            return queryset
        elif usuario_actual.es_gerente:
            return queryset.exclude(rol=1)  # Sin admins
        elif usuario_actual.es_digitador:
            return queryset.filter(rol__in=[3, 4])  # Solo digitadores y compradores
        else:
            return queryset.filter(id=usuario_actual.id)  # Solo su perfil
```

**Reglas**:
- ✅ DEBE encapsular acceso a base de datos
- ✅ NO debe contener lógica de negocio
- ✅ DEBE usar querysets optimizados (select_related, prefetch_related)
- ✅ PUEDE definir excepciones de dominio (UsuarioNoEncontrado)

---

### 3.4 CAPA SEMÁNTICA

**Responsabilidad**: Procesamiento de embeddings, búsqueda semántica, generación de vectores.

**Componentes**:
- **Embedding Services**: Generación de embeddings
- **Vector Search**: Búsqueda en espacio vectorial
- **Semantic Repositories**: Acceso a datos semánticos
- **Text Processing**: Procesamiento de texto

**Ubicación Propuesta**:
```
backend/apps/
├── busqueda/
│   ├── semantic/
│   │   ├── embedding_service.py    # ⭐ REORGANIZAR
│   │   ├── vector_search.py        # ⭐ NUEVO
│   │   ├── text_processor.py       # ⭐ NUEVO
│   │   └── semantic_repository.py # ⭐ NUEVO
│   └── utils_embeddings.py         # ⚠️ Mover a semantic/
└── core/
    └── semantic/
        └── base_embedding_service.py  # ⭐ NUEVO (interfaz)
```

**Ejemplo de Estructura**:
```python
# apps/busqueda/semantic/embedding_service.py
class EmbeddingService:
    """Servicio para generación de embeddings"""
    
    def __init__(self, provider: str = 'openai'):
        self.provider = provider
        self.client = self._get_client()
    
    def generar_embedding(self, texto: str, modelo: str = None) -> dict:
        """
        Genera embedding de un texto
        
        Returns:
            {
                'embedding': List[float],
                'tokens': int,
                'costo': float,
                'modelo': str
            }
        """
        # Lógica de generación
        pass
    
    def generar_embedding_envio(self, envio: Envio) -> EnvioEmbedding:
        """Genera embedding para un envío"""
        texto = TextProcessor.generar_texto_envio(envio)
        resultado = self.generar_embedding(texto)
        
        return SemanticRepository.guardar_embedding(
            envio=envio,
            embedding=resultado['embedding'],
            texto_indexado=texto,
            modelo=resultado['modelo']
        )

# apps/busqueda/semantic/vector_search.py
class VectorSearchService:
    """Servicio para búsqueda en espacio vectorial"""
    
    def buscar_similares(
        self,
        embedding_consulta: List[float],
        limite: int = 20,
        umbral: float = 0.35
    ) -> List[dict]:
        """
        Busca envíos similares usando búsqueda vectorial
        
        Usa pgvector para búsqueda eficiente en PostgreSQL
        """
        return SemanticRepository.buscar_por_similitud(
            embedding=embedding_consulta,
            limite=limite,
            umbral=umbral
        )
```

**Reglas**:
- ✅ DEBE encapsular toda la lógica de embeddings
- ✅ DEBE ser independiente del proveedor (OpenAI, Cohere, etc.)
- ✅ DEBE usar repositorios semánticos para persistencia
- ✅ PUEDE usar caché para embeddings frecuentes

---

## 4. PATRONES DE DISEÑO IDENTIFICADOS

### 4.1 Patrones Actuales

#### ✅ **Repository Pattern** (Parcial)
- **Ubicación**: No implementado explícitamente
- **Estado**: Los modelos Django actúan como repositorios implícitos
- **Recomendación**: Implementar repositorios explícitos

#### ✅ **Service Layer Pattern** (Parcial)
- **Ubicación**: `utils_*.py` contienen lógica similar a servicios
- **Estado**: Lógica dispersa en utils y views
- **Recomendación**: Consolidar en servicios estructurados

#### ✅ **Serializer Pattern** (Completo)
- **Ubicación**: `serializers.py` en cada app
- **Estado**: ✅ Bien implementado
- **Uso**: Serialización/deserialización de datos

#### ✅ **ViewSet Pattern** (Completo)
- **Ubicación**: `views.py` usando DRF ViewSets
- **Estado**: ✅ Bien implementado
- **Uso**: Endpoints REST

#### ⚠️ **Factory Pattern** (No implementado)
- **Estado**: No hay factories para creación de objetos complejos
- **Recomendación**: Implementar para creación de envíos, usuarios, etc.

#### ⚠️ **Strategy Pattern** (Parcial)
- **Ubicación**: `utils_embeddings.py` tiene múltiples métricas
- **Estado**: Métricas de similitud implementadas, pero no como estrategias
- **Recomendación**: Refactorizar a Strategy Pattern

#### ⚠️ **Observer Pattern** (Parcial)
- **Ubicación**: Django Signals en `signals.py`
- **Estado**: ✅ Implementado con signals
- **Uso**: Notificaciones cuando cambia estado de envío

#### ⚠️ **Singleton Pattern** (Implícito)
- **Ubicación**: `get_openai_client()` en múltiples lugares
- **Estado**: Función global, no singleton real
- **Recomendación**: Implementar singleton para clientes externos

### 4.2 Patrones Recomendados

#### 🎯 **Dependency Injection**
```python
# Ejemplo: Inyectar dependencias en servicios
class BusquedaSemanticaService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_search: VectorSearchService,
        repository: SemanticRepository
    ):
        self.embedding_service = embedding_service
        self.vector_search = vector_search
        self.repository = repository
```

#### 🎯 **Unit of Work**
```python
# Para transacciones complejas
class EnvioService:
    def crear_envio_completo(self, data: dict):
        with transaction.atomic():
            envio = EnvioRepository.crear(data['envio'])
            productos = [ProductoRepository.crear(p) for p in data['productos']]
            EnvioRepository.agregar_productos(envio, productos)
            EmbeddingService.generar_embedding_envio(envio)
            NotificacionService.enviar_notificacion(envio)
```

#### 🎯 **Specification Pattern**
```python
# Para consultas complejas
class EnvioSpecification:
    @staticmethod
    def por_estado(estado: str):
        return Q(estado=estado)
    
    @staticmethod
    def por_comprador(comprador: Usuario):
        return Q(comprador=comprador)
    
    @staticmethod
    def por_fecha_rango(fecha_desde, fecha_hasta):
        return Q(fecha_emision__gte=fecha_desde, fecha_emision__lte=fecha_hasta)
```

---

## 5. RECOMENDACIONES Y CORRECCIONES

### 5.1 🔴 CRÍTICO - Separar Lógica de Negocio

**Problema Actual**:
```python
# apps/busqueda/views.py - Línea 196
@action(detail=False, methods=['post'])
def busqueda_semantica(self, request):
    # ⚠️ 200+ líneas de lógica de negocio en la vista
    consulta_texto = request.data.get('texto', '').strip()
    # ... lógica de generación de embedding ...
    # ... lógica de búsqueda ...
    # ... lógica de filtrado ...
    # ... lógica de ordenamiento ...
```

**Solución**:
```python
# apps/busqueda/views.py
@action(detail=False, methods=['post'])
def busqueda_semantica(self, request):
    serializer = BusquedaSemanticaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Delegar a servicio
    resultado = BusquedaSemanticaService.buscar(
        consulta=serializer.validated_data['texto'],
        usuario=request.user,
        filtros=serializer.validated_data.get('filtrosAdicionales', {}),
        limite=serializer.validated_data.get('limite', 20)
    )
    
    return Response(resultado)

# apps/busqueda/services.py - ⭐ NUEVO
class BusquedaSemanticaService:
    @staticmethod
    def buscar(consulta: str, usuario: Usuario, filtros: dict, limite: int):
        # Toda la lógica aquí
        pass
```

### 5.2 🔴 CRÍTICO - Eliminar Duplicación de Código

**Problema Actual**:
- `get_openai_client()` duplicado en `views.py` y `utils_embeddings.py`
- Lógica de generación de embeddings duplicada

**Solución**:
```python
# apps/busqueda/semantic/embedding_service.py - ⭐ NUEVO
class EmbeddingService:
    _client = None
    
    @classmethod
    def get_client(cls):
        """Singleton para cliente OpenAI"""
        if cls._client is None:
            cls._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return cls._client
```

### 5.3 🟡 IMPORTANTE - Implementar Repositorios

**Problema Actual**:
- Acceso directo a modelos desde views y services
- Querysets duplicados

**Solución**:
```python
# apps/archivos/repositories.py - ⭐ NUEVO
class EnvioRepository:
    @staticmethod
    def obtener_por_usuario(usuario: Usuario):
        """Queryset optimizado reutilizable"""
        queryset = Envio.objects.select_related(
            'comprador'
        ).prefetch_related(
            'productos'
        )
        
        if usuario.es_comprador:
            return queryset.filter(comprador=usuario)
        return queryset
```

### 5.4 🟡 IMPORTANTE - Centralizar Manejo de Errores

**Problema Actual**:
- Manejo de errores disperso
- Respuestas inconsistentes

**Solución**:
```python
# apps/core/exceptions.py - ⭐ NUEVO
class CustomExceptionHandler:
    @staticmethod
    def handle(exc, context):
        # Manejo centralizado
        pass

# settings.py
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}
```

### 5.5 🟢 MEJORA - Optimizar Consultas

**Problema Actual**:
```python
# apps/busqueda/views.py - Línea 592
for envio in envios_queryset[:500]:  # ⚠️ Carga 500 en memoria
    envio_embedding = EnvioEmbedding.objects.get(...)  # ⚠️ N+1 queries
```

**Solución**:
```python
# Usar prefetch_related y búsqueda vectorial nativa
embeddings = EnvioEmbedding.objects.filter(
    envio__in=envios_queryset
).select_related('envio').prefetch_related('envio__productos')

# O mejor: usar pgvector para búsqueda nativa
resultados = EnvioEmbedding.objects.annotate(
    similitud=CosineDistance('embedding_vector', embedding_consulta)
).order_by('similitud')[:limite]
```

---

## 6. PLAN DE IMPLEMENTACIÓN

### 6.1 Fase 1: Preparación (Semana 1-2)

#### Tareas:
1. ✅ Crear estructura de carpetas para servicios
2. ✅ Crear estructura de carpetas para repositorios
3. ✅ Documentar arquitectura actual
4. ✅ Identificar código duplicado

#### Estructura a Crear:
```
backend/apps/
├── usuarios/
│   ├── services.py       # ⭐ NUEVO
│   └── repositories.py   # ⭐ NUEVO
├── archivos/
│   ├── services.py       # ⭐ NUEVO
│   └── repositories.py   # ⭐ NUEVO
├── busqueda/
│   ├── services.py       # ⭐ NUEVO
│   ├── repositories.py   # ⭐ NUEVO
│   └── semantic/         # ⭐ NUEVO
│       ├── embedding_service.py
│       ├── vector_search.py
│       └── text_processor.py
└── core/
    ├── exceptions.py     # ⭐ NUEVO
    └── base/             # ⭐ NUEVO
        ├── base_service.py
        └── base_repository.py
```

### 6.2 Fase 2: Refactorización de Capa de Datos (Semana 3-4)

#### Tareas:
1. Crear repositorios para cada modelo principal
2. Mover lógica de querysets a repositorios
3. Optimizar consultas (select_related, prefetch_related)
4. Crear excepciones de dominio

#### Ejemplo:
```python
# apps/archivos/repositories.py
class EnvioRepository:
    @staticmethod
    def obtener_por_id(envio_id: int) -> Envio:
        return Envio.objects.select_related(
            'comprador'
        ).prefetch_related(
            'productos'
        ).get(id=envio_id)
    
    @staticmethod
    def filtrar_por_usuario(usuario: Usuario):
        queryset = Envio.objects.select_related('comprador')
        if usuario.es_comprador:
            return queryset.filter(comprador=usuario)
        return queryset
```

### 6.3 Fase 3: Refactorización de Capa de Negocio (Semana 5-6)

#### Tareas:
1. Extraer lógica de negocio de views a services
2. Crear servicios para cada dominio
3. Implementar reglas de negocio en servicios
4. Mover utilidades a servicios apropiados

#### Ejemplo:
```python
# apps/archivos/services.py
class EnvioService:
    @staticmethod
    def crear_envio(data: dict, usuario: Usuario) -> Envio:
        # Validar permisos
        if not usuario.puede_crear_envio():
            raise PermissionDenied()
        
        # Validar reglas de negocio
        if not EnvioService.validar_cupo_anual(usuario, data['peso_total']):
            raise ValidationError("Cupo anual excedido")
        
        # Crear envío
        envio = EnvioRepository.crear(data)
        
        # Operaciones post-creación
        EmbeddingService.generar_embedding_envio(envio)
        NotificacionService.enviar_notificacion(envio)
        
        return envio
```

### 6.4 Fase 4: Refactorización de Capa Semántica (Semana 7-8)

#### Tareas:
1. Reorganizar código de embeddings
2. Crear servicios semánticos
3. Implementar repositorio semántico
4. Optimizar búsqueda vectorial

#### Ejemplo:
```python
# apps/busqueda/semantic/embedding_service.py
class EmbeddingService:
    def generar_embedding_envio(self, envio: Envio) -> EnvioEmbedding:
        texto = TextProcessor.generar_texto_envio(envio)
        resultado = self._generar_embedding(texto)
        return SemanticRepository.guardar_embedding(envio, resultado)
```

### 6.5 Fase 5: Refactorización de Capa de Presentación (Semana 9-10)

#### Tareas:
1. Simplificar views (solo HTTP)
2. Mejorar serializers
3. Centralizar manejo de errores
4. Agregar validaciones

### 6.6 Fase 6: Testing y Documentación (Semana 11-12)

#### Tareas:
1. Escribir tests unitarios para servicios
2. Escribir tests de integración
3. Actualizar documentación
4. Code review

---

## 7. DIAGRAMAS DE ARQUITECTURA

### 7.1 Flujo de Petición HTTP

```
Cliente (Angular)
    │
    ▼
┌─────────────────────────────────────┐
│   CAPA DE PRESENTACIÓN              │
│   - ViewSet                         │
│   - Serializer                      │
│   - Permission                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   CAPA DE LÓGICA DE NEGOCIO         │
│   - Service                         │
│   - Business Logic                  │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐  ┌──────────────┐
│ CAPA DATOS   │  │ CAPA SEMÁNTICA│
│ - Repository │  │ - Embedding   │
│ - Model      │  │ - Vector     │
└──────────────┘  └──────────────┘
       │                │
       └───────┬────────┘
               │
               ▼
        PostgreSQL
```

### 7.2 Ejemplo: Búsqueda Semántica

```
POST /api/busqueda/semantica/
    │
    ▼
BusquedaViewSet.busqueda_semantica()
    │
    ▼
BusquedaSemanticaService.buscar()
    │
    ├──► EmbeddingService.generar_embedding()
    │    │
    │    └──► OpenAI API
    │
    ├──► EnvioRepository.filtrar_por_usuario()
    │    │
    │    └──► PostgreSQL (filtros)
    │
    └──► VectorSearchService.buscar_similares()
         │
         └──► PostgreSQL + pgvector (búsqueda vectorial)
```

---

## 8. MÉTRICAS DE ÉXITO

### 8.1 Código

- ✅ Reducción de líneas en views (objetivo: -50%)
- ✅ Aumento de cobertura de tests (objetivo: >80%)
- ✅ Reducción de duplicación (objetivo: <5%)

### 8.2 Mantenibilidad

- ✅ Tiempo para agregar nueva funcionalidad (objetivo: -30%)
- ✅ Tiempo para entender código existente (objetivo: -40%)

### 8.3 Performance

- ✅ Reducción de queries N+1 (objetivo: 0)
- ✅ Tiempo de respuesta de búsqueda semántica (objetivo: <500ms)

---

## 9. CONCLUSIÓN

La implementación de arquitectura en capas mejorará significativamente:

1. **Mantenibilidad**: Código más organizado y fácil de entender
2. **Testabilidad**: Cada capa puede ser testeada independientemente
3. **Escalabilidad**: Fácil agregar nuevas funcionalidades
4. **Reutilización**: Servicios y repositorios reutilizables
5. **Separación de Responsabilidades**: Cada componente tiene un propósito claro

**Próximos Pasos**:
1. Revisar y aprobar este documento
2. Crear issues/tareas para cada fase
3. Comenzar con Fase 1 (Preparación)

---

**Documento creado:** Enero 2025  
**Última actualización:** Enero 2025  
**Versión:** 1.0


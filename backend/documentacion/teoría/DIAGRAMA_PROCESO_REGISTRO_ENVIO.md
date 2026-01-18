# Diagrama del Proceso de Registro de Envío

## 📊 Diagrama Completo del Flujo

```mermaid
graph TB
    subgraph Frontend["🖥️ FRONTEND - Angular"]
        A[Usuario ingresa datos<br/>en formulario] --> B{Validar<br/>formulario}
        B -->|Válido| C[ApiService.createEnvio]
        B -->|Inválido| A
        C --> D[HTTP POST Request<br/>/api/envios/envios/]
        D --> E[Mostrar loading]
        E --> F{Respuesta<br/>Backend}
        F -->|201 Created| G[Mostrar éxito<br/>Actualizar lista]
        F -->|400/500 Error| H[Mostrar error<br/>al usuario]
    end

    subgraph Backend_Entry["🔌 BACKEND - Django REST Framework"]
        D --> I[EnvioViewSet.create]
        I --> J[EnvioCreateSerializer<br/>Validación de datos]
        J -->|Válido| K[EnvioService.crear_envio]
        J -->|Inválido| L[Retornar errores<br/>400 Bad Request]
        L --> F
    end

    subgraph Backend_Service["⚙️ BACKEND - Servicio (Lógica de Negocio)"]
        K --> M{Validar<br/>permisos}
        M -->|Admin/Gerente/<br/>Digitador| N{Validar<br/>HAWB único}
        M -->|Sin permisos| O[ValidationError<br/>403 Forbidden]
        O --> F
        N -->|HAWB existe| P[ValidationError<br/>HAWB duplicado]
        N -->|HAWB único| Q{Validar<br/>cupo comprador}
        P --> F
        Q -->|Cupo OK| R[Calcular costo<br/>del servicio]
        Q -->|Cupo excedido| S[ValidationError<br/>Cupo insuficiente]
        S --> F
        R --> T[Iniciar transacción<br/>atómica]
    end

    subgraph Backend_Repository["💾 BACKEND - Repositorio (Acceso a Datos)"]
        T --> U[envio_repository.crear<br/>Crear registro Envio]
        U --> V[producto_repository.crear<br/>Crear productos asociados]
        V --> W[envio.calcular_totales<br/>Recalcular totales]
        W --> X[Calcular costo<br/>basado en tarifas]
    end

    subgraph Backend_Processing["🔄 BACKEND - Procesamiento Asíncrono"]
        X --> Y[_generar_embedding_async<br/>Búsqueda semántica]
        Y --> Z[_notificar_envio_creado<br/>Notificar comprador]
        Z --> AA[log_operacion<br/>Registrar auditoría]
        AA --> AB[log_metrica<br/>Registrar métrica]
    end

    subgraph Backend_Response["📤 BACKEND - Respuesta"]
        AB --> AC[EnvioSerializer<br/>Serializar respuesta]
        AC --> AD[HTTP 201 Created<br/>Retornar envío creado]
        AD --> F
    end

    style Frontend fill:#e1f5ff
    style Backend_Entry fill:#fff4e1
    style Backend_Service fill:#ffe1f5
    style Backend_Repository fill:#e1ffe1
    style Backend_Processing fill:#f5e1ff
    style Backend_Response fill:#ffe1e1
```

## 🔄 Flujo Detallado Paso a Paso

### 1. FRONTEND - Captura de Datos

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Formulario Angular
    participant AS as ApiService
    participant HTTP as HTTP Client

    U->>F: Ingresa datos del envío
    U->>F: HAWB, comprador, productos, etc.
    U->>F: Clic en "Guardar"
    F->>F: Validar formulario
    alt Formulario válido
        F->>AS: createEnvio(envioData)
        AS->>HTTP: POST /api/envios/envios/
        Note over HTTP: Headers: Authorization, Content-Type
        Note over HTTP: Body: JSON con datos del envío
    else Formulario inválido
        F->>U: Mostrar errores de validación
    end
```

### 2. BACKEND - Recepción y Validación Inicial

```mermaid
sequenceDiagram
    participant HTTP as HTTP Request
    participant VS as EnvioViewSet
    participant SR as EnvioCreateSerializer
    participant SVC as EnvioService

    HTTP->>VS: POST /api/envios/envios/
    VS->>VS: Verificar autenticación
    VS->>VS: Obtener usuario actual
    VS->>SR: Validar datos (data=request.data)
    
    SR->>SR: Validar campos requeridos
    SR->>SR: Validar tipos de datos
    SR->>SR: Validar relaciones (comprador)
    
    alt Datos válidos
        SR->>SVC: crear_envio(validated_data, usuario)
    else Datos inválidos
        SR-->>VS: Errores de validación
        VS-->>HTTP: 400 Bad Request + errores
    end
```

### 3. BACKEND - Lógica de Negocio

```mermaid
sequenceDiagram
    participant SVC as EnvioService
    participant PERM as Validación Permisos
    participant REPO as EnvioRepository
    participant USER as UsuarioService
    participant TAR as TarifaService

    SVC->>PERM: validar_puede_gestionar_envios(usuario)
    alt Usuario autorizado
        PERM->>REPO: existe_hawb(hawb)
        alt HAWB existe
            REPO-->>SVC: True
            SVC-->>VS: ValidationError (HAWB duplicado)
        else HAWB único
            REPO-->>SVC: False
            SVC->>USER: validar_cupo_disponible(comprador, peso)
            alt Cupo suficiente
                USER-->>SVC: OK
                SVC->>TAR: calcular_costo_servicio(productos)
                TAR-->>SVC: costo_total
                SVC->>SVC: Iniciar transacción atómica
            else Cupo insuficiente
                USER-->>SVC: CupoExcedidoError
                SVC-->>VS: ValidationError
            end
        end
    else Usuario no autorizado
        PERM-->>SVC: PermissionDenied
        SVC-->>VS: 403 Forbidden
    end
```

### 4. BACKEND - Creación en Base de Datos

```mermaid
sequenceDiagram
    participant SVC as EnvioService
    participant TX as Transacción Atómica
    participant E_REPO as EnvioRepository
    participant P_REPO as ProductoRepository
    participant T_REPO as TarifaRepository
    participant DB as Base de Datos

    SVC->>TX: Iniciar transacción atómica
    TX->>E_REPO: crear(**data)
    E_REPO->>DB: INSERT INTO envio
    DB-->>E_REPO: Envio creado (id generado)
    E_REPO-->>TX: envio
    
    loop Para cada producto
        TX->>P_REPO: crear(envio=envio, **producto_data)
        P_REPO->>T_REPO: buscar_tarifa_aplicable(categoria, peso)
        T_REPO->>DB: SELECT tarifa WHERE...
        DB-->>T_REPO: Tarifa
        T_REPO->>T_REPO: calcular_costo(peso)
        T_REPO-->>P_REPO: costo_producto
        P_REPO->>DB: INSERT INTO producto
        DB-->>P_REPO: Producto creado
        P_REPO-->>TX: producto
    end
    
    TX->>E_REPO: calcular_totales()
    E_REPO->>E_REPO: Sumar pesos, valores, cantidades
    E_REPO->>E_REPO: calcular_costo_servicio()
    E_REPO->>DB: UPDATE envio SET totales...
    DB-->>E_REPO: Envio actualizado
    E_REPO-->>TX: envio con totales
    
    alt Todo OK
        TX->>TX: commit()
        TX-->>SVC: envio creado exitosamente
    else Error
        TX->>TX: rollback()
        TX-->>SVC: Exception
    end
```

### 5. BACKEND - Procesamiento Asíncrono

```mermaid
sequenceDiagram
    participant SVC as EnvioService
    participant SEM as BusquedaSemanticaService
    participant NOT as NotificacionRepository
    participant LOG as Sistema de Logs
    participant MET as Sistema de Métricas

    SVC->>SEM: _generar_embedding_async(envio)
    Note over SEM: Proceso asíncrono<br/>No bloquea creación
    SEM->>SEM: Generar embedding para búsqueda
    SEM->>SEM: Guardar embedding
    
    SVC->>NOT: _notificar_envio_creado(envio)
    NOT->>NOT: crear_notificacion_envio_asignado
    NOT->>DB: INSERT INTO notificacion
    Note over NOT: Notificar al comprador<br/>sobre nuevo envío
    
    SVC->>LOG: log_operacion(crear, Envio, ...)
    LOG->>DB: INSERT INTO log_operacion
    Note over LOG: Registrar auditoría<br/>de la operación
    
    SVC->>MET: log_metrica(envio_creado, 1, ...)
    MET->>DB: INSERT INTO metrica
    Note over MET: Registrar métrica<br/>para estadísticas
```

### 6. BACKEND - Respuesta al Frontend

```mermaid
sequenceDiagram
    participant SVC as EnvioService
    participant VS as EnvioViewSet
    participant SR as EnvioSerializer
    participant HTTP as HTTP Response

    SVC-->>VS: envio (objeto Envio creado)
    VS->>SR: EnvioSerializer(envio)
    SR->>SR: Serializar datos del envío
    SR->>SR: Incluir relaciones (comprador_info, productos)
    SR-->>VS: data (dict serializado)
    VS->>HTTP: Response(data, status=201)
    HTTP-->>Frontend: JSON con envío creado
```

## 📋 Resumen del Flujo Completo

### Tiempos Estimados por Etapa

| Etapa | Componente | Tiempo Estimado | Tipo |
|-------|-----------|-----------------|------|
| 1. Validación Frontend | Angular Form | 0.01-0.05s | Síncrono |
| 2. Request HTTP | Network | 0.05-0.2s | Síncrono |
| 3. Validación Serializer | Django REST | 0.01-0.05s | Síncrono |
| 4. Validación Permisos | Service | 0.001-0.01s | Síncrono |
| 5. Validación HAWB | Repository | 0.01-0.05s | Síncrono |
| 6. Validación Cupo | Service | 0.01-0.05s | Síncrono |
| 7. Cálculo Costo | TarifaService | 0.01-0.1s | Síncrono |
| 8. Creación Envío | Repository | 0.02-0.1s | Síncrono |
| 9. Creación Productos | Repository | 0.05-0.2s | Síncrono |
| 10. Cálculo Totales | Model Method | 0.01-0.1s | Síncrono |
| 11. Generación Embedding | Async Service | 0.1-1.0s | Asíncrono |
| 12. Notificación | Async Service | 0.05-0.2s | Asíncrono |
| 13. Logs y Métricas | Log Service | 0.01-0.05s | Asíncrono |
| 14. Serialización Respuesta | Serializer | 0.01-0.05s | Síncrono |
| **TOTAL (Síncrono)** | | **0.2-0.8s** | |
| **TOTAL (Incluyendo Async)** | | **0.3-1.0s** | |

### Puntos de Validación

1. ✅ **Frontend**: Validación de formulario (campos requeridos, tipos)
2. ✅ **Serializer**: Validación de estructura y tipos de datos
3. ✅ **Permisos**: Solo Admin/Gerente/Digitador pueden crear
4. ✅ **HAWB**: Debe ser único en el sistema
5. ✅ **Cupo**: Comprador debe tener cupo disponible
6. ✅ **Comprador**: Debe ser rol Comprador (4)
7. ✅ **Productos**: Cada producto debe tener datos válidos
8. ✅ **Tarifas**: Debe existir tarifa aplicable para cada producto

### Puntos de Error

1. ❌ **400 Bad Request**: Datos inválidos en formulario
2. ❌ **400 Bad Request**: HAWB duplicado
3. ❌ **400 Bad Request**: Cupo insuficiente
4. ❌ **403 Forbidden**: Usuario sin permisos
5. ❌ **404 Not Found**: Comprador no encontrado
6. ❌ **500 Internal Server Error**: Error en base de datos o proceso

### Transacciones Atómicas

- ✅ Toda la creación del envío y productos está dentro de una transacción
- ✅ Si falla cualquier paso, se hace rollback completo
- ✅ Garantiza consistencia de datos

### Procesos Asíncronos

- 🔄 Generación de embedding (no bloquea)
- 🔄 Notificaciones al comprador (no bloquea)
- 🔄 Logs de auditoría (no bloquea)
- 🔄 Métricas (no bloquea)

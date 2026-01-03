# 🐳 Cómo Funciona Docker y PostgreSQL Local

## 🎯 ¿Qué es Docker?

Docker es como una "mini-máquina virtual" muy ligera que contiene todo lo necesario para ejecutar una aplicación de forma aislada.

### Analogía Simple

Imagina que Docker es como una **caja de plástico transparente**:
- Dentro de la caja está PostgreSQL (la base de datos)
- La caja está **aislada** de tu computadora
- Pero puedes **meter y sacar cosas** por puertas específicas (puertos)
- Si rompes algo dentro de la caja, tu computadora sigue intacta

## 🏗️ Arquitectura de Tu Sistema Actual

```
┌─────────────────────────────────────────────────────────────┐
│                    TU COMPUTADORA (Windows)                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Docker Desktop                       │  │
│  │                                                       │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │   Contenedor: postgres_local                   │  │  │
│  │  │                                                 │  │  │
│  │  │   ┌─────────────────────────────────────┐     │  │  │
│  │  │   │  PostgreSQL 16 + pgvector           │     │  │  │
│  │  │   │                                      │     │  │  │
│  │  │   │  Base de datos: UBAppDB              │     │  │  │
│  │  │   │  Puerto interno: 5432                │     │  │  │
│  │  │   └─────────────────────────────────────┘     │  │  │
│  │  │                     ↕                          │  │  │
│  │  │            Puerto mapeado: 5435                │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Django (backend)                         │  │
│  │         Se conecta a localhost:5435                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        PostgreSQL Local (si tienes)                   │  │
│  │              Puerto: 5432                             │  │
│  │         (No interfiere con Docker)                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔑 Conceptos Clave

### 1. Contenedor (`postgres_local`)

Es la "caja" que contiene PostgreSQL:
- **Nombre**: `postgres_local`
- **ID**: `f7653f0906b3` (identificador único)
- **Estado**: Puede estar corriendo o detenido
- **Datos**: Se guardan en un "volumen" persistente

### 2. Imagen (`ankane/pgvector`)

Es como una "plantilla" o "receta" para crear el contenedor:
- Contiene PostgreSQL + pgvector preinstalado
- Se descarga una sola vez
- Pesa ~500MB
- Puedes crear múltiples contenedores desde la misma imagen

### 3. Puertos

**Mapeo de puertos:**
```
Windows (localhost:5435) ←→ Contenedor (5432)
         ↑                           ↑
    Puerto externo              Puerto interno
    (el que usas)              (dentro del Docker)
```

**¿Por qué 5435 y no 5432?**
- `5432`: Ya está ocupado por tu PostgreSQL local
- `5433`: Ya está ocupado por otro servicio
- `5434`: Ya está ocupado
- `5435`: ¡Libre! ✅

Django se conecta a `localhost:5435`, y Docker lo redirige internamente al `5432` del contenedor.

### 4. Volumen (`pgdata`)

Es un "disco duro virtual" donde se guardan los datos:
- **Persistente**: Los datos NO se pierden cuando detienes el contenedor
- **Ubicación**: Docker lo gestiona automáticamente
- **Tamaño**: Crece según los datos que guardes

## 🔄 Ciclo de Vida del Contenedor

### Estado Actual

```bash
docker ps
```

Muestra:
```
CONTAINER ID   IMAGE              STATUS          PORTS                    NAMES
f7653f0906b3   ankane/pgvector    Up 10 minutes   0.0.0.0:5435->5432/tcp   postgres_local
```

### Comandos Importantes

```bash
# Ver contenedores corriendo
docker ps

# Ver TODOS los contenedores (incluso detenidos)
docker ps -a

# Iniciar contenedor (si está detenido)
docker start postgres_local

# Detener contenedor
docker stop postgres_local

# Reiniciar contenedor
docker restart postgres_local

# Ver logs (errores, actividad)
docker logs postgres_local

# Ver logs en tiempo real
docker logs -f postgres_local

# Ver uso de recursos
docker stats postgres_local

# Acceder a la terminal del contenedor
docker exec -it postgres_local bash

# Acceder directamente a PostgreSQL
docker exec -it postgres_local psql -U postgres -d UBAppDB
```

## 🗄️ Base de Datos UBAppDB

### Estructura

```
Contenedor: postgres_local
  └── PostgreSQL Server
      ├── Base de datos: postgres (por defecto)
      ├── Base de datos: UBAppDB ← Tu base de datos
      │   ├── Esquema: public
      │   │   ├── Tablas (se crean con migrate)
      │   │   ├── Extensiones:
      │   │   │   └── vector (pgvector v0.5.1) ✅
      │   └── Usuarios:
      │       └── postgres (superusuario)
      └── Configuración:
          ├── Puerto: 5432 (interno)
          ├── SSL: Disabled (para local)
          └── Max Connections: 100
```

### Conexión desde Django

Django usa esta configuración de `.env`:

```env
DB_HOST=localhost      # Tu computadora
DB_PORT=5435           # Puerto mapeado
DB_NAME=UBAppDB        # Base de datos específica
DB_USER=postgres       # Usuario
DB_PASSWORD=admin      # Contraseña
```

## 🔍 Verificaciones Útiles

### Verificar que el contenedor esté corriendo

```bash
docker ps | findstr postgres_local
```

Si no aparece nada, inícialo:
```bash
docker start postgres_local
```

### Verificar conexión desde Windows

```bash
# Requiere psql instalado en Windows
psql -h localhost -p 5435 -U postgres -d UBAppDB
```

O desde Docker:
```bash
docker exec -it postgres_local psql -U postgres -d UBAppDB
```

### Ver bases de datos disponibles

```bash
docker exec -it postgres_local psql -U postgres -c "\l"
```

### Ver tablas en UBAppDB

```bash
docker exec -it postgres_local psql -U postgres -d UBAppDB -c "\dt"
```

### Verificar pgvector

```bash
docker exec -it postgres_local psql -U postgres -d UBAppDB -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

## ⚡ ¿Qué Pasa Cuando...?

### Reinicias tu computadora

1. Docker Desktop se detiene
2. El contenedor se detiene
3. **Los datos NO se pierden** (están en el volumen)

Para volver a usar:
```bash
# Inicia Docker Desktop (manualmente o automático)
# Luego inicia el contenedor
docker start postgres_local
```

### Apagas Docker Desktop

1. El contenedor se detiene
2. Django no puede conectarse
3. Los datos siguen intactos

### Eliminas el contenedor

```bash
docker rm postgres_local  # ⚠️ Cuidado
```

1. El contenedor desaparece
2. **Los datos del volumen persisten**
3. Puedes recrear el contenedor y recuperar los datos

### Eliminas el volumen

```bash
docker volume rm pgdata  # ⚠️⚠️ MUY PELIGROSO
```

1. **PIERDES TODOS LOS DATOS** 💀
2. No hay forma de recuperarlos
3. Solo haz esto si quieres empezar de cero

## 🆚 Docker vs PostgreSQL Local

| Aspecto | Docker PostgreSQL | PostgreSQL Local |
|---------|------------------|------------------|
| Puerto | 5435 (configurable) | 5432 (fijo) |
| Base de datos | UBAppDB | Múltiples |
| Aislamiento | ✅ Completamente aislado | ❌ Sistema |
| pgvector | ✅ Incluido | ⚠️ Manual |
| Fácil eliminar | ✅ Un comando | ❌ Desinstalar |
| Rendimiento | ⭐⭐⭐⭐ (98%) | ⭐⭐⭐⭐⭐ (100%) |
| Portabilidad | ✅ Fácil mover | ❌ Difícil |
| Uso RAM | ~200MB | ~150MB |

## 🚀 Flujo de Trabajo Típico

### Al iniciar tu día

```bash
# 1. Verificar Docker Desktop (ícono en bandeja)
# 2. Si no está corriendo el contenedor:
docker start postgres_local

# 3. Verificar que esté listo
docker ps

# 4. Iniciar Django
cd backend
python manage.py runserver
```

### Al terminar tu día

```bash
# Opción 1: Dejar corriendo (recomendado)
# No hagas nada, consume pocos recursos

# Opción 2: Detener para liberar RAM
docker stop postgres_local
```

## 🔧 Solución de Problemas Comunes

### Error: "Cannot connect to the Docker daemon"

**Causa**: Docker Desktop no está corriendo

**Solución**: Inicia Docker Desktop desde el menú de Windows

### Error: "port 5435 already in use"

**Causa**: Otro servicio usa el puerto 5435

**Solución**: El script automático debería encontrar otro puerto libre

### Error: "container postgres_local not found"

**Causa**: El contenedor no existe

**Solución**: 
```bash
python setup_docker_postgres_auto.py
```

### Django no puede conectar

**Verificaciones:**
```bash
# 1. ¿Está corriendo?
docker ps

# 2. ¿Responde PostgreSQL?
docker exec postgres_local pg_isready

# 3. ¿Configuración correcta en .env?
# Verifica DB_PORT=5435
```

## 📝 Resumen

1. **Docker** = Caja aislada que contiene PostgreSQL
2. **postgres_local** = Nombre del contenedor
3. **UBAppDB** = Tu base de datos dentro del contenedor
4. **Puerto 5435** = Puerta de entrada desde tu PC
5. **Volumen pgdata** = Disco duro virtual que guarda los datos
6. **pgvector** = Extensión para embeddings (ya instalada)

Todo está listo para que Django se conecte y funcione igual que con Supabase, pero localmente en tu PC.


# 🐳 Explicación: Cómo Funciona Docker para la Base de Datos

## 📚 ¿Qué es Docker?

Docker es una plataforma que permite ejecutar aplicaciones en **contenedores** aislados. Piensa en un contenedor como una "caja" que contiene todo lo necesario para ejecutar una aplicación (código, librerías, dependencias) sin afectar tu sistema operativo.

### Analogía Simple

Imagina que Docker es como una **máquina virtual ligera**:
- **Máquina Virtual tradicional**: Tiene su propio sistema operativo completo (muy pesado)
- **Contenedor Docker**: Comparte el sistema operativo de tu PC, pero está aislado (muy ligero)

## 🗄️ ¿Cómo Docker Maneja la Base de Datos?

### Arquitectura

```
Tu PC (Windows)
  └── Docker Desktop
      └── Contenedor: postgres_local
          └── PostgreSQL Server (puerto interno 5432)
              └── Base de datos: UBAppDB
                  ├── Tablas (usuarios, envíos, productos, etc.)
                  └── Extensiones (pgvector)
```

### Componentes Clave

1. **Docker Desktop**: Aplicación que gestiona los contenedores
2. **Contenedor `postgres_local`**: El "caja" que contiene PostgreSQL
3. **PostgreSQL**: El servidor de base de datos dentro del contenedor
4. **Volumen `pgdata`**: Donde se guardan los datos permanentemente

## 📍 ¿Dónde se Guardan los Datos?

### Ubicación Física

Los datos se guardan en un **volumen de Docker** llamado `pgdata`. Docker gestiona este volumen automáticamente.

**En Windows, Docker guarda los volúmenes en:**
```
C:\Users\<tu_usuario>\AppData\Local\Docker\wsl\data\ext4.vhdx
```

⚠️ **No necesitas acceder directamente a esta ubicación**. Docker lo gestiona todo automáticamente.

### Persistencia de Datos

✅ **Los datos NO se pierden cuando:**
- Detienes el contenedor (`docker stop postgres_local`)
- Reinicias tu PC
- Cierras Docker Desktop

❌ **Los datos SÍ se pierden cuando:**
- Eliminas el contenedor Y el volumen (`docker rm -v postgres_local`)
- Eliminas el volumen manualmente

### Cómo Verificar que los Datos Están Guardados

```powershell
# Ver volúmenes de Docker
docker volume ls

# Ver detalles del volumen pgdata
docker volume inspect pgdata
```

## 🔌 Mapeo de Puertos

### ¿Por qué Puerto 5435?

Docker mapea puertos entre tu PC y el contenedor:

```
Tu PC (Windows)          Docker (Contenedor)
localhost:5435    ←→    postgres_local:5432
```

**Explicación:**
- **5435** (externo): Puerto en tu PC Windows
- **5432** (interno): Puerto dentro del contenedor (estándar de PostgreSQL)

**¿Por qué no usar 5432 directamente?**
- Porque probablemente ya tienes PostgreSQL instalado localmente usando el puerto 5432
- Docker usa 5435 para evitar conflictos

### Cambiar el Puerto

Si quieres usar otro puerto (por ejemplo, 5436):

1. Detener y eliminar el contenedor actual:
```powershell
docker stop postgres_local
docker rm postgres_local
```

2. Crear nuevo contenedor con otro puerto:
```powershell
docker run -d --name postgres_local -e POSTGRES_DB=UBAppDB -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=admin -p 5436:5432 -v pgdata:/var/lib/postgresql/data ankane/pgvector
```

3. Actualizar `.env`:
```env
DB_PORT=5436
```

## 🚀 Ventajas de Usar Docker

### 1. **Aislamiento**
- No interfiere con tu PostgreSQL local
- No afecta otras aplicaciones
- Fácil de eliminar si algo sale mal

### 2. **Portabilidad**
- Misma configuración en cualquier PC
- No necesitas instalar PostgreSQL manualmente
- Incluye pgvector preconfigurado

### 3. **Facilidad**
- Un comando para iniciar: `docker start postgres_local`
- Un comando para detener: `docker stop postgres_local`
- No necesitas configurar servicios de Windows

### 4. **Rendimiento**
- Más rápido que una máquina virtual completa
- Usa recursos eficientemente
- Inicio rápido

## 📊 Flujo de Trabajo con Docker

### Escenario 1: Trabajando en Casa (Supabase)

```
1. Conectado a red con IPv6
2. .env configurado para Supabase:
   DB_HOST=db.xxxxx.supabase.co
   DB_PORT=5432
3. Django se conecta directamente a Supabase
4. Todos los cambios se guardan en la nube
```

### Escenario 2: Trabajando en Otra Red (Docker)

```
1. Sin acceso a Supabase (sin IPv6)
2. Exportar datos desde Supabase:
   python funciones/exportar_datos_supabase.py
3. Cambiar .env a Docker:
   DB_HOST=localhost
   DB_PORT=5435
4. Iniciar Docker:
   docker start postgres_local
5. Importar datos:
   python funciones/importar_datos_local.py
6. Trabajar localmente con Docker
```

## 🔧 Comandos Esenciales

### Gestión del Contenedor

```powershell
# Ver si está corriendo
docker ps | findstr postgres_local

# Iniciar contenedor
docker start postgres_local

# Detener contenedor
docker stop postgres_local

# Reiniciar contenedor
docker restart postgres_local

# Ver logs (errores, actividad)
docker logs postgres_local

# Ver logs en tiempo real
docker logs -f postgres_local
```

### Acceso a la Base de Datos

```powershell
# Acceder a PostgreSQL desde Docker
docker exec -it postgres_local psql -U postgres -d UBAppDB

# Ejecutar comando SQL directamente
docker exec -it postgres_local psql -U postgres -d UBAppDB -c "SELECT COUNT(*) FROM usuarios_usuario;"
```

### Gestión de Volúmenes

```powershell
# Ver todos los volúmenes
docker volume ls

# Ver detalles del volumen pgdata
docker volume inspect pgdata

# Hacer backup del volumen (avanzado)
docker run --rm -v pgdata:/data -v ${PWD}:/backup alpine tar czf /backup/pgdata_backup.tar.gz /data
```

## 🔄 Sincronización de Datos

### Exportar desde Supabase → Docker

```powershell
# 1. En casa, conectado a Supabase
python funciones/exportar_datos_supabase.py

# 2. Cambiar a Docker
python funciones/setup_docker_postgres_auto.py

# 3. Importar datos
python funciones/importar_datos_local.py
```

### Los Archivos de Backup

Los archivos se guardan en `backend/backup/`:
- `usuarios.json` - Usuarios
- `envios.json` - Envíos
- `productos.json` - Productos
- `embeddings.json` - Embeddings (sin vectores)
- `envio_embeddings.pgdump` - Vectores (si pg_dump está disponible)

## ⚠️ Preguntas Frecuentes

### ¿Qué pasa si apago Docker Desktop?

El contenedor se detiene, pero los datos se conservan. Cuando vuelvas a iniciar Docker Desktop:

```powershell
docker start postgres_local
```

### ¿Puedo tener Supabase y Docker corriendo al mismo tiempo?

Sí, pero Django solo puede conectarse a uno a la vez. Cambia `DB_HOST` en `.env` para alternar entre ellos.

### ¿Los datos en Docker son los mismos que en Supabase?

No necesariamente. Docker es una copia local. Debes sincronizarlos manualmente usando los scripts de exportación/importación.

### ¿Cuánto espacio ocupa Docker?

- Imagen de PostgreSQL + pgvector: ~500 MB
- Volumen con datos: Depende de tus datos (puede ser desde MB hasta GB)

### ¿Puedo eliminar Docker sin perder datos?

Sí, si solo eliminas Docker Desktop. Pero si eliminas el contenedor Y el volumen, perderás los datos. Siempre haz backup antes de eliminar.

### ¿Cómo hago backup completo de Docker?

```powershell
# Opción 1: Exportar datos con el script
python funciones/exportar_datos_supabase.py

# Opción 2: Backup del volumen (avanzado)
docker run --rm -v pgdata:/data -v ${PWD}:/backup alpine tar czf /backup/pgdata_backup.tar.gz /data
```

## 🎯 Resumen

1. **Docker** ejecuta PostgreSQL en un contenedor aislado
2. **Los datos** se guardan en un volumen persistente (`pgdata`)
3. **El puerto** 5435 en tu PC se mapea al puerto 5432 del contenedor
4. **Los datos persisten** aunque detengas el contenedor
5. **Docker es más rápido** y fácil que instalar PostgreSQL manualmente

## 📝 Próximos Pasos

1. ✅ Entender cómo funciona Docker
2. ✅ Configurar Docker: `python funciones/setup_docker_postgres_auto.py`
3. ✅ Exportar desde Supabase: `python funciones/exportar_datos_supabase.py`
4. ✅ Importar a Docker: `python funciones/importar_datos_local.py`
5. ✅ Trabajar localmente con Docker

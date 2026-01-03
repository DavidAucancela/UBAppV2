# 🔄 Guía: Configuración Dual de Base de Datos (Supabase ↔️ Local)

## 🎯 Objetivo

Configurar dos bases de datos:
- **Supabase** (en casa) - Base de datos principal en la nube
- **Local** (otras redes) - Copia local para trabajar sin internet

Ambas con soporte para **pgvector** (embeddings).

## 📊 Opciones de Base de Datos Local

### Opción 1: Docker + PostgreSQL + pgvector (RECOMENDADO ⭐)

**Ventajas:**
- ✅ Más fácil de instalar y configurar
- ✅ No afecta tu sistema
- ✅ pgvector incluido
- ✅ Misma versión que Supabase

**Requisitos:**
- Docker Desktop instalado

### Opción 2: PostgreSQL Local + pgvector

**Ventajas:**
- ✅ Rendimiento nativo
- ✅ No requiere Docker

**Desventajas:**
- ❌ Instalación manual
- ❌ Puede conflictuar con otros servicios

### Opción 3: Sincronización Bajo Demanda

**Ventajas:**
- ✅ No requiere base de datos local
- ✅ Solo sincronizas cuando necesitas

**Desventajas:**
- ❌ Requiere estar en casa para sincronizar
- ❌ No puedes trabajar completamente offline

---

## 🚀 OPCIÓN 1: Docker + PostgreSQL (Recomendado)

### Paso 1: Instalar Docker Desktop

1. Descarga desde: https://www.docker.com/products/docker-desktop/
2. Instala y reinicia
3. Verifica: `docker --version`

### Paso 2: Crear Base de Datos con Docker

Ejecuta este script:

```powershell
cd backend
python setup_docker_postgres.py
```

O manualmente:

```powershell
# Crear y ejecutar contenedor PostgreSQL con pgvector
docker run -d \
  --name postgres_local \
  -e POSTGRES_DB=UBAppDB \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=admin \
  -p 5433:5432 \
  -v pgdata:/var/lib/postgresql/data \
  ankane/pgvector

# Verificar que esté corriendo
docker ps

# Nota: Puerto 5433 externo para evitar conflictos con PostgreSQL local
```

### Paso 3: Configurar .env para Local

Actualiza `backend/.env`:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=UBAppDB
DB_USER=postgres
DB_PASSWORD=admin
```

### Paso 4: Ejecutar Migraciones

```powershell
cd backend
python manage.py migrate
```

### Paso 5: Importar Datos desde Supabase

```powershell
# Cuando estés en casa (conectado a Supabase)
python exportar_datos_supabase.py

# Luego en cualquier red
python importar_datos_local.py
```

---

## 🔧 OPCIÓN 2: PostgreSQL Local Manual

### Paso 1: Instalar PostgreSQL

1. Descarga desde: https://www.postgresql.org/download/windows/
2. Instala PostgreSQL 14 o superior
3. Configura:
   - Base de datos: `equityDB`
   - Usuario: `postgres`
   - Contraseña: `admin`
   - Puerto: `5432`

### Paso 2: Instalar pgvector

**Opción A: Pre-compilado**

1. Descarga desde: https://github.com/pgvector/pgvector/releases
2. Copia archivos a la carpeta de PostgreSQL
3. Reinicia PostgreSQL

**Opción B: Compilar (Avanzado)**

Requiere Visual Studio Build Tools.

### Paso 3: Habilitar pgvector

```sql
-- Conéctate a equityDB
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Paso 4: Ejecutar Migraciones

```powershell
cd backend
python manage.py migrate
```

---

## 📦 Scripts de Exportación/Importación

He creado scripts automáticos para sincronizar datos:

### Script 1: Exportar desde Supabase

```powershell
# Ejecuta cuando estés en casa
cd backend
python exportar_datos_supabase.py
```

Esto crea:
- `backup/usuarios.json`
- `backup/envios.json`
- `backup/productos.json`
- `backup/embeddings.json`
- `backup/envio_embeddings.pgdump` (datos pgvector)

### Script 2: Importar a Local

```powershell
# Ejecuta en cualquier red
cd backend
python importar_datos_local.py
```

Restaura todos los datos incluyendo embeddings.

### Script 3: Sincronización Bidireccional

```powershell
# Sincronizar cambios entre local y Supabase
cd backend
python sincronizar_bases_datos.py
```

---

## 🔄 Flujo de Trabajo Recomendado

### Cuando estás en CASA:

1. **Configuración:** Supabase
   ```powershell
   python configuracion_dual_red.py
   # Selecciona: Supabase
   ```

2. **Exportar datos antes de salir:**
   ```powershell
   python exportar_datos_supabase.py
   ```

3. **Trabajar normalmente con Supabase**

### Cuando NO estás en casa:

1. **Cambiar a local:**
   ```powershell
   python configuracion_dual_red.py
   # Selecciona: Local
   ```

2. **Importar datos (primera vez):**
   ```powershell
   python importar_datos_local.py
   ```

3. **Trabajar con base de datos local**

### Cuando vuelves a CASA:

1. **Cambiar a Supabase:**
   ```powershell
   python configuracion_dual_red.py
   # Selecciona: Supabase
   ```

2. **Sincronizar cambios (si hiciste cambios en local):**
   ```powershell
   python sincronizar_bases_datos.py
   ```

---

## 🛠️ Herramientas de Gestión

### DBeaver (Recomendado)

**Instalación:**
1. Descarga: https://dbeaver.io/download/
2. Instala DBeaver Community Edition
3. Es gratis y funciona con PostgreSQL + pgvector

**Conexión a Supabase:**
- Host: `db.gybrifikqkibwqpzjuxm.supabase.co`
- Port: `5432`
- Database: `postgres`
- Username: `postgres`
- Password: [tu password]
- SSL: Required

**Conexión a Local (Docker):**
- Host: `localhost`
- Port: `5432`
- Database: `equityDB`
- Username: `postgres`
- Password: `admin`

**Con DBeaver puedes:**
- Ver y editar datos
- Exportar/importar datos fácilmente
- Ejecutar consultas SQL
- Comparar esquemas entre bases de datos

### pgAdmin 4

**Alternativa a DBeaver:**
1. Se instala con PostgreSQL
2. Interfaz más compleja pero poderosa
3. Específica para PostgreSQL

---

## 📋 Comandos Docker Útiles

```powershell
# Iniciar contenedor
docker start postgres_local

# Detener contenedor
docker stop postgres_local

# Ver logs
docker logs postgres_local

# Acceder a PostgreSQL dentro del contenedor
docker exec -it postgres_local psql -U postgres -d equityDB

# Backup manual
docker exec postgres_local pg_dump -U postgres equityDB > backup.sql

# Restaurar backup
docker exec -i postgres_local psql -U postgres equityDB < backup.sql

# Eliminar contenedor (si necesitas reinstalar)
docker rm postgres_local

# Eliminar volumen de datos (¡cuidado!)
docker volume rm pgdata
```

---

## 🔍 Verificar que Todo Funciona

### Verificar pgvector en Docker:

```powershell
docker exec -it postgres_local psql -U postgres -d equityDB -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

Debe mostrar la extensión vector.

### Verificar desde Django:

```powershell
cd backend
python manage.py shell
```

```python
from django.db import connection

# Verificar conexión
cursor = connection.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())

# Verificar pgvector
cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
print(cursor.fetchone())
```

---

## 📊 Comparación de Opciones

| Característica | Docker | PostgreSQL Local | Sincronización |
|----------------|--------|------------------|----------------|
| Facilidad | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| pgvector | ✅ Incluido | ⚠️ Manual | N/A |
| Rendimiento | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Portabilidad | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Espacio | ~500MB | ~200MB | ~50MB |
| Offline | ✅ Total | ✅ Total | ❌ Parcial |

---

## 🎯 Recomendación Final

**Para la mayoría de casos:**
1. Usa **Docker + PostgreSQL** (Opción 1)
2. Instala **DBeaver** para gestión visual
3. Usa los scripts de exportación/importación
4. Sincroniza cuando vuelvas a casa

**Si tienes experiencia con PostgreSQL:**
1. Instala **PostgreSQL local** (Opción 2)
2. Configura pgvector manualmente
3. Mayor control y rendimiento

**Si prefieres simplicidad:**
1. Usa **sincronización bajo demanda** (Opción 3)
2. Solo exporta/importa cuando necesites
3. No requiere base de datos local siempre activa

---

## 📝 Próximos Pasos

1. Lee esta guía completa
2. Elige una opción (recomiendo Docker)
3. Ejecuta los scripts de configuración
4. Prueba exportar/importar datos
5. ¡Listo para trabajar en cualquier red!

Voy a crear los scripts mencionados en esta guía.


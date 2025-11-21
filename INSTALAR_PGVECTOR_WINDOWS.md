# 🪟 Instalar pgvector en PostgreSQL - Windows

## Opción 1: Instalación Pre-compilada (Recomendada) ⭐

### Paso 1: Descargar pgvector

1. Visita: https://github.com/pgvector/pgvector/releases
2. Descarga la versión para Windows según tu PostgreSQL:
   - `pgvector-0.5.1-pg14-windows.zip` (PostgreSQL 14)
   - `pgvector-0.5.1-pg15-windows.zip` (PostgreSQL 15)
   - `pgvector-0.5.1-pg16-windows.zip` (PostgreSQL 16)

### Paso 2: Verificar tu versión de PostgreSQL

```powershell
# En PowerShell
psql --version

# Debe mostrar algo como:
# psql (PostgreSQL) 14.x
```

### Paso 3: Ubicar el directorio de PostgreSQL

```powershell
# Usualmente está en:
C:\Program Files\PostgreSQL\14\

# O en Program Files (x86):
C:\Program Files (x86)\PostgreSQL\14\
```

### Paso 4: Copiar archivos de pgvector

Extraer el ZIP descargado y copiar:

```powershell
# Copiar archivos .dll
# DESDE: pgvector-0.5.1-pg14-windows\lib\
# HACIA: C:\Program Files\PostgreSQL\14\lib\

# Copiar archivos .sql y .control
# DESDE: pgvector-0.5.1-pg14-windows\share\extension\
# HACIA: C:\Program Files\PostgreSQL\14\share\extension\
```

**Comando PowerShell (como Administrador):**

```powershell
# Ajustar rutas según tu instalación
$pgPath = "C:\Program Files\PostgreSQL\14"
$pgvectorZip = "C:\Users\david\Downloads\pgvector-0.5.1-pg14-windows"

# Copiar DLL
Copy-Item "$pgvectorZip\lib\vector.dll" -Destination "$pgPath\lib\"

# Copiar archivos de extensión
Copy-Item "$pgvectorZip\share\extension\*" -Destination "$pgPath\share\extension\"

Write-Host "✅ Archivos copiados exitosamente" -ForegroundColor Green
```

### Paso 5: Habilitar la extensión en PostgreSQL

```powershell
# Conectar a PostgreSQL
psql -U postgres -d equityDB

# En psql:
CREATE EXTENSION IF NOT EXISTS vector;

# Verificar
\dx

# Debe mostrar:
# Name   | Version | Schema | Description
# vector | 0.5.1   | public | vector data type and operations
```

---

## Opción 2: Usar Docker (Más Fácil) 🐳

Si tienes Docker instalado, es la forma más sencilla:

### Paso 1: Crear docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: ankane/pgvector:latest
    container_name: postgres_pgvector
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: admin
      POSTGRES_DB: equityDB
    ports:
      - "5432:5432"
    volumes:
      - pgvector_data:/var/lib/postgresql/data

volumes:
  pgvector_data:
```

### Paso 2: Iniciar contenedor

```powershell
# En el directorio con docker-compose.yml
docker-compose up -d

# Verificar que está corriendo
docker ps

# Conectar
psql -h localhost -U postgres -d equityDB

# La extensión ya está incluida, solo habilitarla:
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Opción 3: Usar Supabase (Cloud) ☁️

La más simple, sin instalación local:

### Paso 1: Crear proyecto en Supabase

1. Visita: https://supabase.com/
2. Crear cuenta (gratis)
3. Crear nuevo proyecto
4. Esperar ~2 minutos a que se configure

### Paso 2: Habilitar pgvector

```sql
-- En el SQL Editor de Supabase:
CREATE EXTENSION IF NOT EXISTS vector;
```

### Paso 3: Actualizar .env

```env
DB_HOST=db.xxxxx.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=tu_password_de_supabase
```

**Ventajas:**
- ✅ pgvector ya incluido
- ✅ Sin instalación local
- ✅ Backups automáticos
- ✅ Panel web incluido

---

## Verificación Final

Una vez instalado pgvector por cualquier método:

```powershell
# 1. Conectar a PostgreSQL
psql -U postgres -d equityDB

# 2. Verificar extensión
SELECT * FROM pg_extension WHERE extname = 'vector';

# Debe retornar una fila con:
# extname | extowner | extnamespace | ...
# vector  | ...      | ...          | ...

# 3. Probar crear una tabla con vector
CREATE TABLE test_vector (
    id SERIAL PRIMARY KEY,
    embedding vector(1536)
);

# Si no da error, ¡funciona! ✅

# 4. Limpiar prueba
DROP TABLE test_vector;
```

---

## Solución de Problemas

### Error: "extension 'vector' is not available"

**Causa:** Archivos no copiados correctamente.

**Solución:**

```powershell
# Verificar que existen los archivos
Test-Path "C:\Program Files\PostgreSQL\14\lib\vector.dll"
Test-Path "C:\Program Files\PostgreSQL\14\share\extension\vector.control"

# Si alguno no existe, volver a copiar
```

### Error: "Access Denied" al copiar archivos

**Causa:** Falta permisos de administrador.

**Solución:**

```powershell
# Abrir PowerShell como Administrador:
# Click derecho en PowerShell → "Ejecutar como Administrador"

# Luego ejecutar los comandos de copia
```

### Error: "Could not load library 'vector.dll'"

**Causa:** Versión incorrecta de pgvector.

**Solución:**

```powershell
# Verificar versión de PostgreSQL
psql --version

# Descargar pgvector para esa versión específica
# PostgreSQL 14 → pgvector-pg14
# PostgreSQL 15 → pgvector-pg15
# etc.
```

### PostgreSQL no inicia después de instalar

**Causa:** DLL incompatible.

**Solución:**

```powershell
# 1. Detener PostgreSQL
net stop postgresql-x64-14

# 2. Remover vector.dll
Remove-Item "C:\Program Files\PostgreSQL\14\lib\vector.dll"

# 3. Iniciar PostgreSQL
net start postgresql-x64-14

# 4. Descargar versión correcta de pgvector
```

---

## Alternativa: Compilar desde Código Fuente

**Solo para usuarios avanzados:**

### Requisitos

- Visual Studio 2019+
- PostgreSQL con headers de desarrollo
- Git

### Pasos

```powershell
# 1. Clonar repositorio
git clone https://github.com/pgvector/pgvector.git
cd pgvector

# 2. Compilar (requiere Visual Studio)
# Seguir instrucciones en:
# https://github.com/pgvector/pgvector#windows

# 3. Copiar archivos compilados
# (Similar a Opción 1)
```

**No recomendado** a menos que sepas lo que haces.

---

## Recomendación Final

Para desarrollo en Windows:

1. **Primera opción:** Docker con `ankane/pgvector` ⭐
   - Más fácil y sin problemas
   - No afecta tu instalación local

2. **Segunda opción:** Supabase (Cloud) ⭐⭐
   - Cero configuración
   - Ideal para pruebas

3. **Tercera opción:** Instalación manual
   - Solo si necesitas PostgreSQL local
   - Más pasos pero funciona bien

---

## Después de Instalar

Una vez que pgvector esté funcionando:

```powershell
# 1. Volver al proyecto
cd C:\Users\david\App\backend

# 2. Ejecutar migraciones
python manage.py migrate busqueda

# 3. Generar embeddings de prueba
python manage.py generar_embeddings_masivo --limite 10

# 4. ¡Listo! ✅
```

---

## Recursos

- **pgvector GitHub:** https://github.com/pgvector/pgvector
- **Releases:** https://github.com/pgvector/pgvector/releases
- **Docker image:** https://hub.docker.com/r/ankane/pgvector
- **Supabase:** https://supabase.com/

---

**Nota:** Si tienes problemas, la opción de Docker o Supabase son las más confiables para Windows.


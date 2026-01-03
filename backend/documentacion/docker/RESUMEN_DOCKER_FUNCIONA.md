# ✅ Resumen: Docker y Base de Datos Funcionando

## 🎉 ¡Configuración Exitosa!

Tu base de datos Docker con PostgreSQL + pgvector está funcionando correctamente.

## 📊 Estado Actual

### Contenedor Docker
- ✅ **Nombre**: `postgres_local`
- ✅ **Estado**: Corriendo
- ✅ **Puerto externo**: `5435`
- ✅ **Puerto interno**: `5432`
- ✅ **Base de datos**: `UBAppDB`
- ✅ **Usuario**: `postgres`
- ✅ **Contraseña**: `admin`

### PostgreSQL
- ✅ **Versión**: PostgreSQL 16
- ✅ **pgvector**: v0.5.1 habilitado
- ✅ **Migraciones**: Todas aplicadas correctamente

### Configuración .env
- ✅ **DB_HOST**: `localhost`
- ✅ **DB_PORT**: `5435`
- ✅ **DB_NAME**: `UBAppDB`
- ✅ **DB_USER**: `postgres`
- ✅ **DB_PASSWORD**: `admin`
- ✅ **SSL**: Deshabilitado (para conexión local)

## 🐳 Cómo Funciona Docker (Resumen)

### Concepto Simple

```
Tu PC (Windows)
  └── Docker Desktop
      └── Contenedor: postgres_local
          └── PostgreSQL Server
              └── Base de datos: UBAppDB
                  └── Tablas (usuarios, envíos, productos, etc.)
```

### Mapeo de Puertos

```
Windows: localhost:5435  ←→  Docker: postgres_local:5432
                              ↑
                        Puerto interno del contenedor
```

**¿Por qué 5435?**
- Tu PostgreSQL local usa 5432
- Otros servicios usan 5433 y 5434
- Docker encontró 5435 libre automáticamente

### Volumen Persistente

Los datos se guardan en un volumen de Docker llamado `pgdata`:
- **Persistente**: Los datos NO se pierden al detener el contenedor
- **Ubicación**: Docker lo gestiona automáticamente
- **Backup**: Puedes hacer backup del volumen o exportar datos

## 🚀 Comandos Esenciales

### Gestión del Contenedor

```powershell
# Ver estado
docker ps | findstr postgres_local

# Iniciar (si está detenido)
docker start postgres_local

# Detener
docker stop postgres_local

# Reiniciar
docker restart postgres_local

# Ver logs (útil para errores)
docker logs postgres_local

# Ver logs en tiempo real
docker logs -f postgres_local
```

### Acceso a PostgreSQL

```powershell
# Acceder directamente a PostgreSQL
docker exec -it postgres_local psql -U postgres -d UBAppDB

# Ejecutar comando SQL directo
docker exec postgres_local psql -U postgres -d UBAppDB -c "SELECT version();"

# Ver tablas
docker exec postgres_local psql -U postgres -d UBAppDB -c "\dt"

# Verificar pgvector
docker exec postgres_local psql -U postgres -d UBAppDB -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Django

```powershell
# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver

# Acceder al shell de Django
python manage.py shell
```

## 🔄 Flujo de Trabajo

### Al Iniciar tu Día

```powershell
# 1. Verificar que Docker Desktop esté corriendo (ícono en bandeja)
# 2. Iniciar contenedor (si está detenido)
docker start postgres_local

# 3. Verificar que esté listo
docker ps

# 4. Iniciar Django
cd backend
python manage.py runserver
```

### Al Terminar tu Día

```powershell
# Opción 1: Dejar corriendo (recomendado - consume pocos recursos)
# No hacer nada

# Opción 2: Detener para liberar RAM
docker stop postgres_local
```

### Si Reinicias tu PC

```powershell
# Docker Desktop puede iniciar automáticamente
# Solo necesitas iniciar el contenedor:
docker start postgres_local

# O configurar Docker Desktop para iniciar contenedores automáticamente
```

## 📦 Datos y Backups

### ¿Dónde están los datos?

Los datos están en el **volumen Docker `pgdata`**:
- No están en tu sistema de archivos directamente
- Docker los gestiona automáticamente
- Son persistentes (no se pierden al reiniciar)

### Hacer Backup

```powershell
# Backup completo de la base de datos
docker exec postgres_local pg_dump -U postgres UBAppDB > backup_$(Get-Date -Format 'yyyyMMdd').sql

# Backup solo estructura (sin datos)
docker exec postgres_local pg_dump -U postgres -s UBAppDB > schema.sql

# Backup solo datos (sin estructura)
docker exec postgres_local pg_dump -U postgres -a UBAppDB > data.sql
```

### Restaurar Backup

```powershell
# Restaurar desde archivo
docker exec -i postgres_local psql -U postgres UBAppDB < backup.sql
```

## 🔍 Verificación de Salud

### Verificar que Todo Funciona

```powershell
# 1. Verificar contenedor
docker ps | findstr postgres_local

# 2. Verificar conexión
docker exec postgres_local pg_isready -U postgres

# 3. Verificar base de datos
docker exec postgres_local psql -U postgres -d UBAppDB -c "SELECT current_database();"

# 4. Verificar pgvector
docker exec postgres_local psql -U postgres -d UBAppDB -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"

# 5. Verificar desde Django
cd backend
python manage.py dbshell
```

### Si Algo No Funciona

```powershell
# Ver logs de errores
docker logs postgres_local

# Reiniciar contenedor
docker restart postgres_local

# Ver recursos usados
docker stats postgres_local
```

## 🆚 Docker vs Supabase

| Aspecto | Docker Local | Supabase |
|---------|-------------|----------|
| Ubicación | Tu PC | Nube (AWS) |
| Puerto | 5435 | 5432 |
| Base de datos | UBAppDB | postgres |
| Requiere internet | ❌ No | ✅ Sí (IPv6) |
| Velocidad | ⚡ Muy rápido | 🐌 Depende de internet |
| Datos | Tu PC | Nube |
| pgvector | ✅ Incluido | ✅ Incluido |
| Backup | Manual | Automático |
| Costo | Gratis | Gratis (con límites) |

## 📝 Próximos Pasos

### 1. Importar Datos desde Supabase (Opcional)

Cuando estés en casa (conectado a Supabase):

```powershell
# Cambiar a Supabase temporalmente
# Editar .env: DB_HOST=db.gybrifikqkibwqpzjuxm.supabase.co

# Exportar datos
python exportar_datos_supabase.py

# Cambiar de vuelta a local
# Editar .env: DB_HOST=localhost, DB_PORT=5435

# Importar datos
python importar_datos_local.py
```

### 2. Crear Superusuario

```powershell
python manage.py createsuperuser
```

### 3. Iniciar Desarrollo

```powershell
python manage.py runserver
```

## 🎯 Ventajas de Docker

- ✅ **Aislado**: No afecta tu PostgreSQL local
- ✅ **Portátil**: Puedes mover el contenedor fácilmente
- ✅ **Consistente**: Mismo entorno que producción
- ✅ **Fácil de limpiar**: Solo eliminas el contenedor
- ✅ **pgvector incluido**: No necesitas instalarlo manualmente
- ✅ **Funciona offline**: No requiere internet

## 🎉 ¡Todo Listo!

Tu entorno está configurado y funcionando. Puedes trabajar con Django normalmente usando la base de datos local en Docker.


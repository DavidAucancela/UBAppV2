# 🐳 Instrucciones: Configurar Docker con PostgreSQL

## ⚠️ Problema Detectado

El puerto 5432 ya está en uso. Esto significa que tienes PostgreSQL instalado localmente.

## ✅ Solución Aplicada

El script ahora usa:
- **Puerto externo**: `5433` (para evitar conflicto)
- **Puerto interno**: `5432` (dentro del contenedor)
- **Base de datos**: `UBAppDB` (según tu preferencia)

## 🚀 Pasos para Configurar

### 1. Limpiar Contenedor Anterior (Si Existe)

```powershell
cd backend
python limpiar_docker_postgres.py
```

### 2. Crear Nuevo Contenedor

```powershell
python setup_docker_postgres.py
```

El script:
- Descargará la imagen pgvector (ya está descargada)
- Creará contenedor con puerto 5433
- Configurará base de datos UBAppDB
- Habilitará pgvector

### 3. Actualizar .env

El script te preguntará si deseas actualizar `.env`. Si dices que sí, configurará:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=UBAppDB
DB_USER=postgres
DB_PASSWORD=admin
```

### 4. Ejecutar Migraciones

```powershell
python manage.py migrate
```

### 5. Importar Datos (Opcional)

Si ya exportaste datos desde Supabase:

```powershell
python importar_datos_local.py
```

## 🔧 Comandos Útiles

```powershell
# Iniciar contenedor
docker start postgres_local

# Detener contenedor
docker stop postgres_local

# Ver logs
docker logs postgres_local

# Acceder a PostgreSQL
docker exec -it postgres_local psql -U postgres -d UBAppDB

# Verificar que esté corriendo
docker ps

# Ver todos los contenedores (incluso detenidos)
docker ps -a
```

## 📊 Conexión en DBeaver

Si usas DBeaver para gestionar la base de datos:

**Configuración:**
- Host: `localhost`
- Port: `5433`
- Database: `UBAppDB`
- Username: `postgres`
- Password: `admin`
- SSL: Disabled (para conexión local)

## 🆚 Diferencias con PostgreSQL Local

| Aspecto | Docker (Puerto 5433) | PostgreSQL Local (Puerto 5432) |
|---------|----------------------|--------------------------------|
| Base de datos | UBAppDB | Puede ser diferente |
| Puerto | 5433 | 5432 |
| Usuario | postgres | postgres |
| Contraseña | admin | Tu contraseña local |
| pgvector | ✅ Incluido | ⚠️ Requiere instalación |
| Aislamiento | ✅ Contenedor | ❌ Sistema |

## ⚡ Ventajas de Usar Docker

- ✅ **No interfiere** con tu PostgreSQL local
- ✅ **pgvector incluido** - No requiere instalación manual
- ✅ **Portátil** - Puedes mover el contenedor
- ✅ **Aislado** - No afecta tu sistema
- ✅ **Fácil de eliminar** - Solo elimina el contenedor

## 🔄 Ambos PostgreSQL Funcionando

Puedes tener ambos corriendo simultáneamente:

**PostgreSQL Local:**
- Puerto: 5432
- Tus bases de datos existentes

**PostgreSQL Docker:**
- Puerto: 5433
- UBAppDB para este proyecto

Para cambiar entre ellos, solo cambia `DB_PORT` en `.env`:
- `DB_PORT=5432` → PostgreSQL local
- `DB_PORT=5433` → PostgreSQL Docker

## 🎯 Próximos Pasos

1. Ejecuta: `python setup_docker_postgres.py`
2. Cuando pregunte si actualizar .env, di: `s`
3. Ejecuta: `python manage.py migrate`
4. ¡Listo para trabajar!

## ❓ Preguntas Frecuentes

**¿Por qué puerto 5433 y no 5432?**
Porque 5432 está ocupado por tu PostgreSQL local.

**¿Puedo cambiar el puerto después?**
Sí, tendrías que eliminar y recrear el contenedor con otro puerto.

**¿Afecta mi PostgreSQL local?**
No, Docker usa un contenedor completamente aislado.

**¿Qué pasa si apago Docker Desktop?**
El contenedor se detendrá. Cuando lo vuelvas a iniciar, ejecuta:
```powershell
docker start postgres_local
```

**¿Los datos se guardan permanentemente?**
Sí, Docker usa un volumen persistente (`pgdata`) que conserva los datos.


# 📊 Resumen: Opciones para Base de Datos Local

## 🎯 Tu Situación

- **Problema**: Supabase solo tiene IPv6 (IPv4 es de pago)
- **Tu red de casa**: Soporta IPv6 → Supabase funciona ✅
- **Otras redes**: NO soportan IPv6 → Supabase NO funciona ❌
- **Necesitas**: Trabajar desde cualquier red

## 🚀 Opciones Disponibles

### Opción 1: Docker + PostgreSQL (RECOMENDADO ⭐)

**Ventajas:**
- ✅ Más fácil de instalar
- ✅ pgvector incluido
- ✅ No afecta tu sistema
- ✅ Portátil y aislado

**Pasos rápidos:**
```powershell
# 1. Instalar Docker Desktop
#    https://www.docker.com/products/docker-desktop/

# 2. Configurar PostgreSQL automáticamente
cd backend
python setup_docker_postgres.py

# 3. Ejecutar migraciones
python manage.py migrate

# 4. Importar datos (cuando estés en casa primero exporta)
python exportar_datos_supabase.py  # En casa
python importar_datos_local.py      # En cualquier red
```

### Opción 2: Usar Hotspot Móvil

**Ventajas:**
- ✅ No requiere configuración
- ✅ Acceso directo a Supabase
- ✅ Sin sincronización necesaria

**Pasos:**
1. Activa hotspot en tu móvil
2. Conéctate desde tu PC
3. Verifica: `python configuracion_dual_red.py`
4. Si funciona, usa Supabase normalmente

**Desventaja:** Consume datos móviles

### Opción 3: DBeaver para Gestión Manual

**Uso:**
- Ver y editar datos en ambas bases de datos
- Exportar/importar datos manualmente
- Comparar esquemas

**Instalación:**
1. Descarga: https://dbeaver.io/download/
2. Instala DBeaver Community
3. Conecta a Supabase y/o local
4. Exporta/importa datos según necesites

### Opción 4: Sincronización Bajo Demanda

**Ventajas:**
- ✅ No requiere base de datos local permanente
- ✅ Solo sincronizas cuando necesitas

**Pasos:**
```powershell
# En casa (antes de salir)
python exportar_datos_supabase.py

# Los archivos quedan en: backend/backup/

# En cualquier red
# Trabaja con los archivos JSON directamente
# O importa cuando tengas base de datos local
```

## 📋 Flujo de Trabajo Completo

### Primera Vez (Configuración Inicial)

#### Opción A: Con Docker (Recomendado)

```powershell
# 1. Instalar Docker Desktop
#    https://www.docker.com/products/docker-desktop/

# 2. Configurar base de datos local
cd backend
python setup_docker_postgres.py

# 3. Ejecutar migraciones
python manage.py migrate
```

#### Opción B: Hotspot Móvil (Más Simple)

```powershell
# 1. Activa hotspot en tu móvil
# 2. Conéctate desde tu PC
# 3. Usa Supabase normalmente
# No requiere configuración adicional
```

### Cuando estás en CASA

```powershell
# 1. Configurar para Supabase
python configuracion_dual_red.py
# Selecciona: Supabase

# 2. Trabajar normalmente

# 3. Antes de salir, exportar datos
python exportar_datos_supabase.py
# Esto crea backup en: backend/backup/
```

### Cuando NO estás en casa

#### Si tienes Docker configurado:

```powershell
# 1. Cambiar a local
python configuracion_dual_red.py
# Selecciona: Local

# 2. Importar datos (primera vez o actualizar)
python importar_datos_local.py

# 3. Trabajar normalmente
python manage.py runserver
```

#### Si usas hotspot móvil:

```powershell
# 1. Activar hotspot móvil
# 2. Conectar PC al hotspot
# 3. Verificar
python configuracion_dual_red.py
# Si funciona, usar Supabase normalmente
```

### Cuando vuelves a CASA

```powershell
# 1. Cambiar a Supabase
python configuracion_dual_red.py
# Selecciona: Supabase

# 2. Si hiciste cambios en local, sincronizar
#    (Próximamente: python sincronizar_bases_datos.py)

# 3. Exportar datos actualizados
python exportar_datos_supabase.py
```

## 🛠️ Herramientas Instaladas

### DBeaver (Opcional pero Recomendado)

**Para qué sirve:**
- Ver datos en Supabase y local
- Exportar/importar datos fácilmente
- Ejecutar consultas SQL
- Comparar esquemas

**Instalación:**
```powershell
# 1. Descarga: https://dbeaver.io/download/
# 2. Instala DBeaver Community (gratis)
# 3. Conecta a tus bases de datos
```

**Conexiones:**

**Supabase:**
- Host: `db.gybrifikqkibwqpzjuxm.supabase.co`
- Port: `5432`
- Database: `postgres`
- Username: `postgres`
- Password: [tu password]
- SSL: Required

**Local (Docker):**
- Host: `localhost`
- Port: `5433` (externo, internamente usa 5432)
- Database: `UBAppDB`
- Username: `postgres`
- Password: `admin`

## 📁 Archivos Creados

1. **`setup_docker_postgres.py`** - Configura Docker + PostgreSQL
2. **`exportar_datos_supabase.py`** - Exporta desde Supabase
3. **`importar_datos_local.py`** - Importa a local
4. **`configuracion_dual_red.py`** - Cambia entre Supabase/local
5. **`documentacion/GUIA_DUAL_BASE_DATOS.md`** - Guía completa

## 🎯 Recomendación por Escenario

### Si trabajas mucho fuera de casa:
👉 **Docker + PostgreSQL** (Opción 1)
- Instala una vez
- Exporta/importa cuando necesites
- Trabajo completamente offline

### Si sales poco de casa:
👉 **Hotspot Móvil** (Opción 2)
- Sin configuración
- Acceso directo a Supabase
- Más simple

### Si tienes experiencia con bases de datos:
👉 **Docker + DBeaver**
- Control total
- Gestión visual de datos
- Sincronización manual cuando quieras

### Si prefieres no complicarte:
👉 **Solo exportar datos**
- Exporta antes de salir
- Trabaja con archivos JSON
- Importa cuando vuelvas a casa

## 📝 Comandos Rápidos

```powershell
# Configurar Docker + PostgreSQL
python setup_docker_postgres.py

# Cambiar entre Supabase/local
python configuracion_dual_red.py

# Exportar desde Supabase (en casa)
python exportar_datos_supabase.py

# Importar a local (cualquier red)
python importar_datos_local.py

# Verificar conexión actual
python verificar_dns_antes_iniciar.py

# Iniciar Django
python manage.py runserver

# Comandos Docker útiles
docker start postgres_local     # Iniciar
docker stop postgres_local      # Detener
docker logs postgres_local      # Ver logs
```

## 🎉 Conclusión

Tienes varias opciones, elige la que mejor se ajuste a tu forma de trabajar:

- **Más fácil**: Hotspot móvil
- **Más versátil**: Docker + PostgreSQL
- **Más control**: DBeaver + sincronización manual
- **Más simple**: Solo exportar/importar archivos

Todas son válidas y compatibles entre sí. Puedes empezar con una y cambiar a otra después.


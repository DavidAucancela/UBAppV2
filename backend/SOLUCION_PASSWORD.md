# 🔧 Solución al Problema de Contraseña de PostgreSQL

## Problema Detectado
Tu contraseña de PostgreSQL contiene caracteres especiales (acentos, ñ, etc.) que causan problemas de codificación en Windows.

## ✅ SOLUCIÓN 1: Cambiar la Contraseña (RECOMENDADO)

### Opción A: Usando pgAdmin
1. Abre **pgAdmin 4**
2. Conéctate al servidor PostgreSQL
3. Click derecho en **Login/Group Roles** → **postgres**
4. Ve a la pestaña **Definition**
5. Cambia la contraseña a una sin acentos (ej: `Admin123`)
6. Click en **Save**

### Opción B: Usando SQL Shell (psql)
1. Abre **SQL Shell (psql)** desde el menú de inicio
2. Presiona Enter 4 veces para usar los valores por defecto
3. Ingresa tu contraseña actual (con acentos)
4. Ejecuta este comando:
```sql
ALTER USER postgres PASSWORD 'Admin123';
```
5. Escribe `\q` y presiona Enter para salir

### Paso Final: Actualizar el archivo .env
Después de cambiar la contraseña en PostgreSQL, actualiza tu archivo `.env`:

```env
DB_PASSWORD=Admin123
```

**Contraseñas seguras recomendadas (sin acentos):**
- `Admin123!`
- `Postgres#2024`
- `SecurePass_99`
- `MyDB@2024`

---

## ✅ SOLUCIÓN 2: Usar SQLite (Temporal)

Si no puedes cambiar la contraseña ahora, puedes usar SQLite temporalmente:

1. Edita tu archivo `.env`:
```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

2. Ejecuta las migraciones:
```bash
python manage.py migrate
```

3. Cuando cambies la contraseña de PostgreSQL, actualiza el `.env` nuevamente.

---

## ✅ SOLUCIÓN 3: Verificar Servicios

Asegúrate de que PostgreSQL esté corriendo:

1. Presiona `Win + R`
2. Escribe `services.msc` y presiona Enter
3. Busca `postgresql-x64-XX` (donde XX es la versión)
4. Verifica que el estado sea **Iniciado**
5. Si no está iniciado, click derecho → **Iniciar**

---

## 🧪 Probar la Conexión

Después de aplicar cualquier solución, ejecuta:

```bash
python test_db_connection.py
```

Si todo está bien, verás:
```
✅ ¡CONEXIÓN EXITOSA!
```

---

## 📌 Verificar la Base de Datos

Asegúrate de que la base de datos existe:

```sql
-- En psql o pgAdmin, ejecuta:
CREATE DATABASE "DB_UniversalBox";

-- O verifica si existe:
\l
```

---

## ❓ ¿Aún tienes problemas?

Verifica:
1. ✅ PostgreSQL está corriendo (services.msc)
2. ✅ La base de datos "DB_UniversalBox" existe
3. ✅ La contraseña NO tiene acentos ni caracteres especiales
4. ✅ El usuario es "postgres"
5. ✅ El puerto es 5432

Si todo está correcto y aún falla, es posible que necesites reinstalar psycopg2:
```bash
pip uninstall psycopg2 psycopg2-binary
pip install psycopg2-binary
```


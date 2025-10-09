# 🗄️ Guía de Conexión a Base de Datos

## 🎯 Resumen del Problema

Tu aplicación Django está configurada para usar **variables de entorno** desde un archivo `.env`, pero la **contraseña de PostgreSQL contiene caracteres especiales** (acentos) que causan errores de codificación en Windows.

---

## ⚡ SOLUCIÓN RÁPIDA (3 Pasos)

### 1️⃣ Ejecuta el Menú Interactivo
```bash
python menu_db.py
```

### 2️⃣ Elige una Opción:
- **Opción 1**: Probar la conexión actual
- **Opción 2**: Cambiar a SQLite (temporal, sin contraseña)
- **Opción 3**: Diagnosticar problema de PostgreSQL

### 3️⃣ Si Usas PostgreSQL: Cambia la Contraseña
```sql
-- En pgAdmin o psql:
ALTER USER postgres PASSWORD 'Admin123';
```

Luego actualiza tu archivo `.env`:
```env
DB_PASSWORD=Admin123
```

---

## 🛠️ Scripts Creados para Ti

| Script | Descripción |
|--------|-------------|
| `menu_db.py` | ⭐ **MENÚ PRINCIPAL** - Interfaz interactiva para todo |
| `test_db_connection.py` | 🧪 Prueba completa de conexión |
| `test_postgres_direct.py` | 🔍 Diagnóstico específico de PostgreSQL |
| `cambiar_db.py` | 🔄 Cambiar entre SQLite y PostgreSQL |
| `fix_env_encoding.py` | 📄 Verificar codificación del .env |

---

## 📚 Documentación Creada

| Archivo | Contenido |
|---------|-----------|
| `COMO_PROBAR_DB.md` | 📖 Guía completa de pruebas y comandos |
| `SOLUCION_PASSWORD.md` | 🔧 Solución detallada al problema de contraseña |
| `ENV_TEMPLATE.md` | 📝 Plantilla y ejemplos de .env |

---

## 🚀 Pasos para Empezar

### Si Quieres Usar PostgreSQL:

1. **Abre pgAdmin o psql**
2. **Cambia la contraseña** (sin acentos):
   ```sql
   ALTER USER postgres PASSWORD 'Admin123';
   ```
3. **Actualiza `.env`**:
   ```env
   DB_PASSWORD=Admin123
   ```
4. **Prueba la conexión**:
   ```bash
   python menu_db.py
   # Selecciona opción 1
   ```
5. **Aplica migraciones**:
   ```bash
   python manage.py migrate
   ```

### Si Prefieres SQLite (Más Fácil):

1. **Ejecuta**:
   ```bash
   python cambiar_db.py
   # Selecciona opción 1
   ```
2. **Aplica migraciones**:
   ```bash
   python manage.py migrate
   ```
3. **¡Listo!** Ya puedes trabajar

---

## ✅ Verificación Final

Una vez configurada la base de datos:

```bash
# 1. Probar conexión
python test_db_connection.py

# Deberías ver:
# ✅ ¡CONEXIÓN EXITOSA!

# 2. Aplicar migraciones
python manage.py migrate

# 3. Crear superusuario
python manage.py createsuperuser

# 4. Iniciar servidor
python manage.py runserver
```

---

## 🔧 Configuración Actual

Tu archivo `settings.py` ya está configurado para leer del `.env`:

```python
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}
```

---

## 📋 Ejemplos de Configuración

### SQLite (Desarrollo)
```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

### PostgreSQL
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=DB_UniversalBox
DB_USER=postgres
DB_PASSWORD=Admin123
DB_HOST=localhost
DB_PORT=5432
```

### MySQL
```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=mi_base_datos
DB_USER=root
DB_PASSWORD=MiPass123
DB_HOST=localhost
DB_PORT=3306
```

---

## ❓ FAQ

### ¿Por qué falla mi conexión?
Tu contraseña tiene **caracteres acentuados** (á, é, í, ó, ú, ñ) que causan problemas en Windows.

### ¿Qué base de datos debo usar?
- **SQLite**: Fácil, sin configuración, ideal para desarrollo
- **PostgreSQL**: Potente, ideal para producción

### ¿Puedo cambiar después?
Sí, pero necesitarás migrar los datos. Usa `dumpdata` y `loaddata`.

### ¿Necesito instalar algo más?
- **PostgreSQL**: Ya tienes `psycopg2` instalado ✅
- **MySQL**: Necesitas `pip install mysqlclient`

---

## 🆘 ¿Aún no Funciona?

### Checklist:

- [ ] PostgreSQL está corriendo (Servicios de Windows)
- [ ] La base de datos existe (`CREATE DATABASE DB_UniversalBox;`)
- [ ] La contraseña NO tiene acentos
- [ ] El archivo `.env` está en `backend/.env`
- [ ] El usuario es correcto (normalmente `postgres`)
- [ ] El puerto es 5432 (PostgreSQL) o 3306 (MySQL)

### Si todo falla:

```bash
# Reinstalar psycopg2
pip uninstall psycopg2 psycopg2-binary
pip install psycopg2-binary

# O usa SQLite temporalmente
python cambiar_db.py
# Opción 1: SQLite
```

---

## 💡 Recomendación

Para desarrollo local, usa **SQLite** (es más simple):
```bash
python cambiar_db.py
# Selecciona opción 1
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Cuando vayas a producción, cambia a PostgreSQL.

---

## 📞 Comandos Útiles

```bash
# Menú interactivo (RECOMENDADO)
python menu_db.py

# Probar conexión
python test_db_connection.py

# Diagnosticar PostgreSQL
python test_postgres_direct.py

# Cambiar configuración
python cambiar_db.py

# Verificar .env
python fix_env_encoding.py

# Comandos Django
python manage.py check
python manage.py showmigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## ✨ ¡Listo!

Ahora tienes todas las herramientas para gestionar tu conexión a la base de datos. 

**Empieza por aquí:**
```bash
python menu_db.py
```

¡Buena suerte! 🚀


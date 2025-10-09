# 🧪 Cómo Probar la Conexión a la Base de Datos

## 🎯 Problema Actual
Tu contraseña de PostgreSQL contiene **caracteres especiales con acentos** que causan errores en Windows.

---

## ⚡ SOLUCIÓN RÁPIDA

### Opción 1: Cambiar a SQLite temporalmente
```bash
python cambiar_db.py
# Selecciona opción 1
python test_db_connection.py
```

### Opción 2: Cambiar la contraseña de PostgreSQL
Lee el archivo `SOLUCION_PASSWORD.md` con las instrucciones detalladas.

---

## 🛠️ Scripts Disponibles

### 1. `test_db_connection.py` - Prueba Completa
Prueba la conexión y muestra información detallada:
```bash
python test_db_connection.py
```

**Muestra:**
- ✅ Configuración actual
- ✅ Estado de la conexión
- ✅ Versión de la base de datos
- ✅ Tablas existentes

---

### 2. `test_postgres_direct.py` - Diagnóstico PostgreSQL
Diagnostica problemas específicos de PostgreSQL:
```bash
python test_postgres_direct.py
```

**Detecta:**
- ❌ Caracteres especiales problemáticos
- ❌ Errores de codificación
- ❌ Problemas de conexión

---

### 3. `fix_env_encoding.py` - Verificar .env
Verifica que el archivo .env esté correctamente codificado:
```bash
python fix_env_encoding.py
```

---

### 4. `cambiar_db.py` - Cambiar Base de Datos
Cambia fácilmente entre SQLite y PostgreSQL:
```bash
python cambiar_db.py
```

---

## 📋 Comandos de Django para Probar

### Verificar configuración
```bash
python manage.py check
python manage.py check --database default
```

### Ver estado de migraciones
```bash
python manage.py showmigrations
```

### Aplicar migraciones
```bash
python manage.py migrate
```

### Crear un superusuario (requiere DB funcionando)
```bash
python manage.py createsuperuser
```

### Abrir shell de Django
```bash
python manage.py shell
```

Dentro del shell:
```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT 1")
print(cursor.fetchone())  # Debería mostrar: (1,)
```

---

## 🔍 Verificar PostgreSQL en Windows

### 1. Verificar que PostgreSQL esté corriendo
```powershell
# Abrir PowerShell como Administrador
Get-Service -Name postgresql*
```

### 2. Iniciar PostgreSQL si está detenido
```powershell
Start-Service -Name "postgresql-x64-XX"
```

### 3. Ver logs de PostgreSQL
```
C:\Program Files\PostgreSQL\XX\data\log\
```

---

## 🎨 Configuraciones de Ejemplo

### SQLite (Desarrollo)
```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

### PostgreSQL (Producción)
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
DB_PASSWORD=Admin123
DB_HOST=localhost
DB_PORT=3306
```

---

## ✅ Pasos para Solucionar

1. **Cambiar la contraseña de PostgreSQL**
   ```sql
   ALTER USER postgres PASSWORD 'Admin123';
   ```

2. **Actualizar .env**
   ```env
   DB_PASSWORD=Admin123
   ```

3. **Probar conexión**
   ```bash
   python test_db_connection.py
   ```

4. **Aplicar migraciones**
   ```bash
   python manage.py migrate
   ```

5. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

---

## 🚀 Una Vez que Funcione

```bash
# 1. Aplicar migraciones
python manage.py migrate

# 2. Crear superusuario
python manage.py createsuperuser

# 3. Iniciar servidor
python manage.py runserver

# 4. Acceder al admin
# http://localhost:8000/admin/
```

---

## ❓ Preguntas Frecuentes

### ¿Por qué no funciona mi contraseña?
Las contraseñas con **acentos, ñ, u otros caracteres especiales** causan problemas de codificación en Windows con psycopg2.

### ¿Debo usar SQLite o PostgreSQL?
- **Desarrollo local**: SQLite es más fácil
- **Producción**: PostgreSQL es más robusto

### ¿Puedo cambiar de SQLite a PostgreSQL después?
Sí, pero necesitarás:
1. Exportar los datos de SQLite
2. Importarlos en PostgreSQL
3. O usar `python manage.py dumpdata` y `loaddata`

### ¿Qué pasa si cambio de base de datos?
- Las migraciones seguirán funcionando
- Perderás los datos si no haces backup
- Necesitarás volver a crear el superusuario

---

## 📞 Soporte

Si después de seguir estos pasos aún tienes problemas:

1. Verifica los logs de PostgreSQL
2. Asegúrate de que PostgreSQL esté corriendo
3. Verifica que la base de datos exista
4. Prueba conectarte con pgAdmin directamente
5. Reinstala psycopg2-binary si es necesario

```bash
pip uninstall psycopg2 psycopg2-binary
pip install psycopg2-binary
```


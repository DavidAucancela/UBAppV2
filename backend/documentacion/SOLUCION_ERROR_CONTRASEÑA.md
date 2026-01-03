# 🔧 Solución: Error con Contraseña en DATABASE_URL

## ❌ Error Común

```
ValueError: 'iiOrZHzlu3pA9xZH' does not appear to be an IPv4 or IPv6 address
```

**Causa**: La contraseña tiene caracteres especiales que rompen el parseo de la URL en `DATABASE_URL`.

## ✅ Solución: Usar Variables Individuales

En lugar de usar `DATABASE_URL` cuando tienes caracteres especiales en la contraseña, usa **variables individuales** que son más seguras y fáciles de manejar.

### Para Docker Local (importar datos)

Edita `backend/.env` y usa esta configuración:

```env
# Comenta DATABASE_URL
# DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres

# Usa variables individuales para Docker
DB_NAME=UBAppDB
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5435
```

### Para Supabase (exportar datos)

Si necesitas conectarte a Supabase para exportar, también puedes usar variables individuales:

```env
# Comenta DATABASE_URL
# DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres

# Usa variables individuales para Supabase
DB_HOST=db.gybrifikqkibwqpzjuxm.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=TU_CONTRASEÑA_AQUI
```

**Ventajas de usar variables individuales:**
- ✅ No necesitas codificar caracteres especiales
- ✅ Más fácil de leer y editar
- ✅ Funciona con cualquier tipo de contraseña
- ✅ Ya está soportado en `settings.py`

## 🔄 Cambiar Entre Docker y Supabase

Solo cambia las variables según necesites:

### Para Docker:
```env
DB_HOST=localhost
DB_PORT=5435
DB_NAME=UBAppDB
DB_USER=postgres
DB_PASSWORD=admin
```

### Para Supabase:
```env
DB_HOST=db.gybrifikqkibwqpzjuxm.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=TU_CONTRASEÑA_REAL_DE_SUPABASE
```

## 📝 Pasos para Importar Datos

1. **Configura .env para Docker** (usa las variables de arriba)
2. **Verifica que Docker esté corriendo**:
   ```powershell
   docker ps | findstr postgres_local
   ```
3. **Ejecuta el script de importación**:
   ```powershell
   cd backend
   python importar_datos_local.py
   ```

## 🔐 Si Prefieres Usar DATABASE_URL

Si realmente quieres usar `DATABASE_URL`, necesitas codificar la contraseña:

1. **Copia el Connection String completo desde Supabase Dashboard**
   - Ve a Settings → Database
   - Copia el "Connection string" (URI mode)
   - Ya viene codificado correctamente

2. **O codifica manualmente la contraseña**:
   ```python
   from urllib.parse import quote
   password = "tu_contraseña_con_caracteres_especiales"
   encoded = quote(password)
   # Usa encoded en la URL
   ```

**Recomendación**: Es más fácil usar variables individuales para evitar estos problemas.


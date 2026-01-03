# 🔑 Cómo Encontrar la Contraseña de Supabase

## 📍 Dónde Está la Contraseña

La contraseña que necesitas **NO es** la contraseña de tu cuenta de Supabase. Es la **contraseña de la base de datos PostgreSQL** que se generó cuando creaste tu proyecto en Supabase.

## 🔍 Pasos para Encontrarla

### Opción 1: En el Dashboard de Supabase (RECOMENDADO)

1. **Ve a tu proyecto en Supabase**: https://app.supabase.com
2. **Inicia sesión** con tu cuenta de Supabase
3. **Selecciona tu proyecto**
4. **Ve a Settings** (Configuración) en el menú lateral izquierdo
5. **Haz clic en "Database"** (Base de datos)
6. **Busca la sección "Connection string"** o **"Connection pooling"**
7. **Busca "Database password"** o **"Postgres password"**
8. **Si no la ves directamente**, busca un botón que diga:
   - "Reset database password" (si no la has guardado)
   - "Show password" o un ícono de ojo 👁️
   - "Copy connection string" (ahí viene la contraseña)

### Opción 2: Si Tienes Acceso al Connection String

Si ya tienes un connection string completo (de algún script o configuración anterior), la contraseña está ahí:

```
postgresql://postgres:TU_CONTRASEÑA_AQUI@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres
                                      ↑
                              Esta es la contraseña
```

### Opción 3: Si No Recuerdas la Contraseña

Si no tienes la contraseña guardada en ningún lugar:

1. **Ve a Settings → Database en Supabase**
2. **Busca "Reset database password"** o **"Change database password"**
3. **Haz clic en "Reset"**
4. **Copia la nueva contraseña** que te muestre (⚠️ solo se muestra UNA VEZ)
5. **Guárdala en un lugar seguro** (puedes usar un gestor de contraseñas)
6. **Actualiza tu `.env`** con la nueva contraseña

## 📝 Formato en el .env

Una vez que tengas la contraseña, úsala así en tu `.env`:

```env
DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA_AQUI@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres
```

**⚠️ IMPORTANTE:**
- Sin corchetes `[]`
- Sin comillas `""`
- Directamente después de los dos puntos `:`
- La contraseña puede contener caracteres especiales, úsala tal cual

## 🔐 Ejemplo

Si tu contraseña es `MiContraseña123!@#`, el DATABASE_URL sería:

```env
DATABASE_URL=postgresql://postgres:MiContraseña123!@#@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres
```

**Nota**: Si tu contraseña tiene caracteres especiales que pueden causar problemas, Supabase generalmente los codifica. En ese caso, puedes copiar directamente el connection string completo desde el dashboard.

## 💡 Consejos

1. **Guarda la contraseña en un lugar seguro** (gestor de contraseñas)
2. **No la subas a Git** (el `.env` ya debería estar en `.gitignore`)
3. **Si la cambias**, actualiza también tu `.env`
4. **Copia el connection string completo** desde Supabase si es posible (viene ya codificado)

## 🆘 Si Aún No Puedes Encontrarla

1. **Busca en tu historial de navegador** o notas donde guardaste información del proyecto
2. **Revisa si tienes algún backup** de configuración anterior
3. **Usa "Reset database password"** en Supabase para generar una nueva
4. **Asegúrate de actualizar** todos los lugares donde uses esta contraseña


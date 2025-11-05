# 🚀 Guía de Inicio Rápido - Backend y Frontend

Esta guía te ayudará a levantar tanto el backend (Django) como el frontend (Angular) de la aplicación UBApp.

---

## 📋 Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.8+** (recomendado 3.11+)
- **Node.js 18+** y npm
- **Angular CLI** (se instalará automáticamente con las dependencias)

---

## 🚀 MÉTODO RÁPIDO: Usar Scripts Automáticos

### ⚡ Opción 1: Scripts Automáticos (Recomendado)

Para levantar el backend automáticamente:

```powershell
powershell -ExecutionPolicy Bypass -File iniciar_backend.ps1
```

Para levantar el frontend automáticamente (en otra terminal):

```powershell
powershell -ExecutionPolicy Bypass -File iniciar_frontend.ps1
```

Los scripts automáticamente:
- ✅ Verifican y crean el archivo `.env` si es necesario
- ✅ Activan el entorno virtual
- ✅ Instalan dependencias si faltan
- ✅ Ejecutan migraciones
- ✅ Inician los servidores

---

## 🔧 PASO 1: Configurar el Backend (Django)

### 1.1. Crear archivo .env

**Opción A: Usar el script automático (Recomendado)**

```powershell
cd backend
powershell -ExecutionPolicy Bypass -File crear_env.ps1
```

**Opción B: Crear manualmente**

Navega al directorio del backend y crea el archivo `.env`:

```powershell
cd backend
```

Luego crea el archivo `.env` con este contenido:

```env
SECRET_KEY=django-insecure-dev-key-change-in-production-123456789012345678901234567890
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

OPENAI_API_KEY=sk-proj-temp-key-replace-with-your-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536
```

> **Nota:** Si no tienes una API key de OpenAI, puedes dejar el valor temporal, pero la funcionalidad de búsqueda semántica no funcionará.

### 1.2. Activar el entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

Si tienes problemas con la política de ejecución de PowerShell, ejecuta primero:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 1.3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 1.4. Ejecutar migraciones

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 1.5. Crear superusuario (opcional)

Si es la primera vez que ejecutas el proyecto, crea un superusuario:

```powershell
python manage.py createsuperuser
```

### 1.6. Iniciar el servidor de desarrollo

```powershell
python manage.py runserver
```

El backend estará disponible en: **http://localhost:8000**

- **API Base:** http://localhost:8000/api
- **Admin Panel:** http://localhost:8000/admin
- **Documentación API:** http://localhost:8000/api/docs

---

## 🎨 PASO 2: Configurar el Frontend (Angular)

Abre una **nueva terminal** (mantén el backend corriendo) y sigue estos pasos:

### 2.1. Navegar al directorio del frontend

```powershell
cd frontend
```

### 2.2. Instalar dependencias

```powershell
npm install
```

> **Nota:** Si es la primera vez, esto puede tomar varios minutos.

### 2.3. Verificar la configuración

El archivo `src/app/environments/environment.ts` ya está configurado para apuntar a:
```typescript
apiUrl: 'http://localhost:8000/api'
```

No necesitas cambiar nada si el backend está en el puerto 8000.

### 2.4. Iniciar el servidor de desarrollo

```powershell
npm start
```

O también puedes usar:
```powershell
ng serve
```

El frontend estará disponible en: **http://localhost:4200**

> **💡 Tip:** También puedes usar el script automático desde la raíz del proyecto:
> ```powershell
> powershell -ExecutionPolicy Bypass -File iniciar_frontend.ps1
> ```

---

## ✅ Verificación

Una vez que ambos servidores estén corriendo:

1. **Backend:** http://localhost:8000/admin (deberías ver el panel de administración de Django)
2. **Frontend:** http://localhost:4200 (deberías ver la página de login de UBApp)

### Prueba de conexión

1. Abre el frontend en http://localhost:4200
2. Intenta hacer login (si tienes un usuario creado)
3. Si no tienes usuario, puedes crear uno desde el admin panel del backend

---

## 🛠️ Comandos Útiles

### Backend

```powershell
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver

# Ejecutar servidor en puerto específico
python manage.py runserver 8000
```

### Frontend

```powershell
# Iniciar servidor de desarrollo
npm start

# Compilar para producción
npm run build

# Ejecutar tests
npm test

# Linting
npm run lint
```

---

## ⚠️ Solución de Problemas Comunes

### Error: "No module named 'decouple'"

**Solución:** Asegúrate de tener el entorno virtual activado y las dependencias instaladas:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Error: "Cannot find module '@angular/core'"

**Solución:** Reinstala las dependencias del frontend:
```powershell
cd frontend
rm -rf node_modules
npm install
```

### Error: "Port 8000 already in use"

**Solución:** Cambia el puerto del backend:
```powershell
python manage.py runserver 8001
```

Y actualiza `frontend/src/app/environments/environment.ts`:
```typescript
apiUrl: 'http://localhost:8001/api'
```

### Error: CORS en el navegador

**Solución:** El backend ya está configurado para permitir CORS desde `localhost:4200`. Si persiste el problema, verifica que `CORS_ALLOW_ALL_ORIGINS = True` en `backend/settings.py`.

### Error: "SECRET_KEY not found"

**Solución:** Asegúrate de tener el archivo `.env` en la carpeta `backend/` con la variable `SECRET_KEY` definida.

---

## 📝 Notas Importantes

1. **Mantén ambos servidores corriendo** mientras trabajas:
   - Backend en una terminal
   - Frontend en otra terminal

2. **Base de datos SQLite** por defecto: Los datos se guardan en `backend/db.sqlite3`

3. **Archivo .env**: Nunca subas el archivo `.env` al repositorio. Contiene información sensible.

4. **Puertos por defecto**:
   - Backend: `8000`
   - Frontend: `4200`

---

## 🎯 Siguiente Paso

Una vez que ambos servidores estén corriendo, puedes:

1. Acceder al admin panel: http://localhost:8000/admin
2. Crear usuarios desde el admin o desde el frontend
3. Explorar la documentación de la API: http://localhost:8000/api/docs
4. Comenzar a desarrollar nuevas funcionalidades

---

¡Listo! 🎉 Tu aplicación debería estar corriendo correctamente.


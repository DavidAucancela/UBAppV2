# Inicio Rápido - Nuevas Mejoras del Sistema

## 🚀 Guía de Inicio Rápido

### 1. Ejecutar Migraciones del Backend

```powershell
# Ir al directorio del backend
cd c:\Users\david\App\backend

# Aplicar migraciones
python manage.py migrate usuarios

# Verificar que la migración se aplicó correctamente
python manage.py showmigrations usuarios
```

### 2. Actualizar Cupo Anual de Usuarios Existentes (Opcional)

```powershell
# Entrar a la shell de Django
python manage.py shell
```

```python
# En la shell de Python/Django
from apps.usuarios.models import Usuario

# Actualizar cupo anual de todos los compradores (1000 kg por defecto)
Usuario.objects.filter(rol=4).update(cupo_anual=1000.00)

# O personalizar por usuario
usuario = Usuario.objects.get(username='nombre_usuario')
usuario.cupo_anual = 1500.00  # 1500 kg
usuario.save()

# Salir de la shell
exit()
```

### 3. Iniciar el Backend

```powershell
# Asegurarse de estar en el directorio backend
cd c:\Users\david\App\backend

# Iniciar el servidor
python manage.py runserver
```

El backend estará disponible en: `http://localhost:8000`

### 4. Iniciar el Frontend

```powershell
# En una nueva terminal, ir al directorio frontend
cd c:\Users\david\App\frontend

# Iniciar el servidor de desarrollo
ng serve
```

El frontend estará disponible en: `http://localhost:4200`

---

## 🎯 Rutas Disponibles

### Páginas Públicas (No requieren autenticación)

| Ruta | Descripción |
|------|-------------|
| `/` o `/informacion` | Página de información general del sistema |
| `/ubicaciones` | Ubicaciones de la empresa con mapa |
| `/login` | Inicio de sesión |

### Páginas Protegidas

| Ruta | Descripción | Roles Permitidos |
|------|-------------|------------------|
| `/inicio` | Página de inicio | Todos |
| `/dashboard-usuario` | Dashboard personal del usuario | Todos |
| `/mis-envios` | Lista de envíos del usuario | Todos |
| `/dashboard` | Dashboard gerencial | Admin, Gerente |
| `/usuarios` | Gestión de usuarios | Admin, Gerente |
| `/envios` | Gestión de envíos | Admin, Gerente, Digitador |
| `/busqueda-semantica` | Búsqueda avanzada | Admin, Gerente |
| `/mapa-compradores` | Mapa de compradores | Admin, Gerente, Digitador |
| `/importacion-excel` | Importar desde Excel | Admin, Gerente, Digitador |

---

## 🧪 Pruebas Rápidas

### 1. Probar Dashboard de Usuario

```bash
# Iniciar sesión como comprador y visitar:
http://localhost:4200/dashboard-usuario
```

**Deberías ver:**
- ✅ Barra de progreso del cupo anual
- ✅ Estadísticas de envíos
- ✅ Lista de envíos recientes

### 2. Probar Páginas Informativas

```bash
# Sin autenticar, visitar:
http://localhost:4200/informacion
http://localhost:4200/ubicaciones
```

**Deberías ver:**
- ✅ Página de información con características
- ✅ Página de ubicaciones con oficinas
- ✅ Botones para iniciar sesión

### 3. Probar Permisos por Rol

**Como Comprador:**
- ✅ Puede ver `/dashboard-usuario`
- ✅ Puede ver `/mis-envios`
- ❌ NO puede ver `/dashboard` (gerencial)
- ❌ NO puede ver `/busqueda-semantica`

**Como Digitador:**
- ✅ Puede ver `/envios` (gestión)
- ✅ Puede ver `/importacion-excel`
- ❌ NO puede ver `/busqueda-semantica`

**Como Gerente:**
- ✅ Puede ver `/dashboard` (gerencial)
- ✅ Puede ver `/busqueda-semantica`
- ✅ Puede ver `/usuarios`

**Como Admin:**
- ✅ Puede ver TODAS las rutas

---

## 📊 Endpoints del Backend para Probar

### Dashboard de Usuario
```bash
# Con autenticación
GET http://localhost:8000/api/usuarios/dashboard_usuario/
GET http://localhost:8000/api/usuarios/dashboard_usuario/?anio=2025
```

### Estadísticas de Cupo
```bash
GET http://localhost:8000/api/usuarios/estadisticas_cupo/
GET http://localhost:8000/api/usuarios/estadisticas_cupo/?anio=2025
```

### Mis Envíos
```bash
GET http://localhost:8000/api/usuarios/mis_envios/
GET http://localhost:8000/api/usuarios/mis_envios/?estado=pendiente
GET http://localhost:8000/api/usuarios/mis_envios/?fecha_desde=2025-01-01
```

---

## 🎨 Características Visuales Destacadas

### 1. Barra de Progreso del Cupo
- 🟢 Verde: < 50% usado
- 🔵 Azul: 50-79% usado
- 🟡 Amarillo: 80-89% usado
- 🔴 Rojo: ≥ 90% usado

### 2. Alertas Inteligentes
Cuando el usuario alcanza el 80% de su cupo, aparece una alerta visual.

### 3. Animaciones
- Fade-in suave al cargar componentes
- Hover effects en tarjetas
- Progress bar animada
- Iconos flotantes

---

## 🔧 Solución de Problemas

### Error: "Module not found"
```bash
cd frontend
npm install
```

### Error: "No module named 'apps'"
```bash
cd backend
# Asegurarse de que el entorno virtual esté activado
.\venv\Scripts\activate  # Windows
python manage.py runserver
```

### Error: "CORS not allowed"
Verificar que en `backend/settings.py` esté configurado:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
]
```

### Los cambios no se reflejan
```bash
# Frontend
cd frontend
ng serve --poll=2000

# Backend
cd backend
python manage.py runserver
```

---

## 📱 Navegación Recomendada

### Para Usuario Nuevo (Primera Vez)
1. Visitar `/informacion` → Conocer el sistema
2. Visitar `/ubicaciones` → Ver oficinas
3. Click en "Iniciar Sesión" → `/login`
4. Después del login → Redirigido a `/inicio`
5. Ir a `/dashboard-usuario` → Ver tu dashboard personal

### Para Comprador Regular
1. Login → `/dashboard-usuario`
2. Ver cupo disponible
3. Ver envíos recientes
4. Ir a `/mis-envios` para ver todos

### Para Gerente
1. Login → `/inicio`
2. Ir a `/dashboard` para ver dashboard gerencial
3. Usar `/busqueda-semantica` para búsquedas avanzadas

---

## 📞 Datos de Prueba

### Usuarios de Ejemplo (si existen)

```
Admin:
- username: admin
- password: [tu password]

Gerente:
- username: gerente
- password: [tu password]

Digitador:
- username: digitador
- password: [tu password]

Comprador:
- username: comprador
- password: [tu password]
```

---

## ✅ Lista de Verificación Post-Instalación

- [ ] Migraciones aplicadas correctamente
- [ ] Backend corriendo sin errores
- [ ] Frontend compilando sin errores
- [ ] Página `/informacion` carga correctamente
- [ ] Página `/ubicaciones` carga correctamente
- [ ] Login funciona correctamente
- [ ] Dashboard de usuario muestra cupo anual
- [ ] Envíos se visualizan correctamente
- [ ] Permisos por rol funcionan
- [ ] Búsqueda semántica (solo admin/gerente)

---

## 🎉 ¡Listo!

Tu sistema ahora cuenta con:
- ✅ Sistema de roles y permisos mejorado
- ✅ Dashboard personalizado por usuario
- ✅ Visualización de cupo anual
- ✅ Páginas informativas profesionales
- ✅ Mejor experiencia de usuario

**¡Disfruta de las nuevas funcionalidades!**

---

Para más información detallada, consulta: `MEJORAS_SISTEMA_ROLES_DASHBOARD.md`


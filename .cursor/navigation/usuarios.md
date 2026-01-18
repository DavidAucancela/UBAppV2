# 👥 Módulo de Gestión de Usuarios

## 📍 Ubicación
- **Frontend:** `frontend/src/app/components/usuarios/usuarios-list/`
- **Backend:** `backend/apps/usuarios/`
- **Ruta:** `/usuarios`

## 🎯 Funcionalidad
Administración completa de usuarios del sistema con roles, permisos, ubicaciones geográficas y control de acceso.

## 📁 Estructura de Archivos

### Frontend
```
usuarios/
└── usuarios-list/
    ├── usuarios-list.component.ts
    ├── usuarios-list.component.html
    └── usuarios-list.component.css
```

### Backend
```
usuarios/
├── models.py          # Modelo Usuario
├── views.py           # UsuarioViewSet
├── serializers.py     # UsuarioSerializer
├── services.py        # UsuarioService (cambiar_password)
├── validators.py      # validar_password_fuerte
└── permissions.py     # Permisos por rol
```

## 🔑 Componentes Clave

### 1. Modelo Usuario
**Archivo:** `backend/apps/usuarios/models.py`
- Campos básicos: username, nombre, correo, cedula
- Rol (1=Admin, 2=Gerente, 3=Digitador, 4=Comprador)
- Ubicación: provincia, canton, ciudad
- Cupo anual (para compradores)
- Estado activo/inactivo

### 2. Roles del Sistema
1. **Admin (1):** Acceso completo
2. **Gerente (2):** Gestión de usuarios y envíos
3. **Digitador (3):** Registro de envíos y productos
4. **Comprador (4):** Solo sus propios envíos

### 3. Validación de Contraseñas
**Archivo:** `backend/apps/usuarios/validators.py`
- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos una minúscula
- Al menos un número
- Al menos un carácter especial

### 4. Ubicaciones Geográficas
- Selectores en cascada: Provincia → Cantón → Ciudad
- Carga dinámica desde API
- Almacenamiento en modelo Usuario

## 📊 Funcionalidades

### Crear/Editar Usuario
- Formulario completo con validaciones
- Selección de rol
- Configuración de ubicación
- Contraseña segura (solo en creación)

### Vista de Detalles
- Información completa del usuario
- Historial de fechas
- Estado y rol

### Filtros
- Por rol
- Por estado (activo/inactivo)
- Búsqueda por texto

## 🚀 Prompts Útiles

1. **"Cómo se implementan los roles y permisos"**
2. **"Dónde se validan las contraseñas"**
3. **"Cómo funcionan los selectores de ubicación en cascada"**
4. **"Dónde se controla el acceso basado en roles"**
5. **"Cómo se restablece una contraseña de usuario"**
6. **"Dónde se muestra la columna de ubicación en la tabla"**

## 🔗 Relaciones
- **Envios:** Cada envío tiene un comprador (Usuario)
- **Autenticación:** JWT tokens
- **Permisos:** Guards en frontend, permissions en backend

## ⚠️ Validaciones Importantes
- Username único
- Correo único
- Cédula única
- Contraseña fuerte (8+ caracteres, mayúsculas, números, especiales)
- Rol requerido


# Sistema de Gestión de Envíos y Usuarios

## Descripción
Sistema completo de gestión de envíos con roles de usuarios, productos y funcionalidades de búsqueda desarrollado con Django REST Framework.

## 📚 Documentación de Arquitectura

### Documentos Principales

1. **[RESUMEN_ARQUITECTURA.md](./RESUMEN_ARQUITECTURA.md)** ⭐ **COMENZAR AQUÍ**
   - Resumen ejecutivo de la arquitectura en capas
   - Visión general de las 4 capas
   - Plan de implementación
   - Métricas de éxito

2. **[ARQUITECTURA_EN_CAPAS.md](./ARQUITECTURA_EN_CAPAS.md)**
   - Documentación completa de arquitectura
   - Detalles de cada capa (Presentación, Negocio, Datos, Semántica)
   - Diagramas de flujo
   - Recomendaciones y correcciones

3. **[PATRONES_DISENO_IMPLEMENTACION.md](./PATRONES_DISENO_IMPLEMENTACION.md)**
   - Patrones de diseño identificados
   - Guía de implementación con ejemplos de código
   - Estrategia de migración gradual
   - Checklist de implementación

### Otros Documentos

- [ANALISIS_COMPLETO_SISTEMA.md](./ANALISIS_COMPLETO_SISTEMA.md) - Análisis del sistema actual
- [RECOMENDACIONES_TECNICAS.md](./RECOMENDACIONES_TECNICAS.md) - Recomendaciones técnicas
- [BUSQUEDA_SEMANTICA_IMPLEMENTADA.md](./BUSQUEDA_SEMANTICA_IMPLEMENTADA.md) - Búsqueda semántica

## Características

### 🔐 **Gestión de Usuarios con Roles**
- **Admin (Rol 1)**: Acceso completo al sistema
- **Gerente (Rol 2)**: Gestión de usuarios y envíos
- **Digitador (Rol 3)**: Registro de envíos y productos
- **Comprador (Rol 4)**: Gestión de sus propios envíos

**Campos de Usuario:**
- Nombre, correo, contraseña y cédula
- Rol asignado
- Información adicional (teléfono, dirección, etc.)

### 📦 **Gestión de Envíos**
- **HAWB**: Número único de identificación
- **Peso Total**: Calculado automáticamente
- **Cantidad Total**: Suma de productos
- **Valor Total**: Valor monetario del envío
- **Fecha de Emisión**: Automática
- **Estado**: Pendiente, En Tránsito, Entregado, Cancelado

### 📋 **Gestión de Productos**
- **Descripción**: Detalles del producto
- **Peso**: Peso individual del producto
- **Cantidad**: Cantidad de unidades
- **Valor**: Valor monetario del producto
- **Categoría**: Electrónica, Ropa, Hogar, Deportes, Otros

### 🔍 **Sistema de Búsqueda**
- Búsqueda en usuarios, envíos y productos
- Historial de búsquedas
- Filtros avanzados por rol
- Estadísticas de uso

## Estructura del Proyecto

```
DRF_APP_BACKEND/
├── DRF_APP_BACKEND/          # Configuración principal
│   ├── settings.py           # Configuraciones del proyecto
│   ├── urls.py              # URLs principales
│   └── wsgi.py              # Configuración WSGI
├── usuarios/                 # App de gestión de usuarios
│   ├── models.py            # Modelo de usuario con roles
│   ├── views.py             # Vistas de usuarios
│   ├── serializers.py       # Serializers para API
│   └── urls.py              # URLs de usuarios
├── archivos/                # App de gestión de envíos y productos
│   ├── models.py            # Modelos de envíos y productos
│   ├── views.py             # Vistas de envíos y productos
│   ├── serializers.py       # Serializers para API
│   └── urls.py              # URLs de envíos y productos
├── busqueda/                # App de búsqueda
│   ├── models.py            # Modelo de historial de búsquedas
│   ├── views.py             # Vistas de búsqueda
│   ├── serializers.py       # Serializers para API
│   └── urls.py              # URLs de búsqueda
└── manage.py                # Script de gestión de Django
```

## Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd DRF_APP_BACKEND
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear superusuario
```bash
python manage.py createsuperuser
```

### 6. Ejecutar el servidor
```bash
python manage.py runserver
```

## API Endpoints

### Usuarios (`/api/usuarios/`)
- `GET /api/usuarios/` - Listar usuarios (filtrado por rol)
- `POST /api/usuarios/` - Crear usuario
- `GET /api/usuarios/{id}/` - Obtener usuario específico
- `PUT /api/usuarios/{id}/` - Actualizar usuario
- `DELETE /api/usuarios/{id}/` - Eliminar usuario
- `GET /api/usuarios/perfil/` - Obtener perfil actual
- `PUT /api/usuarios/actualizar_perfil/` - Actualizar perfil
- `POST /api/usuarios/cambiar_password/` - Cambiar contraseña
- `GET /api/usuarios/compradores/` - Listar solo compradores
- `GET /api/usuarios/por_rol/?rol=X` - Usuarios por rol
- `GET /api/usuarios/estadisticas/` - Estadísticas por rol

### Envíos (`/api/envios/`)
- `GET /api/envios/envios/` - Listar envíos
- `POST /api/envios/envios/` - Crear envío con productos
- `GET /api/envios/envios/{id}/` - Obtener envío específico
- `PUT /api/envios/envios/{id}/` - Actualizar envío
- `DELETE /api/envios/envios/{id}/` - Eliminar envío
- `GET /api/envios/envios/mis_envios/` - Mis envíos (compradores)
- `GET /api/envios/envios/por_estado/?estado=X` - Envíos por estado
- `POST /api/envios/envios/{id}/cambiar_estado/` - Cambiar estado
- `GET /api/envios/envios/estadisticas/` - Estadísticas de envíos

### Productos (`/api/envios/`)
- `GET /api/envios/productos/` - Listar productos
- `POST /api/envios/productos/` - Crear producto
- `GET /api/envios/productos/{id}/` - Obtener producto específico
- `PUT /api/envios/productos/{id}/` - Actualizar producto
- `DELETE /api/envios/productos/{id}/` - Eliminar producto
- `GET /api/envios/productos/por_categoria/?categoria=X` - Productos por categoría
- `GET /api/envios/productos/estadisticas/` - Estadísticas de productos

### Búsqueda (`/api/busqueda/`)
- `GET /api/busqueda/buscar/?q=<termino>&tipo=<tipo>` - Realizar búsqueda
- `GET /api/busqueda/historial/` - Historial de búsquedas
- `DELETE /api/busqueda/limpiar_historial/` - Limpiar historial
- `GET /api/busqueda/estadisticas/` - Estadísticas de búsqueda

## Autenticación

El sistema utiliza autenticación por sesión de Django. Para acceder a los endpoints protegidos:

1. Iniciar sesión en `/admin/`
2. Usar las cookies de sesión en las peticiones API

## Permisos por Rol

### **Admin (Rol 1)**
- ✅ Acceso completo a todos los módulos
- ✅ Gestión de todos los usuarios
- ✅ Visualización de todas las estadísticas

### **Gerente (Rol 2)**
- ✅ Gestión de usuarios (excepto admins)
- ✅ Visualización de todos los envíos
- ✅ Estadísticas generales

### **Digitador (Rol 3)**
- ✅ Visualización de compradores y otros digitadores
- ✅ Gestión de envíos y productos
- ✅ Estadísticas de envíos y productos

### **Comprador (Rol 4)**
- ✅ Gestión de su propio perfil
- ✅ Visualización de sus propios envíos
- ✅ Gestión de productos en sus envíos

## Características Técnicas

- **Framework**: Django 5.2.4
- **API**: Django REST Framework 3.16.0
- **Base de datos**: SQLite (configurable para producción)
- **CORS**: Configurado para desarrollo
- **Filtros**: django-filter para filtrado avanzado
- **Paginación**: Configurada automáticamente

## Desarrollo

### Estructura de Modelos

#### Usuario
- Extiende AbstractUser de Django
- Campos: nombre, correo, cédula, rol
- Roles: Admin, Gerente, Digitador, Comprador
- Control de estado activo/inactivo

#### Envío
- HAWB único
- Relación con comprador
- Cálculo automático de totales
- Estados de seguimiento

#### Producto
- Relación con envío
- Categorización
- Cálculo automático de totales del envío

#### HistorialBusqueda
- Registro de búsquedas realizadas
- Estadísticas de uso por usuario

## Producción

Para desplegar en producción:

1. Cambiar `DEBUG = False`
2. Configurar `ALLOWED_HOSTS`
3. Usar base de datos PostgreSQL
4. Configurar archivos estáticos
5. Configurar CORS apropiadamente
6. Usar HTTPS

## Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. 
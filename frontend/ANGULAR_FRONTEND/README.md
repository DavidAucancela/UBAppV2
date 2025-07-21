# UBApp - Frontend Angular

Este es el frontend de la aplicación UBApp desarrollado con Angular 17. La aplicación proporciona una interfaz moderna y responsiva para gestionar usuarios, envíos y productos.

## 🚀 Características

- **Interfaz Moderna**: Diseño limpio y moderno con gradientes y animaciones
- **Autenticación**: Sistema de login con roles y permisos
- **Dashboard**: Panel de control con estadísticas en tiempo real
- **Gestión de Usuarios**: CRUD completo con filtros y búsqueda
- **Responsive Design**: Optimizado para móviles y tablets
- **Componentes Reutilizables**: Arquitectura modular y escalable

## 🛠️ Tecnologías Utilizadas

- **Angular 17**: Framework principal
- **TypeScript**: Lenguaje de programación
- **CSS3**: Estilos modernos con Flexbox y Grid
- **Font Awesome**: Iconografía
- **RxJS**: Programación reactiva

## 📋 Prerrequisitos

- Node.js (versión 18 o superior)
- npm o yarn
- Angular CLI

## 🔧 Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd frontend/ANGULAR_FRONTEND
   ```

2. **Instalar dependencias**:
   ```bash
   npm install
   ```

3. **Configurar variables de entorno**:
   Crear un archivo `.env` en la raíz del proyecto:
   ```
   API_URL=http://localhost:8000/api
   ```

## 🚀 Ejecución

### Desarrollo
```bash
npm start
# o
ng serve
```

La aplicación estará disponible en `http://localhost:4200`

### Producción
```bash
npm run build
```

Los archivos de producción se generarán en la carpeta `dist/`

## 📁 Estructura del Proyecto

```
src/
├── app/
│   ├── components/
│   │   ├── auth/
│   │   │   └── login/           # Componente de login
│   │   ├── dashboard/
│   │   │   └── dashboard/       # Panel principal
│   │   ├── usuarios/
│   │   │   └── usuarios-list/   # Gestión de usuarios
│   │   ├── envios/
│   │   └── productos/
│   ├── models/
│   │   ├── usuario.ts           # Modelo de usuario
│   │   ├── envio.ts            # Modelo de envío
│   │   └── producto.ts         # Modelo de producto
│   ├── services/
│   │   ├── api.service.ts       # Servicio de API
│   │   └── auth.service.ts      # Servicio de autenticación
│   ├── app.component.ts         # Componente principal
│   ├── app.routes.ts           # Configuración de rutas
│   └── app.config.ts           # Configuración de la app
├── assets/
└── styles.css
```

## 🔐 Autenticación y Roles

La aplicación maneja diferentes roles de usuario:

- **Admin (1)**: Acceso completo al sistema
- **Gerente (2)**: Gestión de usuarios y envíos
- **Digitador (3)**: Gestión de envíos y productos
- **Comprador (4)**: Visualización de envíos propios

### Credenciales de Prueba

- **Usuario**: admin
- **Contraseña**: admin123
- **Rol**: Administrador

## 🎨 Componentes Principales

### Login Component
- Formulario de autenticación moderno
- Validación de campos
- Manejo de errores
- Animaciones suaves

### Dashboard Component
- Estadísticas en tiempo real
- Gráficos y métricas
- Actividad reciente
- Navegación rápida

### Usuarios List Component
- Tabla con paginación
- Filtros avanzados
- Búsqueda en tiempo real
- Modal para crear/editar
- Validación de formularios

## 🔧 Configuración

### Variables de Entorno
```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api'
};
```

### Rutas
```typescript
// src/app/app.routes.ts
export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'usuarios', component: UsuariosListComponent },
  // ... más rutas
];
```

## 🧪 Testing

```bash
# Ejecutar tests unitarios
npm test

# Ejecutar tests con coverage
npm run test:coverage
```

## 📱 Responsive Design

La aplicación está optimizada para diferentes dispositivos:

- **Desktop**: Layout completo con sidebar
- **Tablet**: Layout adaptativo
- **Mobile**: Layout móvil optimizado

## 🎯 Características de UX

- **Loading States**: Indicadores de carga
- **Error Handling**: Manejo de errores amigable
- **Success Messages**: Confirmaciones de acciones
- **Form Validation**: Validación en tiempo real
- **Smooth Animations**: Transiciones suaves

## 🔄 Integración con Backend

La aplicación se conecta con el backend Django a través de:

- **API REST**: Endpoints para CRUD
- **Autenticación**: JWT tokens
- **CORS**: Configurado para desarrollo
- **Error Handling**: Manejo de errores HTTP

## 🚀 Despliegue

### Netlify
```bash
npm run build
# Subir carpeta dist/ a Netlify
```

### Vercel
```bash
npm run build
# Conectar repositorio a Vercel
```

### Docker
```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html
EXPOSE 80
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Email: soporte@ubapp.com
- Documentación: [docs.ubapp.com](https://docs.ubapp.com)

## 🔄 Changelog

### v1.0.0
- ✅ Sistema de autenticación
- ✅ Dashboard con estadísticas
- ✅ Gestión de usuarios
- ✅ Interfaz moderna y responsiva
- ✅ Integración con backend Django

---

**Desarrollado con ❤️ por el equipo UBApp**

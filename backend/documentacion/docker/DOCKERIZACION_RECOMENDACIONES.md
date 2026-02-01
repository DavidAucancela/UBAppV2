# 🐳 Guía de Dockerización - Recomendaciones y Mejores Prácticas

## 📋 Tabla de Contenidos

1. [Recomendaciones ANTES de Dockerizar](#antes-de-dockerizar)
2. [Módulos en Docker Compose](#modulos-en-docker-compose)
3. [Recomendaciones DESPUÉS de Dockerizar](#despues-de-dockerizar)
4. [Troubleshooting](#troubleshooting)

---

## 🔍 ANTES de Dockerizar

### 1. **Revisar y Limpiar el Código**

✅ **Checklist Pre-Docker:**

- [ ] **Variables de entorno**: Mover todas las configuraciones hardcodeadas a variables de entorno
- [ ] **Secrets**: Nunca incluir claves API, passwords, o tokens en el código
- [ ] **Logs**: Verificar que los logs se escriban en ubicaciones accesibles desde Docker
- [ ] **Archivos temporales**: Revisar que no se creen archivos en ubicaciones que no persistan
- [ ] **Dependencias**: Verificar que `requirements.txt` y `package.json` estén actualizados

### 2. **Preparar Variables de Entorno**

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores reales
# ⚠️ IMPORTANTE: Cambiar SECRET_KEY, passwords, y API keys
```

**Variables críticas a configurar:**
- `SECRET_KEY`: Generar una nueva clave secreta única
- `DB_PASSWORD`: Cambiar la contraseña por defecto
- `REDIS_PASSWORD`: Configurar contraseña para Redis
- `OPENAI_API_KEY`: Tu clave de API de OpenAI

### 3. **Backup de Datos Existentes**

Si ya tienes datos en producción o desarrollo:

```bash
# Backup de base de datos PostgreSQL
pg_dump -h localhost -U postgres -d UBAppDB > backup_pre_docker.sql

# Backup de archivos media
tar -czf media_backup.tar.gz backend/media/

# Backup de logs importantes
tar -czf logs_backup.tar.gz logs/
```

### 4. **Verificar Estructura de Directorios**

Asegúrate de que existan estos directorios:
- `backend/logs/` - Para logs de la aplicación
- `backend/media/` - Para archivos subidos por usuarios
- `backend/staticfiles/` - Para archivos estáticos de Django

### 5. **Revisar Configuración de CORS y ALLOWED_HOSTS**

En `backend/settings.py`, verificar que:
- `ALLOWED_HOSTS` incluya los hosts donde se desplegará
- `CORS_ALLOWED_ORIGINS` incluya las URLs del frontend
- `CSRF_TRUSTED_ORIGINS` esté configurado correctamente

### 6. **Instalar Docker y Docker Compose**

```powershell
# Verificar instalación
docker --version
docker-compose --version

# Si no están instalados, descargar desde:
# https://www.docker.com/products/docker-desktop/
```

---

## 🏗️ Módulos en Docker Compose

### Servicios Incluidos en `docker-compose.yml`:

#### 1. **PostgreSQL con pgvector** ✅ OBLIGATORIO
- **Propósito**: Base de datos principal
- **Puerto**: 5432 (interno), configurable externamente
- **Volúmenes**: 
  - `postgres_data`: Datos persistentes
  - `./backend/backup`: Para backups
- **Health Check**: Verifica que PostgreSQL esté listo antes de iniciar otros servicios

#### 2. **Redis** ✅ RECOMENDADO (Opcional pero altamente recomendado)
- **Propósito**: Cache, sesiones, rate limiting
- **Puerto**: 6379
- **Volúmenes**: `redis_data`: Datos persistentes
- **Nota**: Si no usas Redis, el sistema usará cache en memoria (menos eficiente)

#### 3. **Backend Django** ✅ OBLIGATORIO
- **Propósito**: API REST
- **Puerto**: 8000
- **Volúmenes**:
  - `./backend`: Código fuente (desarrollo)
  - `backend_static`: Archivos estáticos
  - `backend_media`: Archivos media
  - `backend_logs`: Logs de la aplicación
- **Comandos automáticos**:
  - Espera a que PostgreSQL esté listo
  - Ejecuta migraciones
  - Recolecta archivos estáticos
  - Inicia servidor Gunicorn

#### 4. **Frontend Angular** ✅ OBLIGATORIO
- **Propósito**: Interfaz de usuario
- **Puerto**: 4200 (mapeado a 80 en el contenedor)
- **Build**: Multi-stage build para optimizar tamaño
- **Volúmenes**: 
  - `./frontend`: Código fuente (desarrollo)
  - `/app/node_modules`: Excluido para evitar conflictos

#### 5. **Nginx** ⚠️ OPCIONAL (Solo para producción)
- **Propósito**: Servir archivos estáticos, reverse proxy, SSL
- **Puerto**: 80 (HTTP), 443 (HTTPS)
- **Profile**: Solo se inicia con `--profile production`
- **Uso**: Para producción con dominio propio y SSL

---

## 🚀 DESPUÉS de Dockerizar

### 1. **Primera Ejecución**

```powershell
# Construir e iniciar todos los servicios
docker-compose up --build

# O en modo detached (segundo plano)
docker-compose up -d --build
```

**Verificar que todo esté funcionando:**
```powershell
# Ver logs
docker-compose logs -f

# Ver estado de los contenedores
docker-compose ps

# Verificar health checks
docker-compose ps
# Todos los servicios deben mostrar "healthy"
```

### 2. **Verificar Conexiones**

```powershell
# Verificar backend
curl http://localhost:8000/api/health/

# Verificar frontend
curl http://localhost:4200/

# Verificar base de datos
docker-compose exec postgres psql -U postgres -d UBAppDB -c "SELECT version();"

# Verificar Redis
docker-compose exec redis redis-cli ping
```

### 3. **Crear Usuario Administrador**

```powershell
# Acceder al contenedor del backend
docker-compose exec backend bash

# Crear superusuario
python manage.py createsuperuser
```

### 4. **Importar Datos Existentes (si aplica)**

```powershell
# Si tienes un backup SQL
docker-compose exec -T postgres psql -U postgres -d UBAppDB < backup_pre_docker.sql

# O usar el script de importación
docker-compose exec backend python funciones/importar_datos_local.py
```

### 5. **Configurar Volúmenes Persistentes**

Los volúmenes Docker ya están configurados para persistir datos:
- **Base de datos**: `postgres_data` - Los datos NO se pierden al detener contenedores
- **Redis**: `redis_data` - Cache persistente
- **Media**: `backend_media` - Archivos subidos por usuarios
- **Logs**: `backend_logs` - Logs de la aplicación

### 6. **Monitoreo y Logs**

```powershell
# Ver logs en tiempo real
docker-compose logs -f backend
docker-compose logs -f frontend

# Ver logs de un servicio específico
docker-compose logs postgres

# Ver últimas 100 líneas
docker-compose logs --tail=100 backend
```

### 7. **Backups Regulares**

**Crear script de backup automático:**

```powershell
# backup.ps1
docker-compose exec -T postgres pg_dump -U postgres UBAppDB > backups/db_$(Get-Date -Format "yyyyMMdd_HHmmss").sql
docker-compose exec backend tar -czf /backup/media_$(Get-Date -Format "yyyyMMdd_HHmmss").tar.gz /app/media/
```

**Programar backups:**
- Usar Task Scheduler de Windows
- O configurar cron job en Linux/Mac

### 8. **Actualizaciones**

```powershell
# Detener servicios
docker-compose down

# Actualizar código (git pull, etc.)

# Reconstruir e iniciar
docker-compose up --build -d

# Aplicar migraciones (si hay nuevas)
docker-compose exec backend python manage.py migrate
```

### 9. **Producción con Nginx**

```powershell
# Iniciar con perfil de producción (incluye Nginx)
docker-compose --profile production up -d

# Configurar SSL en nginx/conf.d/default.conf
# Agregar certificados en nginx/ssl/
```

### 10. **Optimizaciones de Rendimiento**

**Backend:**
- Ajustar número de workers de Gunicorn según CPU:
  ```yaml
  # En docker-compose.yml, cambiar:
  --workers 3
  # A: --workers $(nproc)  # Usa todos los cores disponibles
  ```

**Frontend:**
- El build de producción ya está optimizado
- Considerar CDN para archivos estáticos en producción

**Base de datos:**
- Configurar conexiones pool según carga esperada
- Monitorear uso de memoria y CPU

---

## 🔧 Troubleshooting

### Problema: Contenedores no inician

```powershell
# Ver logs detallados
docker-compose logs

# Verificar puertos ocupados
netstat -ano | findstr :8000
netstat -ano | findstr :4200
netstat -ano | findstr :5432

# Limpiar y reiniciar
docker-compose down -v
docker-compose up --build
```

### Problema: Error de conexión a base de datos

```powershell
# Verificar que PostgreSQL esté corriendo
docker-compose ps postgres

# Ver logs de PostgreSQL
docker-compose logs postgres

# Verificar variables de entorno
docker-compose exec backend env | grep DB_
```

### Problema: Frontend no se conecta al backend

1. Verificar `API_URL` en variables de entorno
2. Verificar CORS en `backend/settings.py`
3. Verificar que el backend esté accesible:
   ```powershell
   curl http://localhost:8000/api/health/
   ```

### Problema: Archivos media no se guardan

```powershell
# Verificar permisos del volumen
docker-compose exec backend ls -la /app/media

# Verificar configuración en settings.py
docker-compose exec backend python manage.py shell
>>> from django.conf import settings
>>> print(settings.MEDIA_ROOT)
```

### Problema: Redis no funciona

```powershell
# Verificar conexión
docker-compose exec redis redis-cli ping

# Verificar password
docker-compose exec redis redis-cli -a redis_password ping

# Si no funciona, el sistema usará cache en memoria (funcional pero menos eficiente)
```

### Limpiar Todo y Empezar de Nuevo

```powershell
# ⚠️ CUIDADO: Esto elimina TODOS los datos
docker-compose down -v
docker system prune -a --volumes
```

---

## 📊 Checklist Post-Dockerización

- [ ] Todos los servicios están corriendo (`docker-compose ps`)
- [ ] Health checks pasan (`/api/health/` responde)
- [ ] Frontend carga correctamente
- [ ] Backend responde a peticiones
- [ ] Base de datos tiene datos (si aplica)
- [ ] Logs se están generando correctamente
- [ ] Archivos media se guardan y sirven
- [ ] Usuario administrador creado
- [ ] Backups configurados
- [ ] Variables de entorno seguras (no en código)
- [ ] Documentación actualizada

---

## 🎯 Próximos Pasos Recomendados

1. **CI/CD**: Configurar pipeline de despliegue automático
2. **Monitoreo**: Implementar Prometheus + Grafana
3. **Logs Centralizados**: Considerar ELK Stack o similar
4. **SSL**: Configurar certificados Let's Encrypt
5. **Escalabilidad**: Considerar Kubernetes para producción a gran escala
6. **Testing**: Agregar tests de integración con Docker
7. **Documentación API**: Verificar que `/api/docs/` funcione correctamente

---

## 📚 Recursos Adicionales

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Angular Deployment](https://angular.io/guide/deployment)

---

**Última actualización**: Enero 2026
**Versión**: 1.0.0

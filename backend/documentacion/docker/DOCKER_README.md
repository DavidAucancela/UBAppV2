# 🐳 Guía Rápida de Docker - UBApp

## Inicio Rápido

### 1. Preparar Variables de Entorno

```powershell
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores (especialmente SECRET_KEY y passwords)
```

### 2. Construir e Iniciar

```powershell
# Construir e iniciar todos los servicios
docker-compose up --build

# O en segundo plano
docker-compose up -d --build
```

### 3. Verificar Estado

```powershell
# Ver estado de contenedores
docker-compose ps

# Ver logs
docker-compose logs -f

# Verificar health check
curl http://localhost:8000/api/health/
```

### 4. Crear Usuario Administrador

```powershell
docker-compose exec backend python manage.py createsuperuser
```

### 5. Acceder a la Aplicación

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs/
- **Admin Django**: http://localhost:8000/admin/

## Comandos Útiles

```powershell
# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (⚠️ elimina datos)
docker-compose down -v

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f frontend

# Ejecutar comandos en contenedores
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py shell

# Reconstruir un servicio específico
docker-compose up --build backend

# Ver uso de recursos
docker stats
```

## Servicios Incluidos

- **PostgreSQL** (puerto 5432): Base de datos con pgvector
- **Redis** (puerto 6379): Cache y sesiones
- **Backend Django** (puerto 8000): API REST
- **Frontend Angular** (puerto 4200): Interfaz web
- **Nginx** (puerto 80): Solo con `--profile production`

## Troubleshooting

Ver `DOCKERIZACION_RECOMENDACIONES.md` para guía completa de troubleshooting.

## Documentación Completa

Para recomendaciones detalladas antes y después de dockerizar, ver:
- `DOCKERIZACION_RECOMENDACIONES.md`

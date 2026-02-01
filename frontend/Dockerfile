# Dockerfile para Frontend Angular
# Multi-stage build para optimizar el tamaño de la imagen

# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --legacy-peer-deps

# Copiar código fuente
COPY . .

# Construir la aplicación
RUN npm run build:prod

# Stage 2: Production
FROM nginx:alpine

# Copiar archivos construidos desde el stage de build
COPY --from=builder /app/dist/angular-frontend /usr/share/nginx/html

# Copiar configuración personalizada de nginx (opcional)
# Si tienes una configuración personalizada, descomenta la siguiente línea:
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Nginx inicia automáticamente

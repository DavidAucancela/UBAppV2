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

# Copiar archivos del navegador (Angular 17+ con SSR genera browser/ y server/)
COPY --from=builder /app/dist/angular-frontend/browser /usr/share/nginx/html

# Configuración nginx para SPA (rutas de Angular)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Nginx inicia automáticamente

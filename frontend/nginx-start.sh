#!/bin/sh
set -e

PORT="${PORT:-8080}"

echo "Iniciando nginx en puerto $PORT"

cat > /etc/nginx/conf.d/default.conf << NGINX_CONF
server {
    listen ${PORT};
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()";

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)\$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINX_CONF

echo "Config de nginx generada:"
cat /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"

#!/bin/sh
set -e

# Railway target port está configurado en 80 - nginx siempre escucha en 80
PORT=80

echo "Iniciando nginx en puerto $PORT"

cat > /etc/nginx/conf.d/default.conf << NGINX_CONF
server {
    listen ${PORT};
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

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

#!/bin/sh
# Reemplaza ${PORT} con el valor real de PORT en la config de nginx
envsubst '${PORT}' < /etc/nginx/conf.d/default.conf > /tmp/default.conf
mv /tmp/default.conf /etc/nginx/conf.d/default.conf

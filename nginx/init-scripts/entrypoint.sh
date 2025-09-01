#!/bin/bash
set -e

envsubst '$BACKEND_NGINX_PORT $BACKEND_NGINX_HOST $GATEWAY_PORT' < /init-scripts/template.conf > /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"



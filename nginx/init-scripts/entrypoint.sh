#!/bin/bash
set -e

envsubst '$NGINX_PORT $NGINX_HOST $GATEWAY_PORT' < /init-scripts/default.conf.template > /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"
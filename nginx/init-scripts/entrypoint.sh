#!/bin/bash
set -e

envsubst '$NGINX_APP_PORT $NGINX_HOST $GATEWAY_APP_PORT' < /init-scripts/default.conf.template > /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"
#!/bin/bash
set -e

envsubst < /init-scripts/init-template.sql > /docker-entrypoint-initdb.d/init.sql

exec docker-entrypoint.sh postgres "$@"
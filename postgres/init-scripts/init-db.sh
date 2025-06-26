#!/bin/bash
set -e

echo "Processing SQL template with envsubst..."
envsubst < /init-scripts/init-template.sql > /init-scripts/init.sql

cp /init-scripts/init.sql /docker-entrypoint-initdb.d/init.sql
rm -f /init-scripts/*
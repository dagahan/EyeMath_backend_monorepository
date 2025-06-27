#!/bin/bash
set -e

envsubst < /init-scripts/init-template.sql > /init-scripts/init.sql

mv /init-scripts/init.sql /docker-entrypoint-initdb.d/init.sql
rm -f /init-scripts/*
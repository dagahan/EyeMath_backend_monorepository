#!/bin/bash
set -escripts

echo "Running initialization script..."
/init-scripts/init-db.sh

exec docker-entrypoint.sh postgres "$@"
#!/bin/bash
set -e

echo "Running initialization script..."
/init-scripts/init-db.sh

exec docker-entrypoint.sh postgres "$@"
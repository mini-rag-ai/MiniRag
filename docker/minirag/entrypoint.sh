#!/usr/bin/env bash
set -e

echo "Running database migrations..."
cd /app/models/db_schemes/minirag/
alembic upgrade head
cd /app

echo "Starting FastAPI server..."
exec "$@"

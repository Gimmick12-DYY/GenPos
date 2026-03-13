#!/usr/bin/env bash
set -e

echo "Running database migrations..."
python -m alembic upgrade head

echo "Starting GenPos API..."
exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8000}"

#!/bin/sh
set -e

echo "Waiting for database..."
until alembic upgrade head; do
  echo "Database not ready, retrying in 2s..."
  sleep 2
done

echo "Migrations applied successfully."
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

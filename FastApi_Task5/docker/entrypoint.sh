#!/bin/bash
set -e

echo "Starting FastAPI Application..."

# Запускаем миграции Alembic (если есть)
if command -v alembic &> /dev/null; then
    echo "Running Alembic migrations..."
    cd /app
    alembic upgrade head
fi

# Запускаем приложение
echo "Starting Uvicorn server..."
exec uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8000 --reload

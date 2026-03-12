#!/bin/bash

# Poetry環境をアクティベート
source $VENV_PATH/bin/activate

# 環境変数で動作モードを切り替え（デフォルトはproduction）
APP_ENV=${APP_ENV:-production}

if [ "$APP_ENV" = "development" ]; then
    echo "🚀 Starting in DEVELOPMENT mode..."
    echo "Starting Vite development server..."
    cd /workspace/frontend-inertia
    npm run dev -- --host 0.0.0.0 &

    echo "Running database migrations..."
    cd /workspace
    alembic upgrade head

    echo "Starting FastAPI server with reload..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --proxy-headers
else
    echo "🚀 Starting in PRODUCTION mode..."
    echo "Building frontend assets..."
    cd /workspace/frontend-inertia
    npm run build

    echo "Running database migrations..."
    cd /workspace
    alembic upgrade head

    echo "Starting FastAPI server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers
fi

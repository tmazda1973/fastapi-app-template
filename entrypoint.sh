#!/bin/bash

# conda環境をアクティベート
source activate myenv

# 環境変数で動作モードを切り替え（デフォルトはproduction）
APP_ENV=${APP_ENV:-production}

if [ "$APP_ENV" = "development" ]; then
    echo "🚀 Starting in DEVELOPMENT mode..."
    echo "Starting Vite development server..."
    cd /usr/src/app/frontend-inertia
    npm run dev -- --host 0.0.0.0 &
    
    echo "Starting FastAPI server with reload..."
    cd /usr/src/app
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "🚀 Starting in PRODUCTION mode..."
    echo "Building frontend assets..."
    cd /usr/src/app/frontend-inertia
    npm run build
    
    echo "Starting FastAPI server..."
    cd /usr/src/app
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
fi
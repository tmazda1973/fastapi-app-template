#!/bin/bash

echo "=== 開発環境自動セットアップ ==="

# Dockerコンテナが起動しているかチェック
if docker exec fastapi-app echo "Container check" &> /dev/null; then
    echo "🐳 Dockerコンテナが起動中 → コンテナ環境を設定"
    ./scripts/vscode-setup-container-dev.sh
else
    echo "💻 Dockerコンテナが未起動 → ローカル環境を設定"
    ./scripts/vscode-setup-local-dev.sh
fi

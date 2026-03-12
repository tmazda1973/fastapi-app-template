#!/bin/bash

echo "=== コンテナ開発環境セットアップ ==="

# Dockerコンテナが起動しているかチェック
if ! docker exec fastapi-app echo "Container is running" &> /dev/null; then
    echo "❌ fastapi-appコンテナが起動していません"
    echo "💡 'docker-compose up -d' でコンテナを起動してください"
    exit 1
fi

echo "✅ fastapi-appコンテナが起動中"

# コンテナ内のツールバージョン確認
echo "🔧 コンテナ内ツールバージョン確認:"
docker exec fastapi-app ruff --version
docker exec fastapi-app python --version

# コンテナ用VS Code設定に切り替え
echo "🔧 VS Code設定をコンテナ用に切り替え中..."
cp .vscode/settings.container.json .vscode/settings.json
echo "✅ コンテナ開発環境の設定完了"

echo ""
echo "🎉 コンテナ開発環境のセットアップが完了しました！"
echo "📝 以下のコマンドが使用可能です："
echo "   docker exec fastapi-app ruff check app/"
echo "   docker exec fastapi-app ruff format app/"
echo "   ./scripts/ruff-container.sh check app/"

#!/bin/bash

echo "=== ローカル開発環境セットアップ ==="

# requirements-dev.txtからローカルツールをインストール
if [ -f "requirements-dev.txt" ]; then
    echo "📦 開発ツールをインストール中..."
    pip install -r requirements-dev.txt
    echo "✅ 開発ツールのインストール完了"
else
    echo "❌ requirements-dev.txt が見つかりません"
    exit 1
fi

# ローカル用VS Code設定に切り替え
echo "🔧 VS Code設定をローカル用に切り替え中..."
cp .vscode/settings.local.json .vscode/settings.json
echo "✅ ローカル開発環境の設定完了"

echo ""
echo "🎉 ローカル開発環境のセットアップが完了しました！"
echo "📝 以下のコマンドが使用可能です："
echo "   ruff check app/"
echo "   ruff format app/"
echo "   black app/"
echo "   mypy app/"

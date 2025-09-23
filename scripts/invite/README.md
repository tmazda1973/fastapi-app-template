# 招待機能CLIツール

招待機能のAPIを実行するためのコマンドラインスクリプトです。

Typerライブラリを使用して実装されており、美しく使いやすいCLIインターフェースを提供します。

## 使用方法

> **💡 注意**: このツールは **コンテナベース** で動作します。ホストからMakeコマンドで実行してください。

### 🚀 Makeコマンド使用（推奨）

```bash
cd scripts/invite

# ヘルプ表示
make help

# CLIツールの詳細ヘルプ
make show-commands

# 招待メール送信
make send EMAIL=user@example.com

# 招待トークン検証
make verify TOKEN=<招待トークン>

# 招待受諾
make accept TOKEN=<招待トークン> PASSWORD=<パスワード>

# コンテナ状態確認
make check-container

# テスト送信（user@example.com固定）
make test-send
```

### 📋 各コマンドの詳細

**1. 招待メールの送信**
```bash
make send EMAIL=user@example.com
```
指定されたメールアドレスのユーザーに招待メールを送信します。
ユーザーがデータベースに存在している必要があります。

**2. 招待トークンの検証**
```bash
make verify TOKEN=<招待トークン>
```
招待トークンが有効かどうかを検証します。トークンの有効期限や関連するユーザー情報が表示されます。

**3. 招待の受諾**
```bash
make accept TOKEN=<招待トークン> PASSWORD=<パスワード>
```
招待トークンを使用してユーザーアカウントを有効化し、パスワードを設定します。

**4. コンテナ状態確認**
```bash
make check-container
```
FastAPIコンテナが正常に起動しているかを確認します。

**5. テスト送信**
```bash
make test-send
```
`user@example.com`に対してテスト用の招待メールを送信します（固定メールアドレス）。

**6. CLIツールの詳細ヘルプ**
```bash
make show-commands
```
CLIツール本体のヘルプコマンドを表示します。

### 🔧 Docker execコマンド直接実行（上級者向け）

> **💡 説明**: コンテナにログインせず、ホストから直接コンテナ内でコマンドを実行する方法です。

```bash
# ヘルプ表示（ホストから実行）
docker exec fastapi-app bash -c "source activate myenv && cd /usr/src/app && PYTHONPATH=/usr/src/app python scripts/invite/cli.py --help"

# 招待送信（ホストから実行）
docker exec fastapi-app bash -c "source activate myenv && cd /usr/src/app && PYTHONPATH=/usr/src/app python scripts/invite/cli.py send-invite user@example.com"

# ※ これらのコマンドはホストのターミナルから実行します
# ※ コンテナにログイン（docker exec -it fastapi-app bash）は不要です
```

## 前提条件

- **FastAPIアプリケーションコンテナが起動していること**
  ```bash
  make env-up-all  # または docker-compose up -d
  ```
- **データベースが起動していること**
- **招待を送信する場合、対象のユーザーがデータベースに存在していること**
- **適切な環境変数が設定されていること** (`.env`ファイル)

## ⚡ クイックスタート

```bash
# 1. 招待ツールディレクトリに移動
cd scripts/invite

# 2. 利用可能なコマンドを確認
make help

# 3. CLIツールの詳細ヘルプ（必要に応じて）
make show-commands

# 4. テスト用ユーザーに招待送信
make send EMAIL=user@example.com

# 5. 招待トークンの検証（出力から取得したトークンを使用）
make verify TOKEN=<取得したトークン>
```

## 出力形式

すべてのコマンドはJSON形式で結果を出力します。

### 成功例

```json
{
  "success": true,
  "message": "招待メールの送信処理が完了しました",
  "user_email": "user@example.com",
  "user_name": "テストユーザー",
  "invite_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "invite_expires": 1754305627
}
```

### エラー例

```json
{
  "success": false,
  "error": "ユーザーが見つかりません: user@example.com",
  "suggestion": "まずユーザーをデータベースに作成してください"
}
```

## 各コマンドのヘルプ

### 📋 利用可能なコマンド一覧

```bash
cd scripts/invite

# 基本的なヘルプ（推奨）
make help

# CLIツールの詳細ヘルプ
make show-commands
```

### 🔍 詳細なコマンドヘルプ

CLIツール本体の詳細ヘルプを確認したい場合（**ホストから実行**）：

```bash
# 全体のヘルプ（ホストターミナルで実行）
docker exec fastapi-app bash -c "source activate myenv && cd /usr/src/app && PYTHONPATH=/usr/src/app python scripts/invite/cli.py --help"

# 個別コマンドのヘルプ（ホストターミナルで実行）
docker exec fastapi-app bash -c "source activate myenv && cd /usr/src/app && PYTHONPATH=/usr/src/app python scripts/invite/cli.py send-invite --help"
docker exec fastapi-app bash -c "source activate myenv && cd /usr/src/app && PYTHONPATH=/usr/src/app python scripts/invite/cli.py verify-invite --help"
docker exec fastapi-app bash -c "source activate myenv && cd /usr/src/app && PYTHONPATH=/usr/src/app python scripts/invite/cli.py accept-invite --help"
```

> **⚠️ 注意**: これらは全て**ホストのターミナル**から実行します。  
> コンテナ内にログイン（`docker exec -it fastapi-app bash`）してから実行するものではありません。

## Typerの特徴

- **美しい出力**: リッチなテキスト表示でコマンドが見やすい
- **自動補完**: `--install-completion`で補完機能をインストール可能
- **型安全**: Python型ヒントによる引数検証
- **直感的**: サブコマンド構造で分かりやすい

## 注意事項

- このスクリプトは開発・テスト目的で使用してください
- 本番環境での使用は推奨されません
- メール送信機能は`BackgroundTasks`をモックしているため、実際のメール送信は行われません

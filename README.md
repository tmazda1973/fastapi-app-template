# FastAPI製 Webアプリケーション テンプレート

モダンなWebアプリケーション開発のためのモノリス SPAアーキテクチャテンプレートです。

FastAPI + Inertia.js + Reactの組み合わせで、伝統的なサーバーサイドルーティングとモダンなSPA体験を両立し、多言語対応（i18n）とカスタムAPIフックによる効率的な開発を実現しています。

## アーキテクチャ

このプロジェクトは**Inertia.js**を用いた**モダンモノリス**を採用しています：

- **サーバーサイド**: FastAPIでルーティングとデータ処理
- **フロントエンド**: Inertia.js + Reactで完全なSPA体験
- **データフロー**: JSON形式でサーバーとクライアント間のシームレスな通信
- **ビルドシステム**: ViteによるReactコンポーネントの高速ビルド

### 主要な利点

- 🚀 **SPAライクな体験**: ページ遷移時のフルリロードなし
- ⚡ **シンプルな開発**: 従来のサーバーサイドルーティングの直感性
- 🔧 **TypeScript対応**: エンドツーエンドの型安全性
- 📦 **効率的な配信**: 必要なデータのみのJSON転送
- 🌐 **多言語対応**: i18nextによる完全な国際化対応（日本語・英語）
- 🎣 **カスタムAPIフック**: 型安全で再利用可能なAPI通信システム
- 🎨 **モダンUI**: TailwindCSS + CSS Modulesによる保守性の高いスタイリング
- 🔐 **認証システム**: セッションベース認証とロール管理

## 技術スタック

### バックエンド
- **FastAPI** - WebフレームワークとAPI
- **fastapi-inertia** - Inertia.jsアダプター
- **PostgreSQL** - データベース
- **SQLAlchemy/SQLModel** - ORM
- **Alembic** - データベースマイグレーション
- **Jinja2** - テンプレートエンジン（Inertia.js用のみ）

### フロントエンド
- **Inertia.js** - モダンモノリスアーキテクチャ
- **@inertiajs/react** - React用Inertiaアダプター
- **React** - UIコンポーネント
- **TypeScript** - 型安全な開発
- **Vite** - モジュールバンドラー・開発サーバー
- **Tailwind CSS** - ユーティリティファーストCSS
- **CSS Modules** - スコープ付きCSS
- **i18next** - 多言語対応フレームワーク
- **Heroicons** - 高品質なSVGアイコンライブラリ
- **カスタムフック** - 型安全なAPI通信とローディング状態管理

### インフラ・ツール
- **Docker / Docker Compose** - コンテナ化
- **Poetry** - Python依存関係管理
- **ESLint** - コード品質（未使用変数、型チェック等）
- **Prettier** - コードフォーマット（quotes、commas、spacing等）
- **OpenSSL** - セキュリティ

## プロジェクト構造

```
fastapi-app-template/
├── app/                         # FastAPI アプリケーション
│   ├── api/                     # API エンドポイント
│   │   ├── api_v1/              # API v1 エンドポイント
│   │   │   ├── auth/            # 認証関連API
│   │   │   └── user/            # ユーザー関連API
│   │   ├── application/         # アプリケーション層
│   │   ├── domain/              # ドメイン層
│   │   └── infra/               # インフラ層
│   ├── core/                    # 核となる設定・ユーティリティ
│   │   ├── config.py            # アプリケーション設定
│   │   ├── i18n/                # 多言語対応
│   │   │   ├── locales/         # 翻訳ファイル
│   │   │   │   ├── ui.ja.json   # UI翻訳（日本語）
│   │   │   │   ├── ui.en.json   # UI翻訳（英語）
│   │   │   │   └── message.*.json # メッセージ翻訳
│   │   │   └── manager.py       # 翻訳管理
│   │   └── errors/              # エラー定義
│   ├── enums/                   # 列挙型定義
│   │   └── base_enum.py         # 多言語対応ベース列挙型
│   ├── models/                  # SQLModelによるデータモデル
│   ├── templates/               # Inertia.js テンプレート
│   │   └── inertia.html         # Inertiaベーステンプレート
│   ├── web/                     # Webページルート（Inertia.js統合）
│   │   ├── inertia_pages.py     # ページルーター統合（メイン）
│   │   └── pages/               # 機能別ページルーター
│   │       ├── auth_pages.py    # 認証関連（ログイン・ログアウト）
│   │       ├── user_pages.py    # ユーザー関連（ダッシュボード・設定）
│   │       ├── invite_pages.py  # 招待関連（招待受諾）
│   │       ├── password_pages.py # パスワード関連（リセット・リマインダー）
│   │       └── common_pages.py  # 共通ページ（ホーム）
│   └── static/                  # 静的ファイル（Viteでビルド）
├── frontend-inertia/            # フロントエンド（Inertia.js + React）
│   ├── src/
│   │   ├── Pages/               # Inertia.js ページコンポーネント
│   │   │   ├── Dashboard/       # ダッシュボードページ
│   │   │   ├── Settings/        # 設定ページ（プロフィール・言語設定）
│   │   │   └── Login/           # ログインページ
│   │   ├── layouts/             # レイアウトコンポーネント
│   │   ├── components/          # 共通コンポーネント
│   │   │   ├── LanguageSwitcher.tsx # 言語切り替えコンポーネント
│   │   │   └── Navbar.tsx       # ナビゲーションバー
│   │   ├── hooks/               # カスタムフック
│   │   │   ├── api/             # APIフック群
│   │   │   └── useI18n.ts       # 多言語対応フック
│   │   ├── i18n/                # 多言語設定
│   │   │   └── config.ts        # i18next設定
│   │   ├── styles/              # CSS Modules
│   │   ├── types/               # TypeScript型定義
│   │   └── utils/               # ユーティリティ
│   ├── vite.config.ts           # Vite 設定（パス設定含む）
│   └── package.json             # フロントエンド依存関係
├── alembic/                     # データベースマイグレーション
├── docker-compose.yml           # Docker 構成
└── pyproject.toml              # Python プロジェクト設定
```

## 開発環境設定

### 必要なソフトウェア

- **Docker Desktop** - コンテナ実行環境（必須）
- **Make 3.81+** - タスクランナー（必須）
- **OpenSSL 3.4.0+** - セキュリティキー生成（必須）

> **💡 重要**: 本プロジェクトは **コンテナベース開発** を前提としています。  
> Node.js、Python、npm等のローカルインストールは **不要** です。

### 🚀 クイックスタート

#### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd fastapi-app-template
```

#### 2. 環境設定ファイルの作成

```bash
cp .env.example .env
```

JWT秘密鍵を生成して`.env`ファイルに設定：

```bash
# JWT秘密鍵の生成
openssl rand -base64 32

# .envファイルのJWT_SECRET_KEYに上記で生成された文字列を設定
# JWT_SECRET_KEY="<生成された文字列>"
```

#### 3. 開発環境の起動（コンテナベース）

```bash
# 全コンテナ起動 + データベースマイグレーション
make env-up-all

# VSCode settings.jsonの自動適用（ローカル/コンテナ環境を自動判定）
make setup-vscode-auto
```

#### 4. テストユーザーの作成

```bash
make env-seed-users
```

以下のテストユーザーが作成されます：

| メールアドレス | パスワード | 役割 |
|---|---|---|
| admin@example.com | DevAdmin2024! | 管理者 |
| user@example.com | TestUser2024! | 一般ユーザー |

#### 5. 起動確認

ブラウザで以下のURLにアクセス：

- **アプリケーション**: http://localhost:8000
- **ログイン画面**: http://localhost:8000/login
- **ダッシュボード**: http://localhost:8000/dashboard
- **設定画面**: http://localhost:8000/settings
- **ヘルスチェック**: http://localhost:8000/healthcheck
- **API ドキュメント**: http://localhost:8000/docs

### 🔧 開発時の主要コマンド

```bash
# コンテナ状態 確認
docker-compose ps

# アプリケーションログ 確認
make app-logs

# コンテナ停止
make env-down

# コンテナ再起動
make env-reload-all
make env-reload-app # appコンテナのみ

# Viteサーバー再起動（React/Viteの変更反映）
make vite-restart
```

> **💡 Viteサーバー再起動が必要なケース:**
> - **Reactコンポーネントの変更が反映されない時**
> - **`vite.config.ts`の設定変更後** （エイリアス、プラグイン設定等）
> - **新しいパッケージをインストールした後** （`npm install`実行後）
> - **CSS ModulesやTailwind設定の変更後** （`tailwind.config.js`等）
> - **TypeScript設定変更後** （`tsconfig.json`等）
> - **ホットリロードが停止した時**
> 
> **自動再起動しない場合の対処:**
> ```bash
> # Viteサーバーのみ再起動（軽量・高速）
> make vite-restart
> 
> # それでもダメな場合はコンテナ全体を再起動
> make env-reload-app
> ```

## 主要機能

### 🌐 多言語対応（i18n）

- **対応言語**: 日本語（デフォルト）・英語
- **言語切り替え**: ログイン画面・ダッシュボード・設定画面で言語切り替え可能
- **動的翻訳**: Enumラベルなども含めた完全な多言語対応
- **翻訳管理**: `app/core/i18n/locales/` で翻訳ファイル管理

### 🎣 カスタムAPIフック

**型安全なAPI通信とローディング状態管理を提供**

- 基本APIフック（`useApi`）をベースとした専用フックを実装
- ローディング状態とエラーハンドリングを自動化
- TypeScriptによる型安全なAPI通信

### 🔐 認証・ユーザー管理

- **セッションベース認証**: Cookieベースの安全な認証
- **ロール管理**: 管理者・一般ユーザーの権限制御
- **プロフィール編集**: 名前変更・言語設定・パスワード変更
- **リアルタイム通知**: トーストによる成功・エラー通知

### 🎨 モダンUI

- **レスポンシブデザイン**: モバイル・タブレット・デスクトップ対応
- **エメラルドテーマ**: 統一されたカラーパレット
- **CSS Modules**: コンポーネント固有のスタイリング
- **Heroicons**: 高品質なSVGアイコン

## 詳細な開発環境設定

本プロジェクトは **コンテナベース開発** を基本としていますが、必要に応じて **ローカル環境** での開発も可能です。

### 🔧 開発環境の種類

| 環境 | 説明 | メリット | 適用場面 |
|------|------|----------|----------|
| **ローカル環境** | ホストマシン上でツールを実行 | 高速、軽量、オフライン対応 | 軽い編集作業、エディタ設定 |
| **コンテナ環境** | Docker内でツールを実行 | 環境統一、再現性 | チーム開発、本格的な開発 |

### 🚀 自動セットアップ（推奨）

環境を自動検出して適切な設定に切り替えます：

```bash
# 自動検出＆VSCode settings.json更新
make setup-vscode-auto

# または直接実行
./scripts/auto-setup-dev.sh
```

### ⚙️ 手動セットアップ

#### ローカル環境
```bash
# ローカル開発環境のVSCode設定
make setup-vscode-local

# 手動でも可能
pip install -r requirements-dev.txt
cp .vscode/settings.local.json .vscode/settings.json
```

**利用可能コマンド：**
```bash
ruff check app/
ruff format app/
black app/
mypy app/
```

#### コンテナ環境
```bash
# コンテナ環境のVSCode設定
make setup-vscode-container

# 手動でも可能
docker-compose up -d  # コンテナ起動
cp .vscode/settings.container.json .vscode/settings.json
```

**利用可能コマンド：**
```bash
docker exec fastapi-app ruff check app/
./scripts/ruff-container.sh check app/
make run-format-be  # Poetry経由
```

### 🔄 環境切り替え

開発中にいつでも環境を切り替えできます：

```bash
# ローカル → コンテナ
make setup-vscode-container

# コンテナ → ローカル  
make setup-vscode-local

# 自動検出で再設定
make setup-vscode-auto
```

### 📝 エディタ統合

#### VS Code / Cursor
- **Ruff**: コード整形・リンター
- **Tailwind CSS IntelliSense**: CSSクラス補完
- **Python**: 型チェック・デバッグ

設定は開発環境に応じて自動的に最適化されます。

## 開発ワークフロー

### フロントエンド開発

```bash
cd frontend-inertia

# 本番ビルド
npm run build

# 開発サーバー（Dockerコンテナ内で起動）
make vite-restart    # Viteサーバーを自動再起動
make vite-status     # Viteサーバーの状態確認
make vite-logs       # Viteサーバーのログ確認

# ウォッチモード（ファイル変更を監視してビルド）
npm run build -- --watch

# 型チェック
npm run type-check

# コード品質・フォーマット
npm run format        # Prettierでフォーマット修正
npm run format:check  # Prettierでフォーマットチェック
npm run lint          # ESLintでコード品質チェック
npm run lint:fix      # ESLintでコード品質修正
```

### バックエンド開発

```bash
# ログの確認
make app-logs

# データベース操作
make env-db-migration          # マイグレーション実行
make env-db-rev-generate       # マイグレーション生成

# コード品質・フォーマット
make check-format-be           # バックエンドフォーマットチェック
make run-format-be             # バックエンドフォーマット修正
make check-format-fe           # フロントエンドフォーマットチェック
make run-format-fe             # フロントエンドフォーマット修正

# テストユーザーリセット
make env-reset-users
```

### 新しいページの追加

1. `frontend-inertia/src/Pages/` に新しいページコンポーネントを作成
2. 機能に応じて適切なページルーターファイルにルーターを追加
   - 認証関連: `app/web/pages/auth_pages.py`
   - ユーザー関連: `app/web/pages/user_pages.py`
   - 新機能の場合: 新しいファイル（例：`app/web/pages/admin_pages.py`）を作成
3. 新しい機能ファイルを作成した場合は `app/web/inertia_pages.py` で統合
4. 必要に応じて`frontend-inertia/src/styles/` にCSS Modulesを作成
5. 多言語対応が必要な場合は翻訳ファイルに追加

例（既存の機能に追加）：
```python
# app/web/pages/user_pages.py に追加
@router.get("/profile")
async def profile_page(
    request: Request,
    inertia: InertiaDep,
    user_domain_service: UserDomainService = Depends(provide_user_domain_service),
) -> Union[InertiaResponse, RedirectResponse]:
    """プロフィールページ"""
    
    user_data = request.session.get("user")
    if not user_data:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    # ユーザー情報を取得
    user = user_domain_service.get_current_user_from_session(request)
    user_locale = get_user_locale_from_request(request)
    set_current_locale(user_locale)  # 多言語対応
    
    return await inertia.render(
        "Profile/Index",  # frontend-inertia/src/Pages/Profile/Index.tsx
        {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role_name": user.role.label if user.role else None,  # 動的翻訳
            },
            **get_i18n_data_for_response(user_locale),  # 翻訳データ追加
        }
    )
```

例（新しい機能の追加）：
```python
# app/web/pages/admin_pages.py
from typing import Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from inertia import InertiaResponse

from app.api.di.domain_di import provide_user_domain_service
from app.api.domain.services.user_domain_service import UserDomainService
from app.core.i18n import get_i18n_data_for_response, get_user_locale_from_request
from app.enums.base_enum import set_current_locale
from app.web.config import InertiaDep

router = APIRouter()

@router.get("/admin")
async def admin_page(
    request: Request,
    inertia: InertiaDep,
    user_domain_service: UserDomainService = Depends(provide_user_domain_service),
) -> Union[InertiaResponse, RedirectResponse]:
    """管理者ページ"""
    
    user_data = request.session.get("user")
    if not user_data:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    # 管理者権限チェック
    user = user_domain_service.get_current_user_from_session(request)
    if user.role.value != "admin":
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    
    user_locale = get_user_locale_from_request(request)
    set_current_locale(user_locale)
    
    return await inertia.render(
        "Admin/Index",  # frontend-inertia/src/Pages/Admin/Index.tsx
        {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role_name": user.role.label,
            },
            **get_i18n_data_for_response(user_locale),
        }
    )
```

```python
# app/web/inertia_pages.py に統合
from .pages.admin_pages import router as admin_router

router.include_router(admin_router, tags=["Admin"])
```

```tsx
// frontend-inertia/src/Pages/Admin/Index.tsx
import React from 'react';
import { AuthenticatedLayout } from '@layouts/AuthenticatedLayout';
import { useI18n } from '@hooks/useI18n';

interface Props {
  user: User;
}

const AdminPage: React.FC<Props> = ({ user }) => {
  const { t } = useI18n();

  return (
    <AuthenticatedLayout user={user} currentPath="/admin">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold">{t('ui.admin.title')}</h1>
        <p>{t('ui.admin.welcome', { name: user.name })}</p>
        
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold">{t('ui.admin.user_management')}</h3>
            <p className="text-gray-600 mt-2">{t('ui.admin.user_management_desc')}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold">{t('ui.admin.system_settings')}</h3>
            <p className="text-gray-600 mt-2">{t('ui.admin.system_settings_desc')}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold">{t('ui.admin.logs')}</h3>
            <p className="text-gray-600 mt-2">{t('ui.admin.logs_desc')}</p>
          </div>
        </div>
      </div>
    </AuthenticatedLayout>
  );
};

export default AdminPage;
```

### 多言語対応の追加

新しい翻訳キーを追加する場合：

```json
// app/core/i18n/locales/ui.ja.json
{
  "admin": {
    "title": "管理者ページ",
    "welcome": "ようこそ、{{name}}さん",
    "user_management": "ユーザー管理",
    "user_management_desc": "ユーザーアカウントの作成、編集、削除を行います",
    "system_settings": "システム設定",
    "system_settings_desc": "アプリケーションの設定を管理します",
    "logs": "ログ管理",
    "logs_desc": "システムログとエラーログを確認します"
  }
}
```

```json
// app/core/i18n/locales/ui.en.json
{
  "admin": {
    "title": "Admin Panel",
    "welcome": "Welcome, {{name}}",
    "user_management": "User Management",
    "user_management_desc": "Create, edit, and delete user accounts",
    "system_settings": "System Settings",
    "system_settings_desc": "Manage application settings",
    "logs": "Log Management",
    "logs_desc": "View system logs and error logs"
  }
}
```

## 利用可能なコマンド

`make` コマンドで利用可能なタスクを確認：

```bash
make
```

主要なコマンド：

| コマンド | 説明 |
|---|---|
| `make env-up-app` | アプリケーション起動 |
| `make env-reload-app` | アプリケーション再起動 |
| `make env-up-db` | データベース起動 |
| `make env-db-migration` | マイグレーション実行 |
| `make env-seed-users` | テストユーザー作成 |
| `make app-logs` | アプリケーションログ確認 |
| `make vite-restart` | Viteサーバー自動再起動 |
| `make vite-status` | Viteサーバー状態確認 |
| `make vite-logs` | Viteサーバーログ確認 |
| `make check-format-be` | バックエンドフォーマットチェック |
| `make run-format-be` | バックエンドフォーマット修正 |
| `make check-format-fe` | フロントエンドフォーマットチェック |
| `make run-format-fe` | フロントエンドフォーマット修正 |

## アーキテクチャの詳細

### Inertia.jsレンダリング

1. **初期リクエスト**: FastAPIがInertia.jsレスポンス（JSON + 翻訳データ）を返却
2. **翻訳初期化**: i18nextがサーバーから受け取った翻訳データを設定
3. **クライアントレンダリング**: ReactがInertia.jsページコンポーネントを多言語対応で描画
4. **ページ遷移**: Inertia.jsが差分データのみをフェッチしてSPAライクな遷移
5. **API通信**: カスタムAPIフックによる型安全なAPI呼び出し

### 多言語対応システム

- **サーバーサイド**: `contextvars`によるリクエストスコープでの言語管理
- **Enum翻訳**: `BaseEnum`でEnumラベルの動的翻訳
- **フロントエンド**: i18nextによるReactコンポーネントの翻訳
- **言語切り替え**: `LanguageSwitcher`コンポーネントでリアルタイム言語変更

### APIフックシステム

- **階層化設計**: 基本APIフック（`useApi`）をベースとした専用フック群
- **共通機能**: ローディング状態管理、エラーハンドリング、型安全性
- **モジュール性**: 機能別に分離された再利用可能なAPIフック

### 状態管理

- **サーバー状態**: FastAPIセッション + PostgreSQL + contextvars（言語）
- **クライアント状態**: Inertia.jsページプロパティ + Reactコンポーネント内のstate
- **認証**: セッションベース認証（Inertia.jsが自動処理）
- **API状態**: カスタムAPIフックによるローディング・エラー状態管理

### 開発時の注意点

- **HMR無効**: 現在HMRは無効化されているため、フロントエンド変更時は `make vite-restart` で手動再起動
- **フロントエンド変更**: Reactコンポーネントを更新した場合は Viteサーバーの再起動またはビルドが必要
- **確認方法**: 常に http://localhost:8000 のFastAPIサーバーでアプリケーションを確認
- **データベース**: スキーマ変更時は Alembic マイグレーションを生成
- **ページ追加**: 新しいページは適切な機能別ファイル（`app/web/pages/`）にルーターを追加し、対応するReactコンポーネントを作成
- **翻訳追加**: 新しい翻訳キーは `app/core/i18n/locales/ui.ja.json` と `ui.en.json` の両方に追加
- **APIフック**: 新しいAPIエンドポイントには対応するカスタムフックを作成して管理
- **サービス再起動**: 翻訳ファイル変更時は `make env-reload-all` でサービス全体を再起動
- **コードスタイル**: 業界標準（Airbnb Style Guide）準拠。JavaScript文字列はシングルクォート、JSX属性はダブルクォート。VS Code保存時にPrettierが自動実行

### 推奨開発フロー

```bash
# ターミナル1: バックエンドログ確認  
make app-logs

# ターミナル2: Viteサーバー管理
make vite-status     # 状態確認
make vite-restart    # 変更時の再起動
make vite-logs       # Viteログ確認

# ブラウザ: http://localhost:8000 で確認
```

## プロジェクト特徴まとめ

### 🎯 アーキテクチャ
- **モダンモノリス**: Inertia.js によるSPAライクな体験
- **Clean Architecture**: 層分離による保守性の高い設計、機能別ページルーターによる責任分離
- **型安全性**: エンドツーエンドのTypeScript対応

### 🌍 多言語対応
- **完全なi18n**: UIからEnumラベルまで全て翻訳対応
- **動的言語切り替え**: リアルタイムでの言語変更
- **サーバー主導**: 翻訳データの確実な整合性

### 🚀 開発体験
- **カスタムAPIフック**: 再利用可能で型安全なAPI通信
- **CSS Modules**: コンポーネント固有のスタイリング
- **Docker開発環境**: 一貫した開発環境の提供
- **統一コマンド**: Makefileによる開発タスクの簡素化

このテンプレートは、モダンなWebアプリケーション開発のベストプラクティスを取り入れながら、実用性と保守性を両立したプロジェクト構成となっています。

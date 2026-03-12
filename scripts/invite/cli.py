#!/usr/bin/env python3
"""
招待機能CLIツール

Usage:
    python scripts/invite/cli.py send-invite user@example.com
    python scripts/invite/cli.py verify-invite <token>
    python scripts/invite/cli.py accept-invite <token> <password>
"""

import asyncio
import json
import sys
from pathlib import Path

import typer
from rich.console import Console

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Rich console インスタンス
console = Console()

# ruff: noqa: E402 - sys.path変更後のインポートのため
from fastapi import BackgroundTasks

from app.api.di.invite_di import provide_invite_service
from app.db.database import get_master_db
from app.models.user import User

app = typer.Typer(
    help="招待機能CLIツール",
    epilog="開発・テスト目的で招待機能のAPIを実行するためのスクリプトです。",
)


class InviteAPIScript:
    """
    招待API実行スクリプト
    """

    def __init__(self):
        self._db_session = None
        self._invite_service = None

    def setup_dependencies(self):
        """
        依存関係をセットアップ
        """
        # データベースセッション取得
        db_generator = get_master_db()
        self._db_session = next(db_generator)

        # InviteServiceの取得
        self._invite_service = provide_invite_service()

    def cleanup(self):
        """
        クリーンアップ
        """
        if self._db_session:
            self._db_session.close()

    async def send_invite(self, email: str) -> dict:
        """
        招待メールを送信

        :param email: 招待するユーザーのメールアドレス
        :return: 実行結果
        """
        try:
            # ユーザーを検索または作成
            user = self._db_session.query(User).filter(User.email == email).first()
            if not user:
                return {
                    "success": False,
                    "error": f"ユーザーが見つかりません: {email}",
                    "suggestion": "まずユーザーをデータベースに作成してください",
                }

            background_tasks = BackgroundTasks()
            result = self._invite_service.send_invite(user, background_tasks)
            return {
                "success": True,
                "message": "招待メールの送信処理が完了しました",
                "user_email": email,
                "user_name": user.name,
                "invite_token": user.invite_token,
                "invite_expires": user.invite_expires,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"招待送信中にエラーが発生しました: {str(e)}",
            }

    def verify_invite(self, token: str) -> dict:
        """
        招待トークンを検証

        :param token: 招待トークン
        :return: 検証結果
        """
        try:
            result = self._invite_service.verify_invite_token(token)

            return {
                "success": True,
                "message": "トークン検証が完了しました",
                "verification_result": result,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"トークン検証中にエラーが発生しました: {str(e)}",
            }

    def accept_invite(self, token: str, password: str) -> dict:
        """
        招待を受諾

        :param token: 招待トークン
        :param password: 設定するパスワード
        :return: 受諾結果
        """
        try:
            result = self._invite_service.accept_invite(token, password)
            return {
                "success": True,
                "message": "招待受諾処理が完了しました",
                "accept_result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"招待受諾中にエラーが発生しました: {str(e)}",
            }


def print_result(result: dict) -> None:
    """
    結果を美しいJSON形式で出力
    """
    console.print_json(json.dumps(result, ensure_ascii=False))


def handle_script_execution(script_method_name: str, *args):
    """
    スクリプト実行の共通処理
    """
    script = InviteAPIScript()

    try:
        script.setup_dependencies()
        script_method = getattr(script, script_method_name)

        if asyncio.iscoroutinefunction(script_method):
            result = asyncio.run(script_method(*args))
        else:
            result = script_method(*args)

        print_result(result)

        if not result.get("success", False):
            raise typer.Exit(1)

    except Exception as e:
        print_result({
            "success": False,
            "error": f"スクリプト実行中にエラーが発生しました: {str(e)}",
        })
        raise typer.Exit(1)

    finally:
        script.cleanup()


@app.command()
def send_invite(
    email: str = typer.Argument(..., help="招待するユーザーのメールアドレス"),
) -> None:
    """
    招待メールを送信
    """
    handle_script_execution("send_invite", email)


@app.command()
def verify_invite(
    token: str = typer.Argument(..., help="検証する招待トークン"),
) -> None:
    """
    招待トークンを検証
    """
    handle_script_execution("verify_invite", token)


@app.command()
def accept_invite(
    token: str = typer.Argument(..., help="招待トークン"),
    password: str = typer.Argument(..., help="設定するパスワード"),
) -> None:
    """
    招待を受諾
    """
    handle_script_execution("accept_invite", token, password)


if __name__ == "__main__":
    app()

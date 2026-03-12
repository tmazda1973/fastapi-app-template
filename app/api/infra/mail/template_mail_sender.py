from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from fastapi import BackgroundTasks
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas.base_response_model import BaseResponseModel

from .mail_sender import MailSender, MailSenderProtocol

__all__ = [
    "TemplateMailSender",
]


class TemplateMailSender(MailSenderProtocol):
    """
    メール送信サービス（テンプレート対応）
    """

    def __init__(self, mail_sender: MailSender, app_name: str = "FastAPI App"):
        """
        コンストラクタ

        :param mail_sender: ベースメール送信サービス
        :param app_name: アプリケーション名
        """
        self._mail_sender = mail_sender
        self._app_name = app_name

        # テンプレートディレクトリの設定
        template_dir = Path(__file__).parent / "templates"
        self._env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def send(
        self,
        to_email: str | list[str],
        subject: str,
        body: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> BaseResponseModel:
        """
        通常のメール送信（テンプレート未使用）
        """
        return self._mail_sender.send(to_email, subject, body, background_tasks)

    def send_template_mail(
        self,
        to_email: str | list[str],
        subject: str,
        template_name: str,
        template_vars: Dict[str, any] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> BaseResponseModel:
        """
        テンプレートを使用したメール送信

        :param to_email: 受信者のメールアドレス
        :param subject: メールの件名
        :param template_name: テンプレートファイル名（例: "password_reset.html"）
        :param template_vars: テンプレート変数
        :param background_tasks: バックグラウンドタスク
        :return: メール送信結果
        """
        try:
            # テンプレートの読み込み
            template = self._env.get_template(template_name)

            # デフォルト変数の設定
            default_vars = {
                "app_name": self._app_name,
                "current_year": datetime.now().year,
            }

            # 変数をマージ
            vars_dict = {**default_vars, **(template_vars or {})}

            # HTMLの生成
            html_body = template.render(**vars_dict)

            # メール送信
            return self._mail_sender.send(
                to_email=to_email,
                subject=subject,
                body=html_body,
                background_tasks=background_tasks,
            )

        except Exception as e:
            # テンプレートエラーの場合も基盤のエラーハンドリングに委譲
            raise e

    def send_password_reset_mail(
        self,
        to_email: str,
        user_name: str,
        reset_url: str,
        reset_code: str,
        expires_in: int = 30,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> BaseResponseModel:
        """
        パスワードリセットメール送信

        :param to_email: 受信者のメールアドレス
        :param user_name: ユーザー名
        :param reset_url: リセットURL
        :param reset_code: リセットコード
        :param expires_in: 有効期限（分）
        :param background_tasks: バックグラウンドタスク
        :return: メール送信結果
        """
        return self.send_template_mail(
            to_email=to_email,
            subject="パスワードリセットのご依頼",
            template_name="password_reset.html",
            template_vars={
                "user_name": user_name,
                "reset_url": reset_url,
                "reset_code": reset_code,
                "expires_in": expires_in,
            },
            background_tasks=background_tasks,
        )

    def send_welcome_mail(
        self,
        to_email: str,
        user_name: str,
        login_url: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> BaseResponseModel:
        """
        ウェルカムメール送信

        :param to_email: 受信者のメールアドレス
        :param user_name: ユーザー名
        :param login_url: ログインURL
        :param background_tasks: バックグラウンドタスク
        :return: メール送信結果
        """
        return self.send_template_mail(
            to_email=to_email,
            subject=f"{self._app_name} へようこそ",
            template_name="welcome.html",
            template_vars={
                "user_name": user_name,
                "user_email": to_email,
                "login_url": login_url,
            },
            background_tasks=background_tasks,
        )

    def send_invite_mail(
        self,
        to_email: str,
        user_name: str,
        invite_url: str,
        expires_in_hours: int,
        background_tasks: BackgroundTasks,
    ) -> BaseResponseModel:
        """
        招待メール送信

        :param to_email: 受信者のメールアドレス
        :param user_name: ユーザー名
        :param invite_url: 招待URL
        :param expires_in_hours: 有効期限（時間）
        :param background_tasks: バックグラウンドタスク
        :return: メール送信結果
        """
        return self.send_template_mail(
            to_email=to_email,
            subject=f"{self._app_name} へのご招待",
            template_name="invite.html",
            template_vars={
                "user_name": user_name,
                "invite_url": invite_url,
                "expires_in_hours": expires_in_hours,
                "app_name": self._app_name,
            },
            background_tasks=background_tasks,
        )

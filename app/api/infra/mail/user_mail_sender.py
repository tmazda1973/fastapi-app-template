import logging
from typing import List, Optional, Union
from urllib.parse import quote

from accessify import private
from fastapi import BackgroundTasks

from app.constants.mail_constant import get_change_password_content
from app.core.config import settings
from app.schemas.base_response_model import BaseResponseModel

from .mail_sender import MailSender

__all__ = [
    "UserMailSender",
]


class UserMailSender:
    """
    メール送信サービス（ユーザー）
    """

    def __init__(self, mail_sender: MailSender):
        """
        コンストラクタ

        :param mail_sender: メール送信サービス
        """
        self._mail_sender = mail_sender
        self._logger = logging.getLogger(__name__)

    def invite(
        self,
        *,
        email: str | list[str],
        user_name: str,
        inviter_name: str,
        invite_token: str,
        background_tasks: BackgroundTasks | None = None,
    ) -> BaseResponseModel:
        """
        招待メールを送信します。

        :param email: 被招待者メールアドレス
        :param user_name: 被招待者名
        :param inviter_name: 招待者名
        :param invite_token: 招待トークン
        :param background_tasks: バックグラウンドタスク（オプション）
        :return: メール送信結果
        """

        subject = "アカウント招待のお知らせ"
        body = self._create_invite_email_body(
            user_name=user_name,
            email=email,
            inviter_name=inviter_name,
            token=invite_token,
        )

        return self._mail_sender.send(
            to_email=email,
            subject=subject,
            body=body,
            background_tasks=background_tasks,
        )

    def password_change(
        self,
        user_email: str | list[str],
        user_name: str,
        new_password: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> BaseResponseModel:
        """
        パスワード変更通知メールを送信します。

        :param user_email: 受信者メールアドレス
        :param user_name: 受信者名
        :param new_password: 新しいパスワード
        :param background_tasks: バックグラウンドタスク（オプション）
        """

        subject = "パスワードが変更されました"
        body = self._create_password_change_body(
            user_name,
            user_email,
            new_password,
        )

        return self._mail_sender.send(
            to_email=user_email,
            subject=subject,
            body=body,
            background_tasks=background_tasks,
        )

    def password_reset(
        self,
        user_email: Union[str, List[str]],
        user_name: str,
        reset_token: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> BaseResponseModel:
        """
        メールを送信します。（パスワードリセット）

        :param user_email: 受信者メールアドレス
        :param user_name: 受信者名
        :param reset_token: パスワードリセットトークン
        :param background_tasks: バックグラウンドタスク（オプション）
        :return: メール送信結果
        """

        subject = "パスワード再設定のお知らせ"
        body = self._create_password_reset_body(user_name, reset_token)

        return self._mail_sender.send(
            to_email=user_email,
            subject=subject,
            body=body,
            background_tasks=background_tasks,
        )

    @private
    def _create_invite_email_body(
        self,
        user_name: str,
        email: str,
        inviter_name: str,
        company_name: str,
        token: str,
    ) -> str:
        """
        メール本文を生成します。（招待メール）
        """

        callback_url = f"{settings.FRONTEND_URL}/user/accept-invitation?email={quote(email)}&token={token}"
        expire_minutes = settings.INVITE_TOKEN_EXPIRE_MINUTES  # 有効期限

        return f"""
        <html>
        <body>
        <p>{user_name}様</p>
        <p>
          {inviter_name} から当サービスに招待されました。
        </p>
        <p>
          <a href="{callback_url}">パスワード作成URL</a>
          <br><br>
          上記のURLにアクセスすると、パスワード作成画面に移動します。
          <br>
          ※URLの有効期限は {self._format_expire_minutes(expire_minutes)} になります。
          それ以降のアクセスは無効となりますので、ご注意ください。
        </p>
        <p>よろしくお願い致します。</p>
        </body>
        </html>
        """

    @private
    def _create_password_change_body(
        self,
        user_name: str,
        user_email: str | list[str],
        new_password: str,
    ) -> str:
        """
        メール本文を生成します。（パスワード変更）

        :param user_name: ユーザー名
        :param user_email: ユーザーのメールアドレス
        :return: HTML形式のメール本文
        """

        if isinstance(user_email, list):
            # リスト型の場合は最初のメールアドレスを使用する
            email = user_email[0]  # type: ignore
        else:
            email = user_email

        return get_change_password_content(
            username=user_name,
            email=email,
            new_password=new_password,
        )

    @private
    def _create_password_reset_body(
        self,
        user_name: str,
        reset_token: str,
    ) -> str:
        """
        メール本文を生成します。（パスワードリセット）

        :param user_name: ユーザー名
        :param reset_token: パスワードリセットトークン
        :return: HTML形式のメール本文
        """
        return f"""
        <html>
        <body>
        <p>{user_name}様</p>

        <p>パスワード再設定のリクエストを受け付けました。<br>
        以下のトークンでパスワードを再設定してください。</p>

        <p><strong>リセットトークン:</strong> {reset_token}</p>

        <p>このメールに心当たりがない場合は、メールの破棄をお願い致します。</p>
        </body>
        </html>
        """

    @private
    def _format_expire_minutes(
        self,
        minutes: int,
    ) -> str:
        """
        有効期限の分数を適切なフォーマットに変換します。

        - 1440分（24時間）以上の場合は日数と残りの分に分割して表示
        - それ以下の場合は分のみ表示

        :param minutes: 分数
        :return: フォーマットされた文字列
        """

        if not isinstance(minutes, int):
            self._logger.error(
                f'有効期限は整数である必要があります。[有効期限: "{minutes}"]'
            )
            return ""

        if minutes >= 60:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes > 0:
                return f"{hours}時間 {remaining_minutes}分"
            else:
                return f"{hours}時間"
        else:
            return f"{minutes}分"

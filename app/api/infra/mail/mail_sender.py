import asyncio
from abc import ABC, abstractmethod
from typing import Optional

from accessify import private
from fastapi import BackgroundTasks, status
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from typing_extensions import override

from app.schemas.base_response_model import BaseResponseModel

from .mail_config import MailConfig

__all__ = [
    "MailSenderProtocol",
    "MailSender",
]


class MailSenderProtocol(ABC):
    """
    プロトコル（メール送信サービス）
    """

    @abstractmethod
    def send(
        self,
        to_email: str | list[str],
        subject: str,
        body: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> BaseResponseModel:
        """
        メールを送信します。

        :param to_email: 受信者のメールアドレス（単一またはリスト）
        :param subject: メールの件名
        :param body: メールの本文
        :param background_tasks: バックグラウンドタスク（オプション）
        :return: メール送信結果
        """
        pass


class MailSender(MailSenderProtocol):
    """
    メール送信サービス
    """

    def __init__(self, config: MailConfig):
        """
        コンストラクタ

        :param config: メール設定
        """
        self._config = config
        self._connection_config = ConnectionConfig(
            MAIL_USERNAME=config.username,
            MAIL_PASSWORD=config.password,  # type: ignore
            MAIL_FROM=config.default_sender,  # type: ignore
            MAIL_PORT=config.smtp_port,
            MAIL_SERVER=config.smtp_server,
            MAIL_FROM_NAME=config.from_name,
            MAIL_STARTTLS=config.use_tls,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
        )

    @override
    def send(
        self,
        to_email: str | list[str],
        subject: str,
        body: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> BaseResponseModel:
        if background_tasks:
            # バックグラウンドタスクが指定されている
            # 非同期で送信する
            return self._send_in_background(
                to_email=to_email,
                subject=subject,
                body=body,
                background_tasks=background_tasks,
            )
        else:
            # 同期的に送信する
            return self._send_sync(
                to_email=to_email,
                subject=subject,
                body=body,
            )

    def _send_sync(
        self,
        to_email: str | list[str],
        subject: str,
        body: str,
    ) -> BaseResponseModel:
        """
        同期的にメールを送信する
        """
        try:
            recipients = self._get_recipients(to_email)
            message = MessageSchema(
                subject=subject,
                subtype=MessageType.html,
                recipients=recipients,  # type: ignore
                body=body,
            )

            fm = FastMail(self._connection_config)

            # 新しいイベントループで実行
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            loop.run_until_complete(fm.send_message(message))

            return BaseResponseModel(
                code=status.HTTP_200_OK,
                message="Success",
            )
        except Exception as e:
            return BaseResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed: {str(e)}",
            )

    def send_mail_sync(self, message: MessageSchema) -> None:
        """
        メールを同期的に送信する（BackgroundTask用）
        """
        fm = FastMail(self._connection_config)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(fm.send_message(message))

    @private
    def _send_in_background(
        self,
        to_email: str | list[str],
        subject: str,
        body: str,
        background_tasks: BackgroundTasks,
    ) -> BaseResponseModel:
        """
        バックグラウンドでメールを送信する
        """
        try:
            recipients = self._get_recipients(to_email)
            message = MessageSchema(
                subject=subject,
                subtype=MessageType.html,
                recipients=recipients,  # type: ignore
                body=body,
            )

            # async関数を同期的にラップしてBackgroundTasksに渡す
            background_tasks.add_task(self.send_mail_sync, message)

            return BaseResponseModel(
                code=status.HTTP_200_OK,
                message="Success",
            )
        except Exception as e:
            return BaseResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed: {str(e)}",
            )

    @private
    def _get_recipients(
        self,
        email: str | list[str],
    ) -> list[str]:
        """
        受信者リストを取得します。

        :param email: 受信者のメールアドレス（単一またはリスト）
        """
        if isinstance(email, str):
            return [email]

        return email

"""
メール送信サービスの依存性注入設定
"""

from functools import lru_cache

from app.api.infra.mail.mail_config import MailConfig
from app.api.infra.mail.mail_sender import MailSender
from app.api.infra.mail.template_mail_sender import TemplateMailSender

__all__ = [
    "provide_mail_config",
    "provide_mail_sender",
    "provide_template_mail_sender",
]


@lru_cache()
def provide_mail_config() -> MailConfig:
    """
    メール設定を提供
    """
    return MailConfig.from_settings()


@lru_cache()
def provide_mail_sender() -> MailSender:
    """
    メール送信サービス
    """
    config = provide_mail_config()
    return MailSender(config)


@lru_cache()
def provide_template_mail_sender() -> TemplateMailSender:
    """
    メール送信サービス（テンプレート対応）
    """
    mail_sender = provide_mail_sender()
    return TemplateMailSender(mail_sender, app_name="FastAPI App Template")

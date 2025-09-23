from fastapi import Depends

from app.api.infra.mail import MailConfig, MailSender, UserMailSender

__all__ = [
    "provide_user_mail_sender",
]


def provide_mail_config() -> MailConfig:
    return MailConfig.from_settings()


def provide_mail_sender(
    config: MailConfig = Depends(provide_mail_config),
) -> MailSender:
    return MailSender(config)


def provide_user_mail_sender(
    mail_sender: MailSender = Depends(provide_mail_sender),
) -> UserMailSender:
    return UserMailSender(mail_sender)

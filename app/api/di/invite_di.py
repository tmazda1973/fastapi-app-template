"""
招待関連サービスの依存性注入設定
"""

from fastapi import Depends

from app.api.application.services.invite_service import InviteService
from app.api.di.domain_di import provide_user_domain_service
from app.api.di.infra_di import provide_datastore_adapter
from app.api.di.mail_di import provide_template_mail_sender
from app.api.domain.services.user_domain_service import UserDomainService
from app.api.infra.adapters.datastore_adapter import DatastoreAdapter
from app.api.infra.mail.template_mail_sender import TemplateMailSender

__all__ = [
    "provide_invite_service",
]


def provide_invite_service(
    user_domain_service: UserDomainService = Depends(provide_user_domain_service),
    datastore_adapter: DatastoreAdapter = Depends(provide_datastore_adapter),
    template_mail_sender: TemplateMailSender = Depends(provide_template_mail_sender),
) -> InviteService:
    """
    招待サービス

    :param user_domain_service: ユーザードメインサービス
    :param datastore_adapter: データストアアダプター
    :param template_mail_sender: メール送信サービス
    :return: 招待サービス
    """
    return InviteService(
        user_domain_service,
        datastore_adapter,
        template_mail_sender,
    )

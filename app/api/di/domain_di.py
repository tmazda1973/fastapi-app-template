"""
ドメインサービスの依存性注入設定
"""

from functools import lru_cache

from fastapi import Depends

from app.api.di.infra_di import provide_datastore_adapter
from app.api.domain.protocols.token_generator_protocol import TokenGeneratorProtocol
from app.api.domain.services.user_domain_service import UserDomainService
from app.api.infra.adapters.datastore_adapter import DatastoreAdapter
from app.api.infra.services.jwt_token_generator import JwtTokenGenerator

__all__ = [
    "provide_token_generator",
    "provide_user_domain_service",
]


@lru_cache()
def provide_token_generator() -> TokenGeneratorProtocol:
    """
    トークン生成サービス
    """
    return JwtTokenGenerator()


def provide_user_domain_service(
    token_generator: TokenGeneratorProtocol = Depends(provide_token_generator),
    datastore_adapter: DatastoreAdapter = Depends(provide_datastore_adapter),
) -> UserDomainService:
    """
    ユーザードメインサービス
    """
    return UserDomainService(token_generator, datastore_adapter)

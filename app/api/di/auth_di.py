"""
認証関連サービスの依存性注入設定
"""

from functools import lru_cache

from app.api.infra.services.password_service import PasswordService

__all__ = [
    "provide_password_service",
]


@lru_cache()
def provide_password_service() -> PasswordService:
    """
    パスワードサービス
    """
    return PasswordService()

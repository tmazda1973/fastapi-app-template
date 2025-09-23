"""
認証依存関数の依存性注入設定
"""

from typing import Annotated

from fastapi import Depends, Header, Request, status

from app.api.di.domain_di import provide_user_domain_service
from app.api.domain.services.user_domain_service import UserDomainService
from app.constants.token_constant import TOKEN_TYPE
from app.core.exception import AccessDeniedException, UnauthorizedException
from app.core.i18n.error_message import ErrorCode, ErrorMessage
from app.enums.user import RoleEnum
from app.models.user import User
from app.utils.common_util import verify_jwt

__all__ = [
    "get_current_user_from_session",
    "authenticate_router",
    "authenticate_admin_router",
]


def get_current_user_from_session(
    request: Request,
    user_domain_service: UserDomainService = Depends(provide_user_domain_service),
) -> User:
    """
    ログインユーザー情報を取得します。

    :param request: FastAPIリクエスト
    :param user_domain_service: ユーザードメインサービス
    :return: 現在のユーザー
    """
    return user_domain_service.get_current_user_from_session(request)


def authenticate_router(
    authorization: Annotated[str | None, Header()] = None,
    user_domain_service: UserDomainService = Depends(provide_user_domain_service),
) -> User:
    """
    Bearer token認証を行い、認証されたユーザーを返します。

    :param authorization: Authorization ヘッダー
    :param user_domain_service: ユーザードメインサービス
    :return: 認証されたユーザー
    """
    if not authorization:
        raise UnauthorizedException(
            message=ErrorMessage(ErrorCode.UNAUTHORIZED).value,
            error_code=status.HTTP_401_UNAUTHORIZED,
        )

    token_format = authorization.replace("Bearer ", "")
    token = verify_jwt(token_format, TOKEN_TYPE.get("DEFAULT"))

    if not token:
        raise UnauthorizedException(
            message=ErrorMessage(ErrorCode.UNAUTHORIZED).value,
            error_code=status.HTTP_401_UNAUTHORIZED,
        )

    user = user_domain_service.get_user_by_email(token.get("sub"))

    if not user:
        raise UnauthorizedException(
            message=ErrorMessage(ErrorCode.UNAUTHORIZED).value,
            error_code=status.HTTP_401_UNAUTHORIZED,
        )

    return user


def authenticate_admin_router(
    authorization: Annotated[str | None, Header()] = None,
    user_domain_service: UserDomainService = Depends(provide_user_domain_service),
) -> User:
    """
    Bearer token認証を行い、管理者権限をチェックして認証されたユーザーを返します。

    :param authorization: Authorization ヘッダー
    :param user_domain_service: ユーザードメインサービス
    :return: 認証された管理者ユーザー
    """
    if not authorization:
        raise UnauthorizedException(
            message=ErrorMessage(ErrorCode.UNAUTHORIZED).value,
            error_code=status.HTTP_401_UNAUTHORIZED,
        )

    token_format = authorization.replace("Bearer ", "")
    token = verify_jwt(token_format, TOKEN_TYPE.get("DEFAULT"))

    if not token:
        raise UnauthorizedException(
            message=ErrorMessage(ErrorCode.UNAUTHORIZED).value,
            error_code=status.HTTP_401_UNAUTHORIZED,
        )

    user = user_domain_service.get_user_by_email(token.get("sub"))

    if not user:
        raise UnauthorizedException(
            message=ErrorMessage(ErrorCode.UNAUTHORIZED).value,
            error_code=status.HTTP_401_UNAUTHORIZED,
        )

    if user.role != RoleEnum.admin:
        raise AccessDeniedException(
            message=ErrorMessage(ErrorCode.FORBIDDEN).value,
            error_code=status.HTTP_403_FORBIDDEN,
        )

    return user

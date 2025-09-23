"""
ユーザーAPIルーター
"""

from fastapi import APIRouter, Depends, Request, status

from app.api.application.services import update_session_user_data
from app.api.di.auth_dependency import get_current_user_from_session
from app.api.di.domain_di import provide_user_domain_service
from app.api.domain.services.user_domain_service import UserDomainService
from app.core.exception import BadRequestException
from app.core.i18n.error_message import ErrorCode, ErrorMessage
from app.core.response import public_api_responses
from app.models import User

from .schemas import ProfileResponse, ProfileUpdateRequest

router = APIRouter(responses=public_api_responses)


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="プロフィール情報取得API",
    description="現在ログイン中のユーザーのプロフィール情報を取得します。",
    operation_id="user_profile_get",
)
def get_profile(
    user: User = Depends(get_current_user_from_session),
) -> ProfileResponse:
    """
    プロフィール情報取得API

    :param user: ログインユーザー
    :return: プロフィール情報
    """

    try:
        return ProfileResponse.model_validate(user)
    except Exception:
        raise BadRequestException(
            error_code=status.HTTP_400_BAD_REQUEST,
            message=ErrorMessage(ErrorCode.BAD_REQUEST).value,
        )


@router.patch(
    "/profile",
    response_model=ProfileResponse,
    summary="プロフィール更新API",
    description="ログインユーザーのプロフィール情報を更新します。",
    operation_id="user_profile_update",
)
def update_profile(
    request: Request,
    profile_request: ProfileUpdateRequest,
    user: User = Depends(get_current_user_from_session),
    user_domain_service: UserDomainService = Depends(provide_user_domain_service),
) -> ProfileResponse:
    """
    プロフィール更新API

    :param request: リクエストデータ
    :param profile_request: リクエストデータ（プロフィール更新API）
    :param user: ログインユーザー
    :param user_domain_service: ユーザードメインサービス
    :return: プロフィール情報
    """

    try:
        user_domain_service.update_profile_name(user, profile_request.name)
        update_session_user_data(request.session, user)

        return ProfileResponse.model_validate(user)
    except BadRequestException:
        raise

    except Exception:
        raise BadRequestException(
            error_code=status.HTTP_400_BAD_REQUEST,
            message=ErrorMessage(ErrorCode.BAD_REQUEST).value,
        )

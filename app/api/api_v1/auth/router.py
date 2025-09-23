"""
ルーター（認証API）
"""

from fastapi import APIRouter, Depends, status

from app.api.api_v1.auth.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.api.application.services import is_exist_user_by_email
from app.api.di.auth_dependency import authenticate_router
from app.api.di.domain_di import provide_user_domain_service
from app.api.domain.services.user_domain_service import UserDomainService
from app.constants.token_constant import TOKEN_TYPE
from app.core.config import settings
from app.core.exception import BadRequestException, UnauthorizedException
from app.core.i18n.error_message import ErrorCode, ErrorMessage
from app.core.response import public_api_responses
from app.models import User
from app.schemas.base_response_model import BaseResponseModel
from app.utils.common_util import verify_jwt

router = APIRouter(responses=public_api_responses)


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[
        Depends(is_exist_user_by_email),
    ],
    summary="ログインAPI",
    description="ユーザーの認証を行います。",
    operation_id="auth_login",
)
async def login(
    request: LoginRequest,
    user_domain_service: UserDomainService = Depends(provide_user_domain_service),
) -> TokenResponse:
    """
    ログインAPI

    :param request: リクエストデータ
    :param user_domain_service: ユーザードメインサービス
    :return: レスポンスデータ
    """

    try:
        # ユーザーを認証する
        user = user_domain_service.verify_user(
            request.email,
            request.password,
        )
        if not user:
            raise UnauthorizedException(
                error_code=status.HTTP_401_UNAUTHORIZED,
                message=ErrorMessage(ErrorCode.USER_LOGIN_FAILED).value,
            )

        # トークンを生成する
        access_token = user_domain_service.create_access_token(
            user, TOKEN_TYPE.get("DEFAULT")
        )
        refresh_token_ = user_domain_service.create_refresh_token(
            user,
            TOKEN_TYPE.get("REFRESH_TOKEN"),
            settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        )

        return TokenResponse(
            role=user.role,
            role_name=user.role.label,
            email=user.email,
            username=user.name,
            access_token=access_token,
            refresh_token=refresh_token_,
            last_login_at=user.last_login_at,
        )
    except Exception as e:
        if isinstance(e, UnauthorizedException):
            raise e

        raise UnauthorizedException(
            error_code=status.HTTP_401_UNAUTHORIZED,
            message=ErrorMessage(ErrorCode.UNAUTHORIZED).value,
        )


@router.post(
    "/refresh-token",
    response_model=TokenResponse,
    summary="リフレッシュトークンAPI",
    description="リフレッシュトークンを使用して新しいアクセストークンを取得します。",
    operation_id="auth_refresh_token",
)
async def refresh_token(
    request: RefreshTokenRequest,
    user_domain_service: UserDomainService = Depends(provide_user_domain_service),
) -> TokenResponse:
    """
    リフレッシュトークンAPI

    :param request: リクエストデータ
    :param user_domain_service: ユーザードメインサービス
    :return: レスポンスデータ
    """

    try:
        # リフレッシュトークンを検証する
        payload = verify_jwt(
            request.refresh_token,
            TOKEN_TYPE.get("REFRESH_TOKEN"),
        )
        if not payload:
            raise UnauthorizedException(
                error_code=status.HTTP_401_UNAUTHORIZED,
                message=ErrorMessage(ErrorCode.UNAUTHORIZED).value,
            )

        # ペイロードからユーザーのメールアドレスを取得する
        email = payload.get("sub")
        user = user_domain_service.get_user_by_email(email)
        if not user:
            raise UnauthorizedException(
                error_code=status.HTTP_401_UNAUTHORIZED,
                message=ErrorMessage(ErrorCode.UNAUTHORIZED).value,
            )

        # トークンを再生成する
        access_token = user_domain_service.create_access_token(
            user, TOKEN_TYPE.get("DEFAULT")
        )
        new_refresh_token = user_domain_service.create_refresh_token(
            user,
            TOKEN_TYPE.get("REFRESH_TOKEN"),
            settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        )

        return TokenResponse(
            email=user.email,
            username=user.name,
            role_name=user.role.label,
            role=user.role,
            access_token=access_token,
            refresh_token=new_refresh_token,
        )
    except Exception:
        raise UnauthorizedException(
            error_code=status.HTTP_401_UNAUTHORIZED,
            message=ErrorMessage(ErrorCode.UNAUTHORIZED).value,
        )


@router.post(
    "/logout",
    response_model=BaseResponseModel,
    summary="ログアウトAPI",
    description="ログアウト処理を行います。",
    operation_id="auth_logout",
)
def logout(
    user: User = Depends(authenticate_router),
    user_domain_service: UserDomainService = Depends(provide_user_domain_service),
) -> BaseResponseModel:
    """
    ログアウトAPI

    :param user: ログインユーザー
    :param user_domain_service: ユーザードメインサービス
    :return: レスポンスデータ
    """

    try:
        if not user.refresh_token:
            raise UnauthorizedException(
                error_code=status.HTTP_401_UNAUTHORIZED,
                message=ErrorMessage(ErrorCode.UNAUTHORIZED).value,
            )

        user_domain_service.logout(user)

        return BaseResponseModel()
    except UnauthorizedException as e:
        raise e

    except Exception:
        raise BadRequestException(
            error_code=status.HTTP_400_BAD_REQUEST,
            message=ErrorMessage(ErrorCode.BAD_REQUEST).value,
        )


# 招待機能がOFFの場合のみユーザー登録APIを有効化
if not settings.ENABLE_USER_INVITATION:

    @router.post(
        "/register",
        response_model=RegisterResponse,
        summary="ユーザー登録API",
        description="新しいユーザーアカウントを作成します。",
        operation_id="auth_register",
    )
    async def register(
        request: RegisterRequest,
        user_domain_service: UserDomainService = Depends(provide_user_domain_service),
    ) -> RegisterResponse:
        """
        ユーザー登録API

        :param request: リクエストデータ
        :param user_domain_service: ユーザードメインサービス
        :return: レスポンスデータ
        """

        try:
            user = user_domain_service.create_user(
                email=request.email,
                name=request.name,
                password=request.password,
            )

            return RegisterResponse(
                message=ErrorMessage(ErrorCode.USER_REGISTER_SUCCESS).value,
                user_id=user.id,
                user_email=user.email,
                user_name=user.name,
                role=user.role,
                verify_status=user.verify_status.value,
            )

        except BadRequestException:
            raise
        except Exception as e:
            raise BadRequestException(
                error_code=ErrorCode.USER_REGISTER_FAILED,
                message=ErrorMessage(ErrorCode.USER_REGISTER_FAILED).value,
            ) from e

"""
認証関連のページルーター
"""

from typing import Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from inertia import InertiaResponse

from app.api.api_v1.auth.schemas import LoginRequest
from app.api.di.domain_di import provide_user_domain_service
from app.api.domain.services.user_domain_service import UserDomainService
from app.core.i18n import get_i18n_data_for_response, get_user_locale_from_request, i18n
from app.enums.base_enum import set_current_locale
from app.web.config import InertiaDep

router = APIRouter()


@router.get(
    "/login",
    response_model=None,
    summary="ログインページ",
    description="ログインページを表示します。",
    operation_id="login_page",
)
async def login_page(
    request: Request,
    inertia: InertiaDep,
) -> Union[InertiaResponse, RedirectResponse]:
    """
    ログインページ

    :param request: リクエストデータ
    :param inertia: Inertiaインスタンス
    :return: レスポンスデータ
    """

    if request.session.get("user"):
        # ログイン済み
        return RedirectResponse(
            url="/dashboard",
            status_code=status.HTTP_302_FOUND,
        )

    user_locale = get_user_locale_from_request(request)

    # セッションからフラッシュエラーメッセージを取得
    flash_error = request.session.pop("flash_error", None)
    email = request.query_params.get("email", "")

    errors = {}
    if flash_error:
        error_message = i18n.translate(flash_error, user_locale)
        errors["email"] = error_message

    return await inertia.render(
        "Login/Index",
        {
            "errors": errors,
            "email": email,
            **get_i18n_data_for_response(user_locale),
        },
    )


@router.post(
    "/auth/login",
    response_model=None,
    summary="ログイン処理",
    description="ログイン処理を行います。",
    operation_id="login_submit",
)
async def login_submit(
    request: Request,
    inertia: InertiaDep,
    login_data: LoginRequest,
    user_domain_service: UserDomainService = Depends(provide_user_domain_service),
) -> Union[InertiaResponse, RedirectResponse]:
    """
    ログイン処理

    :param request: リクエストデータ
    :param inertia: Inertiaインスタンス
    :param login_data: ログインデータ
    :param user_domain_service: ユーザードメインサービス
    :return: レスポンスデータ
    """

    try:
        # ユーザーを認証する
        user = user_domain_service.verify_user(
            login_data.email,
            login_data.password,
        )
        if not user:
            # 認証失敗 - セッションにエラーメッセージを保存してリダイレクト
            request.session["flash_error"] = "message.errors.user.invalid_credentials"
            return RedirectResponse(
                url=f"/login?email={login_data.email}",
                status_code=302,
            )

        current_locale = get_user_locale_from_request(request)
        set_current_locale(current_locale)

        request.session["user"] = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "role_name": user.role.label,
            "last_login_at": user.last_login_at.isoformat()
            if user.last_login_at
            else None,
        }

        return RedirectResponse(
            url="/dashboard",
            status_code=status.HTTP_302_FOUND,
        )
    except Exception:
        # エラーの場合はログインページにリダイレクト
        request.session["flash_error"] = "message.errors.user.login_failed"
        return RedirectResponse(
            url=f"/login?email={login_data.email}",
            status_code=302,
        )


@router.get(
    "/auth/logout",
    response_model=None,
    summary="ログアウト処理",
    description="ログアウト処理を行います。",
    operation_id="logout",
)
async def logout(request: Request) -> RedirectResponse:
    """
    ログアウト処理

    :param request: リクエストデータ
    :return: レスポンスデータ
    """

    request.session.clear()
    return RedirectResponse(
        url="/login",
        status_code=status.HTTP_302_FOUND,
    )

"""
ページルーター（ユーザー）
"""

from typing import Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from inertia import InertiaResponse

from app.api.di.domain_di import provide_user_domain_service
from app.api.domain.services.user_domain_service import UserDomainService
from app.core.i18n import get_i18n_data_for_response, get_user_locale_from_request
from app.enums.base_enum import set_current_locale
from app.web.config import InertiaDep

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=None,
    summary="ダッシュボードページ",
    description="ダッシュボードページを表示します。",
    operation_id="dashboard_page",
)
async def dashboard(
    request: Request,
    inertia: InertiaDep,
    user_domain_service: UserDomainService = Depends(provide_user_domain_service),
) -> Union[InertiaResponse, RedirectResponse]:
    """
    ダッシュボードページ

    :param request: リクエストデータ
    :param inertia: Inertiaインスタンス
    :param user_domain_service: ユーザードメインサービス
    :return: レスポンスデータ
    """

    user_data = request.session.get("user")
    if not user_data:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_302_FOUND,
        )

    # ユーザー情報を取得する
    user = user_domain_service.get_current_user_from_session(request)
    user_locale = get_user_locale_from_request(request)
    set_current_locale(user_locale)

    result = await inertia.render(
        "Dashboard/Index",
        {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.value if user.role else None,
                "role_name": user.role.label if user.role else None,
                "last_login_at": user.last_login_at.isoformat()
                if user.last_login_at
                else None,
            },
            **get_i18n_data_for_response(user_locale),
        },
    )

    return result


@router.get(
    "/settings",
    response_model=None,
    summary="設定ページ",
    description="設定ページを表示します。",
    operation_id="settings_page",
)
async def settings_page(
    request: Request,
    inertia: InertiaDep,
    user_domain_service: UserDomainService = Depends(provide_user_domain_service),
) -> Union[InertiaResponse, RedirectResponse]:
    """
    設定ページ

    :param request: リクエストデータ
    :param inertia: Inertiaインスタンス
    :param user_domain_service: ユーザードメインサービス
    :return: レスポンスデータ
    """

    user_data = request.session.get("user")
    if not user_data:
        return RedirectResponse(
            url="/login",
            status_code=status.HTTP_302_FOUND,
        )

    # ユーザー情報を取得する
    user = user_domain_service.get_current_user_from_session(request)
    user_locale = get_user_locale_from_request(request)
    set_current_locale(user_locale)

    return await inertia.render(
        "Settings/Index",
        {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.value if user.role else None,
                "role_name": user.role.label if user.role else None,
            },
            **get_i18n_data_for_response(user_locale),
        },
    )

"""
ページルーター（招待）
"""

from typing import Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from inertia import InertiaResponse

from app.api.api_v1.invite.schemas.invite_request import AcceptInviteRequest
from app.api.application.services.invite_service import InviteService
from app.api.di.invite_di import provide_invite_service
from app.core.i18n import get_i18n_data_for_response, get_user_locale_from_request, i18n
from app.enums.base_enum import set_current_locale
from app.web.config import InertiaDep

router = APIRouter()


@router.get(
    "/invite/accept",
    response_model=None,
    summary="招待受諾ページ",
    description="招待受諾ページを表示します。",
    operation_id="invite_accept_page",
)
async def invite_accept_page(
    request: Request,
    inertia: InertiaDep,
    token: str | None = None,
    invite_service: InviteService = Depends(provide_invite_service),
) -> Union[InertiaResponse, RedirectResponse]:
    """
    招待受諾ページ

    :param request: リクエストデータ
    :param inertia: Inertiaインスタンス
    :param token: 招待トークン
    :param invite_service: 招待サービス
    :return: レスポンスデータ
    """

    if request.session.get("user"):
        # ログイン済み
        return RedirectResponse(
            url="/dashboard",
            status_code=status.HTTP_302_FOUND,
        )

    user_locale = get_user_locale_from_request(request)
    set_current_locale(user_locale)

    # セッションからフラッシュエラーメッセージを取得
    flash_error = request.session.pop("flash_error", None)
    if flash_error:
        return await inertia.render(
            "Invite/Accept",
            {
                "error": i18n.t(flash_error, user_locale),
                "token": token or "",
                "invite_info": None,
                **get_i18n_data_for_response(user_locale),
            },
        )

    if not token:
        # トークンが提供されていない
        return await inertia.render(
            "Invite/Accept",
            {
                "error": i18n.t("invite.errors.token_not_provided", user_locale),
                "token": "",
                "invite_info": None,
                **get_i18n_data_for_response(user_locale),
            },
        )

    # トークンを検証する
    try:
        verification_result = invite_service.verify_invite_token(token)
        if not verification_result["is_valid"]:
            return await inertia.render(
                "Invite/Accept",
                {
                    "error": verification_result.get(
                        "error_message",
                        i18n.t("invite.errors.invalid_token", user_locale),
                    ),
                    "token": token,
                    "invite_info": None,
                    **get_i18n_data_for_response(user_locale),
                },
            )

        # 有効な招待の場合、招待情報を渡す
        return await inertia.render(
            "Invite/Accept",
            {
                "error": None,
                "token": token,
                "invite_info": {
                    "user_email": verification_result["user_email"],
                    "user_name": verification_result["user_name"],
                    "expires_in_minutes": verification_result["expires_in_minutes"],
                },
                **get_i18n_data_for_response(user_locale),
            },
        )
    except Exception:
        return await inertia.render(
            "Invite/Accept",
            {
                "error": i18n.t("invite.errors.verification_failed", user_locale),
                "token": token,
                "invite_info": None,
                **get_i18n_data_for_response(user_locale),
            },
        )


@router.post(
    "/invite/accept",
    response_model=None,
    summary="招待受諾処理",
    description="招待受諾処理を行います。",
    operation_id="invite_accept_submit",
)
async def invite_accept_submit(
    request: Request,
    inertia: InertiaDep,
    accept_data: AcceptInviteRequest,
    invite_service: InviteService = Depends(provide_invite_service),
) -> Union[InertiaResponse, RedirectResponse]:
    """
    招待受諾処理

    :param request: リクエストデータ
    :param inertia: Inertiaインスタンス
    :param accept_data: 招待受諾データ
    :param invite_service: 招待サービス
    :return: レスポンスデータ
    """

    user_locale = get_user_locale_from_request(request)
    set_current_locale(user_locale)

    try:
        # 招待を受諾する
        result = invite_service.accept_invite(
            token=accept_data.token,
            password=accept_data.password,
        )
        if result["success"]:
            # 成功時はログインページにリダイレクト（成功メッセージ付き）
            return RedirectResponse(
                url="/login?message=invitation_accepted",
                status_code=status.HTTP_302_FOUND,
            )
        else:
            # 失敗時は招待ページにリダイレクト（エラーメッセージ付き）
            request.session["flash_error"] = "invite.errors.accept_failed"
            return RedirectResponse(
                url=f"/invite/accept?token={accept_data.token}", status_code=302
            )

    except Exception:
        # 例外時は招待ページにリダイレクト
        request.session["flash_error"] = "invite.errors.unexpected_error"
        return RedirectResponse(
            url=f"/invite/accept?token={accept_data.token}", status_code=302
        )

"""
ページルーター（パスワード）
"""

from typing import Union

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.responses import RedirectResponse
from inertia import InertiaResponse

from app.api.api_v1.auth.password.schemas import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.api.di.auth_di import provide_password_service
from app.api.di.mail_di import provide_template_mail_sender
from app.api.infra.mail.template_mail_sender import TemplateMailSender
from app.api.infra.services.password_service import PasswordService
from app.core.config import settings
from app.core.exception import BadRequestException
from app.core.i18n import get_i18n_data_for_response, get_user_locale_from_request, i18n
from app.enums.base_enum import set_current_locale
from app.web.config import DbDep, InertiaDep

router = APIRouter()


@router.get(
    "/forgot-password",
    response_model=None,
    summary="パスワードリマインダーページ",
    description="パスワードリマインダーページを表示します。",
    operation_id="forgot_password_page",
)
async def forgot_password_page(
    request: Request,
    inertia: InertiaDep,
    success: bool = False,
) -> Union[InertiaResponse, RedirectResponse]:
    """
    パスワードリマインダーページ

    :param request: リクエストデータ
    :param inertia: Inertiaインスタンス
    :param success: 成功フラグ
    :return: レスポンスデータ
    """

    current_user = request.session.get("user")
    if current_user:
        # ログイン済み
        return RedirectResponse(
            url="/dashboard",
            status_code=status.HTTP_302_FOUND,
        )

    user_locale = get_user_locale_from_request(request)
    set_current_locale(user_locale)

    # セッションからフラッシュエラーメッセージを取得
    flash_error = request.session.pop("flash_error", None)
    error_message = None
    if flash_error:
        error_message = i18n.t(flash_error, user_locale)

    return await inertia.render(
        "Password/ForgotPassword",
        {
            "success": success,
            "error": error_message,
            **get_i18n_data_for_response(user_locale),
        },
    )


@router.post(
    "/forgot-password",
    response_model=None,
    summary="パスワードリマインド処理",
    description="パスワードリマインド処理を行います。",
    operation_id="forgot_password_submit",
)
async def forgot_password_submit(
    request: Request,
    inertia: InertiaDep,
    forgot_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: DbDep,
    password_service: PasswordService = Depends(provide_password_service),
    template_mail_sender: TemplateMailSender = Depends(provide_template_mail_sender),
) -> Union[InertiaResponse, RedirectResponse]:
    """
    パスワードリマインド処理

    :param request: リクエストデータ
    :param inertia: Inertiaインスタンス
    :param forgot_data: リマインドデータ
    :param background_tasks: バックグラウンドタスク
    :param db: DBセッション
    :param password_service: パスワードサービス
    :param template_mail_sender: メール送信サービス
    :return: レスポンスデータ
    """

    user_locale = get_user_locale_from_request(request)
    set_current_locale(user_locale)

    try:
        user = password_service.get_user_by_email(db, forgot_data.email)
        if user:
            # リセットトークンを生成する
            reset_token = password_service.create_password_reset_token(db, user)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}&email={user.email}"

            # メールを送信する
            template_mail_sender.send_password_reset_mail(
                to_email=user.email,
                user_name=user.name,
                reset_url=reset_url,
                reset_code=reset_token.reset_code,
                expires_in=30,  # 30分
                background_tasks=background_tasks,
            )

        return RedirectResponse(
            url="/forgot-password?success=true",
            status_code=status.HTTP_302_FOUND,
        )
    except BadRequestException:
        request.session["flash_error"] = "ui.password_reset.errors.send_failed"
        return RedirectResponse(url="/forgot-password", status_code=302)
    except Exception:
        request.session["flash_error"] = "ui.password_reset.errors.send_failed"
        return RedirectResponse(url="/forgot-password", status_code=302)


@router.get(
    "/reset-password",
    response_model=None,
    summary="パスワードリセットページ",
    description="パスワードリセットページを表示します。",
    operation_id="reset_password_page",
)
async def reset_password_page(
    request: Request,
    inertia: InertiaDep,
    token: str | None = None,
    email: str | None = None,
    success: bool = False,
) -> Union[InertiaResponse, RedirectResponse]:
    """
    パスワードリセットページ

    :param request: リクエストデータ
    :param inertia: Inertiaインスタンス
    :param token: リセットトークン
    :param email: メールアドレス
    :param success: 成功フラグ
    :return: レスポンスデータ
    """

    current_user = request.session.get("user")
    if current_user:
        # ログイン済み
        return RedirectResponse(
            url="/dashboard",
            status_code=status.HTTP_302_FOUND,
        )

    user_locale = get_user_locale_from_request(request)
    set_current_locale(user_locale)

    # セッションからフラッシュエラーメッセージを取得
    flash_error = request.session.pop("flash_error", None)
    error_message = None
    if flash_error:
        error_message = i18n.t(flash_error, user_locale)

    if not token or not email:
        return await inertia.render(
            "Password/ResetPassword",
            {
                "success": False,
                "error": i18n.t("ui.password_reset.errors.token_invalid", user_locale),
                "token": "",
                "email": "",
                **get_i18n_data_for_response(user_locale),
            },
        )

    return await inertia.render(
        "Password/ResetPassword",
        {
            "success": success,
            "error": error_message,
            "token": token,
            "email": email,
            **get_i18n_data_for_response(user_locale),
        },
    )


@router.post(
    "/reset-password",
    response_model=None,
    summary="パスワードリセット処理",
    description="パスワードリセット処理を行います。",
    operation_id="reset_password_submit",
)
async def reset_password_submit(
    request: Request,
    inertia: InertiaDep,
    reset_data: ResetPasswordRequest,
    db: DbDep,
    password_service: PasswordService = Depends(provide_password_service),
) -> Union[InertiaResponse, RedirectResponse]:
    """
    パスワードリセット処理

    :param request: リクエストデータ
    :param inertia: Inertiaインスタンス
    :param reset_data: リセットデータ
    :param db: DBセッション
    :param password_service: パスワードサービス
    :return: レスポンスデータ
    """

    user_locale = get_user_locale_from_request(request)
    set_current_locale(user_locale)

    try:
        # パスワードリセットを実行する
        password_service.reset_password(
            db=db,
            email=reset_data.email,
            reset_code=reset_data.reset_code,
            new_password=reset_data.new_password,
        )
        return RedirectResponse(
            url="/login?message=password_reset_success",
            status_code=status.HTTP_302_FOUND,
        )
    except BadRequestException:
        request.session["flash_error"] = "ui.password_reset.errors.reset_failed"
        return RedirectResponse(
            url=f"/reset-password?email={reset_data.email}&token={reset_data.token}",
            status_code=302,
        )
    except Exception:
        request.session["flash_error"] = "ui.password_reset.errors.reset_failed"
        return RedirectResponse(
            url=f"/reset-password?email={reset_data.email}&token={reset_data.token}",
            status_code=302,
        )

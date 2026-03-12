"""
ルーター（パスワードAPI）
"""

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.api.di.auth_dependency import get_current_user_from_session
from app.api.di.auth_di import provide_password_service
from app.api.di.mail_di import provide_template_mail_sender
from app.api.infra.mail.template_mail_sender import TemplateMailSender
from app.api.infra.services.password_service import PasswordService
from app.core.config import settings
from app.core.errors.codes import ErrorCode
from app.core.exception import BadRequestException
from app.core.i18n.error_message import ErrorMessage
from app.core.response import public_api_responses
from app.db.database import get_master_db
from app.models.user import User
from app.schemas.error_response import APISuccessResponse

from .schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

router = APIRouter(responses=public_api_responses)


@router.post(
    "/change-password",
    response_model=APISuccessResponse,
    summary="パスワード変更API",
    description="ログインユーザーのパスワードを変更します。",
    operation_id="auth_change_password",
)
async def change_password(
    request_data: ChangePasswordRequest,
    db: Session = Depends(get_master_db),
    current_user: User = Depends(get_current_user_from_session),
    password_service: PasswordService = Depends(provide_password_service),
) -> APISuccessResponse:
    """
    パスワード変更API

    :param request_data: リクエストデータ
    :param db: DBセッション
    :param current_user: ログインユーザー
    :param password_service: パスワードサービス
    :return: レスポンスデータ
    """

    try:
        password_service.change_password(
            db=db,
            user=current_user,
            current_password=request_data.current_password,
            new_password=request_data.new_password,
        )
        return APISuccessResponse(
            message=ErrorMessage(ErrorCode.PASSWORD_CHANGE_SUCCESS).value,
        )
    except Exception as e:
        if isinstance(e, BadRequestException):
            raise e

        raise BadRequestException(
            error_code=ErrorCode.PASSWORD_CHANGE_FAILED,
            message=ErrorMessage(ErrorCode.PASSWORD_CHANGE_FAILED).value,
        )


@router.post(
    "/forgot-password",
    response_model=APISuccessResponse,
    summary="パスワードリマインダーAPI",
    description="パスワードリセット用のメールを送信します。",
    operation_id="auth_forgot_password",
)
async def forgot_password(
    request_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_master_db),
    mail_sender: TemplateMailSender = Depends(provide_template_mail_sender),
    password_service: PasswordService = Depends(provide_password_service),
) -> APISuccessResponse:
    """
    パスワードリマインダーAPI

    :param request_data: リクエストデータ
    :param background_tasks: バックグラウンドタスク
    :param db: データベースセッション
    :param mail_sender: メール送信サービス
    :param password_service: パスワードサービス
    :return: レスポンスデータ
    """

    try:
        user = password_service.get_user_by_email(db, request_data.email)
        if user:
            reset_token = password_service.create_password_reset_token(db, user)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}&email={user.email}"

            # リマインダーメールを送信する
            mail_sender.send_password_reset_mail(
                to_email=user.email,
                user_name=user.name,
                reset_url=reset_url,
                reset_code=reset_token.reset_code,
                expires_in=30,  # 30分
                background_tasks=background_tasks,
            )

        return APISuccessResponse(
            message=ErrorMessage(ErrorCode.PASSWORD_RESET_EMAIL_SENT).value,
        )
    except Exception as e:
        if isinstance(e, BadRequestException):
            raise e

        raise BadRequestException(
            error_code=ErrorCode.PASSWORD_RESET_PROCESS_FAILED,
            message=ErrorMessage(ErrorCode.PASSWORD_RESET_PROCESS_FAILED).value,
        )


@router.post(
    "/reset-password",
    response_model=APISuccessResponse,
    summary="パスワードリセットAPI",
    description="リセットコードを使用してパスワードをリセットします。",
    operation_id="auth_reset_password",
)
async def reset_password(
    request_data: ResetPasswordRequest,
    db: Session = Depends(get_master_db),
    password_service: PasswordService = Depends(provide_password_service),
) -> APISuccessResponse:
    """
    パスワードリセットAPI

    :param request_data: リクエストデータ
    :param db: DBセッション
    :param password_service: パスワードサービス
    :return: レスポンスデータ
    """

    try:
        password_service.reset_password(
            db=db,
            email=request_data.email,
            reset_code=request_data.reset_code,
            new_password=request_data.new_password,
        )
        return APISuccessResponse(
            message=ErrorMessage(ErrorCode.PASSWORD_RESET_SUCCESS).value
        )
    except Exception as e:
        if isinstance(e, BadRequestException):
            raise e

        raise BadRequestException(
            error_code=ErrorCode.PASSWORD_RESET_FAILED,
            message=ErrorMessage(ErrorCode.PASSWORD_RESET_FAILED).value,
        )
